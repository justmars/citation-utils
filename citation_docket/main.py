from collections.abc import Iterator

from .regexes import (
    CitationAC,
    CitationAM,
    CitationBM,
    CitationGR,
    CitationOCA,
    CitationPET,
)
from .simple_matcher import setup_docket_field

DocketReportCitationType = (
    CitationAC | CitationAM | CitationOCA | CitationBM | CitationGR | CitationPET
)  # noqa: E501

CITATIONS = [
    CitationAC,
    CitationAM,
    CitationOCA,
    CitationBM,
    CitationGR,
    CitationPET,
]


def extract_dockets(raw: str) -> Iterator[DocketReportCitationType]:
    """Extract from `raw` text all raw citations which
    should include their `Docket` and `Report` component parts.

    Examples:
        >>> cite = next(extract_dockets("Bagong Alyansang Makabayan v. Zamora, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449"))
        >>> cite.model_dump(exclude_none=True)
        {'publisher': 'SCRA', 'volume': '342', 'page': '449', 'volpubpage': '342 SCRA 449', 'context': 'G.R. Nos. 138570, 138572, 138587, 138680, 138698', 'short_category': <ShortDocketCategory.GR: 'GR'>, 'category': <DocketCategory.GR: 'General Register'>, 'ids': '138570, 138572, 138587, 138680, 138698', 'docket_date': datetime.date(2000, 10, 10)}

    Args:
        raw (str): Text to look for `Dockets` and `Reports`

    Yields:
        Iterator[DocketReportCitationType]: Any of custom `Docket` with `Report` types, e.g. `CitationAC`, etc.
    """  # noqa: E501
    for citation in CITATIONS:
        yield from citation.search(raw)


def extract_docket_from_data(data: dict) -> DocketReportCitationType | None:
    """Return a DocketReportCitationType based on contents of a `data` dict.

    Examples:
        >>> data = {"date_prom": "1985-04-24", "docket": "General Register L-63915, April 24, 1985", "orig_idx": "GR No. L-63915", "phil": "220 Phil. 422", "scra": "136 SCRA 27", "offg": None} # assume transformation from /details.yaml file
        >>> cite = extract_docket_from_data(data)
        >>> cite.model_dump(exclude_none=True)
        {'context': 'G.R. No. L-63915', 'short_category': <ShortDocketCategory.GR: 'GR'>, 'category': <DocketCategory.GR: 'General Register'>, 'ids': 'L-63915', 'docket_date': datetime.date(1985, 4, 24)}

    Args:
        data (dict): Should contain relevant keys.

    Returns:
        DocketReportCitationType: Any of custom `Docket` with `Report` types, e.g. `CitationAC`
    """  # noqa: E501
    try:
        return next(extract_dockets(setup_docket_field(data)))
    except Exception:
        return None
