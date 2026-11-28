# Verified release and deployment evidence

Reviewed on 28 November 2026 using GitHub release tags, workflow records and
merged pull requests. Historical deployment screenshots were supplied by the
student. Current laptop and Render availability require separate live checks.

Repository: https://github.com/Rbrayant/inventory-api

## Completed releases

| Release | Change | Tagged main revision | Pull requests | Successful release workflow |
|---|---|---|---|---|
| [v1.0.0](https://github.com/Rbrayant/inventory-api/tree/v1.0.0) | Initial API | [`94237f2`](https://github.com/Rbrayant/inventory-api/commit/94237f267952f635e96eda53f494a2bee17c1e19) | Initial bootstrap | [Run 43714155403, attempt 1](https://github.com/Rbrayant/inventory-api/actions/runs/43714155403) |
| [v1.1.0](https://github.com/Rbrayant/inventory-api/tree/v1.1.0) | Low-stock feature | [`588a282`](https://github.com/Rbrayant/inventory-api/commit/588a282ba426c298da2e9a77e3f60e3cf0cddda1) | [#1](https://github.com/Rbrayant/inventory-api/pull/1), [#2](https://github.com/Rbrayant/inventory-api/pull/2) | [Run 43718250021, attempt 1](https://github.com/Rbrayant/inventory-api/actions/runs/43718250021) |
| [v1.2.0](https://github.com/Rbrayant/inventory-api/tree/v1.2.0) | Quantity validation fix | [`4b75733`](https://github.com/Rbrayant/inventory-api/commit/4b757335ebf7f605bc72d31cb341c523e94e2bea) | [#3](https://github.com/Rbrayant/inventory-api/pull/3), [#4](https://github.com/Rbrayant/inventory-api/pull/4) | [Run 43736905718, attempt 1](https://github.com/Rbrayant/inventory-api/actions/runs/43736905718) |
| [v1.3.0](https://github.com/Rbrayant/inventory-api/tree/v1.3.0) | Dashboard | [`5c3e15f`](https://github.com/Rbrayant/inventory-api/commit/5c3e15f421245ca2efa15da20e1e8dce201610e8) | [#5](https://github.com/Rbrayant/inventory-api/pull/5), [#6](https://github.com/Rbrayant/inventory-api/pull/6) | [Run 43742364329, attempt 1](https://github.com/Rbrayant/inventory-api/actions/runs/43742364329) |
| [v1.3.1](https://github.com/Rbrayant/inventory-api/tree/v1.3.1) | Render startup correction | [`474a8e1`](https://github.com/Rbrayant/inventory-api/commit/474a8e12209d091fe7836cb8fcdd617d1216f2e0) | [#7](https://github.com/Rbrayant/inventory-api/pull/7), [#8](https://github.com/Rbrayant/inventory-api/pull/8) | [Run 44600919446, attempt 5](https://github.com/Rbrayant/inventory-api/actions/runs/44600919446) |
| [v1.3.2](https://github.com/Rbrayant/inventory-api/tree/v1.3.2) | Release identifier update | [`6928d29`](https://github.com/Rbrayant/inventory-api/commit/6928d29ba962609e93aeb590059c57f2ee43aae0) | [#9](https://github.com/Rbrayant/inventory-api/pull/9) | [Run 45059209547, attempt 4](https://github.com/Rbrayant/inventory-api/actions/runs/45059209547) |
| [v1.3.3](https://github.com/Rbrayant/inventory-api/tree/v1.3.3) | README and version update | [`6860bc6`](https://github.com/Rbrayant/inventory-api/commit/6860bc6ca0d4aceb72e64685e218b6effe025270) | [#10](https://github.com/Rbrayant/inventory-api/pull/10) | [Run 45064287421, attempt 1](https://github.com/Rbrayant/inventory-api/actions/runs/45064287421) |

All seven tagged revisions match the associated successful workflow head SHA.
For v1.3.3, the validation, publish and deploy jobs were also fetched directly
and each concluded success.

## Image and rollout evidence

The release workflow publishes version and commit-SHA tags to
`ghcr.io/rbrayant/inventory-api`, records the digest, and renders the API image
as `IMAGE@DIGEST`. For each run above:

1. Open the publish job's **Publish validated image and record digest** step.
2. Open the deploy job's **Deploy and verify** step for rollout/smoke results.
3. Download the **deployment-evidence** artifact while retained. Its
   `release.txt` records version, revision and image digest; it also contains
   rollout and smoke outputs. Artifacts can expire, so preserve required
   evidence before submission.
4. Capture the corresponding registry tag/digest and live `/version` response
   without credentials.

No individual digest values are invented or transcribed into this index.
The linked workflow records establish their historical execution status;
fresh cluster checks establish the present runtime state.

The supplied 22 November v1.3.3 screenshot shows two `1/1 Running` API pods,
PostgreSQL running, completed initialization/smoke jobs and version v1.3.3.
An earlier browser capture shows v1.3.2 at revision `6928d29`; do not label
that older capture as v1.3.3.

## Failed regression and correction

- [Failed CI run 43735535492](https://github.com/Rbrayant/inventory-api/actions/runs/43735535492)
  records conclusion **failure** at
  [`9a5f72ec5b8314677d856e116f4e44991f1b0d85`](https://github.com/Rbrayant/inventory-api/commit/9a5f72ec5b8314677d856e116f4e44991f1b0d85).
- The retained regression output reports two failures and 28 passes. POST
  and PATCH accepted negative quantities where the new assertions expected
  HTTP 400.
- [Correction `d36451291c6c08be0958e31dfd9655f49918c0a4`](https://github.com/Rbrayant/inventory-api/commit/d36451291c6c08be0958e31dfd9655f49918c0a4)
  added quantity validation.
- [Fix PR #3](https://github.com/Rbrayant/inventory-api/pull/3) and [release PR #4](https://github.com/Rbrayant/inventory-api/pull/4)
  delivered the successful [v1.2.0 release](https://github.com/Rbrayant/inventory-api/actions/runs/43736905718).

The regression failed on a PR, whose workflow does not publish or deploy.
The main release also depends on the shared validation gate. Keep the
recorded v1.1.0 runtime/registry evidence available when explaining that
the failed revision did not replace the previous release.

## Assessment and public hosting

The new source-change demonstration has not been performed by this
documentation update. Record its actual PR, run, new version and runtime
response after completing it.

Render is separate hosting at https://inventory-api-5wpn.onrender.com/.
The supplied successful Render capture is dated 19 November at source
revision `474a8e1`. It does not establish today's cloud version or readiness.

## Submission artifacts

The report and PowerPoint in the repository remain the original files until
replaced. Follow [SUBMISSION_SYNC.md](../SUBMISSION_SYNC.md) to upload the
updated binaries and retain safe supporting screenshots.
