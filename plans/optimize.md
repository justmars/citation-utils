# Faster Citation Detection and Parsing

## Summary

Optimize both short snippets and long documents while preserving extraction results, ordering, counting, raw compound IDs, and model validation. Coordinate changes across `citation-utils` and `citation-report`; allow `CitableDocument` collections to become cached lazy properties.

Measured priorities include the quadratic report-containment loop, catastrophic near-miss regexes, eight unconditional docket scans, duplicate reporter scans, and repeated serial normalization.

## Implementation Changes

- Make AC, AM, and BM repeated serial branches non-nullable: each repetition must consume a serial, with zero to three additional serials. Preserve all named groups and valid compound forms.
- Add a compiled docket-date preflight, then conservative category hints before invoking each full matcher. The GR hint must cover explicit GR, implicit L/I, and `, Nos.` forms.
- Retain constructor regexes in mutation-aware private caches keyed by their source fields; bind compiled patterns once per detection call. Precompile constant normalization and ownership regexes.
- Anchor metadata-heading detection at the start and reuse the docket detector’s decoded date, eliminating the generic dateutil parse/format/reparse cycle.
- Introduce an internal span index using sorted starts plus prefix maximum ends. Use it for both implicit-GR ownership and report-within-docket checks, preserving exact single-span containment rather than merging overlapping spans.
- Merge already ordered docket and report event streams instead of building and sorting a combined list.
- Compute aggregation keys once per occurrence; make internal identity records slotted. Guard statutory checks by AM/BM category before normalizing, split serials once, add an ASCII-numeric fast path, and retain Pydantic validation.
- Make `reports`, `docketed_reports`, and `undocketed_reports` cached lazy properties with their existing list/list/set values. Normalize document text once and avoid computing unused collections.

## Interface and Dependency Changes

- Add to `citation-report`:

  ```python
  Report.extract_reports_with_spans(
      text: str,
      *,
      text_is_normalized: bool = False,
  ) -> Iterator[tuple[tuple[int, int], Self]]
  ```

  It will perform one `REPORT_PATTERN` pass, returning each full match span and validated model. Existing `extract_reports()` will delegate to it and discard spans.

- `CitableDocument` will call the new method with `text_is_normalized=True`; public citation-utils signatures and serialized fields remain unchanged.
- Preserve `Citation.extract_citation()` enrichment semantics; do not add or substitute a non-enriching fast-first path.
- Preserve exported regex named groups and numeric capture layout for now; capture-group reduction is deferred as a separate compatibility decision.
- Bump `citation-report` to `0.4.0`, require `citation-report>=0.4.0`, and bump `citation-utils` to `0.6.1`; update lock metadata without publishing.

## Tests and Benchmarks

- Add parity tests for every docket category, compound AC/AM/BM serials, OCR repairs, statutory exclusions, report qualifiers, ordering, duplicate counting, and category ownership.
- Add adversarial cases for long comma-heavy AC/AM/BM near misses—including documents containing an unrelated valid date—and long invalid metadata headings.
- Unit-test span indexing with nested, overlapping, adjacent, and equal-start intervals, plus stable docket-first ordering on ties.
- Verify lazy collections retain their public types, compute once, and produce the same values as the eager implementation.
- Test report span extraction on normalized and non-normalized text, optional report dates, qualified Official Gazette forms, empty input, and compatibility with `extract_reports()`.
- Add a standard-library benchmark harness covering short valid snippets, cache eviction, 100 KB no-date prose, report-only text, mixed categories, 2,000 dense docket/report pairs, overlapping ownership, and adversarial near misses.
- Acceptance targets: at least 2× faster dense and no-docket workloads, no more than 10% regression on short snippets, cache-eviction latency within 20% of warm latency, and effectively linear adversarial scaling. Keep timing thresholds out of pytest; record before/after medians and peak memory separately.
- Run `just check` in both repositories and confirm exact model-dump/count/order parity against the current regression corpus.

## Assumptions

- Spans returned after default normalization index the NFC-normalized text; `text_is_normalized=True` indexes the supplied text directly.
- Mutable public models remain supported, so normalized serials are not cached on those models.
- `citation-date` grammar and version remain unchanged.
