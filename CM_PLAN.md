# Configuration Management Plan

## 1. Purpose
Keep every change to the 510(k) Regulatory Intelligence Assistant consistent,
traceable and repeatable across the two planned versions.

## 2. Configuration items (CIs)

| CI | Location | Notes |
|---|---|---|
| Source code | `src/` | One module per feature |
| Tests | `tests/` | Run by CI on every push and PR |
| Configuration | `config/config.json` | App name, version, data-source settings |
| CI workflow | `.github/workflows/ci.yml` | Automated checks |
| Change requests | `docs/change_requests/` | One file per CR |
| Release notes | `CHANGELOG.md` | Updated for every tagged release |
| This plan | `CM_PLAN.md` | Changed only through a PR |

## 3. Tools
- **Git** for local version control.
- **GitHub** for the remote repository, pull requests, reviews and releases.
- **GitHub Actions** for continuous integration.

## 4. Branching strategy

| Branch | Purpose |
|---|---|
| `main` | The master branch described in the assignment. Always releasable. Protected: no direct pushes, PR + passing CI required |
| `feature/v1-*` | Version 1 features (search, results, landscape) |
| `feature/v2-*` | Version 2 features (AI summaries, insights, traceability) |
| `hotfix/*` | Urgent fixes to a released version |

Naming: `feature/<version>-<short-name>`, for example `feature/v1-device-search`.

## 5. Change control process
1. Open a change request in `docs/change_requests/CR-###.md` (what, why, impact).
2. Create a feature branch from `main`.
3. Commit in small steps with clear messages (`Add ...`, `Fix ...`, `Update ...`).
4. Push the branch and open a pull request using the PR template.
5. CI must pass and one review must approve.
6. Merge with a merge commit (`--no-ff`) so each feature stays visible in history.
7. Delete the feature branch after merging.

## 6. Baselines and releases

| Baseline | Tag | Contents | Exit criteria |
|---|---|---|---|
| Version 1 | `v1.0.0` | Device search, submission results, filtering, details, landscape analysis | Full V1 system test passed |
| Version 2 | `v2.0.0` | V1 + AI summaries, AI insights, source traceability, human review | Full V2 system test (incl. V1 regression) passed |

Versioning follows Semantic Versioning (MAJOR.MINOR.PATCH). A version is not
complete until its planned features are implemented and its system test has
passed. Each tag gets a GitHub Release with notes copied from `CHANGELOG.md`.

## 7. Merge conflicts
Conflicts are resolved on the feature branch or during the merge, by the
developer who owns the change, then re-tested before the merge is completed.
The resolution is described in the merge commit message.

## 8. Audit
`git log`, PR history and GitHub Releases are the audit trail: who changed
what, when, and why.
