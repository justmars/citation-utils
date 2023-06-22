import re
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum

from citation_report import Report

from ._types import DocketReportCitationType
from .extracts import extract_docketables
from .regexes import DocketCategory


class DocketRuleSerialNumber(Enum):
    BarMatter = [803, 1922, 1645, 850, 287, 1132, 1755, 1960, 209, 1153, 411, 356]
    AdminMatter = [r"(?:\d{1,2}-){3}SC\b", r"99-10-05-0\b"]

    @property
    def regex(self) -> str:
        return r"(?:" + "|".join(str(i) for i in self.value) + r")"

    @property
    def pattern(self) -> re.Pattern:
        return re.compile(self.regex)


@dataclass
class CitableDocument:
    """

    Examples:
        >>> text_statutes = "Bar Matter No. 803, Jan. 1, 2000; Bar Matter No. 411, Feb. 1, 2000"
        >>> doc0 = CitableDocument(text=text_statutes)
        >>> len(doc0.citeables)
        2
        >>> len(doc0.statute_like)
        2
        >>> len(doc0.case_like)
        0
        >>> text_no_statutes = "374 Phil. 1, 10-11 (1999) 1111 SCRA 1111; G.R. No. 147033, April 30, 2003; G.R. No. 147033, April 30, 2003, 374 Phil. 1, 600; ABC v. XYZ, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449;  XXX, G.R. No. 31711, Sept. 30, 1971, 35 SCRA 190; Hello World, 1111 SCRA 1111; Y v. Z, 35 SCRA 190;"
        >>> doc1 = CitableDocument(text=text_no_statutes)
        >>> len(doc1.citeables)
        4
        >>> len(doc1.statute_like)
        0
        >>> len(doc1.case_like)
        4
        >>> doc1.undocketed_reports
        {'1111 SCRA 1111'}

    """  # noqa: E501

    text: str

    def __post_init__(self):
        self.citeables = list(extract_docketables(self.text))
        self.statute_like = set(self.get_statutory_dockets())
        self.case_like = self.get_decision_dockets()
        self.reports = list(Report.extract_reports(self.text))
        unique_reports = set(Report.get_unique(self.text))
        self.undocketed_reports = self.get_undocketed_reports(unique_reports)

    def get_statutory_dockets(self) -> Iterator[str]:
        for d in self.citeables:  # includes solo reports
            if isinstance(d, DocketReportCitationType):  # excludes solo reports
                if d.category == DocketCategory.BM:
                    if DocketRuleSerialNumber.BarMatter.pattern.search(d.first_id):
                        yield str(d)
                elif d.category == DocketCategory.AM:
                    if DocketRuleSerialNumber.AdminMatter.pattern.search(d.first_id):
                        yield str(d)

    def get_decision_dockets(self) -> list[DocketReportCitationType]:
        if self.citeables:
            if not self.statute_like:
                return self.citeables

        dockets = []
        for d in self.citeables:
            if str(d) not in self.statute_like:
                dockets.append(d)
        return dockets

    def get_undocketed_reports(self, uniq_reports: set[str]):
        """Steps:

        1. From a set of `uniq_reports`;
        2. Compare to reports found in `@case_like`
        3. Limit reports to those _without_ an accompaying docket

        Args:
            text (str): Text to evaluate
        """
        for cite in self.case_like:
            if pre_existing_report := cite.volpubpage:
                if pre_existing_report in uniq_reports:
                    uniq_reports.remove(pre_existing_report)
        return uniq_reports

    def get_citations(self) -> Iterator[str]:
        if self.case_like:
            for cite in self.case_like:
                yield str(cite)
            if self.undocketed_reports:
                yield from self.undocketed_reports  # already <str>
        else:
            if self.reports:
                for report in self.reports:
                    yield str(report)
