"""Small repeatable extraction benchmarks for local optimization checks.

Run with ``uv run python benchmarks/benchmark_extraction.py``.  These are not
test thresholds: they report timings for representative dense and no-match
inputs so results remain meaningful across machines.
"""

from __future__ import annotations

from time import perf_counter

from citation_utils import CitableDocument


def measure(name: str, text: str, repeats: int = 5) -> None:
    timings = []
    for _ in range(repeats):
        start = perf_counter()
        list(CitableDocument(text).get_citations())
        timings.append(perf_counter() - start)
    print(f"{name}: min={min(timings):.4f}s mean={sum(timings) / repeats:.4f}s")


def main() -> None:
    dense = "; ".join(
        f"G.R. No. {index}, Jan. 1, 2000, {index} SCRA 1"
        for index in range(1000, 3000)
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
        "A.M. No. P-13-3116, Jan. 1, 2000, 1 SCRA 1"
        for _ in range(1000)
    )
    adversarial_near_miss = "; ".join(
        "A.M. No. 123 and A.M. No. " for _ in range(1000)
    ) + "; Jan. 1, 2000"
    no_match = "unrelated prose " * 8_000

    measure("short valid snippet", "G.R. No. 1, Jan. 1, 2000, 1 SCRA 1")
    measure("100 KB no-date prose", no_match)
    measure("report-only text", report_only)
    measure("mixed categories", mixed)
    measure("dense docket/report pairs", dense)
    measure("overlapping ownership", overlapping_ownership)
    measure("adversarial AM near miss", adversarial_near_miss)


if __name__ == "__main__":
    main()
