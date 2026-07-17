# Faster Citation Detection and Parsing

## Summary

Optimize both short snippets and long documents while preserving extraction results, ordering, counting, raw compound IDs, and model validation. Coordinate changes across `citation-utils` and `citation-report`; allow `CitableDocument` collections to become cached lazy properties.

Measured priorities include the quadratic report-containment loop, catastrophic near-miss regexes, eight unconditional docket scans, duplicate reporter scans, and repeated serial normalization.

## Status

Implemented on 2026-07-17. Both repositories pass `just check`; the repeatable
workloads now live in `benchmarks/benchmark_extraction.py`. The acceptance
targets remain comparison targets for future before/after runs, not assertions
embedded in the test suite.

## Implementation Changes

> The before/after snippets below are structural pseudocode. Names such as
> `ALL_DOCKET_SEARCHERS`, `DOCKET_MATCHERS`, and `category_*` describe roles;
> they are not existing symbols or paste-ready replacements. Implementation
> must adapt the current inline tuples, concrete named groups, and event
> consumers rather than copying the sketches verbatim.

### Bound AC, AM, and BM serial-list backtracking

The current repeated branch is nullable: both the repeated key and serial are
optional, and the entire optional branch is repeated. A near match followed by
punctuation but no usable date can therefore be partitioned many different
ways before the regex finally fails.

Before, structurally:

```python
optional = rf"""
    (?P<category_init_optional>{category_and_number})?
    (?P<category_middle_optional>{serial})?
    {serial_separator}*
"""

category_phrase = rf"{required}({optional}){{1,3}}"
```

After, every repetition consumes an actual serial and the repetition count
expresses the intended zero to three additional serials directly:

```python
additional_serial = rf"""
    (?P<category_init_optional>{category_and_number})?
    (?P<category_middle_optional>{serial})
    {serial_separator}*
"""

category_phrase = rf"{required}(?:{additional_serial}){{0,3}}"
```

Apply this shape separately to AC, AM, and BM while retaining their existing
named groups. Confirm that single-serial matches and compound forms such as
`A.M. Nos. P-13-3116 & P-13-3112` produce the same captured phrase and public
model. Intentionally reject the malformed
`A.M. No. 123 and A.M. No. , Jan 1, 2020`: the old nullable repetition could
consume the dangling second key without a serial and widen `context`, while the
new grammar requires every additional key to own a serial.

### Avoid impossible full-pattern scans

Every docket matcher requires a `DOCKET_DATE_REGEX` match, but the current
orchestrator runs all eight full patterns for every input.

`citation-date` exports the raw regex string, not a compiled
`DOCKET_DATE_PATTERN`. Compile the preflight once in `citation-utils`, with both
mandatory flags:

```python
DOCKET_DATE_PATTERN = re.compile(DOCKET_DATE_REGEX, re.I | re.X)
```

`re.X` is required because `DOCKET_DATE_REGEX` is verbose-mode grammar;
compiling it without that flag silently turns formatting whitespace and
comments into pattern content. Keep `citation-date` itself unchanged.

Before:

```python
candidates = []
for search_func in ALL_DOCKET_SEARCHERS:
    candidates.extend(search_func(text))
```

After:

```python
if not DOCKET_DATE_PATTERN.search(text):
    return

candidates = []
for hint_pattern, search_func in DOCKET_MATCHERS:
    if hint_pattern.search(text):
        candidates.extend(search_func(text))
```

Use each constructor's key/number grammar as the conservative hint for AC,
AM, OCA, BM, PET, UDK, and JIB. Give GR a dedicated union hint covering its
explicit `G.R.` branch, implicit L/I-prefixed branch, and irregular `, Nos.`
branch. Hints may produce false positives, which only cost a full scan, but
must never produce false negatives.

### Retain compiled patterns without freezing public constructors

The constructor properties currently call `re.compile()` whenever accessed
and rely on CPython's global regex cache. The key pattern is also looked up
again for each detected match.

Before:

```python
for match in self.pattern.finditer(raw):
    raw_id = self.key_num_pattern.sub("", context)
```

After:

```python
_pattern_cache = PrivateAttr(default=None)
_key_num_pattern_cache = PrivateAttr(default=None)

pattern = self.pattern
key_num_pattern = self.key_num_pattern

for match in pattern.finditer(raw):
    raw_id = key_num_pattern.sub("", context)
```

Back `pattern` and `key_num_pattern` with private caches that store both the
compiled object and the source-field tuple used to build it. On access, return
the retained object when the tuple is unchanged; otherwise recompile and
replace the cache. Because `CitationConstructor` is a Pydantic `BaseModel`,
declare both caches with `PrivateAttr`; assigning undeclared plain attributes
would raise. This preserves mutation of exported `constructed_*` instances
while preventing unrelated regex activity from evicting the large docket
patterns. Compile constant serial-cleaning and implicit-owner patterns once at
module scope as well.

