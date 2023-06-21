import re
from typing import Any

from dateutil.parser import parse

from .main import extract_dockets

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
        {'docket': 'G.R. No. 234179', 'decision_date': datetime.date(2022, 12, 5), 'upload_date': '01/26/2023', 'context': 'G.R. No. 234179', 'short_category': 'GR', 'category': 'General Register', 'ids': '234179', 'docket_date': datetime.date(2022, 12, 5)}
        >>> extract_docket_meta("G.R. No. 180350/G.R. No. 205186/G.R. No. 222919/G.R. No. 223237. July 6, 2022 [Date Uploaded: 09/21/2022]")
        {'docket': 'G.R. No. 180350/G.R. No. 205186/G.R. No. 222919/G.R. No. 223237', 'decision_date': datetime.date(2022, 7, 6), 'upload_date': '09/21/2022', 'context': 'G.R. No. 180350/G.R. No. 205186/G.R. No. 222919/G.R. No. 223237', 'short_category': 'GR', 'category': 'General Register', 'ids': '180350', 'docket_date': datetime.date(2022, 7, 6)}

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
        citation_obj = next(extract_dockets(citation_text))
        cleaned_id = citation_obj.first_id
        res |= citation_obj.dict(
            exclude={
                "volume",
                "publisher",
                "page",
                "report",
                "report_date",
                "volpubpage",
            }
        )
        if res.get("short_category") is None:
            return None
        if res.get("ids") is None:
            return None
        else:
            res["ids"] = cleaned_id
    except Exception:
        res["decision_date"] = None
        return None
    return res
