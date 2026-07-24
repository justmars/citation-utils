"""Internal citation identity and occurrence aggregation.

This module deliberately does not use model equality.  A shared reporter can
be useful evidence, but it is not a transitive Python equality relation.
"""

import hashlib
import logging
from dataclasses import dataclass, replace
from datetime import date
from functools import lru_cache
from typing import Iterable

from citation_date import DOCKET_DATE_FORMAT
from citation_report import Report

from .dockets import Docket, DocketCategory


@dataclass(slots=True)
class CitationParts:
    category: DocketCategory | None = None
    serial: str | None = None
    docket_date: date | None = None
    phil: str | None = None
    scra: str | None = None
    offg: str | None = None
    start: int = -1

    @property
    def docket_key(self) -> tuple[str, str, str] | None:
        if not (self.category and self.serial and self.docket_date):
            return None
        serial = Docket.clean_serial(self.serial, self.category)
        if not serial:
            return None
        return (self.category.name.casefold(), serial, self.docket_date.isoformat())

    @property
    def report_keys(self) -> tuple[tuple[str, str], ...]:
        return tuple(
            (field, value.casefold())
            for field, value in (
                ("phil", self.phil),
                ("scra", self.scra),
                ("offg", self.offg),
            )
            if value
        )


@dataclass(frozen=True, slots=True)
class CitationOccurrence:
    """One lossless, source-ordered citation occurrence."""

    raw_text: str
    start: int
    end: int
    category: DocketCategory | None = None
    serial: str | None = None
    docket_date: date | None = None
    phil: str | None = None
    scra: str | None = None
    offg: str | None = None

    @property
    def occurrence_key(self) -> str:
        identity = "\0".join(
            (
                str(self.start),
                str(self.end),
                self.raw_text,
                self.category.name if self.category else "",
                self.serial or "",
                self.docket_date.isoformat() if self.docket_date else "",
                self.phil or "",
                self.scra or "",
                self.offg or "",
            )
        )
        return hashlib.sha256(identity.encode()).hexdigest()

    def to_parts(self) -> CitationParts:
        return CitationParts(
            category=self.category,
            serial=self.serial,
            docket_date=self.docket_date,
            phil=self.phil,
            scra=self.scra,
            offg=self.offg,
            start=self.start,
        )


@dataclass(slots=True)
class CitationGroup:
    parts: CitationParts
    mentions: int = 1
    first_start: int = -1

    def add(self, other: CitationParts) -> None:
        self.mentions += 1
        self.first_start = min(self.first_start, other.start)
        for field in ("phil", "scra", "offg"):
            incoming = getattr(other, field)
            current = getattr(self.parts, field)
            if incoming and not current:
                setattr(self.parts, field, incoming)
            elif incoming and current and incoming.casefold() != current.casefold():
                logging.warning(
                    "Conflicting %s evidence for %s; retaining first-seen %r over %r",
                    field,
                    self.parts.docket_key,
                    current,
                    incoming,
                )


def aggregate_occurrences(occurrences: Iterable[CitationParts]) -> list[CitationGroup]:
    """Aggregate ordered source occurrences into deterministic normalized groups.

    Docket triples are primary identities.  A report-only occurrence can enrich
    a docket only if that qualified report identity is attached to exactly one
    docket identity in the same document.
    """
    keyed_items = [(item, item.docket_key, item.report_keys) for item in occurrences]
    docket_groups: dict[tuple[str, str, str], CitationGroup] = {}
    report_to_dockets: dict[tuple[str, str], set[tuple[str, str, str]]] = {}

    for item, docket_key, report_keys in keyed_items:
        if not docket_key:
            continue
        group = docket_groups.get(docket_key)
        if group is None:
            group = CitationGroup(parts=replace(item), first_start=item.start)
            docket_groups[docket_key] = group
        else:
            group.add(item)
        for report_key in report_keys:
            report_to_dockets.setdefault(report_key, set()).add(docket_key)

    standalone_groups: dict[tuple[str, str], CitationGroup] = {}
    for item, docket_key, report_keys in keyed_items:
        if docket_key:
            continue
        if len(report_keys) != 1:
            continue
        report_key = report_keys[0]
        linked_dockets = report_to_dockets.get(report_key, set())
        if len(linked_dockets) == 1:
            docket_groups[next(iter(linked_dockets))].add(item)
            continue
        group = standalone_groups.get(report_key)
        if group is None:
            standalone_groups[report_key] = CitationGroup(
                parts=replace(item), first_start=item.start
            )
        else:
            group.add(item)

    return sorted(
        [*docket_groups.values(), *standalone_groups.values()],
        key=lambda group: group.first_start,
    )


@lru_cache(maxsize=4096)
def display_report(raw: str | None, field: str) -> str | None:
    if not raw:
        return None
    report = next(Report.extract_reports(raw), None)
    if not report:
        return raw
    if field == "offg":
        return report.qualified_offg or raw
    return getattr(report, field) or raw


def render_parts(parts: CitationParts) -> str:
    reports = [value for value in (parts.phil, parts.scra, parts.offg) if value]
    docket = None
    if parts.category and parts.serial and parts.docket_date:
        docket = (
            f"{parts.category.name} No. {parts.serial.upper()}, "
            f"{parts.docket_date.strftime(DOCKET_DATE_FORMAT)}"
        )
    return ", ".join([value for value in [docket, *reports] if value])
