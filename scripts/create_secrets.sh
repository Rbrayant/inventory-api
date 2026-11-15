#!/usr/bin/env bash
# Run on the cluster host. Generated values are never printed.
set -euo pipefail
set +x
kubectl create namespace inventory-api --dry-run=client -o yaml | kubectl apply -f -
if kubectl -n inventory-api get secret postgres-secret >/dev/null 2>&1; then
  echo "Secrets already exist. Do not rotate database credentials implicitly." >&2
  exit 1
fi
tmp=$(mktemp -d)
chmod 700 "$tmp"
trap 'rm -rf "$tmp"' EXIT
password=$(openssl rand -hex 24)
token=$(openssl rand -hex 24)
printf 'POSTGRES_USER=item\nPOSTGRES_DB=items\nPOSTGRES_PASSWORD=%s\n' "$password" > "$tmp/postgres.env"
printf 'API_TOKEN=%s\nDATABASE_URL=postgresql+psycopg://item:%s@postgres:5432/items\n' "$token" "$password" > "$tmp/api.env"
kubectl -n inventory-api create secret generic postgres-secret --from-env-file="$tmp/postgres.env"
kubectl -n inventory-api create secret generic inventory-api-secret --from-env-file="$tmp/api.env"
echo "Created secrets. Keep database credentials consistent with existing PVC data."