### Make span ownership and containment indexed

The current report filtering compares every report span with every docket
span. Implicit GR ownership performs the same kind of repeated linear scan over
explicit-category spans.

Before:

```python
report_events = [
    (span, report)
    for span, report in self._report_occurrences
    if not any(
        docket_start <= span[0] and span[1] <= docket_end
        for (docket_start, docket_end), _ in docket_events
    )
]
```

After:

```python
span_index = _SpanIndex.from_spans(
    result._source_span for result in self.docketed_reports
)

report_events = [
    (span, report)
    for span, report in self._report_occurrences
    if not span_index.contains_span(span)
]
```

`_SpanIndex` will sort starts once and keep a prefix maximum of ends. For a
query, use `bisect_right(starts, query_start) - 1`; a report is contained only
when the corresponding prefix maximum is at least its end. The same index can
answer `contains_point(start)` for implicit GR ownership. Do not merge spans
into their union, because a report crossing two overlapping spans is not
necessarily contained by either original match.

Both docket and uncontained-report events are already source ordered. Replace
the combined list allocation and sort with a two-way merge, using docket events
first when starts are equal:

```python
docket_events = (
    (span[0], 0, "docket", result)
    for span, result in docket_events
)
report_events = (
    (span[0], 1, "report", report)
    for span, report in report_events
)

merged_events = heapq.merge(
    docket_events,
    report_events,
    key=lambda event: event[:2],
)
for start, _, kind, value in merged_events:
    if kind == "docket":
        yield docket_parts(value, start)
    else:
        yield report_parts(value, start)
```

The merged representation is a four-tuple rather than the current event
three-tuple. Update the consumer in the same change to unpack
`start, tie_breaker, kind, value`, ignore `tie_breaker` after ordering, and run
the existing docket/report `CitationParts` projection based on `kind`.
`docket_parts()` and `report_parts()` above stand for those existing projection
branches; they are not new required helpers.

### Parse reporter models and spans in one pass

`CitableDocument` currently asks `citation-report` for models and then scans
the same normalized text again to recover their spans.

Before:

```python
self.reports = list(Report.extract_reports(self.text))
self._report_occurrences = list(
    zip(
        (match.span() for match in REPORT_PATTERN.finditer(self.text)),
        self.reports,
        strict=True,
    )
)
```

After the new upstream API is available:

```python
self._report_occurrences = list(
    Report.extract_reports_with_spans(
        self.text,
        text_is_normalized=True,
    )
)
self.reports = [report for _, report in self._report_occurrences]
```

Inside `citation-report`, preserve the existing completeness filter and attach
the span only after a model qualifies:

```python
for match in REPORT_PATTERN.finditer(normalized_text):
    publisher = get_publisher_label(match)
    volume = match.group("volume")
    page = match.group("page")
    if not (publisher and volume and page):
        continue

    report = Report(
        publisher=publisher,
        volume=volume,
        page=page,
        # Decode and pass the existing optional fields unchanged.
    )
    yield match.span(), report
```

`extract_reports()` must delegate by discarding spans from this already
filtered iterator. Do not yield a span for a regex match that lacks publisher,
volume, or page: that would break current extraction parity and could
misalign callers that assume every occurrence contains a validated model.

The match-to-model conversion remains owned by `citation-report`; do not copy
publisher, date, supplement, or issue-number parsing into `citation-utils`.

### Make document collections lazy but type-compatible

Construction currently computes all document views even when extraction only
needs docket and report occurrences.

Before:

```python
def __post_init__(self):
    self.text = normalize_report_text(self.text)
    self.reports = ...
    self.docketed_reports = ...
    self._report_occurrences = ...
    self.undocketed_reports = ...
```

After:

```python
def __post_init__(self):
    self.text = normalize_report_text(self.text)

@cached_property
def _report_occurrences(self):
    return list(
        Report.extract_reports_with_spans(
            self.text,
            text_is_normalized=True,
        )
    )

@cached_property
def reports(self):
    return [report for _, report in self._report_occurrences]

@cached_property
def docketed_reports(self):
    return list(self._get_docketed_reports_from_normalized_text())

@cached_property
def undocketed_reports(self):
    return self.get_undocketed_reports()
```

Keep the public values as `list`, `list`, and `set`, respectively. The public
`get_docketed_reports()` classmethod continues to normalize arbitrary caller
input; the lazy property uses a private normalized-text helper so the same
document is not normalized twice.

### Remove repeated identity and serial normalization work

Compute each `CitationParts.docket_key` and `report_keys` once, then reuse those
values for both docket grouping and report-only linking rather than invoking
the properties in both aggregation passes.

