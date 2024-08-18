import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass

from citation_report import Report

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


@dataclass
class CitableDocument:
    """Creates three main reusable lists:

    list | concept
    :--:|:--:
    `@docketed_reports` | list of `DocketReportCitation` found in the text, excluding exceptional statutory dockets
    `@reports` | list of `Report` found in the text (which may already be included in `@docketed_reports`)
    `@undocketed_reports` | = `@docketed_reports` - `@reports`

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
        self.text = unicodedata.normalize("NFKD", self.text)
        self.reports = list(Report.extract_reports(self.text))
        self.docketed_reports = list(self.get_docketed_reports(self.text))
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
        text = unicodedata.normalize("NFKD", text)
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
            # Each search function is applied to the text, each match yielded
            for result in search_func(text):
                if exclude_docket_rules:
                    if is_statutory_rule(result):
                        continue
                    yield result

    def get_undocketed_reports(self):
        """Steps:

        1. From a set of `uniq_reports` (see `self.reports`);
        2. Compare to reports found in `@docketed_reports`
        3. Limit reports to those _without_ an accompaying docket
        """
        uniq_reports = set(Report.get_unique(self.text))
        for cite in self.docketed_reports:
            if cite.volpubpage in uniq_reports:
                uniq_reports.remove(cite.volpubpage)
        return uniq_reports

    def get_citations(self) -> Iterator[str]:
        """There are two main lists to evaluate:

        1. `@docketed_reports` - each includes a `Docket` (optionally attached to a `Report`)
        2. `@reports` - from the same text, just get `Report` objects.

        Can filter out `Report` objects not docketed and thus return
        a more succinct citation list which includes both constructs mentioned above but
        without duplicate `reports`.
        """  # noqa: E501
        if self.docketed_reports:
            for doc_report_cite in self.docketed_reports:
                yield str(doc_report_cite)

            if self.undocketed_reports:
                yield from self.undocketed_reports  # already <str>
        else:
            if self.reports:
                for report in self.reports:
                    yield str(report)
