#!/usr/bin/env bash
# Short-lived, namespace-scoped kubeconfig for the protected GitHub secret.
set -euo pipefail
set +x
umask 077
output="${1:-/tmp/item-runner-kubeconfig.b64}"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kubectl config view --raw --minify --flatten -o json > "$tmp/current.json"
kubectl -n inventory-api create token item-deployer --duration=24h > "$tmp/token"
python3 - "$tmp" "$output" <<'PYTHON'
import base64
import json
import sys
from pathlib import Path
folder = Path(sys.argv[1])
source = json.loads((folder / "current.json").read_text())
cluster = source["clusters"][0]["cluster"]
if not cluster.get("certificate-authority-data"):
    raise SystemExit("A trusted cluster CA is required")
config = {
    "apiVersion": "v1", "kind": "Config",
    "clusters": [{"name": "lab", "cluster": cluster}],
    "users": [{"name": "deployer", "user": {
        "token": (folder / "token").read_text().strip()}}],
    "contexts": [{"name": "lab", "context": {
        "cluster": "lab", "user": "deployer", "namespace": "inventory-api"}}],
    "current-context": "lab",
}
Path(sys.argv[2]).write_bytes(base64.b64encode(json.dumps(config).encode()))
PYTHON
echo "Wrote protected runner configuration to $output"
echo "Token expires within 24 hours, subject to cluster policy. Refresh before assessment."
