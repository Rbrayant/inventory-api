# Inventory Tracker CI/CD

Technical implementation and verification report

Course: Foundations and Efficient Operation of Modern Infrastructure

Assignment: End-to-End CI/CD Pipeline with GitHub, Docker, and Kubernetes

Prepared: 15 November 2026

## Purpose

This project packages a Flask inventory API as a Docker image and provides a GitHub Actions pipeline that validates, scans, publishes and deploys the application to Kubernetes. It supports the initial release, a low-stock filtering feature and a quantity-validation bug fix through separate source snapshots and a documented PR workflow.

## Verification status

The implementation has passed local Python tests, lint checks, release-snapshot checks and a real HTTP smoke test with two Gunicorn workers. The negative-quantity regression fails against the earlier source as expected. These are local results. No GitHub repository, registry publication, Kubernetes deployment or instructor demonstration was executed from this workspace.

The PostgreSQL integration test is included and configured for CI, but skipped locally because no test PostgreSQL server was supplied. Docker, Trivy and kubectl are not available in this workspace. Their execution results remain pending.

## Submission completion

Before submission, perform the three actual releases, add the repository and PR URLs, attach real CI/CD and deployment evidence, and update this report and the presentation with verified findings. Prepared source files and documentation do not establish that the practical requirements have been completed.

# 1. Architecture

Hosted CI runners perform validation and image publication. A trusted self-hosted runner on the Kubernetes host performs deployment, because a hosted runner cannot be assumed to reach a private kind cluster. The runner reads a scoped kubeconfig from a protected GitHub Environment secret.

The Kubernetes Service routes traffic to two API replicas. Every worker uses the same PostgreSQL database. A persistent volume retains records across database pod restarts within the cluster. Configuration and credentials enter containers through ConfigMap and Secret references.

Architecture: architecture.svg and architecture.dot

# 2. Application and storage

The API provides item creation, listing, quantity updates and deletion. Write requests require a bearer token. Names and SKUs must contain 1-120 non-whitespace characters. In the final release, quantities must be whole numbers from 0 to 2147483647; negative values, fractions, booleans, strings and null are rejected. SKUs must be unique.

Route | Behavior

GET /health | Process liveness, independent of database availability.

GET /ready | Tests database connectivity and the items table. Returns 503 if unavailable.

GET /version | Reports application name, configured release version and Git revision.

GET /items | Lists records, with low-stock filtering below five from v1.1.0.

POST /items | Creates a validated stock item with a unique SKU and database-generated ID.

PATCH /items/<id> | Updates quantity, with the negative-quantity check introduced in v1.2.0.

DELETE /items/<id> | Deletes a record or returns 404 when it does not exist.

## Shared records

The original process-local dictionary could produce different results for different workers or replicas. SQLAlchemy now connects the application to a shared database. Local Python tests use isolated SQLite files. Docker Compose and Kubernetes use PostgreSQL. Inserts use database-generated IDs and transactional writes.

## Schema initialization

The init-db command creates the schema before application rollout. PostgreSQL initialization uses an advisory transaction lock to serialize concurrent initialization. Worker startup does not create tables. The three demonstration releases share the same schema; a general migration framework is outside this implementation.

# 3. CI and image publication

## Validation triggers

The CI workflow runs for pushes to dev and PRs targeting dev or main. It checks out the source, installs Python dependencies, lints app/tests/scripts, and runs the unit and integration tests. GitHub supplies a disposable PostgreSQL service for the integration test. A failed test stops subsequent image steps.

## Build and security gate

CI builds one image and scans it with Trivy. HIGH and CRITICAL vulnerabilities with available fixes fail validation. The workflow records a scan artifact. Only successful validation exports the Docker image as an artifact for publication. The release workflow invokes this same CI workflow, so it cannot bypass its scan gate.

## Release identifiers

A main push starts the release pipeline. Publication requires successful validation, a semantic VERSION value greater than the parent main revision, and an unused Git release tag. The workflow downloads and loads the exact image artifact that passed scanning, then publishes a version tag and a commit-SHA tag to GHCR. It records the image digest and creates the Git release tag.

Kubernetes receives an image reference containing the content digest. A digest identifies fixed image content even if a registry tag later changes. Version-tag protection also depends on repository rules and trusted registry writers. The setup guide requires protected branches, restricted release tags and reviewed PR merges.

## Failure and retry behavior

A release identifier is consumed once publication and tagging complete. Deployment-only failures can be retried using Re-run failed jobs without rebuilding or replacing the successful image. Changed source requires a new patch version. A full rerun of successful publication is intentionally rejected if its release tag already exists.

# 4. Kubernetes and deployment

Component | Implementation

Deployment | Two API replicas; two Gunicorn workers per pod.

