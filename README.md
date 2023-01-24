# citation-docket

![Github CI](https://github.com/justmars/citation-docket/actions/workflows/main.yml/badge.svg)

Regex formula of Philippine Supreme Court citations in docket format (with reports); utilized in the [LawSQL dataset](https://lawsql.com).

## Documentation

See [documentation](https://justmars.github.io/citation-docket), building on top of [citation-report](https://justmars.github.io/citation-report).

## Development

Checkout code, create a new virtual environment:

```sh
poetry add citation-docket # python -m pip install citation-docket
poetry update # install dependencies
poetry shell
```

Run tests:

```sh
pytest
```
