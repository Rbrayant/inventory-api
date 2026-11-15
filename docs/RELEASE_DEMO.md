# Three real releases and a blocked regression

These steps create genuine commits, PRs, pipeline runs and deployments in your
account. The source snapshots are preparation material. They are not evidence
that these releases have already happened. Use a new empty assignment repository;
do not overwrite an existing repository's history.

## Initial release: v1.0.0

Complete SETUP.md. Prepare the initial source before the first main push:

```bash
python scripts/prepare_release.py v1.0.0
python -m flake8 app tests scripts
python -m pytest -q -ra
git init -b main
git add .
git commit -m "Initial item API and validated Kubernetes pipeline"
git remote add origin https://github.com/YOUR-USERNAME/inventory-api.git
git push -u origin main
```

Replace YOUR-USERNAME with your actual username. The main push invokes CD,
which validates, publishes v1.0.0 and deploys it. Ensure GHCR visibility is ready
before the cluster tries to pull it. Configure branch protection after bootstrap.
Record the actual result; troubleshoot failures rather than claiming success.

Wait for the release to finish. Save its workflow URL, version tag, digest,
rollout output and `/version` response before proceeding.

## Feature release: v1.1.0

```bash
git switch -c dev
git push -u origin dev
git switch -c feature/low-stock
python scripts/prepare_release.py v1.1.0
python -m pytest -q -ra
git add app/main.py tests VERSION
git commit -m "Add low-stock filter and automated test"
git push -u origin feature/low-stock
```

Open a PR from feature/low-stock into dev. Check CI and complete review.
Merge it, then open and review a PR from dev into main. The approved main merge
automatically releases v1.1.0 and performs the rolling update.

Show that `/items?low_stock=true` returns only items below five after you
create records with quantities 0, 4, 5 and 10. Capture the PR, workflow, GHCR tag,
rollout status and `/version` output. The source snapshot adds real low-stock filtering
logic and its test, rather than changing only VERSION.

## Bug report and intentional failed test

Issue: earlier source accepts a quantity such as -1. Expected behavior: reject
negative quantities with HTTP 400 and leave the stored quantity unchanged.

After v1.1.0 has deployed, synchronize dev with main so its next release has the
latest history. Use a PR from main into dev if your branch rules require one.
Then create the regression branch:

```bash
git fetch origin
git switch dev
git pull --ff-only origin dev
git switch -c fix/quantity-range
cp demo/v1.2.0/test_quantity.py tests/test_quantity.py
# The existing v1.1.0 app has not been fixed yet.
python -m pytest -q 'tests/test_quantity.py::test_invalid_quantity[-1]'
```

That command must fail because the old code accepts -1. Commit the regression
test, push and open a PR into dev:

```bash
git add tests/test_quantity.py
git commit -m "Reproduce missing quantity range validation"
git push -u origin fix/quantity-range
```

Wait for the PR CI run to fail. Save its link/log and explain the failing
assertion. Verify the published release and deployed `/version` remain v1.1.0.
Do not merge this revision. PR pipelines do not contain a publish/deploy job,
and the failing test also stops the main release's shared validation stage.

## Corrected release: v1.2.0

On the same fix/quantity-range branch:

```bash
python scripts/prepare_release.py v1.2.0
python -m flake8 app tests scripts
python -m pytest -q -ra
git add app/main.py tests VERSION
git commit -m "Reject invalid quantities and release v1.2.0"
git push
```

The same PR now passes. Complete review and merge to dev, then open the reviewed
release PR from dev to main. Observe publishing and rollout automatically.
Verify quantities 0 and 100 succeed, while -1 returns HTTP 400 on both creation and update.

For each release, collect the deployment-evidence workflow artifact and save
links in docs/evidence/releases.md. Confirm the `/version` revision matches the
main merge commit. `/version` uses deployment-provided VERSION and revision,
so release metadata must be kept consistent with the image digest.

## Live assessment

Show the three completed releases and one failed run. Then make a small genuine
source change on a new branch, add/update a relevant test, bump VERSION to
v1.2.1, and pass it through dev and main PRs. Show the new workflow run, GHCR
image, rolling update and Service response. Prepare enough time for scans and
runner execution. Be ready to explain every command and file.

## Rollback

```bash
kubectl -n inventory-api rollout history deployment/inventory-api
kubectl -n inventory-api rollout undo deployment/inventory-api
kubectl -n inventory-api rollout status deployment/inventory-api
```

The workflow attempts this automatically only when a previous API deployment
exists and an application update was attempted. Initial deployment has no prior
revision. Rollback restores the API pod template, including version/revision
variables; it does not reverse database data/schema changes or ConfigMaps.
This project uses the same additive schema throughout its three demo releases.
