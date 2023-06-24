import datetime
import logging
import re
from collections.abc import Iterator
from typing import Self

from citation_report import Report
from citation_report.main import is_eq
from pydantic import BaseModel, ConfigDict, Field

from .dockets import DocketCategory
from .document import CitableDocument

docket_serial_export_pattern = re.compile(r"^[a-z0-9-]+$")
"""Alphanumeric lowercase with dash"""


class Citation(BaseModel):
    """
    A Philippine Supreme Court `Citation` consists of:

    1. `Docket` includes:
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

    def is_serial_ok(self) -> bool:
        """If a serial number exists, ensure it meets criteria prior to row creation."""
        if self.docket_serial:
            if docket_serial_export_pattern.search(self.docket_serial.lower()):
                return True
            return False
        return True

    def make_row(self):
        """This presumes that a valid docket exists. Although a citation can
        be a non-docket, e.g. phil, scra, etc., for purposes of creating a
        a database row, the identifier will be based on a docket id."""
        if not self.is_serial_ok():
            logging.error(f"Invalid {self.docket_serial=}")
            return None

        docket_id = None
        if self.docket_category and self.docket_serial and self.docket_date:
            cat = self.docket_category.name.lower()
            num = self.docket_serial.lower()
            date = self.docket_date.isoformat()
            docket_id = "-".join([cat, num, date])
            return {
                "id": docket_id,
                "cat": cat,
                "num": self.docket_serial,
                "date": date,
                "docket": str(self.docket),
                "phil": self.phil,
                "scra": self.scra,
                "offg": self.offg,
            }
        logging.error(f"Could not make docket slug: {self.docket=}")
        return None

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
            docket_str = f"{self.docket_category} No. {self.docket_serial}, {self.docket_date.strftime('%b %d, %Y')}"  # type: ignore # noqa: E501

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
    def from_source(cls, text: str) -> list[Self]:
        """Computes mentions of `counted_dockets()` vis-a-vis `counted_reports()` and
        count the number of unique items, taking into account the Citation
        structure and the use of __eq__ re: what is considered unique.

        Examples:
            >>> source = "374 Phil. 1, 10-11 (1999) 1111 SCRA 1111; G.R. No. 147033, April 30, 2003; G.R. No. 147033, April 30, 2003, 374 Phil. 1, 600; ABC v. XYZ, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449;  XXX, G.R. No. 31711, Sept. 30, 1971, 35 SCRA 190; Hello World, 1111 SCRA 1111; Y v. Z, 35 SCRA 190; 1 Off. Gaz. 41 Bar Matter No. 803, Jan. 1, 2000 Bar Matter No. 411, Feb. 1, 2000 Bar Matter No. 412, Jan. 1, 2000, 1111 SCRA 1111; 374 Phil. 1"
            >>> list(CountedCitation.from_source(source))
            [BM No. 412, Jan 01, 2000, 1111 SCRA 1111: 3, GR No. 147033, Apr 30, 2003, 374 Phil. 1: 3, GR No. 138570, Oct 10, 2000, 342 SCRA 449: 1, GR No. 31711, Sep 30, 1971, 35 SCRA 190: 2, 1 Off. Gaz. 41: 1]

        Args:
            text (str): Text to Evaluate.

        Returns:
            list[Self]: Unique citations with their counts.
        """  # noqa: E501
        all_reports = cls.counted_reports(text)  # includes reports in docket_reports
        docket_reports = cls.counted_docket_reports(text)
        for report in all_reports:
            for dr in docket_reports:
                if report == dr:  # uses Citation __eq__
                    balance = 0
                    if report.mentions > dr.mentions:
                        balance = report.mentions - dr.mentions
                    dr.mentions = dr.mentions + balance
                    report.mentions = 0

        return docket_reports + [
            report for report in all_reports if report.mentions > 0
        ]

    @classmethod
    def from_repr_format(cls, repr_texts: list[str]) -> Iterator[Self]:
        """Generate their pydantic counterparts from `<cat> <id>: <mentions>` format.

        Examples:
            >>> repr_texts = ['BM No. 412, Jan 01, 2000, 1111 SCRA 1111: 3', 'GR No. 147033, Apr 30, 2003, 374 Phil. 1: 3']
            >>> results = list(CountedCitation.from_repr_format(repr_texts))
            >>> len(results)
            2

        Args:
            repr_texts (str): list of texts having `__repr__` format of a `CountedRule`

        Yields:
            Iterator[Self]: Instances of CountedCitation.
        """  # noqa: E501
        for text in repr_texts:
            counted_bits = text.split(":")
            if len(counted_bits) == 2:
                if cite := cls.extract_citation(counted_bits[0].strip()):
                    obj = cite.model_dump()
                    citation = cls(**obj)
                    citation.mentions = int(counted_bits[1].strip())
                    yield citation

    @classmethod
    def counted_reports(cls, text: str):
        """Detect _reports_ only from source `text` by first converting
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
        """Detect _dockets with reports_ from source `text` by first converting
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
                included.mentions += 1
                included.add_values(cite)  # for citations, can add missing
        return seen

    def add_values(self, other: Citation):
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
