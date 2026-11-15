# Run Inventory Tracker on Windows with Ubuntu WSL

This corrected archive is separate from your running student project. Keep the
student folder, .env and volume intact. Inventory uses port 8001 and a separate
Compose project/database volume.

## Extract the corrected ZIP

Use the corrected ZIP downloaded after this review, not the earlier 13KB archive.
In Ubuntu, replace the ZIP filename below if your browser adds (1) or (2):

```bash
mkdir -p ~/inventory-assignment
unzip "/mnt/c/Users/Cherii/Downloads/inventory-api.zip" -d ~/inventory-assignment
cd ~/inventory-assignment/inventory-api
ls
```

## Create credentials once and start Docker

Run only on the first setup. Never regenerate .env over a database with existing
credentials unless intentionally rotating them correctly.

```bash
umask 077
printf 'DB_PASSWORD=%s\nAPI_TOKEN=%s\n' "$(openssl rand -hex 24)" "$(openssl rand -hex 24)" > .env
docker compose up --build -d
docker compose ps -a
curl -fsS http://localhost:8001/health
curl -fsS http://localhost:8001/ready
curl -fsS http://localhost:8001/version
```

The migration container should exit with code 0. The API and database stay up.
If the API is still starting, wait a few seconds and repeat the health checks.

## Try the inventory API

```bash
set -a
source .env
set +a
curl -sS -i -X POST http://localhost:8001/items \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"USB Cable","sku":"USB-001","quantity":3}'
curl -fsS http://localhost:8001/items
curl -fsS 'http://localhost:8001/items?low_stock=true'
```

A duplicate SKU returns HTTP 409. Use the returned item ID to update its quantity.
The final v1.2.0 source rejects negative, fractional, boolean and text quantities.
Open http://localhost:8001/items in your Windows browser to view the JSON API.

## Next stages

Read README.md, then docs/SETUP.md. For the three actual GitHub releases, follow
docs/RELEASE_DEMO.md. Prepare v1.0.0 before the first main push to a new repository.
The initial and feature snapshots intentionally preserve the negative-quantity
bug so you can demonstrate the failing regression before deploying the fix.
All snapshots share the same database schema. Never invent CI or deployment logs.
