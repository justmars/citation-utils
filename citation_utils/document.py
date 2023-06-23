from collections.abc import Iterator
from dataclasses import dataclass

from citation_report import Report

from .extracts import extract_docketables


@dataclass
class CitableDocument:
    """Creates three main reusable lists:

    list | concept
    :--:|:--:
    `@citeables` | list of `DocketReportCitation` found in the text, excluding exceptional statutory dockets
    `@reports` | list of `Report` found in the text (which may already be included in `@citeables`)
    `@undocketed_reports` | = `@citeables` - `@reports`

    Examples:
        >>> text_statutes = "Bar Matter No. 803, Jan. 1, 2000; Bar Matter No. 411, Feb. 1, 2000"
        >>> len(CitableDocument(text=text_statutes).citeables) # no citations, since these are 'statutory dockets'
        0
        >>> text_cites = "374 Phil. 1, 10-11 (1999) 1111 SCRA 1111; G.R. No. 147033, April 30, 2003; G.R. No. 147033, April 30, 2003, 374 Phil. 1, 600; ABC v. XYZ, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449;  XXX, G.R. No. 31711, Sept. 30, 1971, 35 SCRA 190; Hello World, 1111 SCRA 1111; Y v. Z, 35 SCRA 190;"
        >>> doc1 = CitableDocument(text=text_cites)
        >>> len(doc1.citeables)
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
        self.citeables = list(extract_docketables(self.text, exclude_docket_rules=True))
        self.reports = list(Report.extract_reports(self.text))
        self.undocketed_reports = self.get_undocketed_reports()

    def get_undocketed_reports(self):
        """Steps:

        1. From a set of `uniq_reports` (see `self.reports`);
        2. Compare to reports found in `@citeables`
        3. Limit reports to those _without_ an accompaying docket

        Args:
            text (str): Text to evaluate
        """
        uniq_reports = set(Report.get_unique(self.text))
        for cite in self.citeables:
            if cite.volpubpage in uniq_reports:
                uniq_reports.remove(cite.volpubpage)
        return uniq_reports

    def get_citations(self) -> Iterator[str]:
        """There are two main constructs to evaluate:

        1. A list of `citeables` - each will include a `Docket` (attached to a `Report`)
        2. A list of `reports` - from the same text, just get `Report` objects.

        Based on two lists, can filter out `Report` objects not docketed and thus return
        a more succinct citation list which includes both constructs mentioned above but
        without duplicate `reports`.
        """  # noqa: E501
        if self.citeables:
            for cite in self.citeables:
                yield str(cite)
            if self.undocketed_reports:
                yield from self.undocketed_reports  # already <str>
        else:
            if self.reports:
                for report in self.reports:
                    yield str(report)
