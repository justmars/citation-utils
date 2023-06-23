import datetime
import logging
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
        None, description="Cleaned: category, single serial id, date"
    )
    phil: str | None = Field(
        None, description="volume Phil. page, see `citation-report`"
    )
    scra: str | None = Field(
        None, description="volume SCRA page, see `citation-report`"
    )
    offg: str | None = Field(
        None, description="volume O.G. page, see `citation-report`"
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
        return f"<Citation: {str(self)}>"

    def __str__(self) -> str:
        return ", ".join(self.elements) if self.elements else "Bad citation."

    @classmethod
    def _set_report(cls, text: str):
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
    def _set_docket_report(cls, text: str):
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
    def extract_citations(cls, text: str) -> Iterator[Self]:
        """Find citations and parse resulting strings to determine whether they are:

        1. `Docket` + `Report` objects (in which case, `_set_docket_report()` will be used); or
        2. `Report` objects (in which case `_set_report()` will be used)

        The result, once unpacked, will be uniform citation list.

        Examples:
            >>> text = "<em>Gatchalian Promotions Talent Pool, Inc. v. Atty. Naldoza</em>, 374 Phil. 1, 10-11 (1999), citing: <em>In re Almacen</em>, 31 SCRA 562, 600 (1970).; People v. Umayam, G.R. No. 147033, April 30, 2003; <i>Bagong Alyansang Makabayan v. Zamora,</i> G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449; Villegas <em>v.</em> Subido, G.R. No. 31711, Sept. 30, 1971, 41 SCRA 190;"
            >>> set(str(a) for a in Citation.extract_citations(text)) == {'GR No. 147033, Apr. 30, 2003', 'GR No. 138570, Oct. 10, 2000, 342 SCRA 449, 342 SCRA 449', 'GR No. 31711, Sep. 30, 1971, 41 SCRA 190, 41 SCRA 190', '374 Phil. 1', '31 SCRA 562'}
            True

        Args:
            text (str): Text to evaluate

        Yields:
            Iterator[Self]: Itemized citations pre-processed via `CitableDocument`
        """  # noqa: E501
        for cite in CitableDocument(text=text).get_citations():
            if _docket := cls._set_docket_report(cite):
                yield _docket
            elif _report := cls._set_report(cite):
                yield _report
            else:
                logging.error(f"Skip invalid {cite=}.")

    @classmethod
    def extract_citation(cls, text: str) -> Self | None:
        try:
            return next(cls.extract_citations(text))
        except StopIteration:
            return None
