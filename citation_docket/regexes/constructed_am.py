from collections.abc import Iterator
from typing import Self

from .models import Constructor, DocketCategory, DocketReportCitation, Num

separator = r"[,\.\s-]*"
digit = r"\d{3}[\d-]*"  # e.g. 323-23, 343-34
acronyms = r"""
    \s?
    (
        A|
        B|
        P|
        R|
        P|
        J|
        OCA|
        O\.C\.A\.|
        SDC|
        CTA|
        RTC|
        CFI|
        RTJ|
        MTJ|
        MJ|
        CJ|
        CTJ|
        CAR|
        CCC|
        CFI|
        JDRC|
        OMB|
        TEL|
        METC|
        MCTC|
        MTCC|
        MTC|
        HOJ|
        RET(?:\.)?|
        SCC?|
        SC(?:\-PHILJA)?|
        CA(?:\-J)?|
        SB(?:\-J)?
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


ipi = r"""
    (
        (IPI)|(I\.P\.I\.)
    )
"""

am_key = rf"""
    (
        (
            a
            {separator}
            m
            {separator}
        )|
        (
            \b
            adm(in)?(istrative)?
            {separator}
            (?:
                \b
                (
                    Matter|
                    Mat\. # ADM. MAT. NO. P-97-1241
                )
                \s* # optional space
            )?
        )
    )
"""


am_num = rf"""
    (
        {am_key}
        {Num.AM.allowed}
    )
"""

required = rf"""
    (?P<am_init>
        {am_num}| # AM No.
        {am_key} # AM
    )
    (?P<am_middle>
        (
            ({letter})|
            ({digit})
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
    (?P<am_init_optional>
        {am_num}
    )?
    (?P<am_middle_optional>
        {letter}|
        {digit}
    )?
    (?:
        (
            [\,\s,\-\&]|
            and
        )*
    )?
"""

am_phrases = rf"""
    (?P<am_phrase>
        ({required})
        ({optional}){{1,3}}
    )
"""


constructed_am = Constructor(
    label=DocketCategory.AM.value,
    short_category=DocketCategory.AM.name,
    group_name="am_phrase",
    init_name="am_init",
    docket_regex=am_phrases,
    key_regex=am_key,
    num_regex=Num.AM.allowed,
)


class CitationAM(DocketReportCitation):
    ...

    @classmethod
    def search(cls, text: str) -> Iterator[Self]:
        """Get all dockets matching the `AM` docket pattern, inclusive of their optional Report object.

        Examples:
            >>> text = "A.M. No. P-88-198, February 25, 1992, 206 SCRA 491."
            >>> cite = next(CitationAM.search(text))
            >>> cite.model_dump(exclude_none=True)
            {'publisher': 'SCRA', 'volume': '206', 'page': '491', 'volpubpage': '206 SCRA 491', 'context': 'A.M. No. P-88-198', 'short_category': <ShortDocketCategory.AM: 'AM'>, 'category': <DocketCategory.AM: 'Administrative Matter'>, 'ids': 'P-88-198', 'docket_date': datetime.date(1992, 2, 25)}

        Args:
            text (str): Text to look for citation objects

        Yields:
            Iterator[Self]: Combination of Docket and Report pydantic model.
        """  # noqa E501
        for result in constructed_am.detect(text):
            yield cls(**result)
