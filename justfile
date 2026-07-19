set dotenv-load

# serve documentation
docs:
  uv run zensical serve --dev-addr localhost:8001

# verify maintained documentation contracts
docs-check:
  uv run pytest -o addopts='-q' tests/test_docs_contract.py
  uv run zensical build --clean --strict

# run all repository gates
check:
  uv run pytest
  uv run marimo check notebooks/*.py
  uv run zensical build --clean --strict
  uv build --no-sources

# create .env file from example
dumpenv:
  op inject -i env.example -o .env

# upload to pypi
publish:
  uv build && \
  uv publish --token $PYPI_TOKEN
