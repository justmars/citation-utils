from collections.abc import Iterator
from typing import Self

from .models import Constructor, DocketCategory, DocketReportCitation, Num

separator = r"[,\.\s-]*"
two_digits = r"[\d-]{2,}"
l_digits = rf"\bL\-{two_digits}"
digits_alone = rf"\b\d{two_digits}"

acronyms = r"""
    \s?
    (
        P| # A.C. No. P-88-198, February 25, 1992, 206 SCRA 491.
        J| # Adm. Case No. 129-J, July 30, 1976, 72 SCRA 172.
        CBD| # A.C. No. CBD-174
        CFI| # Adm. Case No. 1701-CFI
        CJ|# Adm. Matter No. 584-CJ
        MJ|# ADM CASE No. 783-MJ
        SBC|#Adm. Case No. 545-SBC
        SB # A.C. No. SB-95-7-P
    )
    \s?
"""
letter = rf"""
    (
        \b
        {acronyms}
    )?
    [\d-]{{3,}} #  at least two digits and a dash
    ( # don't add \b  to capture "-Ret.""
        {acronyms}
    )?
"""

ac_key = rf"""
    (
        (
            a
            {separator}
            c
            {separator}
            (?:
                CBD # see A.C. CBD No. 190
                \s* # optional space
            )? # optional CBD,
        )|
        (
            \b
            adm
            (in)?
            (istrative)?
            {separator}
            (?:
                \b
                case
                \s* # optional space
            )?
        )
    )
"""

ac_num = rf"""
    (
        {ac_key}
        {Num.AC.allowed}
    )
"""

required = rf"""
    (?P<ac_init>
        {ac_num}
    )
    (?P<ac_middle>
        (
            ({letter})|
            ({l_digits})|
            ({digits_alone})
        )
    )
    (?:
        (
            [\,\s,\-\&]|
            and
        )*
    )?
"""

optional = rf"""
    (?P<ac_init_optional>
        {ac_num}
    )?
    (?P<ac_middle_optional>
        ({letter})|
        ({l_digits})|
        ({digits_alone})
    )?
    (?:
        (
            [\,\s,\-\&]|
            and
        )*
    )?
"""

ac_phrases = rf"""
    (?P<ac_phrase>
        ({required})
        ({optional}){{1,3}}
    )
"""


constructed_ac = Constructor(
    label=DocketCategory.AC.value,
    short_category=DocketCategory.AC.name,
    group_name="ac_phrase",
    init_name="ac_init",
    docket_regex=ac_phrases,
    key_regex=ac_key,
    num_regex=Num.AC.allowed,
)


class CitationAC(DocketReportCitation):
    ...

    @classmethod
    def search(cls, text: str) -> Iterator[Self]:
        """Get all dockets matching the `AC` docket pattern, inclusive of their optional Report object.

        Examples:
            >>> text = "A.C. No. P-88-198, February 25, 1992, 206 SCRA 491."
            >>> next(CitationAC.search(text))
            CitationAC(publisher='SCRA', volume='206', page='491', volpubpage='206 SCRA 491', report_date=None, context='A.C. No. P-88-198', short_category='AC', category='Administrative Case', ids='P-88-198', docket_date=datetime.date(1992, 2, 25))

        Args:
            text (str): Text to look for citation objects

        Yields:
            Iterator[Self]: Combination of Docket and Report pydantic model.
        """  # noqa E501
        for result in constructed_ac.detect(text):
            yield cls(**result)