Service | NodePort Service, port 80 to container port 8000. Port-forward provides host access.

Configuration | APP_NAME from ConfigMap. API_TOKEN and DATABASE_URL from a Secret.

Readiness / liveness | Readiness uses /ready; liveness uses /health.

Resources | API requests 100m CPU / 128Mi; limits 500m CPU / 256Mi per replica.

Rolling update | maxSurge 1 and maxUnavailable 0, with retained rollout history.

Database | One PostgreSQL replica, Recreate strategy, 1Gi persistent claim.

Jobs | Per-run schema initialization and Service-level smoke verification.

## Deployment sequence

The deployment runner creates a temporary kubeconfig from the protected secret, checks the provisioned application/database Secrets, applies PostgreSQL resources and waits for readiness. It runs the schema job, applies ConfigMap, Service and API Deployment, and waits for the rolling update to finish.

A smoke Job uses the same published image. It connects through the Kubernetes Service, checks readiness and the expected version/revision, creates a record, confirms repeated list requests see it and deletes it. Any failed check fails the deployment job. Workflow artifacts retain status, events, rollout and smoke logs.

## Recovery limits

On application-update failure, the script attempts to restore the previous API pod template and waits for that rollback. The original job still fails. An initial release has no earlier revision to restore. Rollback does not undo database contents, schema changes or ConfigMap changes. PostgreSQL is persistent but has one replica and is not highly available.

# 5. Releases and test evidence

Release | Source change | Local verification

v1.0.0 | Initial API and pipeline. Negative-quantity validation intentionally absent. | 13 passing tests; PostgreSQL test skipped.

v1.1.0 | Adds low-stock filtering and its automated test. | 14 passing tests; PostgreSQL test skipped.

v1.2.0 | Rejects invalid quantities and adds boundary/regression tests. | 29 passing tests; PostgreSQL test skipped.

## Regression demonstration

The included local regression log runs the negative-quantity test against v1.1.0. That source accepts -1 and returns HTTP 200, so the expected HTTP 400 assertion fails. Applying the v1.2.0 source changes the response to 400 and preserves the previous stored value. The final suite passes.

## Additional local checks

Lint checks pass for app, tests and scripts. Bash syntax checks pass for the deployment and secret-creation scripts. A real HTTP smoke test against two Gunicorn worker processes confirms application availability, expected version/revision and shared records using SQLite. This test does not establish PostgreSQL or Kubernetes behavior.

## Evidence locations

docs/evidence/local-checks.txt records the final suite and lint results. release-checks.txt records all three source snapshots. expected-regression.txt records the intentional old-source failure. http-smoke.txt records the multi-worker HTTP check. Remote workflow, GHCR and Kubernetes evidence is explicitly pending in releases.md.

## Required remote demonstration

Follow RELEASE_DEMO.md to commit the initial release, merge the feature through PRs, commit the failing regression test without merging it, then fix and release v1.2.0. Save the failed and successful workflow URLs. Show the failing revision never reaches the registry or running application. During assessment, make another genuine source change and demonstrate the automated update live.

# 6. Security and completion

## Credential handling

Application/database secrets are generated on the cluster host and are absent from source control. The deployer uses a namespace-scoped service account, with its kubeconfig supplied through the production Environment secret. The helper creates an expiring token, so refresh it before later sessions. The runner deletes its temporary kubeconfig after execution.

The API image runs as a non-root user. API pods disable service-account token mounting, drop Linux capabilities and disallow privilege escalation. The trusted deployment runner must be isolated from untrusted contributors. Kubernetes Secrets use base64 encoding and require cluster access controls; base64 alone does not encrypt data.

## Troubleshooting approach

Read the failed stage before changing configuration. CI failures require checking lint/test output or the scan report. ImagePullBackOff usually requires checking registry visibility and pull credentials. Pending storage requires checking the default StorageClass. A readiness failure requires checking database connectivity and schema initialization. The setup guide provides diagnostic commands and credential-expiry remedies.

Requirement evidence | Current status

Source, Dockerfile, workflows and manifests | Included and locally reviewed.

Local tests, lint and HTTP smoke | Executed; logs included.

Docker build and vulnerability scan | Configured; execution pending.

GitHub repository, reviews and three release runs | Must be performed in the user account.

Running Kubernetes application and rollout evidence | Must be performed on a functioning cluster.

Report and ten-slide presentation | Prepared; update with actual remote results.

Live assessment source change | Required during assessment.

## Source basis

Requirements were taken from the supplied CI_CD_Docker_Kubernetes_Student_Assignment.pdf, Tasks 1-7 and submission/practical-demonstration sections. Implementation details come from the accompanying source, workflows, manifests and local logs. No external execution results or screenshots have been invented.
