import re
from collections.abc import Iterator
from dataclasses import dataclass

from citation_report import REPORT_PATTERN, Report, normalize_report_text

from .dockets import (
    CitationAC,
    CitationAM,
    CitationBM,
    CitationGR,
    CitationJIB,
    CitationOCA,
    CitationPET,
    CitationUDK,
    DocketReport,
    is_statutory_rule,
)
from .identity import CitationParts, aggregate_occurrences, render_parts


@dataclass
class CitableDocument:
    """Creates three main reusable lists:

    list | concept
    :--:|:--:
    `@docketed_reports` | list of `DocketReportCitation` found in the text, excluding exceptional statutory dockets
    `@reports` | list of `Report` found in the text (which may already be included in `@docketed_reports`)
    `@undocketed_reports` | reports not attached to any docket match

    Examples:
        >>> text_statutes = "Bar Matter No. 803, Jan. 1, 2000; Bar Matter No. 411, Feb. 1, 2000"
        >>> len(CitableDocument(text=text_statutes).docketed_reports) # no citations, since these are 'statutory dockets'
        0
        >>> text_cites = "374 Phil. 1, 10-11 (1999) 1111 SCRA 1111; G.R. No. 147033, April 30, 2003; G.R. No. 147033, April 30, 2003, 374 Phil. 1, 600; ABC v. XYZ, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449;  XXX, G.R. No. 31711, Sept. 30, 1971, 35 SCRA 190; Hello World, 1111 SCRA 1111; Y v. Z, 35 SCRA 190;"
        >>> doc1 = CitableDocument(text=text_cites)
        >>> len(doc1.docketed_reports)
        4
        >>> doc1.undocketed_reports
        {'1111 SCRA 1111'}
        >>> text = "<em>Gatchalian Promotions Talent Pool, Inc. v. Atty. Naldoza</em>, 374 Phil. 1, 10-11 (1999), citing: <em>In re Almacen</em>, 31 SCRA 562, 600 (1970).; People v. Umayam, G.R. No. 147033, April 30, 2003; <i>Bagong Alyansang Makabayan v. Zamora,</i> G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449; Villegas <em>v.</em> Subido, G.R. No. 31711, Sept. 30, 1971, 41 SCRA 190;"
        >>> doc2 = CitableDocument(text=text)
        >>> set(doc2.get_citations()) == {'GR No. 147033, Apr. 30, 2003', 'GR No. 138570, Oct. 10, 2000, 342 SCRA 449', 'GR No. 31711, Sep. 30, 1971, 41 SCRA 190', '374 Phil. 1', '31 SCRA 562'}
        True
    """  # noqa: E501

    text: str

    def __post_init__(self):
        self.text = normalize_report_text(self.text)
        self.reports = list(Report.extract_reports(self.text))
        self.docketed_reports = list(self.get_docketed_reports(self.text))
        self._report_occurrences = list(
            zip(
                (match.span() for match in REPORT_PATTERN.finditer(self.text)),
                self.reports,
                strict=True,
            )
        )
        self.undocketed_reports = self.get_undocketed_reports()

    @classmethod
    def get_docketed_reports(
        cls, text: str, exclude_docket_rules: bool = True
    ) -> Iterator[DocketReport]:
        """Extract from `raw` text all raw citations which should include their `Docket` and `Report` component parts.
        This may however include statutory rules since some docket categories like AM and BM use this convention.
        To exclude statutory rules, a flag is included as a default.

        Examples:
            >>> cite = next(CitableDocument.get_docketed_reports("Bagong Alyansang Makabayan v. Zamora, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449"))
            >>> cite.model_dump(exclude_none=True)
            {'publisher': 'SCRA', 'volume': '342', 'page': '449', 'context': 'G.R. Nos. 138570, 138572, 138587, 138680, 138698', 'category': 'GR', 'ids': '138570, 138572, 138587, 138680, 138698', 'docket_date': datetime.date(2000, 10, 10)}
            >>> statutory_text = "Bar Matter No. 803, Jan. 1, 2000"
            >>> next(CitableDocument.get_docketed_reports(statutory_text)) # default
            Traceback (most recent call last):
                ...
            StopIteration

        Args:
            text (str): Text to look for `Dockets` and `Reports`

        Yields:
            Iterator[DocketReport]: Any of custom `Docket` with `Report` types, e.g. `CitationAC`, etc.
        """  # noqa: E501
        text = normalize_report_text(text)
        candidates: list[DocketReport] = []
        for search_func in (
            CitationAC.search,
            CitationAM.search,
            CitationOCA.search,
            CitationBM.search,
            CitationGR.search,
            CitationPET.search,
            CitationUDK.search,
            CitationJIB.search,
        ):
            candidates.extend(search_func(text))

        explicit_spans = [
            result._source_span for result in candidates if result._explicit_category
        ]
        seen: set[tuple[int, int, str, str]] = set()
        selected: list[DocketReport] = []
        for result in candidates:
            start, end = result._source_span
            if exclude_docket_rules and is_statutory_rule(result):
                continue
            if (
                result.category.name == "GR"
                and not result._explicit_category
                and cls._implicit_gr_is_owned(text, start, explicit_spans)
            ):
                continue
            key = (start, end, result.category.name, result.serial_text.casefold())
            if key not in seen:
                seen.add(key)
                selected.append(result)

        yield from sorted(selected, key=lambda result: result._source_span)

    @staticmethod
    def _implicit_gr_is_owned(
        text: str, start: int, explicit_spans: list[tuple[int, int]]
    ) -> bool:
        if any(
            explicit_start <= start < explicit_end
            for explicit_start, explicit_end in explicit_spans
        ):
            return True
        prefix = text[max(0, start - 80) : start]
        return bool(
            re.search(
                r"(?ix)(?:\bca\s*-?\s*g\.?r\.?|\bc\.a\.\s*g\.?r\.?|"
                r"\ba\.?c\.?|\ba\.?m\.?|\bb\.?m\.?|"
                r"\badmin(?:istrative)?\s+(?:case|matter)|\bbar\s+matter)"
                r"[^;\n]*$",
                prefix,
            )
        )

    def iter_parts(self) -> Iterator[CitationParts]:
        """Yield source occurrences without double-counting attached reports."""
        docket_events = [
            (result._source_span, result) for result in self.docketed_reports
        ]
        report_events = [
            (span, report)
            for span, report in self._report_occurrences
            if not any(
                docket_start <= span[0] and span[1] <= docket_end
                for (docket_start, docket_end), _ in docket_events
            )
        ]
        events = [
            *((span[0], "docket", result) for span, result in docket_events),
            *((span[0], "report", report) for span, report in report_events),
        ]
        for start, kind, value in sorted(events, key=lambda event: event[0]):
            if kind == "docket":
                yield CitationParts(
                    category=value.category,
                    serial=value.serial_text,
                    docket_date=value.docket_date,
                    phil=value.phil,
                    scra=value.scra,
                    offg=value.qualified_offg or value.offg,
                    start=start,
                )
            else:
                yield CitationParts(
                    phil=value.phil,
                    scra=value.scra,
                    offg=value.qualified_offg or value.offg,
                    start=start,
                )

    def get_undocketed_reports(self):
        """Steps:

        1. From a set of `uniq_reports` (see `self.reports`);
        2. Compare to reports found in `@docketed_reports`
        3. Limit reports to those _without_ an accompaying docket
        """
        docketed_report_keys = {
            value.casefold()
            for docket in self.docketed_reports
            for value in (
                docket.phil,
                docket.scra,
                docket.qualified_offg or docket.offg,
            )
            if value
        }
        undocketed_reports = set()
        for _, report in self._report_occurrences:
            value = next(
                value
                for value in (report.phil, report.scra, report.qualified_offg)
                if value
            )
            if value.casefold() not in docketed_report_keys:
                undocketed_reports.add(value)
        return undocketed_reports

    def get_citations(self) -> Iterator[str]:
        """There are two main lists to evaluate:

        1. `@docketed_reports` - each includes a `Docket` (optionally attached to a `Report`)
        2. `@reports` - from the same text, just get `Report` objects.

        Can filter out `Report` objects not docketed and thus return
        a more succinct citation list which includes both constructs mentioned above but
        without duplicate `reports`.
        """  # noqa: E501
        for group in aggregate_occurrences(self.iter_parts()):
            yield render_parts(group.parts)
