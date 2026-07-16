---
icon: lucide/search-check
---

# Extracting Citations

`citation-utils` turns citation text into a consistent record. It recognizes a
docket reference, a published-report reference, or both together. It is useful
for finding and organizing citations in a collection of documents; it is not a
source of authority and does not prove what an underlying Supreme Court
document says.

Keep the original document text and its location whenever the citation will be
reviewed, cited, or used in a legal workflow. The normalized result records
what the parser recognized; it does not supply a case title, resolve a missing
docket, or verify that a quoted document is authentic.

## Choose the right entry point

| Need | API | Result |
| --- | --- | --- |
| First recognized citation | `Citation.extract_citation(text)` | One `Citation` or `None` |
| All unique citation records | `Citation.extract_citations(text)` | Iterator in first-seen source order |
| Intermediate matches and source-facing docket details | `CitableDocument(text)` | Docketed matches, reports, and strings |
| Number of occurrences | `CountedCitation.from_source(text)` | Unique records with `mentions` |

## Extract records

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

The serialized keys are stable database aliases:

| Key | Meaning | Example |
| --- | --- | --- |
| `cat` | Docket category | `gr` |
| `num` | Canonical first docket serial | `147033` |
| `date` | Docket date in ISO format | `2003-04-30` |
| `phil` | Philippine Reports reference | `374 phil. 1` |
| `scra` | Supreme Court Reports Annotated reference | `342 scra 449` |
| `offg` | Official Gazette reference | `47 o.g. supp. 43` |

The model accepts those aliases when reconstructing a record, including lower
case category codes: `Citation(**citation.model_dump())` is supported.

`Citation.extract_citations()` returns one normalized record for repeated
identical evidence. For a reference with several serials, it records the first
serial. Retain the original citation text or inspect `CitableDocument` when
the complete multi-number reference matters.

## Normalize carefully, not speculatively

The parser applies narrowly defined repairs for recurring document/OCR forms.
For example, `GR L-I9863, Apr. 29, 1964` becomes the canonical database
identifier `gr/l-19863/1964-04-29`; `A.M. No. O.C.A.-00-01` becomes
`am/oca-00-01/...`. It rejects serials such as `---` and `1--` rather than
guessing an identifier.

These repairs make matching more reliable; they do not establish that an OCR
reading is correct. Treat the underlying document as the evidence to check.
The executable regression corpus distinguishes reviewed document forms from
synthetic boundary examples.

## Work with docketed and report-only material

Use `CitableDocument` when a workflow needs intermediate evidence:

```python
from citation_utils import CitableDocument

document = CitableDocument(
    "G.R. No. 147033, April 30, 2003, 374 Phil. 1; 31 SCRA 562"
)

assert len(document.docketed_reports) == 1
assert document.undocketed_reports == {"31 SCRA 562"}
```

`docketed_reports` contains the matched docket object, its original matched
context, and any attached report. `undocketed_reports` is a set of report
references not attached to a recognized docket match. `get_citations()` emits
the same unique, source-ordered textual records used by `Citation` extraction.

Qualified Official Gazette references are retained. For example, the parser
distinguishes `47 O.G. Supp. 43` and `49 O.G. No. 7, 2740` rather than reducing
them to an unqualified volume and page.

## Count occurrences without inventing links

```python
from citation_utils import CountedCitation

citations = CountedCitation.from_source(
    "100 SCRA 1; G.R. No. 1, Jan. 1, 2000, 100 SCRA 1"
)

assert len(citations) == 1
assert citations[0].docket_serial == "1"
assert citations[0].mentions == 2
```

`mentions` counts source occurrences. A report-only occurrence enriches a
docket record only when that report identifies exactly one docket in the same
text. If the same report is attached to two different dockets, the standalone
report is preserved as its own record. The parser will not choose a docket
winner merely to make the count look simpler.

This is intentionally separate from Python model equality: two `Citation`
objects are equal only when their complete normalized records agree.

## Statutory dockets

Some Administrative Matter and Bar Matter references identify rules rather
than decisions. Normal extraction excludes the known statutory serials:

```python
from citation_utils import CitableDocument

rule = "Bar Matter No. 803, Jan. 1, 2000"

assert list(CitableDocument.get_docketed_reports(rule)) == []
assert len(list(CitableDocument.get_docketed_reports(rule, False))) == 1
```

The exclusion is an exact match after canonicalization. It does not exclude
nearby values such as `B.M. No. 1803` or every A.M./B.M. reference. Use
`exclude_docket_rules=False` only when the calling workflow needs those rule
references as evidence.

## Render a stored record

Use `Citation.make_citation_string()` to make a readable string from valid
stored components. It validates the category, serial, date, and report form;
an unknown category returns `None`, while malformed known data raises
`ValueError`. It preserves qualified Official Gazette information.

```python
from citation_utils import Citation

assert Citation.make_citation_string(
    "gr", "L-I9863", "1964-04-29", offg="47 o.g. supp. 43"
) == "G.R. No. L-19863, Apr. 29, 1964, 47 O.G. Supp. 43"
```

## Regression evidence

`tests/fixtures/citation_regressions.json` is the compact decision record for
document-derived changes. Rows marked `observed` describe a reviewed text form;
rows marked `synthetic` establish the nearby acceptance or rejection boundary.
The fixtures are executed by `tests/test_citation_regressions.py`.
