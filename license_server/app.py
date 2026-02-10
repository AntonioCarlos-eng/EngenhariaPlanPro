import os
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from db import fetch_one, execute, execute_returning


APP_NAME = "license-api"
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ADMIN_KEY = os.getenv("ADMIN_KEY", "change-me")
ACCESS_TTL_DAYS = int(os.getenv("ACCESS_TTL_DAYS", "7"))
REFRESH_TTL_DAYS = int(os.getenv("REFRESH_TTL_DAYS", "30"))

app = FastAPI(title=APP_NAME)


class ActivatePayload(BaseModel):
    license_key: str
    device_id: str
    device_name: Optional[str] = None
    app_version: Optional[str] = None


class RefreshPayload(BaseModel):
    refresh_token: str
    device_id: str


class CheckPayload(BaseModel):
    access_token: str


class RevokePayload(BaseModel):
    license_key: Optional[str] = None
    device_id: Optional[str] = None


def _now():
    return datetime.utcnow()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _make_access_token(license_id: int, device_id: str) -> str:
    exp = _now() + timedelta(days=ACCESS_TTL_DAYS)
    payload = {
        "license_id": license_id,
        "device_id": device_id,
        "exp": int(exp.timestamp())
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def _audit(event_type: str, license_key: Optional[str], device_id: Optional[str], app_version: Optional[str], ip: Optional[str]):
    execute(
        """
        INSERT INTO audit_logs (event_type, license_key, device_id, app_version, ip_address)
        VALUES (%s, %s, %s, %s, %s)
        """,
        [event_type, license_key, device_id, app_version, ip]
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/activate")
def activate(payload: ActivatePayload, request: Request):
    lic = fetch_one(
        """
        SELECT id, license_key, status, max_devices, expires_at
        FROM licenses
        WHERE license_key = %s
        """,
        [payload.license_key]
    )

    if not lic or lic["status"] != "active":
        _audit("activate_denied", payload.license_key, payload.device_id, payload.app_version, request.client.host)
        raise HTTPException(status_code=403, detail="license_invalid")

    if lic["expires_at"] <= _now():
        _audit("activate_expired", payload.license_key, payload.device_id, payload.app_version, request.client.host)
        raise HTTPException(status_code=403, detail="license_expired")

    device = fetch_one(
        """
        SELECT id, device_id, active
        FROM devices
        WHERE license_id = %s AND device_id = %s
        """,
        [lic["id"], payload.device_id]
    )

    if device and not device["active"]:
        _audit("activate_blocked", payload.license_key, payload.device_id, payload.app_version, request.client.host)
        raise HTTPException(status_code=403, detail="device_blocked")

    if not device:
        count_row = fetch_one(
            "SELECT COUNT(*) AS cnt FROM devices WHERE license_id = %s AND active = TRUE",
            [lic["id"]]
        )
        if count_row and count_row["cnt"] >= lic["max_devices"]:
            _audit("activate_limit", payload.license_key, payload.device_id, payload.app_version, request.client.host)
            raise HTTPException(status_code=403, detail="device_limit")

        device = execute_returning(
            """
            INSERT INTO devices (license_id, device_id, device_name, app_version, last_seen, active)
            VALUES (%s, %s, %s, %s, NOW(), TRUE)
            RETURNING id, device_id
            """,
            [lic["id"], payload.device_id, payload.device_name, payload.app_version]
        )
    else:
        execute(
            """
            UPDATE devices SET last_seen = NOW(), device_name = %s, app_version = %s
            WHERE id = %s
            """,
            [payload.device_name, payload.app_version, device["id"]]
        )

    refresh_token = str(uuid.uuid4())
    refresh_hash = _hash_token(refresh_token)
    refresh_exp = _now() + timedelta(days=REFRESH_TTL_DAYS)

    execute(
        """
        INSERT INTO refresh_tokens (device_id, token_hash, expires_at)
        VALUES (%s, %s, %s)
        """,
        [device["id"], refresh_hash, refresh_exp]
    )

    access_token = _make_access_token(lic["id"], payload.device_id)

    _audit("activate_ok", payload.license_key, payload.device_id, payload.app_version, request.client.host)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": int(( _now() + timedelta(days=ACCESS_TTL_DAYS) ).timestamp()),
        "license_expires_at": int(lic["expires_at"].timestamp()),
        "max_devices": lic["max_devices"]
    }


@app.post("/refresh")
def refresh(payload: RefreshPayload, request: Request):
    token_hash = _hash_token(payload.refresh_token)
    row = fetch_one(
        """
        SELECT rt.id AS token_id, rt.expires_at, rt.revoked,
               d.id AS device_db_id, d.device_id, d.license_id
        FROM refresh_tokens rt
        JOIN devices d ON d.id = rt.device_id
        WHERE rt.token_hash = %s
        """,
        [token_hash]
    )

    if not row or row["revoked"]:
        raise HTTPException(status_code=403, detail="refresh_invalid")

    if row["expires_at"] <= _now():
        raise HTTPException(status_code=403, detail="refresh_expired")

    if row["device_id"] != payload.device_id:
        raise HTTPException(status_code=403, detail="device_mismatch")

    execute(
        "UPDATE devices SET last_seen = NOW() WHERE id = %s",
        [row["device_db_id"]]
    )

    access_token = _make_access_token(row["license_id"], payload.device_id)

    return {
        "access_token": access_token,
        "expires_at": int(( _now() + timedelta(days=ACCESS_TTL_DAYS) ).timestamp())
    }


@app.post("/check")
def check(payload: CheckPayload):
    try:
        decoded = jwt.decode(payload.access_token, SECRET_KEY, algorithms=["HS256"])
        return {"valid": True, "license_id": decoded.get("license_id"), "device_id": decoded.get("device_id")}
    except Exception:
        return {"valid": False}


@app.post("/revoke")
def revoke(payload: RevokePayload, x_admin_key: Optional[str] = Header(default=None)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="admin_denied")

    if payload.device_id:
        execute(
            "UPDATE devices SET active = FALSE WHERE device_id = %s",
            [payload.device_id]
        )

    if payload.license_key:
        execute(
            "UPDATE licenses SET status = 'revoked' WHERE license_key = %s",
            [payload.license_key]
        )

    return {"ok": True}
