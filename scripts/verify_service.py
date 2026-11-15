"""Run inside the cluster to test the Service and shared database."""
import json
import os
import time
from uuid import uuid4
import urllib.error
import urllib.request

base = os.getenv("BASE_URL", "http://inventory-api")
expected = os.environ["EXPECTED_VERSION"]
revision = os.environ["EXPECTED_REVISION"]
token = os.environ["API_TOKEN"]


def call(path, method="GET", data=None):
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(
        base + path, data=body, method=method,
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + token},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read()) if response.status != 204 else None


for attempt in range(30):
    try:
        for _ in range(5):
            call("/ready")
            version = call("/version")
            assert version["version"] == expected, version
            assert version["revision"] == revision, version
        break
    except (OSError, AssertionError, urllib.error.URLError):
        if attempt == 29:
            raise
        time.sleep(2)
record = call("/items", "POST", {
    "name": "Pipeline smoke test", "sku": "SMOKE-" + uuid4().hex,
    "quantity": 10,
})
try:
    for _ in range(10):
        assert any(s["id"] == record["id"] for s in call("/items"))
finally:
    call(f"/items/{record['id']}", "DELETE")
print(f"Service ready, shared storage verified: {expected} ({revision})")
