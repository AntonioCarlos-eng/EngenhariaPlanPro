import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_conn():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg2.connect(dsn, cursor_factory=RealDictCursor)


def fetch_one(sql, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or [])
            return cur.fetchone()


def fetch_all(sql, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or [])
            return cur.fetchall()


def execute(sql, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or [])
            conn.commit()


def execute_returning(sql, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or [])
            row = cur.fetchone()
            conn.commit()
            return row
