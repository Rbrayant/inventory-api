# Synchronize the assessment submission

This checklist distinguishes completed repository corrections from work
that still requires the final files or the student's running environment.

## Proposed in this branch

- Correct README release status and link it to verified v1.3.3 evidence.
- Replace the placeholder release index with verified tags, commits, PRs
  and successful workflow links.
- Record the failed regression and subsequent quantity-validation correction.
- Propose VERSION v1.3.4 for this documentation release. It is not deployed.
- Keep the new /about feature for the live assessment.

## Upload final documents before merging

The existing binary files have not been replaced by this branch.

1. Download the updated `Inventory_Tracker_Report.pdf` prepared in the chat.
2. Open the updated twelve-slide presentation and export it as PowerPoint.
   The current slide 2 includes the Render deployment, screenshot and URL.
   Presentation: https://chatgpt.com/space/page_6951c72ada3881918c653449e60dcfa8
3. Select this draft PR's branch on GitHub. Under `docs/`, use
   **Add file > Upload files** to replace:
   - `Technical_Report.pdf` with the updated report, renamed accordingly.
   - `Presentation.pptx` with the newly exported deck, renamed accordingly.
4. Keep the updated Word report, presenter walkthrough and command guide
   available for preparation; they can be added as supplementary documents.
5. Add safe deployment screenshots under `docs/evidence/screenshots/` and
   keep the original dates/versions in their captions.
6. Confirm the PDF is 5–10 pages and the deck is 8–12 slides. Do not submit
   source-layout previews or secret-bearing terminal captures as evidence.

Use the newest PowerPoint export from the chat, not the older ZIP's deck.
The report records the v1.3.3 baseline; a later successful release is separate
evidence and must not be retroactively claimed inside older screenshots.

## Merge and deployment preparation

Merging this PR into main starts Release and deploy, even for documentation.

- Ensure Docker Desktop and the existing kind cluster are running.
- Ensure the self-hosted runner is online with linux and k8s labels.
- Refresh the namespace-scoped deployment credential shortly before release
  and set KUBE_CONFIG_B64 in the protected production environment.
- Inspect current tags. v1.3.4 must still be unused and greater than all tags;
  choose a newer value if another release occurs first.
- Wait for PR checks to pass and retain required review/approval rules.
- Finish the binary uploads, then mark the PR ready and merge when the
  deployment environment is ready.
- Verify the new workflow, two ready pods, /ready and /version.
  Do not claim v1.3.4 is deployed before these checks succeed.
- If publish succeeded but deploy failed, fix the environment and rerun
  only failed jobs rather than repeating successful publication.

## Live presentation change

/about is a planned feature, not a current route. Add it with its focused
test during the assessment using the prepared demo helper and command guide.
After the documentation release, select another greater unused version
(expected v1.3.5 only if no intervening releases occur). Promote the feature
through checked dev/main PRs and show the automatic rollout and new response.

## Check Render separately

Open https://inventory-api-5wpn.onrender.com/ready and /version in a browser.
The earlier remote-check failure is inconclusive; it does not prove an outage.

In Render's inventory-api service, inspect its deployment logs and database
status. The Docker Command is `python scripts/start_render.py`. Keep the
existing private DATABASE_URL and API_TOKEN values private. Set APP_VERSION
to the actual intended source release, deploy that revision and recheck
/ready and /version. Local Kubernetes and Render have separate databases
and deployment paths; verify each independently.
