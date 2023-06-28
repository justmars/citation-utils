import re
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
        "00-2-10-sc",
        "10-4-20-sc",
        "02-9-02-sc",
        "19-08-15-sc",
        "07-7-12-sc",
        "02-8-13-sc",
        "02-11-10-sc",
        "04-10-11-sc",
        "03-06-13-sc",
        "19-10-20-sc",
        "99-2-02-sc",
        "02-11-11-sc",
        "12-12-11-sc",
        "01-7-01-sc",
        "00-5-03-sc",
        "07-4-15-sc",
        "02-2-07-sc",
        "01-1-03-sc",
        "02-11-12-sc",
        "19-03-24-sc",
        "02-6-02-sc",
        "03-04-04-sc",
        "03-1-09-sc",
        "08-1-16-sc",
        "15-08-02-sc",
        "99-10-05-0",
        "06-11-5-sc",
        "03-02-05-sc",
        "00-4-07-sc",
        "00-8-10-sc",
        "04-2-04-sc",
        "12-8-8-sc",
        "21-08-09-sc",
        "03-05-01-sc",
        "09-6-8-sc",
        "05-8-26-sc",
        "00-2-03-sc",
        "01-8-10-sc",
    ]

    @property
    def regex(self) -> str:
        return r"(?:" + "|".join(str(i) for i in self.value) + r")"

    @property
    def pattern(self) -> re.Pattern:
        return re.compile(self.regex)


StatutoryBM = DocketRuleSerialNumber.BarMatter.pattern
"""Fixed regex compiled pattern for Statutory Bar Matter"""

StatutoryAM = DocketRuleSerialNumber.AdminMatter.pattern
"""Fixed regex compiled pattern for Statutory Administrative Matter"""


def is_statutory_rule(citeable):
    """Determine if `citeable` object is a statutory pattern based on a specific
    lising of `category` and `serial_text`."""

    if isinstance(citeable, Docket):  # excludes solo reports
        if citeable.category == DocketCategory.BM:
            if StatutoryBM.search(citeable.first_id):
                return True
        elif citeable.category == DocketCategory.AM:
            if StatutoryAM.search(citeable.first_id):
                return True
    return False
