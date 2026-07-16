![Github CI](https://github.com/justmars/citation-utils/actions/workflows/ci.yml/badge.svg)

# Citation Utilities

`citation-utils` extracts and normalizes Philippine Supreme Court citations
that include a docket, a report citation, or both. It composes
[`citation-date`](https://github.com/justmars/citation-date) and
[`citation-report`](https://github.com/justmars/citation-report) for the
[LawSQL](https://lawsql.com) data pipeline.

The package is corpus-driven. It preserves the reported citation components
that are present in the source rather than inferring missing case metadata.

## Quick Example

```python
from citation_utils import Citation

raw = "G.R. No. 147033, April 30, 2003, 374 Phil. 1"
citation = Citation.extract_citation(raw)

assert citation is not None
assert citation.model_dump() == {
    "cat": "gr",
    "num": "147033",
    "date": "2003-04-30",
    "phil": "374 phil. 1",
    "scra": None,
    "offg": None,
}
```

## Documentation

See the [documentation](https://justmars.github.io/citation-utils) for the
extraction flow, supported docket types, SQLite-oriented output, and local
development checks.

## Boundaries

- `citation-date` owns date grammar and date normalization.
- `citation-report` owns reporter grammar and report normalization.
- `citation-utils` owns docket grammar, joins dockets to reports, and provides
  database-ready citation records.

Administrative Matter and Bar Matter references can name rules rather than
decisions. The default extraction flow excludes those statutory dockets; pass
`exclude_docket_rules=False` only when the calling workflow needs them.
