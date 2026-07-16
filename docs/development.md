---
icon: lucide/wrench
---

# Development

## Setup

Use Python 3.14 and keep the sibling `citation-date` and `citation-report`
repositories beside this checkout. The project resolves both as editable local
dependencies:

```bash
uv sync --all-extras --dev
```

Run every repository gate with:

```bash
just check
```

This runs tests and doctests, checks the Marimo example, creates a clean strict
Zensical documentation build, and builds the source and wheel distributions.

## Documentation

Preview the documentation locally:

```bash
just docs
```

Build the static site without starting a server:

```bash
uv run zensical build --clean --strict
```

Documentation explains the public extraction workflow, source-review limits,
and data shapes. Write it for both a lawyer evaluating what a result means and
a developer integrating the API: distinguish source evidence from normalized
indexing data, and state ordering/counting behavior explicitly. Keep regex
implementation detail close to the fixture that proves it, rather than
expanding generated API reference pages.

## Notebook Example

`notebooks/citation_explorer.py` is a small Marimo surface for trying citation
text interactively. It uses Polars to show normalized citation and mention
rows. Keep it focused on examples and review; parser behavior belongs in the
package and its regression tests.

Validate it directly with:

```bash
uv run marimo check notebooks/*.py
```

## Change Boundaries

- `citation-date` owns date grammar and date decoding.
- `citation-report` owns reporter grammar and report-text normalization.
- `citation-utils` owns docket grammar, docket-to-report joins, and
  citation-level normalization.

When extending a docket pattern, add a focused regression for the observed
form and nearby rejection cases. Keep documented serialization aliases stable:
`cat`, `num`, `date`, `phil`, `scra`, and `offg`.

The JSON corpus at `tests/fixtures/citation_regressions.json` is the shared
decision record for document-derived errors. Mark a row `observed` only when
the source text was actually reviewed; use `synthetic` for the neighboring
acceptance and rejection boundaries that make the intended rule explicit. A
corpus screenshot or frequency count is discovery evidence only; the fixture
should quote the text form being tested and must not be presented as direct
proof of the original court document.
