from collections.abc import Iterator
from typing import Self

from .models import CitationConstructor, DocketCategory, DocketReportCitation
from .models.misc import NUMBER_KEYWORD

separator = r"[\.\s]*"
digit = r"(\d{2}|P)[\d-]*"  # e.g. 323-23, 343-34

end_digit = r"""
    (\d{2,})| # AM OCA IPI No. P-07-2403, Feb. 06, 2008; see also OCA I.P.I. No. 17-4757
    RTJ| # AM OCA IPI No. 11-3800-RTJ, Jun. 19, 2017
    MTJ| # AM OCA IPI No. 04-1606-MTJ, Sep. 19, 2012
    P| # AM OCA IPI No. 09-3138-P, Oct. 22, 2013
    SB-J| # AM OCA IPI No. 10-25-SB-J, Jan. 15, 2013
    CA-J| # AM OCA IPI No. 11-184-CA-J, Jan. 31, 2012
    METC # AM OCA IPI NO. 06-11-392-METC, Jan. 15, 2007
"""

full_digit = rf"""
    {digit}
    ({end_digit})
"""

oca_key = rf"""
    (
        (
            a
            {separator}
            m
            {separator}
        )?
        (
            (OCA)|(O{separator}C{separator}A{separator})
        )
        \s*
        (
            (IPI)|(I{separator}P{separator}I{separator})
        )?
        \s*
        {NUMBER_KEYWORD}
    )
"""

required = rf"""
    (?P<oca_init>
        {oca_key}
    )
    (?P<oca_middle>
        {full_digit}
    )
    (?:
        {separator}
    )?
"""


oca_phrases = rf"""
    (?P<oca_phrase>
        {required}
        [\,\s]*
    )
"""

constructed_oca = CitationConstructor(
    label=DocketCategory.OCA.value,
    short_category=DocketCategory.OCA.name,
    group_name="oca_phrase",
    init_name="oca_init",
    docket_regex=oca_phrases,
    key_regex=oca_key,
    num_regex=NUMBER_KEYWORD,
)


class CitationOCA(DocketReportCitation):
    ...

    @classmethod
    def search(cls, text: str) -> Iterator[Self]:
        """Get all dockets matching the `OCA` docket pattern, inclusive of their optional Report object.

        Examples:
            >>> text1 = "AM OCA IPI No. P-07-2403, Feb. 06, 2008"
            >>> cite1 = next(CitationOCA.search(text1))
            >>> cite1.model_dump(exclude_none=True)
            {'context': 'AM OCA IPI No. P-07-2403', 'category': 'OCA', 'ids': 'P-07-2403', 'docket_date': datetime.date(2008, 2, 6)}
            >>> text2 = "OCA IPI No. 10-3450-P, Feb. 06, 2008"
            >>> cite2 = next(CitationOCA.search(text2))
            >>> cite2.model_dump(exclude_none=True)
            {'context': 'OCA IPI No. 10-3450-P', 'category': 'OCA', 'ids': '10-3450-P', 'docket_date': datetime.date(2008, 2, 6)}


        Args:
            text (str): Text to look for citation objects

        Yields:
            Iterator[Self]: Combination of Docket and Report pydantic model.
        """  # noqa E501
        for result in constructed_oca.detect(text):
            yield cls(**result)
