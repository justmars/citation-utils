from datetime import date

from citation_date import DOCKET_DATE_FORMAT
from pydantic import BaseModel, Field

from .docket_category import DocketCategory, ShortDocketCategory
from .gr_clean import gr_prefix_clean


class Docket(BaseModel):
    """
    The Docket is the modern identifier of a Supreme Court decision.

    It is based on a `category`, a `serial id`, and a `date`.

    Field | Type | Description
    --:|:--:|:--
    `context` | optional (str) | Full texted matched by the regex pattern
    `short_category` | optional (ShortDocketCategory) | See [short-docket-category-model][]
    `category` | optional (DocketCategory) | See [docket-category-model][]
    `ids` | optional (str) | The serial number of the docket category
    `docket_date` | optional (date) | The date associated with the docket

    Sample Citation | Category | Serial | Date
    :-- |:--:|:--:|:--:
    _G.R. Nos. 138570, October 10, 2000_ | GR | 74910 | October 10, 2000
    _A.M. RTJ-12-2317 (Formerly OCA I.P.I. No. 10-3378-RTJ), Jan 1, 2000_ | AM | RTJ-12-2317 |Jan 1, 2000
    _A.C. No. 10179 (Formerly CBD 11-2985), March 04, 2014_ | AC | 10179 | Mar. 4, 2014

    The Docket is often paired with a Report, which is the traditional
    identifier based on volume and page numbers.
    """  # noqa: E501

    context: str = Field(
        ...,
        title="Context",
        description="Full texted matched by the regex pattern.",
    )
    short_category: ShortDocketCategory = Field(
        ...,
        title="Docket Acronym",
        description="GR, AM, AC, BM, etc.",
        min_length=2,
        max_length=3,
    )
    category: DocketCategory = Field(
        ...,
        title="Docket Category",
        description=(
            "e.g. General Register, Administrative Matter,"
            " Administrative Case, Bar Matter"
        ),
    )
    ids: str = Field(
        ...,
        title="Raw Docket IDs",
        description="The docket can contain multiple tokens, e.g. 24141, 14234, 2342.",
    )
    docket_date: date = Field(
        ...,
        title="Docket Date",
        description="Either in UK, US styles",
    )

    class Config:
        use_enum_values = True

    def __str__(self) -> str:
        if self.serial_text:
            return f"{self.short_category} {self.serial_text}, {self.formatted_date}"
        return "No proper string detected."

    @property
    def serial_text(self) -> str:
        """From the raw `ids`, get the `cleaned_ids`, and of these `cleaned_ids`,
            extract the `@first_id` found to deal with compound ids, e.g.
            ids separated by 'and' and ','

        Returns:
            str: Singular text identifier
        """
        if x := self.first_id or self.ids:
            if adjust := gr_prefix_clean(x):
                return adjust
        return x

    @property
    def first_id(self) -> str:
        """Get the first element from a list of separators when possible.

        Returns:
            str: First id found
        """

        def first_exists(char: str, text: str):
            """If a `char` exists in the `text`, split on this value."""
            return text.split(char)[0] if char in text else None

        for char in ["/", ",", ";", " and ", " AND ", "&"]:
            if res := first_exists(char, self.ids):
                return res
        return self.ids

    @property
    def formatted_date(self) -> str | None:
        if self.docket_date:
            return self.docket_date.strftime(DOCKET_DATE_FORMAT)
        return None
