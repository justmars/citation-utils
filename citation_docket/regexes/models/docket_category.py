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
    `PET` | Presidential Electoral Tribunal
    `OCA` | Office of the Court Administrator
    `JIB` | Judicial Integrity Board
    `UDK` | Undocketed

    Complication: These categories do not always represent decisions. For instance,
    there are are `AM` and `BM` docket numbers that represent rules rather
    than decisions.
    """

    GR = "General Register"
    AM = "Administrative Matter"
    AC = "Administrative Case"
    BM = "Bar Matter"
    PET = "Presidential Electoral Tribunal"
    OCA = "Office of the Court Administrator"
    JIB = "Judicial Integrity Board"
    UDK = "Undocketed"


class ShortDocketCategory(str, Enum):
    """For purposes of creating an enumeration for use in `sqlpyd` wherein
    the value will be stored in the database.
    """

    GR = DocketCategory.GR.name
    AM = DocketCategory.AM.name
    AC = DocketCategory.AC.name
    BM = DocketCategory.BM.name
    PET = DocketCategory.PET.name
    OCA = DocketCategory.OCA.name
    JIB = DocketCategory.JIB.name
    UDK = DocketCategory.UDK.name
