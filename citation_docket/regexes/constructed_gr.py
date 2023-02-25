from collections.abc import Iterator
from typing import Self

from .models import Constructor, DocketCategory, DocketReportCitation, Num

separator = r"[,\.\s-]*"
digit = r"\d[\d-]*"  # e.g. 323-23, 343-34


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


digits = rf"""
    (
        \b
        ({l_key})?
        {digit}
        \b
        \W* # possible comma
        (&\s*|and\s*)? # possible and between
    ){{1,5}}
    (
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

constructed_gr = Constructor(
    label=DocketCategory.GR.value,
    short_category=DocketCategory.GR.name,
    group_name="gr_phrase",
    init_name="gr_mid",
    docket_regex=gr_phrases,
    key_regex=rf"{gr_key}({l_key})?",
    num_regex=Num.GR.allowed,
)


class CitationGR(DocketReportCitation):
    ...

    @classmethod
    def search(cls, text: str) -> Iterator[Self]:
        """Get all dockets matching the `GR` docket pattern, inclusive of their optional Report object.

        Examples:
            >>> text = "Bagong Alyansang Makabayan v. Zamora, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449"
            >>> next(CitationGR.search(text))
            CitationGR(publisher='SCRA', volume='342', page='449', volpubpage='342 SCRA 449', report_date=None, context='G.R. Nos. 138570, 138572, 138587, 138680, 138698', short_category='GR', category='General Register', ids='138570, 138572, 138587, 138680, 138698', docket_date=datetime.date(2000, 10, 10))

        Args:
            text (str): Text to look for citation objects

        Yields:
            Iterator[Self]: Combination of Docket and Report pydantic model.
        """  # noqa E501
        for result in constructed_gr.detect(text):
            yield cls(**result)
