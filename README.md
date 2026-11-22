# Inventory Tracker: Docker and Kubernetes CI/CD

A Flask item API with shared PostgreSQL storage, automated tests, image
scanning, GHCR publication and verified Kubernetes rolling updates.

**Status:** corrected implementation, with local test evidence. GitHub runs,
registry publication and Kubernetes deployment still need to be performed in
your environment. No remote success or release history is claimed.

## Start here

Use **Ubuntu in WSL or an Ubuntu VM**, not Windows PowerShell, for the Bash
commands in this guide. Docker Desktop can supply Docker through WSL integration.
The inventory app uses host port **8001**, so your existing student app on
port 8000 can remain running. The projects use separate database volumes.
Run commands from this project's extracted `inventory-api` directory.

1. Read `docs/SETUP.md` for GitHub, Docker and Kubernetes setup.
2. Follow `docs/RELEASE_DEMO.md` to perform the three actual releases.
3. Add real screenshots, logs and links to `docs/evidence/`.
4. Update the report and presentation with your remote evidence before submission.

The ZIP contains the final corrected v1.2.0 source. For a fresh assignment
repository, prepare v1.0.0 **before your first push to main**, as described in the
release guide. The `demo/` folders are source snapshots, not Git history.

## API

| Method | Path | Purpose | Authentication |
|---|---|---|---|
| GET | `/health` | Process liveness | None |
| GET | `/ready` | Database and schema readiness | None |
| GET | `/version` | Application version and Git revision | None |
| GET | `/items` | List records | None |
| POST | `/items` | Create a item | Bearer token |
| PATCH | `/items/<id>` | Update a nonnegative integer quantity | Bearer token |
| DELETE | `/items/<id>` | Delete a item | Bearer token |

From v1.1.0, GET `/items?low_stock=true` returns items with a quantity below five.
SKUs are unique. Quantities are whole numbers from 0 to 2147483647.
The negative-quantity check is introduced in v1.2.0. Earlier demo snapshots deliberately
retain that documented bug for the regression demonstration.

## Run without Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export API_TOKEN=$(openssl rand -hex 24)
export APP_VERSION=$(cat VERSION)
flask --app app.main init-db
flask --app app.main run --port 8001
```

SQLite is the local default. Kubernetes and Compose use PostgreSQL so all API
workers and replicas share records. Keep this terminal open. In a second terminal:

```bash
curl -fsS http://localhost:8001/health
curl -fsS http://localhost:8001/version
curl -fsS http://localhost:8001/items
```

## Tests

```bash
python -m flake8 app tests scripts
python -m pytest -q -ra
```

The PostgreSQL integration test skips unless `TEST_POSTGRES_URL` points to a
**disposable test database**. It creates and drops the items table. CI provides
an isolated PostgreSQL service and runs this test automatically.

## Run with Docker (host port 8001)

```bash
umask 077
printf 'DB_PASSWORD=%s\nAPI_TOKEN=%s\n' "$(openssl rand -hex 24)" "$(openssl rand -hex 24)" > .env
docker compose up --build -d
curl -fsS http://localhost:8001/ready
curl -fsS http://localhost:8001/version
docker compose ps
docker compose logs api
```

`.env` is ignored by Git. Docker's health check tests `/health`; Kubernetes
readiness checks `/ready`. `docker compose down` retains the database volume.

## Pipeline

CI on `dev` pushes and PRs installs dependencies, lints, tests against SQLite
and PostgreSQL, builds a Docker image and scans it with Trivy. HIGH/CRITICAL
findings with available fixes block the pipeline. The saved image artifact exists
only after all checks pass.

On a main push, CD invokes the same CI workflow, downloads its exact validated
image, checks that VERSION increases and its Git release tag is unused, then
publishes version and commit tags to GHCR. It deploys by immutable image digest.
A self-hosted runner applies configuration, initializes the schema, waits for the
rollout and runs a smoke test through the Kubernetes Service. A failed check
keeps the job failed and attempts to restore the previous API pod template.

Use protected main and dev branches, PR review and the required CI check.
Protect release tags against changes and avoid manual image tag replacement.
A pushed version is a consumed release identifier. For a deployment-only failure,
use Re-run failed jobs after fixing the environment. Do not rerun successful
publish jobs or overwrite release tags. Source changes require a new patch version.

## Submission files

- `docs/Technical_Report.pdf`: implementation and local verification, with remote
  evidence explicitly pending.
- `docs/Presentation.pptx`: ten editable slides for the practical presentation.
- `docs/architecture.svg`: architecture diagram.
- `docs/evidence/local-checks.txt`: actual local verification output.
- `docs/EVIDENCE_CHECKLIST.md`: required remote evidence to add.


