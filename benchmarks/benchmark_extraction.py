"""Small repeatable extraction benchmarks for local optimization checks.

Run with ``uv run python benchmarks/benchmark_extraction.py``.  These are not
test thresholds: they report timings for representative dense and no-match
inputs so results remain meaningful across machines.
"""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter

from citation_utils import CitableDocument, CountedCitation, Docket
from citation_utils.identity import CitationParts, display_report, render_parts


def measure(name: str, operation: Callable[[], object], repeats: int = 5) -> None:
    timings = []
    for _ in range(repeats):
        start = perf_counter()
        operation()
        timings.append(perf_counter() - start)
    print(f"{name}: min={min(timings):.4f}s mean={sum(timings) / repeats:.4f}s")


def extract(text: str) -> None:
    list(CitableDocument(text).get_citations())


def main() -> None:
    dense = "; ".join(
        f"G.R. No. {index}, Jan. 1, 2000, {index} SCRA 1" for index in range(1000, 3000)
    )
    report_only = "; ".join(f"{index} SCRA 1" for index in range(1000, 3000))
    mixed = "; ".join(
        [
            "G.R. No. 1, Jan. 1, 2000, 1 SCRA 1",
            "A.M. No. P-13-3116, Jan. 1, 2000, 2 SCRA 2",
            "A.C. No. 10179, Jan. 1, 2000, 3 SCRA 3",
            "Bar Matter No. 1678, Jan. 1, 2000, 4 SCRA 4",
        ]
        * 250
    )
    overlapping_ownership = "; ".join(
        "A.M. No. P-13-3116, Jan. 1, 2000, 1 SCRA 1" for _ in range(1000)
    )
    adversarial_near_miss = (
        "; ".join("A.M. No. 123 and A.M. No. " for _ in range(1000)) + "; Jan. 1, 2000"
    )
    no_match = "unrelated prose " * 8_000
    canonical_parts = CitationParts(
        phil="1 Phil. 2", scra="3 SCRA 4", offg="47 O.G. Supp. 43"
    )

    measure(
        "short valid snippet",
        lambda: extract("G.R. No. 1, Jan. 1, 2000, 1 SCRA 1"),
    )
    measure("100 KB no-date prose", lambda: extract(no_match))
    measure("report-only text", lambda: extract(report_only))
    measure("mixed categories", lambda: extract(mixed))
    measure("dense docket/report pairs", lambda: extract(dense))
    measure("overlapping ownership", lambda: extract(overlapping_ownership))
    measure("adversarial AM near miss", lambda: extract(adversarial_near_miss))
    measure("counted reports", lambda: CountedCitation.counted_reports(report_only))
    measure(
        "canonical report rendering",
        lambda: [render_parts(canonical_parts) for _ in range(10_000)],
    )
    measure(
        "cached arbitrary report display",
        lambda: [display_report("47 o.g. supp. 43", "offg") for _ in range(10_000)],
    )
    measure(
        "numeric GR normalization",
        lambda: [Docket.clean_serial("123", "GR") for _ in range(10_000)],
    )
    measure(
        "legacy GR repair",
        lambda: [Docket.clean_serial("L-I9863", "GR") for _ in range(10_000)],
    )


if __name__ == "__main__":
    main()