Before:

```python
for item in items:
    if item.docket_key:
        ...

for item in items:
    if item.docket_key:
        continue
    if len(item.report_keys) == 1:
        ...
```

After:

```python
keyed_items = [
    (item, item.docket_key, item.report_keys)
    for item in items
]

for item, docket_key, report_keys in keyed_items:
    ...
```

Also check the category before canonicalizing statutory-rule serials, split a
compound serial only once, use an ASCII-only digit fast path for already valid
numeric serials, and make internal identity dataclasses slotted. Keep normal
Pydantic construction and assignment validation; do not use `model_construct()`
as a performance shortcut.

### Make metadata-heading parsing single-pass

The metadata helper currently uses an unanchored lazy match, parses the date
generically, formats it back to text, and then asks the docket detector to parse
it again.

Before:

```python
match = DOCKET_PATTERN.search(text)
decision_date = dateutil.parser.parse(raw_date, fuzzy=True).date()
citation_text = f"{docket}, {decision_date:%B %d, %Y}"
citation = next(CitableDocument.get_docketed_reports(citation_text))
```

After:

```python
match = DOCKET_PATTERN.match(text)
citation = next(
    CitableDocument.get_docketed_reports(
        f"{match['docket']}, {match['decision_date']}"
    )
)
result["decision_date"] = citation.docket_date
```

The documented input is one complete subtitle heading, so matching from the
start preserves valid inputs while preventing the engine from retrying the
lazy docket prefix at every character. Do not add an end anchor, so existing
trailing-text tolerance remains intact.

## Interface and Dependency Changes

- Add to `citation-report`:

  ```python
  Report.extract_reports_with_spans(
      text: str,
      *,
      text_is_normalized: bool = False,
  ) -> Iterator[tuple[tuple[int, int], "Report"]]
  ```

  It will perform one `REPORT_PATTERN` pass, returning each full match span only
  when publisher, volume, and page are all present and the validated model is
  yielded. Existing `extract_reports()` will delegate to the same filtered
  iterator and discard spans.

- `CitableDocument` will call the new method with `text_is_normalized=True`; public citation-utils signatures and serialized fields remain unchanged.
- Preserve `Citation.extract_citation()` enrichment semantics; do not add or substitute a non-enriching fast-first path.
- Preserve exported regex named groups and numeric capture layout for now; capture-group reduction is deferred as a separate compatibility decision.
- Bump `citation-report` to `0.4.0`, require `citation-report>=0.4.0`, and bump `citation-utils` to `0.6.1`; update lock metadata without publishing.

## Tests and Benchmarks

- Add parity tests for every docket category, compound AC/AM/BM serials, OCR repairs, statutory exclusions, report qualifiers, ordering, duplicate counting, and category ownership.
- Add adversarial cases for long comma-heavy AC/AM/BM near misses—including
  documents containing an unrelated valid date—and long invalid metadata
  headings. Lock the new malformed-input behavior with
  `A.M. No. 123 and A.M. No. , Jan 1, 2020`, which must yield no citation rather
  than attach the dangling key to the first serial's context.
- Test the date preflight with known US- and UK-order docket dates so omission
  of either `re.I` or `re.X` fails functionally rather than silently skipping
  all docket matchers.
- Unit-test span indexing with nested, overlapping, adjacent, and equal-start intervals, plus stable docket-first ordering on ties.
- Verify lazy collections retain their public types, compute once, and produce the same values as the eager implementation.
- Test report span extraction on normalized and non-normalized text, optional
  report dates, qualified Official Gazette forms, empty input, and compatibility
  with `extract_reports()`. Force an otherwise matching report to resolve a
  missing required component by monkeypatching `get_publisher_label()` to
  return `None`; assert that both APIs skip it. Also assert `CitableDocument`
  receives no occurrence and does not raise the old `zip(..., strict=True)`
  mismatch error.
- Add a standard-library benchmark harness covering short valid snippets, cache eviction, 100 KB no-date prose, report-only text, mixed categories, 2,000 dense docket/report pairs, overlapping ownership, and adversarial near misses.
- Acceptance targets: at least 2× faster dense and no-docket workloads, no more than 10% regression on short snippets, cache-eviction latency within 20% of warm latency, and effectively linear adversarial scaling. Keep timing thresholds out of pytest; record before/after medians and peak memory separately.
- Run `just check` in both repositories and confirm exact model-dump/count/order parity against the current regression corpus.

## Assumptions

- Spans returned after default normalization index the NFC-normalized text; `text_is_normalized=True` indexes the supplied text directly.
- Mutable public models remain supported, so normalized serials are not cached on those models.
- `citation-date` grammar and version remain unchanged.
