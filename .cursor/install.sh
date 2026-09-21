#!/usr/bin/env bash
# Idempotent repository bootstrap for the EngenhariaPlanPro Cloud Agent environment.
# Installs system + Python dependencies and prepares the local PostgreSQL database
# used by the license_server. Safe to run repeatedly.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "==> Installing system packages"
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get install -y -qq \
  python3-tk python3-venv python3-dev \
  postgresql postgresql-contrib libpq-dev \
  fonts-dejavu

echo "==> Creating Python virtualenv (.venv)"
if [ ! -x ".venv/bin/python" ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip -q
pip install -q -r requirements.txt
pip install -q -r license_server/requirements.txt

echo "==> Ensuring PostgreSQL cluster is running"
sudo pg_ctlcluster 16 main start 2>/dev/null || true
# Wait for the socket to accept connections.
for _ in $(seq 1 30); do
  if sudo -u postgres pg_isready -q; then break; fi
  sleep 1
done

echo "==> Provisioning license database (idempotent)"
sudo -u postgres psql -v ON_ERROR_STOP=1 <<'SQL'
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='license') THEN
    CREATE ROLE license LOGIN PASSWORD 'license';
  END IF;
END $$;
SQL
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='licensedb'" | grep -q 1 \
  || sudo -u postgres createdb -O license licensedb

echo "==> Applying schema"
PGPASSWORD=license psql -h 127.0.0.1 -U license -d licensedb -q -f license_server/models.sql

echo "==> Seeding a demo license (idempotent)"
PGPASSWORD=license psql -h 127.0.0.1 -U license -d licensedb -q <<'SQL'
INSERT INTO customers (name, email)
  SELECT 'Demo Customer', 'demo@example.com'
  WHERE NOT EXISTS (SELECT 1 FROM customers WHERE email='demo@example.com');
INSERT INTO licenses (customer_id, license_key, status, max_devices, expires_at)
  SELECT (SELECT id FROM customers WHERE email='demo@example.com' LIMIT 1),
         'DEMO-KEY-0001', 'active', 3, NOW() + INTERVAL '365 days'
  WHERE NOT EXISTS (SELECT 1 FROM licenses WHERE license_key='DEMO-KEY-0001');
SQL

echo "==> install.sh complete"
