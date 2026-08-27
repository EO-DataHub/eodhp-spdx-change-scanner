# Changelog

## v0.1.8 (2026-08-27)
- `mypy_boto3_s3` import in the scanner moved under `TYPE_CHECKING`; `boto3-stubs` is dev-only and the image is built with `UV_NO_DEV=1`, so 0.1.7 failed with `ModuleNotFoundError: No module named 'mypy_boto3_s3'`.

## v0.1.7 (2026-08-27)
- `ENV PATH="/app/.venv/bin:$PATH"` in the Dockerfile so the argocd CronJob's `python3 -m configscanning.git_change_scanner` command override resolves to the venv (0.1.6 failed in test with `ModuleNotFoundError: No module named 'configscanning'`).
- configscanning bumped to v0.1.7, which uses `pygit2.enums.RepositoryOpenFlag` instead of the `GIT_*` constants removed in pygit2 1.20.0.

## v0.1.6 (2026-08-25)
- configscanning declared in `pyproject.toml` (`[tool.uv.sources]`, tag v0.1.6) and locked in `uv.lock`; no longer installed ad hoc in the Dockerfile.

## v0.1.5 (2026-08-25) - commit 5a22d29, first git tag
- Migrate to uv, Renovate onboarding, dependency pins.

## 0.1.2 (image only, 2025-06-05) - commit 51b6f33
- Pin configscanning to v0.1.5.

## 0.1.1 (image only, 2025-03-14) - built from an uncommitted working tree; closest commit cf19dbf
- `SPDX_LICENCE_PATH` read from the environment.

## v0.1.0 (2024-11-22) - commit c0ebb36 (image pushed 2025-01-31)
- Collects files from SPDX Git and updates S3 bucket
