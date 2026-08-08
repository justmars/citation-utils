set dotenv-load

# format maintained Python sources
format:
    uv run ruff check --fix .
    uv run ruff format .

# validate Python formatting and lint rules
lint:
    uv run ruff check .
    uv run ruff format --check .

# validate maintained runtime types
typecheck:
    uv run pyright

# run the repository test suite
test:
    uv run pytest

# serve documentation
docs:
    uv run zensical serve --dev-addr localhost:8001

# verify maintained documentation contracts
docs-check:
    uv run pytest -o addopts='-q' tests/test_docs_contract.py
    uv run zensical build --clean --strict

# build and smoke-test the wheel without touching the repository dist directory
package-check:
    #!/usr/bin/env bash
    set -euo pipefail
    package_check_dir="$(mktemp -d)"
    trap 'rm -rf "$package_check_dir"' EXIT
    uv build --no-sources --out-dir "$package_check_dir"
    wheel_files=("$package_check_dir"/*.whl)
    test "${#wheel_files[@]}" -eq 1
    wheel="${wheel_files[0]}"
    uv run python -c 'import sys, zipfile; names = set(zipfile.ZipFile(sys.argv[1]).namelist()); missing = [name for name in sys.argv[2:] if name not in names]; assert not missing, f"wheel missing required files: {missing}"' "$wheel" "citation_utils/__init__.py" "citation_utils/dockets/__init__.py"
    uv run --no-project --with "$wheel" python -c "import citation_utils"

# run all repository gates
check: lint typecheck docs-check
    just test
    uv run marimo check notebooks/*.py
    uv lock --check
    just package-check

# create .env file from example
dumpenv:
    op inject -i env.example -o .env

# upload to pypi
publish:
    uv build && \
    uv publish --token $PYPI_TOKEN
