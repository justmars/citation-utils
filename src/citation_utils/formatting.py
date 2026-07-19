"""Stable presentation helpers for downstream applications."""

from __future__ import annotations

from .citation import Citation

__all__ = ["get_docket_slug_from_text", "make_citation_string"]


def get_docket_slug_from_text(value: str) -> str | None:
    """Return the canonical decision slug represented by a docket string."""
    return Citation.get_docket_slug_from_text(value)


def make_citation_string(
    category: str,
    number: str,
    decision_date: str,
    phil: str | None = None,
    scra: str | None = None,
    offg: str | None = None,
) -> str | None:
    """Render database citation fields as a reader-facing citation."""
    return Citation.make_citation_string(
        category, number, decision_date, phil, scra, offg
    )
