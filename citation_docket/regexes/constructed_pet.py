from typing import Self
from collections.abc import Iterator
from .models import Constructor, DocketCategory, DocketReportCitation
from .models.misc import NUMBER_KEYWORD


pet_key = rf"""
    (
        P
        [\.\s]*
        E
        [\.\s]*
        T
        [\.\s]*
        (Case)?
    )
    \s+
    {NUMBER_KEYWORD}
"""


required = rf"""
    (?P<pet_init>
        {pet_key}
    )
    (?P<pet_middle>
        \d+
    )
"""


pet_phrases = rf"""
    (?P<pet_phrase>
        {required}
        [\,\s]*
    )
"""

constructed_pet = Constructor(
    label=DocketCategory.PET.value,
    short_category=DocketCategory.PET.name,
    group_name="pet_phrase",
    init_name="pet_init",
    docket_regex=pet_phrases,
    key_regex=pet_key,
    num_regex=NUMBER_KEYWORD,
)


class CitationPET(DocketReportCitation):
    ...

    @classmethod
    def search(cls, text: str) -> Iterator[Self]:
        """Get all dockets matching the `PET` docket pattern, inclusive of their optional Report object.

        Examples:
            >>> text = "P.E.T. Case No. 001, February 13, 1996"
            >>> next(CitationPET.search(text))
            CitationPET(publisher=None, volume=None, page=None, volpubpage=None, report_date=None, context='P.E.T. Case No. 001', short_category='PET', category='Presidential Electoral Tribunal', ids='001', docket_date=datetime.date(1996, 2, 13))

        Args:
            text (str): Text to look for citation objects

        Yields:
            Iterator[Self]: Combination of Docket and Report pydantic model.
        """  # noqa E501
        for result in constructed_pet.detect(text):
            yield cls(**result)
