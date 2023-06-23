from collections.abc import Iterator
from typing import Self

from .models import CitationConstructor, DocketCategory, DocketReportCitation
from .models.misc import NUMBER_KEYWORD

separator = r"[\.\s]*"
digit = r"(\d{2}|P)[\d-]*"  # e.g. P-22-069

end_digit = r"""
    (\d{2,})|
    RTJ| # 21-105-RTJ
    MTJ| # JIB FPI No. 21-018-MTJ. August 17, 2022
    P| # 21-047-P
    SC| # 21-002-SC
    CA-J| # 21-003-CA-J
    METC # 	21-018-MTJ
"""

full_digit = rf"""
    {digit}
    ({end_digit})
"""

jib_key = rf"""
    (
        (
            j
            {separator}
            i
            {separator}
            b
            {separator}
        )
        (
            (FPI)|(F{separator}P{separator}I{separator})
        )?
        \s*
        {NUMBER_KEYWORD}
    )
"""

required = rf"""
    (?P<jib_init>
        {jib_key}
    )
    (?P<jib_middle>
        {full_digit}
    )
    (?:
        {separator}
    )?
"""


jib_phrases = rf"""
    (?P<jib_phrase>
        {required}
        [\,\s]*
    )
"""

constructed_jib = CitationConstructor(
    label=DocketCategory.JIB.value,
    short_category=DocketCategory.JIB.name,
    group_name="jib_phrase",
    init_name="jib_init",
    docket_regex=jib_phrases,
    key_regex=jib_key,
    num_regex=NUMBER_KEYWORD,
)


class CitationJIB(DocketReportCitation):
    ...

    @classmethod
    def search(cls, text: str) -> Iterator[Self]:
        """Get all dockets matching the `JIB` docket pattern, inclusive of their optional Report object.

        Examples:
            >>> text = "JIB FPI No. 21-018-MTJ. August 17, 2022"
            >>> cite = next(CitationJIB.search(text))
            >>> cite.model_dump(exclude_none=True)
            {'context': 'JIB FPI No. 21-018-MTJ.', 'category': 'JIB', 'ids': '21-018-MTJ', 'docket_date': datetime.date(2022, 8, 17)}

        Args:
            text (str): Text to look for citation objects

        Yields:
            Iterator[Self]: Combination of Docket and Report pydantic model.
        """  # noqa E501
        for result in constructed_jib.detect(text):
            yield cls(**result)
