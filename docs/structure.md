---
icon: lucide/files
---

# Docket Types and Normalization

A docket record has three components: a category, a serial, and a decision
date. Together they form the primary docket identity used for grouping. A
published-report reference may be attached to that record, but a report alone
is not assumed to identify a particular docket.

| Code | Category | Typical source form |
| --- | --- | --- |
| `gr` | General Register | `G.R. No. 147033` |
| `am` | Administrative Matter | `A.M. No. RTJ-12-2317` |
| `ac` | Administrative Case | `A.C. No. 10179` |
| `bm` | Bar Matter | `B.M. No. 803` |
| `pet` | Presidential Electoral Tribunal | `P.E.T. No. 001` |
| `oca` | Office of the Court Administrator | `OCA IPI No. 10-3450-P` |
| `jib` | Judicial Integrity Board | `JIB-FPI No. 21-001` |
| `udk` | Undocketed | `UDK No. 12345` |

## What normalization changes

Normalization makes records comparable and database-safe:

- category codes serialize in lower case (`gr`, `am`);
- serials serialize in lower case with hyphens (`oca-00-01`);
- dates serialize as ISO dates (`1997-07-28`); and
- a multi-serial reference uses its first serial in the normalized record.

```python
from citation_utils import Citation

citation = Citation.extract_citation("GR 138570, Oct. 10, 2000")

assert citation is not None
assert citation.set_slug() == "gr-138570-2000-10-10"
assert citation.get_docket_display() == "GR No. 138570, Oct. 10, 2000"
```

The source text remains important. A normalized first serial is a practical
indexing value, not a substitute for a multi-number citation, a redocketing
history, or a document's official caption.

## Bounded OCR handling

The implementation repairs only known forms that have a clear canonical
result. Examples include legacy G.R. serial forms such as `L-I9863`,
`L-L8432`, `I-47629`, and `L-No. 40004`. It also recognizes dotted category-like
serial components such as `O.C.A.-00-01`.

The implementation does not turn arbitrary punctuation into an identifier:
malformed serials such as `---` and `1--` are rejected. These rules reduce
false matches in noisy material but cannot validate an OCR transcription. For
legal review, compare the original document before relying on a repaired form.

## Category ownership

Some serial shapes can look like a General Register number even when they are
part of another category. Category context takes priority:

| Source text | Normalized result |
| --- | --- |
| `A.C. No. L-363, Jan. 1, 2000` | A.C. record only |
| `Bar Matter No. L-363, Jan. 1, 2000` | B.M. record only |
| `CA G.R. No. L-363, Jan. 1, 2000` | no Supreme Court record |
| `L-363, Jan. 1, 2000` | G.R. record |

This prevents a nested or non-Supreme-Court label from producing an additional
phantom G.R. record.

## Docket reports

Each concrete matcher produces a `DocketReportCitation`: the docket fields
plus the report fields supplied by `citation-report`. Use it when the full
matched context matters:

```python
from citation_utils import CitableDocument

result = next(
    CitableDocument.get_docketed_reports(
        "G.R. No. 147033, April 30, 2003, 374 Phil. 1"
    )
)

assert result.context == "G.R. No. 147033"
assert str(result) == "GR No. 147033, Apr. 30, 2003, 374 Phil. 1"
```

The individual `CitationGR`, `CitationAM`, `CitationAC`, `CitationBM`,
`CitationPET`, `CitationOCA`, `CitationJIB`, and `CitationUDK` classes are
matcher implementations. Prefer `Citation` or `CitableDocument` unless a
caller specifically needs a category-specific result.
