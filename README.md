# EO-DataHub SPDX Change Scanner

Updates an S3 bucket from a GitHub repository

## Requirements

- [uv](https://docs.astral.sh/uv/) package manager
- Ensure that configscanning is installed

## Running

```bash
python3 -m configscanning.git_change_scanner https://github.com/EO-DataHub/catalogue-data /path/to/staging/dir/catalogue-data --app-id-from app-id --app-private-key-from app-private-key --enable-scanner /path/to/eodhp/scanner/eodhp-scanner  --s3_bucket my_bucket --s3_prefix git-harvester --workspace workspace_name --harvester-id abc123 --config-scan --branch test_catalog --target my-target
```

## Development Setup

```commandline
make setup
```

This will install dependencies with `uv sync` and install `pre-commit` hooks.

## Available Make Commands

- `make setup` - Install dependencies and set up pre-commit hooks
- `make test` - Run tests in watch mode
- `make testonce` - Run tests once
- `make check` - Run linting, formatting checks, and type checking
- `make format` - Auto-fix linting issues and format code
- `make dockerbuild` - Build the Docker image
- `make dockerpush` - Build and push the Docker image
