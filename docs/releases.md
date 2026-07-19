---
icon: lucide/history
---

# Release History

## 1.0.0

`citation-utils` 1.0.0 is the first stable-contract release. It compares the
last pushed 0.5.0 release at commit `6efb9ff` with the current implementation.
The intermediate 0.6.x version metadata was never pushed as a release and is
therefore included in this 1.0.0 boundary rather than listed separately.

The serialized database fields remain `cat`, `num`, `date`, `phil`, `scra`,
and `offg`. The supported docket categories are unchanged. Reporter grammar
and report-text normalization remain owned by `citation-report`, now required
at version 0.4.0 or newer.

### Before: 0.5.0 and After: 1.0.0

| Area | Before: 0.5.0 | After: 1.0.0 |
| --- | --- | --- |
| Source evidence | Extraction exposed normalized aggregate records. | `iter_occurrences()` also exposes immutable raw text, offsets, parsed fields, and a deterministic occurrence key. |
| Unicode footnotes | Compatibility normalization could promote a superscript footnote to a page digit. | `374 Phil. 1²` retains the report identity `374 Phil. 1`. |
| Official Gazette | Supplement and issue information could collapse into an unqualified volume/page identity. | `47 O.G. Supp. 43` and `49 O.G. No. 7, 2740` remain distinct qualified identities. |
| Citation equality | Dockets sharing any reporter could compare equal. | Equality compares the complete normalized citation record. |
| Counting | Shared-report equality could merge unrelated docket identities. | Report-only evidence enriches a docket only when it identifies exactly one docket in the document. |
| Category ownership | Category-like legacy serials could also produce a phantom G.R. match. | Explicit A.C., A.M., B.M., OCA, and CA-G.R. context owns its serial. |
| Malformed compounds | A nullable repeated key could widen a citation context without owning a serial. | `A.M. No. 123 and A.M. No. , Jan 1, 2020` yields no citation. |
| Serial cleanup | Permissive cleanup could retain trailing junk or malformed separators. | Canonical serials are ASCII alphanumeric segments joined by single hyphens; narrowly documented OCR repairs remain supported. |
| Document evaluation | Reporter and docket scans were eager and repeated, with pairwise span checks. | Views are lazy and cached; report models and spans are extracted once; span containment is indexed. |

### Features

- `CitationOccurrence` is a public, immutable evidence record containing
  `raw_text`, `start`, `end`, docket/report fields, and `occurrence_key`.
- `CitableDocument.iter_occurrences()` preserves every source-ordered
  occurrence, while `Citation.extract_citations()` continues to return unique
  normalized records.
- `citation_utils.formatting` provides the bounded downstream façade
  `get_docket_slug_from_text()` and `make_citation_string()`.
- Qualified Official Gazette supplements and issue numbers survive extraction,
  rendering, equality, uniqueness, and counting.
- Database aliases can reconstruct a model directly, including lower-case
  category codes.

Before 1.0.0, repeated mentions were available only through aggregation:

```python
from citation_utils import Citation

text = "100 SCRA 1; see again 100 SCRA 1"
records = list(Citation.extract_citations(text))
assert len(records) == 1
```

After 1.0.0, callers can retain the two pieces of source evidence before
choosing whether to aggregate them:

```python
from citation_utils import CitableDocument

text = "100 SCRA 1; see again 100 SCRA 1"
occurrences = list(CitableDocument(text).iter_occurrences())

assert [text[item.start:item.end] for item in occurrences] == [
    "100 SCRA 1",
    "100 SCRA 1",
]
assert occurrences[0].occurrence_key != occurrences[1].occurrence_key
```

### Corrections and Bug Fixes

- NFC report normalization prevents superscript and circled footnotes from
  becoming citation digits.
- U.S.- and U.K.-ordered report and docket dates are decoded without treating
  pinpoint pages as dates or inventing a current-year value for malformed text.
- Category ownership prevents nested A.C., A.M., B.M., OCA, and Court of
  Appeals references from emitting an additional G.R. citation.
- Statutory A.M. and B.M. exclusions use exact canonical serial matches rather
  than prefix or substring behavior.
