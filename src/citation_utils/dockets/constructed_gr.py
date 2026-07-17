from collections.abc import Iterator
from typing import Self

from citation_date import day_pattern, month_pattern, year_pattern

from .models import CitationConstructor, DocketCategory, DocketReportCitation, Num

separator = r"[,\.\s-]*"
digit = r"\d[\d-]*"  # e.g. 323-23, 343-34, L

# A day-first date begins with the same kind of numeric token as another docket
# number. The legacy expression resolved that ambiguity by backtracking through
# several nested bounded repetitions. Keep the same choice explicitly so those
# inner repetitions can be possessive and reject long, date-less number lists in
# linear time.
day_first_date = rf"""
    {day_pattern.pattern}
    (?:\s*,\s*,\s*|\s*(?:[,.]\s*)?)
    {month_pattern.pattern}
    \s*(?:[,.]\s*)?
    {year_pattern.pattern}
"""


gr_key = rf"""
    (
        (
            (?<!CA\s)  # CA GR
            (?<!CA-)  # CA-GR
            (?<!C\.A\.) # C.A.G.R.
            (?<!C\.A\.\s) # C.A. G.R.
            \b
            g
        )
        {separator}
        r
        {separator}
    )
"""

l_key = rf"""
    (
        \b # prevent capture of Angara v. Electoral Commission, 63 Phil. 139,
        (
            l|
            i # I is a mistype: De Ramos v. Court of Agrarian Relations, I-19555, May 29, 1964;
        )
        {separator} # Makes possible G.R. L-No. 5110  | # L. No. 464564
    )
"""  # noqa # E501


digit_with_separator = rf"""
    {digit}
    \b
    \W* # possible comma
    (&\s*|and\s*)? # possible and between
"""


digits = rf"""
    (
        \b
        ({l_key})?
        {digit_with_separator}
    )
    (
        (?!{day_first_date})
        ({l_key})?
        {digit_with_separator}
    ){{0,4}}+
    (
        (?!{day_first_date})
        {digit}
        \b
    )?
"""


gr_regular = rf"""
( # G.R. L-No. 5110, G.R. No. 5110, GR 100
    {gr_key}
    ({l_key})?
    ({Num.GR.allowed})?
    {digits}
)
"""

l_irregular = rf"""
( # L-No. 5110, L 5110, No
    {l_key}
    ({Num.GR.allowed})?
    {digits}
)
"""

n_irregular = rf"""
( # , Nos.
    \,\s+
    ({Num.GR.allowed})
    {digits}
)
"""

gr_phrases = rf"""
    (?P<gr_phrase>
        (
            (?P<gr_mid>
                (?P<gr_gist_r>{gr_regular})|
                (?P<gr_gist_l>{l_irregular})|
                (?P<gr_gist_n>{n_irregular})
            )
        ){{1,5}}
    )
"""

constructed_gr = CitationConstructor(
    label=DocketCategory.GR.value,
    short_category=DocketCategory.GR.name,
    group_name="gr_phrase",
    init_name="gr_mid",
    docket_regex=gr_phrases,
    key_regex=gr_key,
    num_regex=Num.GR.allowed,
)


class CitationGR(DocketReportCitation):
    ...

    @classmethod
    def search(cls, text: str) -> Iterator[Self]:
        """Get all dockets matching the `GR` docket pattern, inclusive of their optional Report object.

        Examples:
            >>> text = "Bagong Alyansang Makabayan v. Zamora, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449"
            >>> cite = next(CitationGR.search(text))
            >>> cite.model_dump(exclude_none=True)
            {'publisher': 'SCRA', 'volume': '342', 'page': '449', 'context': 'G.R. Nos. 138570, 138572, 138587, 138680, 138698', 'category': 'GR', 'ids': '138570, 138572, 138587, 138680, 138698', 'docket_date': datetime.date(2000, 10, 10)}

        Args:
            text (str): Text to look for citation objects

        Yields:
            Iterator[Self]: Combination of Docket and Report pydantic model.
        """  # noqa E501
        for result in constructed_gr.detect_with_spans(text):
            explicit = result["context"].lstrip().casefold().startswith("g")
            yield cls.from_detected(result, explicit_category=explicit)
