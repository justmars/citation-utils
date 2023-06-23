import re
from enum import Enum

from .docket_category import DocketCategory
from .docket_model import Docket


class DocketRuleSerialNumber(Enum):
    """A rule is more adequately defined in `statute-utils`. There are are `AM` and `BM` docket numbers
    that represent rules rather than decisions."""  # noqa: E501

    BarMatter = [803, 1922, 1645, 850, 287, 1132, 1755, 1960, 209, 1153, 411, 356]
    AdminMatter = [r"(?:\d{1,2}-){3}SC\b", r"99-10-05-0\b"]

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