- Legacy G.R. OCR forms such as `L-I9863`, `L-L8432`, `I-47629`, and
  `L-No. 40004` retain bounded repairs, while malformed serials such as `---`
  and `1--` are rejected.
- First-seen ordering, duplicate counts, source spans, compound raw IDs, and
  qualified O.G. identities are retained throughout aggregation.

The equality contract is intentionally narrower. Under 0.5.0, the shared SCRA
value could make these different dockets compare equal. Under 1.0.0 they do
not:

```python
from citation_utils import Citation

first = Citation(cat="gr", num="1", date="2000-01-01", scra="100 SCRA 1")
second = Citation(cat="gr", num="2", date="2000-01-02", scra="100 SCRA 1")

assert first != second
```

Counting no longer chooses a docket winner when one reporter is attached to
more than one docket:

```python
from citation_utils import CountedCitation

source = (
    "G.R. No. 1, Jan. 1, 2000, 100 SCRA 1; "
    "G.R. No. 2, Jan. 2, 2000, 100 SCRA 1; "
    "100 SCRA 1"
)
citations = CountedCitation.from_source(source)

assert [item.docket_serial for item in citations] == ["1", "2", None]
assert [item.mentions for item in citations] == [1, 1, 1]
```

Qualified O.G. material is preserved rather than reduced to plain volume and
page:

```python
from citation_utils import Citation

supplement = Citation.extract_citation("47 O.G. Supp. 43")
issue = Citation.extract_citation("49 O.G. No. 7, 2740")

assert supplement is not None and supplement.offg == "47 O.G. Supp. 43"
assert issue is not None and issue.offg == "49 O.G. No. 7, 2740"
```

### Performance and Maintainability

- `citation-report` supplies report models and spans in one normalized scan.
- Date and conservative category preflights avoid impossible full-pattern
  searches.
- Large compiled patterns are retained with mutation-aware private caches.
- Indexed span containment replaces repeated docket-by-report comparisons.
- Docket and report events are merged in source order without a combined sort.
- AC, AM, BM, and G.R. repetition rules avoid catastrophic backtracking on
  malformed and date-less near matches.
- Serial normalization, identity aggregation, and report rendering avoid
  repeated parsing and canonicalization work.

The repository benchmark is a comparison aid, not a machine-independent
performance guarantee. On the development machine used for this release,
report-only extraction improved from approximately 0.014 seconds to 0.009
seconds. Dense docket/report and 100 KB no-date workloads remained stable at
approximately 0.12 seconds and 0.003 seconds, respectively.

### Developer Experience

- Python 3.14 is the supported runtime.
- The package uses `uv_build`, Zensical documentation, a Marimo citation
  explorer, an executable regression corpus, and a standard-library benchmark
  harness.
- `just check` runs tests and doctests, checks the Marimo notebook, performs a
  clean strict documentation build, and builds source and wheel distributions.
- CI checks out the sibling `citation-date` and `citation-report` repositories
  and verifies the same package, documentation, and notebook boundaries.

### Migration from 0.5.0

1. Upgrade to Python 3.14 and install `citation-date>=1.0.0`,
   `citation-report>=1.0.0`, `pydantic>=2.12.5`, and
   `python-dateutil>=2.9.0.post0`.
2. Review code that relied on two citations comparing equal merely because
   they shared one reporter. Use explicit identity fields or
   `CountedCitation.from_source()` instead.
3. Use `iter_occurrences()` when raw source text, offsets, or every repeated
   mention must be retained; use `extract_citations()` for unique normalized
   records.
4. Expect malformed serials and dangling compound keys to be rejected rather
   than partially normalized.
5. Store the complete qualified `offg` value so supplements and issue-number
   references remain distinct.
6. Continue using `cat`, `num`, `date`, `phil`, `scra`, and `offg` for database
   serialization; their names and meanings remain stable.

## 0.5.0

This was the previous pushed release and is the comparison baseline for
1.0.0. It provided docket/report extraction and the stable database aliases,
but not the lossless occurrence, qualified O.G., deterministic aggregation,
or performance contracts documented above.
