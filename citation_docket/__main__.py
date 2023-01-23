from collections.abc import Iterator

from .regexes import (
    CitationAdministrativeCase,
    CitationAdministrativeMatter,
    CitationBarMatter,
    CitationGeneralRegister,
)
from .simple_matcher import setup_docket_field

DocketReportCitationType = (
    CitationAdministrativeCase
    | CitationAdministrativeMatter
    | CitationBarMatter
    | CitationGeneralRegister
)


def extract_dockets(
    raw: str,
) -> Iterator[DocketReportCitationType]:
    """Extract from `raw` text all raw citations which
    should include their `Docket` and `Report` component parts.

    Examples:
        >>> from citation_docket import extract_dockets
        >>> text = "Bagong Alyansang Makabayan v. Zamora, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449"
        >>> docket = next(extract_dockets(text))
        CitationGeneralRegister(publisher='SCRA', volume='342', page='449', volpubpage='342 SCRA 449', report_date=None, context='G.R. Nos. 138570, 138572, 138587, 138680, 138698', short_category='GR', category='General Register', ids='138570, 138572, 138587, 138680, 138698', docket_date=datetime.date(2000, 10, 10))
        >>> str(docket)
        'GR 138570, Oct. 10, 2000'

    Args:
        raw (str): Text to look for `Dockets` and `Reports`

    Yields:
        Iterator[DocketReportCitationType]: Any of custom `Docket` with `Report` types, e.g. `CitationAdministrativeCase`, etc.
    """  # noqa: E501
    for citation in [
        CitationAdministrativeCase,
        CitationAdministrativeMatter,
        CitationBarMatter,
        CitationGeneralRegister,
    ]:
        yield from citation.search(raw)


def extract_docket_from_data(data: dict) -> DocketReportCitationType | None:
    """
    Return a DocketReportCitationType based on contents of a `data` dict.

    Examples:
        >>> from citation_docket import extract_docket_from_data
        >>> data = {
            "date_prom": "1985-04-24",
            "docket": "General Register L-63915, April 24, 1985",
            "orig_idx": "GR No. L-63915",
            "phil": "220 Phil. 422",
            "scra": "136 SCRA 27",
            "offg": None,
        } # assume transformation from /details.yaml file
        >>> extract_citation_from_data(data)
        'CitationGeneralRegister(publisher=None, volume=None, page=None, volpubpage=None, report_date=None, context='G.R. No. L-63915', short_category='GR', category='General Register', ids='L-63915', docket_date=datetime.date(1985, 4, 24))'

    Args:
        data (dict): Should contain relevant keys.

    Returns:
        DocketReportCitationType: _description_
    """  # noqa: E501
    try:
        return next(extract_dockets(setup_docket_field(data)))
    except Exception:
        return None
