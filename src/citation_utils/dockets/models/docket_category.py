from enum import StrEnum


class DocketCategory(StrEnum):
    """Common docket references involving Philippine Supreme Court decisions.

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

    ## Complications

    ### Legacy rules

    These categories do not always represent decisions. For instance,
    there are are `AM` and `BM` docket numbers that represent rules rather
    than decisions.

    ### Redocketed numbers

    From the Supreme Court Stylebook (p. 159, 2024):

    > 11.3.1. Redocketed numbers
    >
    > Some cases may have an undocketed (UDK) number and may be redocketed and assigned
    a General Register (G.R.) number upon payment of the required docket fees. Still
    other cases may have a docket number starting with OCA IPI or JIB and may be
    redocketed as Administrative Matters (A.M.), while Commission on Bar Discipline
    (CBD) cases may be redocketed as Administrative Cases (A.C.). These must still be
    reflected in all court resolutions, orders, and decisions. x x x
    """

    GR = "General Register"
    AM = "Administrative Matter"
    AC = "Administrative Case"
    BM = "Bar Matter"
    PET = "Presidential Electoral Tribunal"
    OCA = "Office of the Court Administrator"
    JIB = "Judicial Integrity Board"
    UDK = "Undocketed"

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        """Uses name of member `gr` instead of Enum default
        `<DocketCategory.GR: 'General Register'>`. It becomes to
        use the following conventions:

        Examples:
            >>> DocketCategory['GR']
            'GR'
            >>> DocketCategory.GR
            'GR'

        Returns:
            str: The value of the Enum name
        """
        return str.__repr__(self.name.upper())
