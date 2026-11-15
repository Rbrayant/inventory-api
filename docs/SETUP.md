# Setup on Ubuntu / WSL

Run these commands in Ubuntu, from the extracted project folder. Required tools:
Python 3.12, Git, Docker with Compose, kubectl, kind, OpenSSL, and optionally the
GitHub CLI (`gh`). Install supported versions using each vendor's installation
instructions. The supplied assignment leaves the cluster environment to you.

## 1. Local verification

Follow the README's Python tests and Docker Compose commands. Save Docker
build/run output and a response from `/version`. Finish local Compose work with
`docker compose down` before continuing if resources are limited.

## 2. Create the local cluster and secrets

```bash
kind create cluster --name inventory-lab
kubectl cluster-info
kubectl get storageclass
bash scripts/create_secrets.sh
kubectl apply -f k8s/runner-rbac.yaml
```

A default dynamic StorageClass must be available for the 1Gi PostgreSQL PVC.
The kind cluster needs Internet access to pull GHCR and PostgreSQL images.
The database uses one replica and persistent local-cluster storage. This is a
item lab, not a highly available database. Deleting the kind cluster deletes
its data. Database backups are outside this assignment's minimum scope.

## 3. Create GitHub repository and branch rules

Create an empty repository named `inventory-api`, accessible to your instructor.
Add its actual URL as `origin` during the release walkthrough. Use a private
repository for the self-hosted runner unless you understand and control every
contributor. Untrusted PR code must never execute on that runner.

In Settings / Rules / Rulesets (or branch protection):
- Require pull requests and review before merging into main.
- Require the CI check `Lint, tests, build and scan` for PR merges.
- Require branches to be up to date and prevent direct pushes and force pushes.
- Protect `v*` release tags against updates and deletion.
- Allow the workflow's GITHUB_TOKEN to create new release tags and publish GHCR
  packages, subject to your repository/organization policy.

Initial bootstrap may require the repository owner's first push before enabling
all protections. Apply the rules before the feature and bug-fix demonstrations.
For an individual project, arrange a reviewer with the instructor or follow the
instructor's approved review process. Do not claim a review that did not occur.

## 4. Self-hosted runner

In the repository Settings / Actions / Runners, choose a new Linux x64
self-hosted runner. Follow the exact registration commands shown by GitHub.
Install it on the same Ubuntu host that runs kind, under a dedicated account.
Give it the custom label `k8s`. The standard labels `self-hosted` and `linux`
are normally supplied automatically.

Install Python 3 and kubectl for that runner account. Confirm the account can
reach the Kubernetes API endpoint, and that the runner is online. Only GitHub's
hosted CI/publish jobs need Docker; the deployment runner needs kubectl and Python.
Keep the runner restricted to trusted repository workflows.

## 5. Cluster authentication in protected secrets

Create the `production` GitHub Environment. Restrict deployment branches to main.
Manual environment approval is optional; omit it if you want automatic deployment
after the reviewed main merge.

On the cluster host with your administrator kubectl context:

```bash
bash scripts/create_runner_config.sh
```

This creates `/tmp/item-runner-kubeconfig.b64`, containing a namespace-scoped
service account token. Set it as environment secret `KUBE_CONFIG_B64` in the
production environment. If `gh` is already signed in to your repository:

```bash
gh secret set KUBE_CONFIG_B64 --env production < /tmp/item-runner-kubeconfig.b64
rm /tmp/item-runner-kubeconfig.b64
```

Alternatively paste the file contents into the GitHub secret field, then delete
the temporary file. Never paste it into chat, screenshots, commits or logs.
Tokens expire within 24 hours (the API server may impose a different duration).
Refresh this secret before a later lab session or assessment. The namespace Role
allows the deployment operations and reading only the two required Secrets.
It is still a trusted deployment identity with access to application data.

## 6. Registry visibility

CD automatically uses GITHUB_TOKEN to publish `ghcr.io/<owner>/<repository>`.
The first deployment may need you to make this GHCR package public after it is
published. Only container images are made public, not your repository or Secrets.
A public image is the simplest lab setup. If deployment fails before you change
visibility, use Actions / Re-run failed jobs to repeat only deployment after fixing
visibility. The successful publish job and its digest stay unchanged. To keep images private instead, create
a `ghcr-pull` docker-registry Secret in inventory-api and add:

```yaml
imagePullSecrets:
  - name: ghcr-pull
```

under `spec.template.spec` in deployment.yaml, init-db.yaml and smoke.yaml before
your first release. Use a registry read-only credential with package access.
Never commit it. Provision it separately with your administrator context.

## 7. Access and inspect

After a successful release:

```bash
kubectl -n inventory-api get pods,svc,pvc
kubectl -n inventory-api rollout status deployment/inventory-api
kubectl -n inventory-api port-forward svc/inventory-api 8080:80
```

Leave port-forward running. In a new terminal, run:

```bash
curl -fsS http://localhost:8080/health
curl -fsS http://localhost:8080/ready
curl -fsS http://localhost:8080/version
```

Open `http://localhost:8080/items` in your browser. The app is a JSON API,
so a graphical dashboard is not required. The NodePort Service is also available
on node addresses where your host networking permits it; port-forward works
without additional kind port mappings.

## Troubleshooting

| Symptom | Check and remedy |
|---|---|
| CI scan fails | Read security-scan artifact. Update vulnerable dependency/base image, then repeat validation. Never disable the scan to pass. |
| Deploy queued | Runner online and labels self-hosted, linux, k8s match. Check production environment restrictions. |
| Unauthorized | Refresh KUBE_CONFIG_B64. Check token expiry and RBAC. |
| Connection refused to API server | Run runner on kind host. Verify cluster exists and runner can reach its API address. |
| ImagePullBackOff | GHCR image visibility or imagePullSecrets, tag/digest and cluster network. |
| PVC Pending | Default StorageClass and free storage. |
| Init-db job fails | Inspect its logs, PostgreSQL readiness and matching credentials. |
| Readiness 503 | Database connection and items table initialization. |
| Duplicate release rejected | VERSION must increase and a consumed release tag cannot be reused. |
| Rolling update fails | Describe pods, inspect events/logs, check image and resource capacity. |
| Secret recreated but DB login fails | Existing PVC retains original DB password. Restore matching credentials or intentionally reset only disposable lab data. |

Diagnostics (do not record Secret values):

```bash
kubectl -n inventory-api describe deployment inventory-api
kubectl -n inventory-api get events --sort-by=.lastTimestamp
kubectl -n inventory-api logs deployment/inventory-api --tail=100
kubectl -n inventory-api get jobs
kubectl -n inventory-api rollout history deployment/inventory-api
```
