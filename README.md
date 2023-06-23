# citation-docket

![Github CI](https://github.com/justmars/citation-docket/actions/workflows/main.yml/badge.svg)

Regex formula of Philippine Supreme Court citations in docket format (with reports); utilized in the [LawSQL dataset](https://lawsql.com).

## Documentation

See [documentation](https://justmars.github.io/citation-docket), building on top of [citation-report](https://justmars.github.io/citation-report).

## Caveats

### DocketCategory

Each `DocketCategory` has its own nuanced regex patterns identifying its _category_, _serial_text_, and _date_

#### Adding new Citation types

Recently, the `JIB` was added as a new category. This means creating a new `CitationConstructor` object with distinct objectts.

#### Adding new DocketRules

There are are `AM` and `BM` docket numbers that represent rules rather than decisions.

### DocketReports

Based on a `CiteableDocument`, construct a temp object prior to formation of `Citation`. This temp object is either:

1. A combination of a `Docket` object with its `Report` object; or
2. A solo, undocketed `Report`.
