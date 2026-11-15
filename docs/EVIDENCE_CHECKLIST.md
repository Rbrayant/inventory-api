# Evidence and submission checklist

## Actual local evidence included
- Python API tests and lint output: evidence/local-checks.txt.
- Release source checks: evidence/release-checks.txt.
- Expected failed regression against v1.1.0: evidence/expected-regression.txt.

These logs are local executions, not GitHub or Kubernetes evidence.

## Complete in your account and cluster
For each of v1.0.0, v1.1.0 and v1.2.0, save:
- Main commit SHA and git log showing real changes.
- Feature/fix PR URL and review/merge evidence as applicable.
- Successful GitHub workflow URL and its validation/security-scan log.
- GHCR release tag and image digest.
- Kubernetes rollout status, two ready API pods, Service and PVC status.
- /version response showing the expected version and main commit.
- Working item create/list/update/delete requests and relevant release feature.

Also save:
- Failed regression CI URL, failing assertion, fix commit and successful retry.
- Proof the failing revision was not published/deployed (registry and /version).
- Local Docker build, running container health and endpoint response.
- Safe configuration/Secret references and protected environment setup. Never
  screenshot tokens, Secret YAML, base64 credentials, kubeconfig or .env.
- A live source modification, PR merge, automatic release and rolling update.

## Submission
- Accessible GitHub repository URL and all source/configuration/history.
- Technical_Report.pdf (add real evidence and findings before submission).
- Presentation.pptx (replace pending status with verified results).
- Screenshots, logs and links organized under docs/evidence/.
- Review the instructor's final evaluation questions in the assignment PDF.

A source ZIP or prepared report cannot substitute for the practical demonstration.
