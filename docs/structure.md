---
icon: lucide/files
---

# Docket Types

A docket has three normalized components: a category, the first serial in the
matched reference, and its decision date. The `Citation` model exposes them as
`cat`, `num`, and `date` when serialized.

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

## Normalization

`Docket` holds the source match before it becomes a `Citation`. It preserves
the matched `context`, the original `ids`, and the parsed `docket_date`.

```python
from citation_utils import Citation

citation = Citation.extract_citation("GR 138570, Oct. 10, 2000")

assert citation is not None
assert citation.set_slug() == "gr-138570-2000-10-10"
assert citation.get_docket_display() == "GR No. 138570, Oct. 10, 2000"
```

Serials are lowercased and reduced to the first serial for database identifiers.
For multiple serials, redocketing history, and other display nuances, keep the
source citation or use a lower-level docket result rather than reconstructing
the full source from the normalized identifier.

## Docket Reports

Each concrete docket matcher produces a `DocketReportCitation`, which combines
the docket fields with the report fields supplied by `citation-report`. The
string form includes whichever side was found:

```python
from citation_utils import CitableDocument

result = next(
    CitableDocument.get_docketed_reports(
        "G.R. No. 147033, April 30, 2003, 374 Phil. 1"
    )
)

assert str(result) == "GR No. 147033, Apr. 30, 2003, 374 Phil. 1"
```

The individual `CitationGR`, `CitationAM`, `CitationAC`, `CitationBM`,
`CitationPET`, `CitationOCA`, `CitationJIB`, and `CitationUDK` classes are
matcher implementations. Prefer `Citation` or `CitableDocument` unless a
caller specifically needs one category's regex result.
