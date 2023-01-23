from collections.abc import Iterator
from typing import Self

from .models import Constructor, DocketCategory, DocketReportCitation, Num

separator = r"[,\.\s-]*"
l_digits = r"\bL\-\d+"
digits_alone = r"\d+"

acronyms = r"""
    \s?
    (
        SBC # B.M. SBC-591, December 1, 1977
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

bm_key = rf"""
    (
        (
            b
            {separator}
            m
            {separator}
        )|
        (
            \b
            bar
            \s+
            matter
            \s*
        )
    )
"""

bm_num = rf"""
    (
        {bm_key}
        {Num.BM.allowed}
    )
"""

required = rf"""
    (?P<bm_init>
        {bm_num}
    )
    (?P<bm_middle>
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
    (?P<bm_init_optional>
        {bm_num}
    )?
    (?P<bm_middle_optional>
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

bm_phrases = rf"""
    (?P<bm_phrase>
        ({required})
        ({optional}){{1,3}}
    )
"""


constructed_bm = Constructor(
    label=DocketCategory.BM.value,
    short_category=DocketCategory.BM.name,
    group_name="bm_phrase",
    init_name="bm_init",
    docket_regex=bm_phrases,
    key_regex=bm_key,
    num_regex=Num.BM.allowed,
)


class CitationBarMatter(DocketReportCitation):
    ...

    @classmethod
    def search(cls, text: str) -> Iterator[Self]:
        """Get all dockets matching the `BM` docket pattern, inclusive of their optional Report object.

        Examples:
            >>> text = "B.M. No. 1678, December 17, 2007"
            >>> next(CitationBarMatter.search(text))
            CitationBarMatter(publisher=None, volume=None, page=None, volpubpage=None, report_date=None, context='B.M. No. 1678', short_category='BM', category='Bar Matter', ids='1678', docket_date=datetime.date(2007, 12, 17))

        Args:
            text (str): Text to look for citation objects

        Yields:
            Iterator[Self]: Combination of Docket and Report pydantic model.
        """  # noqa E501
        for result in constructed_bm.detect(text):
            yield cls(**result)
