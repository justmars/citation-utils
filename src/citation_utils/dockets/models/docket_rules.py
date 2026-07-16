from enum import Enum

from .docket_category import DocketCategory
from .docket_model import Docket


class DocketRuleSerialNumber(Enum):
    """A rule is more adequately defined in `statute-utils`. There are are `AM` and `BM` docket numbers
    that represent rules rather than decisions. The statutes are contained in a folder, e.g.
    `/corpus-statutes/rule-am`, `/corpus-statutes/rule-bm` and thus may be extracted likeso:

    ```py
    from pathlib import Path
    statutes = Path().home() / "code" / "corpus-statutes"
    ams = statutes.glob("rule_am/*")
    [am.stem for am in ams]
    ```

    """  # noqa: E501

    BarMatter = [
        803,
        1922,
        1645,
        850,
        287,
        1132,
        1755,
        1960,
        209,
        1153,
        411,
        356,
    ]
    AdminMatter = [
        "00-2-10-SC",
        "10-4-20-SC",
        "02-9-02-SC",
        "19-08-15-SC",
        "07-7-12-SC",
        "02-8-13-SC",
        "02-11-10-SC",
        "04-10-11-SC",
        "03-06-13-SC",
        "19-10-20-SC",
        "99-2-02-SC",
        "02-11-11-SC",
        "12-12-11-SC",
        "01-7-01-SC",
        "00-5-03-SC",
        "07-4-15-SC",
        "02-2-07-SC",
        "01-1-03-SC",
        "02-11-12-SC",
        "19-03-24-SC",
        "02-6-02-SC",
        "03-04-04-SC",
        "03-1-09-SC",
        "08-1-16-SC",
        "15-08-02-SC",
        "99-10-05-0",
        "06-11-5-SC",
        "03-02-05-SC",
        "00-4-07-SC",
        "00-8-10-SC",
        "04-2-04-SC",
        "12-8-8-SC",
        "21-08-09-SC",
        "03-05-01-SC",
        "09-6-8-SC",
        "05-8-26-SC",
        "00-2-03-SC",
        "01-8-10-SC",
    ]


STATUTORY_BM_SERIALS = frozenset(
    str(value).casefold() for value in DocketRuleSerialNumber.BarMatter.value
)
STATUTORY_AM_SERIALS = frozenset(
    str(value).casefold() for value in DocketRuleSerialNumber.AdminMatter.value
)


def is_statutory_rule(citeable):
    """Determine if `citeable` object is a statutory pattern based on a specific
    lising of `category` and `serial_text`.

    Examples:
        >>> from dateutil.parser import parse
        >>> test_num = '19-03-24-SC' # a statute, see list
        >>> d0 = Docket(context="", category=DocketCategory['AM'], ids=test_num, docket_date=parse("Jan. 1, 2022"))
        >>> is_statutory_rule(d0)
        True
        >>> test_num = '19-03-24-sc' # a statute, see list
        >>> d1 = Docket(context="", category=DocketCategory['AM'], ids=test_num, docket_date=parse("Jan. 1, 2022"))
        >>> is_statutory_rule(d1)
        True
        >>> test_num = '19-03-00-sc' # NOT A STATUTE
        >>> d2 = Docket(context="", category=DocketCategory['AM'], ids=test_num, docket_date=parse("Jan. 1, 2022"))
        >>> is_statutory_rule(d2)
        False
    """  # noqa: E501

    if isinstance(citeable, Docket):  # excludes solo reports
        serial = Docket.clean_serial(citeable.serial_text, citeable.category)
        if not serial:
            return False
        if citeable.category == DocketCategory.BM:
            return serial in STATUTORY_BM_SERIALS
        elif citeable.category == DocketCategory.AM:
            return serial in STATUTORY_AM_SERIALS
    return False
