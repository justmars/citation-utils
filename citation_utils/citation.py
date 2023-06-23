import datetime
import logging
from collections.abc import Iterator
from typing import Self

from citation_report import Report
from citation_report.main import is_eq
from pydantic import BaseModel, ConfigDict, Field

from .dockets import DocketCategory
from .document import CitableDocument


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
    docket: str | None = Field(None, description="Category + single serial id + date")
    phil: str | None = Field(None, description="vol + Phil. (pub) + page")
    scra: str | None = Field(None, description="vol + SCRA (pub) + page")
    offg: str | None = Field(None, description="vol + O.G. (pub) + page")

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

    def __eq__(self, other: Self) -> bool:
        ok_cat = self.docket_category is not None and other.docket_category is not None
        ok_serial = self.docket_serial is not None and other.docket_serial is not None
        ok_date = self.docket_date is not None and other.docket_date is not None
        return any(
            [
                is_eq(self.docket, other.docket),
                is_eq(self.scra, other.scra),
                is_eq(self.offg, other.offg),
                is_eq(self.phil, other.phil),
                all(
                    [
                        ok_cat and (self.docket_category == other.docket_category),
                        ok_serial and (self.docket_serial == other.docket_serial),
                        ok_date and (self.docket_date == other.docket_date),
                    ]
                ),
            ]
        )

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
            logging.debug(f"{text} is not a Report instance.")
            return None

    @classmethod
    def _set_docket_report(cls, text: str):
        try:
            obj = next(CitableDocument.get_docketed_reports(text))
            return cls(
                docket=f"{obj.category} {obj.serial_text}, {obj.docket_date}",
                docket_category=obj.category,
                docket_serial=obj.serial_text,
                docket_date=obj.docket_date,
                phil=obj.phil,
                scra=obj.scra,
                offg=obj.offg,
            )
        except StopIteration:
            logging.debug(f"{text} is not a Docket nor a Report instance.")
            return None

    @classmethod
    def extract_citations(cls, text: str) -> Iterator[Self]:
        """Find citations and parse resulting strings to determine whether they are:

        1. `Docket` + `Report` objects (in which case, `_set_docket_report()` will be used); or
        2. `Report` objects (in which case `_set_report()` will be used)

        Then processing each object so that they can be structured in a uniform format.

        Examples:
            >>> text = "<em>Gatchalian Promotions Talent Pool, Inc. v. Atty. Naldoza</em>, 374 Phil. 1, 10-11 (1999), citing: <em>In re Almacen</em>, 31 SCRA 562, 600 (1970).; People v. Umayam, G.R. No. 147033, April 30, 2003; <i>Bagong Alyansang Makabayan v. Zamora,</i> G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449; Villegas <em>v.</em> Subido, G.R. No. 31711, Sept. 30, 1971, 41 SCRA 190;"
            >>> len(list(Citation.extract_citations(text)))
            5

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
        """Thin wrapper over `cls.extract_citations()`.

        Examples:
            >>> Citation.extract_citation('Hello World') is None
            True
            >>> next(Citation.extract_citations('12 Phil. 24'))
            <Citation: 12 Phil. 24>

        Args:
            text (str): Text to evaluate

        Returns:
            Self | None: First item found from `extract_citations`, if it exists.
        """
        try:
            return next(cls.extract_citations(text))
        except StopIteration:
            return None


class CountedCitation(Citation):
    mentions: int = Field(default=1, description="Get count via Citation __eq__")

    def __repr__(self) -> str:
        return f"{str(self)}: {self.mentions}"

    def __str__(self) -> str:
        docket_str = None
        if all([self.docket_category, self.docket_serial, self.docket_date]):
            docket_str = (
                f"{self.docket_category} {self.docket_serial}, {self.docket_date}"
            )

        report_str = None
        if any([self.phil, self.scra, self.offg]):
            report_str = self.phil or self.scra or self.offg

        if docket_str and report_str:
            return f"{docket_str}, {report_str}"
        elif docket_str:
            return f"{docket_str}"
        elif report_str:
            return f"{report_str}"
        else:
            return "<Bad citation str>"

    @classmethod
    def from_source(cls, text: str):
        docketeds = cls.counted_docket_reports(text)
        reports = cls.counted_reports(text)
        for r in reports:
            for d in docketeds:
                if r == d:  # uses Citation __eq__
                    balance = r.mentions - d.mentions
                    r.mentions = 0  # since match found, make this 0
                    d.mentions = d.mentions + balance
        culled_reports = [report for report in reports if report.mentions > 0]
        return docketeds + culled_reports

    @classmethod
    def counted_reports(cls, text: str):
        """Detect reports only from source `text` by first converting
        raw citations into a `Citation` object to take advantage of `__eq__` in
        a `seen` list. This will also populate the the unique records with missing
        values.
        """
        seen: list[cls] = []
        reports = Report.extract_reports(text=text)
        for report in reports:
            cite = Citation(
                docket=None,
                docket_category=None,
                docket_serial=None,
                docket_date=None,
                phil=report.phil,
                scra=report.scra,
                offg=report.offg,
            )
            if cite not in seen:
                seen.append(cls(**cite.model_dump()))
            else:
                included = seen[seen.index(cite)]
                included.mentions += 1
        return seen

    @classmethod
    def counted_docket_reports(cls, text: str):
        """Detect dockets with reports from source `text` by first converting
        raw citations into a `Citation` object to take advantage of `__eq__` in
        a `seen` list. This will also populate the the unique records with missing
        values.
        """

        seen: list[cls] = []
        for obj in CitableDocument.get_docketed_reports(text=text):
            cite = Citation(
                docket=str(obj),
                docket_category=obj.category,
                docket_serial=obj.serial_text,
                docket_date=obj.docket_date,
                phil=obj.phil,
                scra=obj.scra,
                offg=obj.offg,
            )
            if cite not in seen:
                seen.append(cls(**cite.model_dump()))
            else:
                included = seen[seen.index(cite)]
                included.add_values(cite)
        return seen

    def add_values(self, other: Citation):
        self.mentions += 1

        if not self.docket_category and other.docket_category:
            self.docket_category = other.docket_category

        if not self.docket_serial and other.docket_serial:
            self.docket_serial = other.docket_serial

        if not self.docket_date and other.docket_date:
            self.docket_date = other.docket_date

        if not self.docket and other.docket:
            self.docket = other.docket

        if not self.scra and other.scra:
            self.scra = other.scra

        if not self.phil and other.phil:
            self.phil = other.phil

        if not self.offg and other.offg:
            self.offg = other.offg
