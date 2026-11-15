#!/usr/bin/env bash
set -euo pipefail
: "${IMAGE:?}" "${DIGEST:?}" "${VERSION:?}" "${GITHUB_SHA:?}" "${GITHUB_RUN_ID:?}"
run_id="${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}"
export RUN_ID="$run_id"
mkdir -p rendered/evidence
k() { kubectl -n inventory-api "$@"; }
previous=$(k get deployment inventory-api -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || true)
changed=0
finish() {
  result=$?
  trap - EXIT
  set +e
  k get pods,svc,pvc -o wide > rendered/evidence/resources.txt 2>&1
  k describe deployment inventory-api > rendered/evidence/deployment.txt 2>&1
  k rollout history deployment/inventory-api > rendered/evidence/history.txt 2>&1
  k get events --sort-by=.lastTimestamp > rendered/evidence/events.txt 2>&1
  if [ "$result" -ne 0 ] && [ "$changed" -eq 1 ] && [ -n "$previous" ]; then
    echo "Deployment failed. Attempting rollback to previous pod template."
    k rollout undo deployment/inventory-api
    k rollout status deployment/inventory-api --timeout=180s > rendered/evidence/rollback.txt 2>&1
  fi
  exit "$result"
}
trap finish EXIT
k get secret inventory-api-secret postgres-secret >/dev/null
python3 - <<'PYTHON'
import os
from pathlib import Path
values = {"__IMAGE__": os.environ["IMAGE"],
          "__DIGEST__": os.environ["DIGEST"],
          "__VERSION__": os.environ["VERSION"],
          "__REVISION__": os.environ["GITHUB_SHA"],
          "__RUN_ID__": os.environ["RUN_ID"]}
for name in ["deployment", "init-db", "smoke"]:
    content = Path(f"k8s/{name}.yaml").read_text()
    for key, value in values.items():
        content = content.replace(key, value)
    Path(f"rendered/{name}.yaml").write_text(content)
PYTHON
k apply -f k8s/postgres.yaml
k rollout status deployment/postgres --timeout=180s
k apply -f rendered/init-db.yaml
if ! k wait --for=condition=complete "job/init-db-$run_id" --timeout=130s; then
  k logs "job/init-db-$run_id" > rendered/evidence/init-db.txt 2>&1 || true
  exit 1
fi
k logs "job/init-db-$run_id" > rendered/evidence/init-db.txt
k apply -f k8s/configmap.yaml -f k8s/service.yaml
# Mark before apply, so a partially accepted update still triggers rollback.
changed=1
k apply -f rendered/deployment.yaml
k rollout status deployment/inventory-api --timeout=180s | tee rendered/evidence/rollout.txt
k apply -f rendered/smoke.yaml
if ! k wait --for=condition=complete "job/smoke-$run_id" --timeout=130s; then
  k logs "job/smoke-$run_id" > rendered/evidence/smoke.txt 2>&1 || true
  exit 1
fi
k logs "job/smoke-$run_id" | tee rendered/evidence/smoke.txt
printf 'version=%s\nrevision=%s\nimage=%s@%s\n' "$VERSION" "$GITHUB_SHA" "$IMAGE" "$DIGEST" > rendered/evidence/release.txt
echo "Deployment and Service verification succeeded."
