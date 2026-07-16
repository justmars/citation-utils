import re
from datetime import date
from typing import Self

from citation_date import DOCKET_DATE_FORMAT
from pydantic import BaseModel, Field

from .docket_category import DocketCategory
from .gr_clean import gr_prefix_clean

DB_SERIAL_NUM = re.compile(r"^(?P<serial>[a-z0-9]+(?:-[a-z0-9]+)*)$")
"""Ideally, the docket id for the database should only be alpha-numeric, lowercase with dashes."""  # noqa: E501

_DOTTED_ACRONYM = re.compile(r"(?i)(?:[a-z]\.){2,}")
_SERIAL_SPLIT = re.compile(r"\s*(?:,|;|/|&|\band\b)\s*", re.I)
_NUMBER_PREFIX = re.compile(r"(?i)^nos?\.\s*")


class Docket(BaseModel):
    """
    The `Docket` is the modern identifier of a Supreme Court decision. This data structure
    however is not the final form of the identifier since that description belongs to the `Citation`
    and the `CountedCitation`.

    The purpose of this intermediate structure is that a `Docket` is often paired with a `Report`, which
    is the traditional identifier based on volume and page numbers. The pairing however is not
    mandatory, thus needed flexibility to create structures with the following combinations of
    the eventual Citation object:

    Citation | Docket | Report
    :--:|:--:|:--:
    has both docket and report | yes | yes
    only a docket | yes | no
    only a report | no | yes

    See docket_citation.DocketReportCitation to see structure of paired content.

    A `Docket` is based on a `category`, a `serial id`, and a `date`. Since the serial id
    may required

    Field | Type | Description
    --:|:--:|:--
    `context` | optional (str) | Full text matched by the regex pattern
    `category` | optional (DocketCategory) | Whether GR, AC, etc.
    `ids` | optional (str) | The serial number of the docket category
    `docket_date` | optional (date) | The date associated with the docket

    Sample Citation | Category | Serial | Date
    :-- |:--:|:--:|:--:
    _G.R. Nos. 138570, October 10, 2000_ | GR | 74910 | October 10, 2000
    _A.M. RTJ-12-2317 (Formerly OCA I.P.I. No. 10-3378-RTJ), Jan 1, 2000_ | AM | RTJ-12-2317 |Jan 1, 2000
    _A.C. No. 10179 (Formerly CBD 11-2985), March 04, 2014_ | AC | 10179 | Mar. 4, 2014
    """  # noqa: E501

    context: str = Field(..., description="Full text matched by regex pattern.")
    category: DocketCategory = Field(..., description="e.g. General Register, etc.")
    ids: str = Field(
        ..., description="This may be comma-separated, e.g. '12, 32, and 41'"
    )
    docket_date: date = Field(...)

    def __repr__(self) -> str:
        return f"<Docket: {self.category} {self.serial_text}, {self.formatted_date}>"

    def __str__(self) -> str:
        if self.serial_text:
            return (
                f"{self.category} No. {self.serial_text.upper()}, {self.formatted_date}"  # noqa: E501
            )
        return "No proper string detected."

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Docket):
            return NotImplemented
        serial = self.clean_serial(self.serial_text, self.category)
        other_serial = self.clean_serial(other.serial_text, other.category)
        return (
            self.category == other.category
            and serial is not None
            and serial == other_serial
            and self.docket_date == other.docket_date
        )

    @property
    def slug(self):
        return "-".join(
            [self.category.name, self.serial_text, self.docket_date.isoformat()]
        )

    @property
    def serial_text(self) -> str:
        """From raw `ids`, get the `cleaned_ids`, and of these `cleaned_ids`,
            extract the `@first_id` found to deal with compound ids, e.g.
            ids separated by 'and' and ','

        Returns:
            str: Singular text identifier
        """
        raw = self.first_id or self.ids
        return self.clean_serial(raw, self.category) or raw.strip()

    @property
    def first_id(self) -> str:
        """Get first bit from list of separated ids, when possible.

        Returns:
            str: First id found
        """

        return _SERIAL_SPLIT.split(self.ids, maxsplit=1)[0].strip()

    @property
    def formatted_date(self) -> str | None:
        if self.docket_date:
            return self.docket_date.strftime(DOCKET_DATE_FORMAT)
        return None

    @classmethod
    def check_serial_num(cls, text: str) -> bool:
        """If a serial number exists, ensure it meets criteria prior to row creation."""
        return cls.clean_serial(text) is not None

    @classmethod
    def clean_serial(
        cls, text: str, category: DocketCategory | str | None = None
    ) -> str | None:
        """Criteria:

        1. Must be lowercased
        2. Characters that can be included `a-z`, `0-9`, `-`
        3. Must only contain a single alpha-numeric reference

        Args:
            text (str): Raw text to clean

        Returns:
            str: Cleaned serial text fit for database input.
        """
        raw = _SERIAL_SPLIT.split(text.strip().rstrip("*•[]"), maxsplit=1)[0]
        raw = _NUMBER_PREFIX.sub("", raw)
        category_name = (
            category.name if isinstance(category, DocketCategory) else (category or "")
        ).upper()

        if category_name == DocketCategory.GR.name:
            raw = gr_prefix_clean(raw) or raw

        raw = _DOTTED_ACRONYM.sub(lambda match: match.group().replace(".", ""), raw)
        raw = re.sub(r"\s*-\s*", "-", raw)
        raw = re.sub(r"(?i)^([a-z]+)\s+(?=-?\d)", r"\1-", raw)
        raw = re.sub(r"(?i)(?<=\d)\s+(?=[a-z]+$)", "-", raw)
        raw = re.sub(r"\s+", "", raw).lower()

        if match := DB_SERIAL_NUM.fullmatch(raw):
            return match.group("serial")
        return None
