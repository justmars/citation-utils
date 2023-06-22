import re
from collections.abc import Iterator
from typing import Any

from dateutil.parser import parse

from ._types import CITATION_OPTIONS, DocketReportCitationType


def extract_docketables(raw: str) -> Iterator[DocketReportCitationType]:
    """Extract from `raw` text all raw citations which
    should include their `Docket` and `Report` component parts.

    Examples:
        >>> cite = next(extract_docketables("Bagong Alyansang Makabayan v. Zamora, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449"))
        >>> cite.model_dump(exclude_none=True)
        {'publisher': 'SCRA', 'volume': '342', 'page': '449', 'volpubpage': '342 SCRA 449', 'context': 'G.R. Nos. 138570, 138572, 138587, 138680, 138698', 'category': 'GR', 'ids': '138570, 138572, 138587, 138680, 138698', 'docket_date': datetime.date(2000, 10, 10)}

    Args:
        raw (str): Text to look for `Dockets` and `Reports`

    Yields:
        Iterator[DocketReportCitationType]: Any of custom `Docket` with `Report` types, e.g. `CitationAC`, etc.
    """  # noqa: E501
    for citation in CITATION_OPTIONS:
        yield from citation.search(raw)


DOCKET_PATTERN = re.compile(
    r"""
    (?P<docket>.*?)
    \.
    \s+
    (?P<decision_date>[A-Z]\w+\s\d+,\s\d{4})
    (\s+
    \[
        Date
        \s
        Uploaa?ded: # deal with mispelled word
        \s
        (?P<upload_date>.*?)
    \])? # optional upload date, see Opinions which do not have them
""",
    re.X,
)


def extract_docket_meta(text: str) -> dict[str, Any] | None:
    """Metadata involving the docket.

    Examples:
        >>> extract_docket_meta("G.R. No. 234179. December 5, 2022 [Date Uploaded: 01/26/2023]")
        {'docket': 'G.R. No. 234179', 'decision_date': datetime.date(2022, 12, 5), 'upload_date': '01/26/2023', 'context': 'G.R. No. 234179', 'category': 'GR', 'ids': '234179', 'docket_date': datetime.date(2022, 12, 5)}
        >>> extract_docket_meta("G.R. No. 180350/G.R. No. 205186/G.R. No. 222919/G.R. No. 223237. July 6, 2022 [Date Uploaded: 09/21/2022]")
        {'docket': 'G.R. No. 180350/G.R. No. 205186/G.R. No. 222919/G.R. No. 223237', 'decision_date': datetime.date(2022, 7, 6), 'upload_date': '09/21/2022', 'context': 'G.R. No. 180350/G.R. No. 205186/G.R. No. 222919/G.R. No. 223237', 'category': 'GR', 'ids': '180350', 'docket_date': datetime.date(2022, 7, 6)}

    Args:
        text (str): Line from Supreme Court URL sub-title heading.

    Returns:
        dict[str, Any] | None: Docket-based details.
    """  # noqa: E501
    match = DOCKET_PATTERN.search(text)
    if not match:
        return None
    res = match.groupdict()

    if not res.get("docket"):
        return None

    if not (_date := res.get("decision_date")):
        return None

    try:
        res["decision_date"] = parse(_date, fuzzy=True).date()
        format_date = res["decision_date"].strftime("%B %d, %Y")
        citation_text = f"{res['docket']}, {format_date}"
        citation_obj = next(extract_docketables(citation_text))
        cleaned_id = citation_obj.first_id
        res |= citation_obj.model_dump(
            exclude={
                "volume",
                "publisher",
                "page",
                "report",
                "report_date",
                "volpubpage",
            }
        )
        if res.get("ids") is None:
            return None
        else:
            res["ids"] = cleaned_id
    except Exception:
        res["decision_date"] = None
        return None
    return res
