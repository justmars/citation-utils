from enum import Enum


class DocketCategory(str, Enum):
    """There are four common docket references involving Philippine Supreme Court
    decisions.

    Name | Value
    :--|:--
    `GR` | General Register
    `AM` | Administrative Matter
    `AC` | Administrative Case
    `BM` | Bar Matter

    Complication: These categories do not always represent decisions. For instance,
    there are are `AM` and `BM` docket numbers that represent rules rather
    than decisions.
    """

    GR = "General Register"
    AM = "Administrative Matter"
    AC = "Administrative Case"
    BM = "Bar Matter"


class ShortDocketCategory(str, Enum):
    """For purposes of creating an enumeration for use in `sqlpyd` wherein
    the value will be stored in the database.

    Name | Value
    :--|:--
    `GR` | GR
    `AM` | AM
    `AC` | AC
    `BM` | BM
    """

    GR = DocketCategory.GR.name
    AM = DocketCategory.AM.name
    AC = DocketCategory.AC.name
    BM = DocketCategory.BM.name
