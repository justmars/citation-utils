from collections.abc import Iterator
from typing import Self

from .models import CitationConstructor, DocketCategory, DocketReportCitation
from .models.misc import NUMBER_KEYWORD

separator = r"[\.\s]*"
full_digit = r"\d{4,}"  # e.g. 16915


udk_key = rf"""
    (
        u
        {separator}
        d
        {separator}
        k
        {separator}
        -?
        \s*
        ({NUMBER_KEYWORD})?
    )
"""  # UDK 16915. February 15, 2022, note the number symbol No. may be optional

required = rf"""
    (?P<udk_init>
        {udk_key}
    )
    (?P<udk_middle>
        {full_digit}
    )
    (?:
        {separator}
    )?
"""


udk_phrases = rf"""
    (?P<udk_phrase>
        {required}
        [\,\s]*
    )
"""

constructed_udk = CitationConstructor(
    label=DocketCategory.UDK.value,
    short_category=DocketCategory.UDK.name,
    group_name="udk_phrase",
    init_name="udk_init",
    docket_regex=udk_phrases,
    key_regex=udk_key,
    num_regex=NUMBER_KEYWORD,
)


class CitationUDK(DocketReportCitation):
    ...

    @classmethod
    def search(cls, text: str) -> Iterator[Self]:
        """Get all dockets matching the `UDK` docket pattern, inclusive of their optional Report object.

        Examples:
            >>> text1 = "UDK 16915, February 15, 2022"
            >>> cite = next(CitationUDK.search(text1))
            >>> cite.model_dump(exclude_none=True)
            {'context': 'UDK 16915', 'category': 'UDK', 'ids': '16915', 'docket_date': datetime.date(2022, 2, 15)}
            >>> text2 = "UDK-1111, February 15, 2021"
            >>> cite2 = next(CitationUDK.search(text2))
            >>> cite2.model_dump(exclude_none=True)
            {'context': 'UDK-1111', 'category': 'UDK', 'ids': '1111', 'docket_date': datetime.date(2021, 2, 15)}

        Args:
            text (str): Text to look for citation objects

        Yields:
            Iterator[Self]: Combination of Docket and Report pydantic model.
        """  # noqa E501
        for result in constructed_udk.detect(text):
            yield cls(**result)
