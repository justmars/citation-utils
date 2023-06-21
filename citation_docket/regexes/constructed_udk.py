from collections.abc import Iterator
from typing import Self

from .models import Constructor, DocketCategory, DocketReportCitation
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

constructed_udk = Constructor(
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
            >>> text = "UDK 16915, February 15, 2022"
            >>> cite = next(CitationUDK.search(text))
            >>> cite.model_dump(exclude_none=True)
            {'context': 'UDK 16915', 'short_category': <ShortDocketCategory.UDK: 'UDK'>, 'category': <DocketCategory.UDK: 'Undocketed'>, 'ids': '16915', 'docket_date': datetime.date(2022, 2, 15)}

        Args:
            text (str): Text to look for citation objects

        Yields:
            Iterator[Self]: Combination of Docket and Report pydantic model.
        """  # noqa E501
        for result in constructed_udk.detect(text):
            yield cls(**result)
