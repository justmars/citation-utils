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
