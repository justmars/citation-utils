---
icon: lucide/search-check
---

# Extracting Citations

`Citation` is the application-facing model. It normalizes a docket, a report,
or a joined docket-report citation into the same database-friendly shape.

## Extract One Citation

Use `Citation.extract_citation()` when the first citation is enough:

```python
from citation_utils import Citation

citation = Citation.extract_citation(
    "G.R. No. 147033, April 30, 2003, 374 Phil. 1"
)

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

`Citation.extract_citations()` yields every recognized citation in source
order. A docket with several serials becomes the first serial's normalized
record; the original matched text remains available through the lower-level
docket object when that full evidence is required.

## Separate Docketed and Undocketed Reports

`CitableDocument` is useful when a caller needs the intermediate evidence:

```python
from citation_utils import CitableDocument

document = CitableDocument(
    "G.R. No. 147033, April 30, 2003, 374 Phil. 1; 31 SCRA 562"
)

assert len(document.docketed_reports) == 1
assert document.undocketed_reports == {"31 SCRA 562"}
```

It normalizes report text once, finds docketed reports, and then removes the
reports already attached to those dockets. `get_citations()` returns the
deduplicated citation strings used by `Citation.extract_citations()`.

## Count Repeated Citations

Use `CountedCitation.from_source()` to merge duplicate citations and retain a
`mentions` count:

```python
from citation_utils import CountedCitation

citations = CountedCitation.from_source(
    "G.R. No. 147033, April 30, 2003; G.R. No. 147033, April 30, 2003"
)

assert len(citations) == 1
assert citations[0].mentions == 2
```

Two citations are the same when all three docket components agree, or when a
shared report citation agrees. This allows partially reported forms of the
same decision to be merged without discarding a report-only occurrence.

## Statutory Dockets

Some Administrative Matter and Bar Matter expressions denote rules instead of
decisions. `CitableDocument.get_docketed_reports()` excludes them by default:

```python
from citation_utils import CitableDocument

rule = "Bar Matter No. 803, Jan. 1, 2000"

assert list(CitableDocument.get_docketed_reports(rule)) == []
assert len(list(CitableDocument.get_docketed_reports(rule, False))) == 1
```

Use the opt-in form only for a workflow that needs statutory rules as source
evidence.
