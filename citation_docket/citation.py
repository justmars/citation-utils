import datetime
from collections.abc import Iterator
from typing import Self

from citation_report import Report
from pydantic import BaseModel, ConfigDict, Field

from .document import CitableDocument
from .extracts import extract_docketables
from .regexes import DocketCategory


class Citation(BaseModel):
    """
    A Philippine Supreme Court `Citation` includes fields sourced from:

    1. `Docket` - as defined in [citation-docket](https://github.com/justmars/citation-docket) - includes:
        1. _category_,
        2. _serial number_, and
        3. _date_.
    2. `Report` - as defined in [citation-report](https://github.com/justmars/citation-report) - includes:
        1. _volume number_,
        2. _identifying acronym of the reporter/publisher_,
        3. _page of the reported volume_.

    It is typical to see a `Docket` combined with a `Report`:

    > _Bagong Alyansang Makabayan v. Zamora, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449_

    Taken together (and using _Bagong Alyansang Makabayan_ as an example) the text above can be extracted into fields:

    Example | Field | Type | Description
    --:|:--:|:--|--:
    GR | `docket_category` | optional (`ShortDocketCategory`) | See shorthand
    138570 |`docket_serial` | optional (str) | See serialized identifier
    datetime.date(2000, 10, 10) | `docket_date` | optional (date) | When docket serial issued
    GR 138570, Oct. 10, 2000 | `docket` | optional (str) | Combined `docket_category` `docket_serial` `docket_date`
    None | `phil` | optional (str) | combined `volume` Phil. `page`
    342 SCRA 449 | `scra` | optional (str) | combined `volume` SCRA `page`
    None | `offg` | optional (str) | combined `volume` O.G. `page`
    """  # noqa: E501

    model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)
    docket_category: DocketCategory | None = Field(None)
    docket_serial: str | None = Field(None)
    docket_date: datetime.date | None = Field(None)
    docket: str | None = Field(
        None,
        title="Docket Reference",
        description="Clean parts: category, a single serial id, and date.",
    )
    phil: str | None = Field(
        None,
        title="Philippine Reports",
        description="Combine `volume` Phil. `page` from `citation-report`.",
    )
    scra: str | None = Field(
        None,
        title="Supreme Court Reports Annotated",
        description="Combine `volume` SCRA `page` from `citation-report`.",
    )
    offg: str | None = Field(
        None,
        title="Official Gazette",
        description="Combine `volume` O.G. `page` from `citation-report`.",
    )

    @property
    def elements(self) -> list[str]:
        bits = []
        if self.docket:
            bits.append(self.docket)
        if self.phil:
            bits.append(self.phil)
        if self.scra:
            bits.append(self.scra)
        if self.offg:
            bits.append(self.offg)
        return bits

    def __repr__(self) -> str:
        """Generate a readable instance."""
        return f"<Citation: {str(self)}>"

    def __str__(self) -> str:
        """Generate a readable instance."""
        return ", ".join(self.elements) if self.elements else "Bad citation."

    @classmethod
    def from_report_text(cls, text: str):
        try:
            obj = next(Report.extract_reports(text))
            return cls(
                docket=None,
                docket_category=None,
                docket_serial=None,
                docket_date=None,
                phil=obj.phil,
                scra=obj.scra,
                offg=obj.offg,
            )
        except StopIteration:
            return None

    @classmethod
    def from_docket_text(cls, text: str):
        try:
            obj = next(extract_docketables(text))
            return cls(
                docket=str(obj),
                docket_category=obj.category,
                docket_serial=obj.serial_text,
                docket_date=obj.docket_date,
                phil=obj.phil,
                scra=obj.scra,
                offg=obj.offg,
            )
        except StopIteration:
            return None

    @classmethod
    def from_strings(cls, texts: list[str]):
        for text in texts:
            if obj_docket := cls.from_docket_text(text):
                yield obj_docket
            elif obj_report := cls.from_report_text(text):
                yield obj_report

    @classmethod
    def extract_citations(cls, text: str) -> Iterator[Self]:
        doc = CitableDocument(text=text)
        citation_strings = list(doc.get_citations())
        objs = cls.from_strings(citation_strings)
        yield from objs

    @classmethod
    def extract_citation(cls, text: str) -> Self | None:
        """Thin wrapper around `cls.extract_citations()`.

        Args:
            text (str): Text to look for Citations

        Returns:
            Self | None: First matching Citation found in the text.
        """  # noqa: E501
        try:
            return next(cls.extract_citations(text))
        except StopIteration:
            return None
