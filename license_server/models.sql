-- PostgreSQL schema for licensing

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS licenses (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    license_key TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    max_devices INTEGER NOT NULL DEFAULT 1,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    license_id INTEGER REFERENCES licenses(id),
    device_id TEXT NOT NULL,
    device_name TEXT,
    app_version TEXT,
    last_seen TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (license_id, device_id)
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    token_hash TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    revoked BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    license_key TEXT,
    device_id TEXT,
    app_version TEXT,
    ip_address TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
