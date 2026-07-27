# Releasing & CI runbook

Notes for maintainers (and agents working in this repo) on cutting a version bump and
checking CI without tripping over the same errors twice.

## Cutting a version bump

CI's `version-bump` job (`.github/scripts/check_version_bump.py`) enforces two things whenever
any file under `plugins/` or `.claude-plugin/` changes in a PR:

1. **A monotonic bump** — the version in `plugin.json` must be strictly greater than the PR base.
2. **Version consistency** — the version must be identical in **three** places:

   | Location | Field |
   |---|---|
   | `plugins/brand-kit-os-leafpad/.claude-plugin/plugin.json` | `.version` |
   | `.claude-plugin/marketplace.json` | `.metadata.version` |
   | `.claude-plugin/marketplace.json` | `.plugins[0].version` |

The common failure mode is bumping `plugin.json` by hand and forgetting the two
`marketplace.json` fields — CI then fails with `Version mismatch across manifests`.

**Always bump with the helper so all three stay in sync:**

```bash
scripts/bump-version.sh 1.8.0
```

It rewrites only the `version` values (no JSON reflow), re-validates the JSON, and confirms the
three fields match. Then:

1. Add a `## 1.8.0 — YYYY-MM-DD` entry to `CHANGELOG.md`.
2. Commit the manifest changes **together** with the code change that motivated the bump.

The `version-bump` job only requires a bump when files under `plugins/` or `.claude-plugin/`
change. Docs-only or `scripts/`-only PRs (like this one) don't need a bump and shouldn't get one.

## Cutting a release (tag + GitHub Release)

A merge to `main` does **not** create a release on its own. The `/doctor` version check
(`commands/doctor.md`, step 7) reads
`GET https://api.github.com/repos/NicT89/brand-kit-os-plugin-leafpad/releases/latest`, so until a
**published GitHub Release** exists for a version, that endpoint 404s and the check can't report
"up to date." A bare git tag is **not** enough — `releases/latest` only returns published Releases.

**Tag convention:** `v<semver>` (e.g. `v1.7.0`). `/doctor` strips a leading `v` before comparing,
so `v1.7.0` and `1.7.0` both work — but always tag `v<semver>` for consistency.

**Automated path (the normal case).** `.github/workflows/release.yml` runs on every push to `main`
that touches a version manifest. It reads `.version` from `plugin.json`, and if no `v<version>`
release exists yet, it creates the tag `v<version>` and a GitHub Release, using the matching
`## <version>` section of `CHANGELOG.md` as the release notes (falling back to auto-generated notes
if that section is missing). So: **land the `## <version>` CHANGELOG entry in the same PR as the
bump** — it becomes the release notes. The job is idempotent; a re-run when the release already
exists exits cleanly.

**Manual / backfill path.** To release a version that's already on `main` (the workflow only fires
on the bump commit), or to retry a failed run, trigger `release.yml` manually:

- GitHub UI: **Actions → Release → Run workflow** on `main`, or
- From an agent session: `mcp__github__actions_run_trigger` with
  `method: run_workflow`, `workflow_id: release.yml`, `ref: main`.

**Verify** with `mcp__github__get_latest_release` (expect `tag_name: v<version>`) or
`mcp__github__list_tags`.

## Checking CI from an agent session (GitHub MCP)

The combined-status endpoint only reports **legacy commit statuses**. This repo's checks run as
**GitHub Actions check runs**, so `pull_request_read` with `method: get_status` returns
`total_count: 0` even while a workflow is running — that's not an error, it's the wrong lens.
Use the Actions tools instead.

`mcp__github__actions_list` supports **exactly four** methods:

- `list_workflows`
- `list_workflow_runs`
- `list_workflow_jobs`
- `list_workflow_run_artifacts`

There is **no** `list_workflow_runs_by_pr` and **no** `list_workflow_runs_by_file_name` — passing
those names fails (`missing required parameter … resource_id` / `resource_id must be an integer`).

**List recent runs for our workflow on a branch** (keep `per_page` small — the unfiltered
response is hundreds of KB and will blow the output limit):

```
mcp__github__actions_list
  method: list_workflow_runs
  owner: NicT89
  repo: brand-kit-os-plugin-leafpad
  resource_id: plugin-checks.yml          # workflow file name goes here (or omit for all)
  per_page: 5
  workflow_runs_filter: { branch: <your-branch> }
```

Read `head_sha`, `status`, and `conclusion` off the top run. To drill into a failure:

- `actions_list method: list_workflow_jobs resource_id: <run_id>` → find the failing job.
- `mcp__github__actions_get` / `get_job_logs` → read the failing step's log.

## Waiting for CI without erroring

Do **not** chain a bare `sleep` (e.g. `sleep 25; echo done`) to wait for a run — the harness
blocks it. Use one of:

- **Subscribe** with `mcp__github__subscribe_pr_activity` — CI-completion events wake the session;
  no polling needed. Best when you'll be idle a while.
- **Poll** by re-calling `actions_list` (per_page: 5) after a short wait via `Bash` with
  `run_in_background: true`, or a `Monitor` until-loop.

Since a webhook doesn't always fire for CI success, a subscribe + one manual re-check on the next
turn is the reliable pattern.
