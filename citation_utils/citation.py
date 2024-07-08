import datetime
import logging
from collections.abc import Iterator
from functools import cached_property
from typing import Self

from citation_date import DOCKET_DATE_FORMAT
from citation_report import Report
from dateutil.parser import parse
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    FieldSerializationInfo,
    field_serializer,
    model_serializer,
)

from .dockets import Docket, DocketCategory
from .document import CitableDocument


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

    model_config = ConfigDict(str_strip_whitespace=True)
    docket_category: DocketCategory | None = Field(default=None, alias="cat")
    docket_serial: str | None = Field(default=None, alias="num")
    docket_date: datetime.date | None = Field(default=None, alias="date")
    phil: str | None = Field(default=None)
    scra: str | None = Field(default=None)
    offg: str | None = Field(default=None)

    def __repr__(self) -> str:
        return f"<Citation: {str(self)}>"

    def __str__(self) -> str:
        docket_str = self.get_docket_display()
        report_str = self.phil or self.scra or self.offg
        if docket_str and report_str:
            return f"{docket_str}, {report_str}"
        elif docket_str:
            return f"{docket_str}"
        elif report_str:
            return f"{report_str}"
        return f"<Bad citation str: {self.docket_category=} {self.docket_serial=} {self.docket_date=}>"  # noqa: E501

    def __eq__(self, other: Self) -> bool:
        """Helps `seen` variable in `CountedCitation`: either the docket bits match
        or any of the report fields match."""

        def is_docket_match(other: Self) -> bool:
            """All the docket elements must match to be equal."""
            cat_is_eq = (
                self.docket_category is not None
                and other.docket_category is not None
                and (self.docket_category == other.docket_category)
            )
            num_is_eq = (
                self.docket_serial is not None
                and other.docket_serial is not None
                and (self.docket_serial == other.docket_serial)
            )
            date_is_eq = (
                self.docket_date is not None
                and other.docket_date is not None
                and (self.docket_date == other.docket_date)
            )
            return all([cat_is_eq, num_is_eq, date_is_eq])

        if is_docket_match(other):
            return True

        return any(
            [
                self.scra and other.scra and self.scra.lower() == other.scra.lower(),
                self.phil and other.phil and self.phil.lower() == other.phil.lower(),
                self.offg and other.offg and self.offg.lower() == other.offg.lower(),
            ]
        )

    @field_serializer("docket_date")
    def serialize_dt(self, value: datetime.date | None):
        if value:
            return value.isoformat()

    @field_serializer("docket_serial")
    def serialize_num(self, value: str | None):
        if value:
            return Docket.clean_serial(value)

    @field_serializer("docket_category")
    def serialize_cat(self, value: DocketCategory | None):
        if value:
            return value.name.lower()

    @field_serializer("phil")
    def serialize_phil(self, value: str | None):
        if value:
            return value.lower()

    @field_serializer("scra")
    def serialize_scra(self, value: str | None):
        if value:
            return value.lower()

    @field_serializer("offg")
    def serialize_offg(self, value: str | None):
        if value:
            return value.lower()

    @model_serializer
    def ser_model(self) -> dict[str, str | datetime.date | None]:
        """Generate a database row-friendly format of the model. Note the different
        field names: `cat`, `num`, `dt`, `phil`, `scra`, `offg` map to either a usable
        database value or `None`. The docket values here have the option to be `None`
        since some citations, especially the legacy variants, do not include their
        docket equivalents in the source texts.

        Examples:
            >>> text = "OCA IPI No. 10-3450-P, Feb. 06, 2008"
            >>> cite = Citation.extract_citation(text)
            >>> cite.model_dump_json()
            '{"cat":"oca","num":"10-3450-p","date":"2008-02-06","phil":null,"scra":null,"offg":null}'

        """
        return {
            "cat": self.serialize_cat(self.docket_category),
            "num": self.serialize_num(self.docket_serial),
            "date": self.serialize_dt(self.docket_date),
            "phil": self.serialize_phil(self.phil),
            "scra": self.serialize_scra(self.scra),
            "offg": self.serialize_offg(self.offg),
        }

    def set_slug(self) -> str | None:
        """Create a unique identifier of a decision.

        Examples:
            >>> text = "GR 138570, Oct. 10, 2000"
            >>> Citation.extract_citation(text).set_slug()
            'gr-138570-2000-10-10'

        """
        bits = [
            self.serialize_cat(self.docket_category),
            self.serialize_num(self.docket_serial),
            self.serialize_dt(self.docket_date),
        ]
        if all(bits):
            return "-".join(bits)  # type: ignore
        return None

    @classmethod
    def get_docket_slug_from_text(cls, v: str) -> str | None:
        """Given a docket string, format the string into a slug
        that has the same signature as a database primary key.

        Examples:
            >>> text = "GR 138570, Oct. 10, 2000"
            >>> Citation.get_docket_slug_from_text(text)
            'gr-138570-2000-10-10'

        Args:
            v (str): The text to evaluate

        Returns:
            str | None: The slug to use, if possible.
        """
        if cite := cls.extract_citation(v):
            if cite.is_docket:
                return cite.set_slug()
        return None

    def make_docket_row(self):
        """This presumes that a valid docket exists. Although a citation can
        be a non-docket, e.g. phil, scra, etc., for purposes of creating a
        a route-based row for a prospective decision object, the identifier will be
        based on a docket id."""
        if id := self.set_slug():
            return self.model_dump() | {"id": id}
        logging.error(f"Undocketable: {self=}")
        return None

    @classmethod
    def from_docket_row(
        cls,
        cat: str,
        num: str,
        date: str,
        opt_phil: str | None,
        opt_scra: str | None,
        opt_offg: str | None,
    ):
        return cls(
            cat=DocketCategory[cat.upper()],
            num=num,
            date=parse(date).date(),
            phil=cls.get_report(opt_phil),
            scra=cls.get_report(opt_scra),
            offg=cls.get_report(opt_offg),
        )

    @cached_property
    def is_docket(self) -> bool:
        return all([self.docket_category, self.docket_serial, self.docket_date])

    @cached_property
    def display_date(self):
        """This is the same as Docket@formatted_date."""
        if self.docket_date:
            return self.docket_date.strftime(DOCKET_DATE_FORMAT)
        return None

    def get_docket_display(self) -> str | None:
        if self.is_docket:
            return (
                f"{self.docket_category} No. {self.docket_serial}, {self.display_date}"  # type: ignore # noqa: E501
            )
        return None

    @classmethod
    def get_report(cls, raw: str | None = None) -> str | None:
        """Get a lower cased volpubpage of `publisher` from the `data`. Assumes
        that the publisher key is either `phil`, `scra` or `offg`.

        Examples:
            >>> raw = "123 Phil. 123"
            >>> Citation.get_report(raw)
            '123 phil. 123'

        Args:
            publisher (str): _description_
            data (dict): _description_

        Returns:
            str | None: _description_
        """
        if not raw:
            return None

        try:
            reports = Report.extract_reports(raw)
            report = next(reports)
            if result := report.volpubpage:
                return result.lower()
            else:
                logging.warning(f"No volpubpage {raw=}")
                return None
        except StopIteration:
            logging.warning(f"No {raw=} report")
            return None

    @classmethod
    def _set_report(cls, text: str):
        try:
            obj = next(Report.extract_reports(text))
            return cls(phil=obj.phil, scra=obj.scra, offg=obj.offg)
        except StopIteration:
            logging.debug(f"{text} is not a Report instance.")
            return None

    @classmethod
    def _set_docket_report(cls, text: str):
        try:
            obj = next(CitableDocument.get_docketed_reports(text))
            return cls(
                cat=obj.category,
                num=obj.serial_text,
                date=obj.docket_date,
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

    @classmethod
    def make_citation_string(
        cls,
        cat: str,
        num: str,
        date: str,
        phil: str | None = None,
        scra: str | None = None,
        offg: str | None = None,
    ) -> str | None:
        """Assume that because of citation-utils, the extracted values are inputted into a database.

        When the values are pulled from the database, it becomes necessary to convert these database (lowercased) values
        to a unified properly-cased citation string with readable date (vs. isoformat db-counterpart).

        Examples:
            >>> Citation.make_citation_string(cat='gr', num='111', date='2000-01-01', phil='100 phil. 100', scra='122 scra 100-a')
            'G.R. No. 111, Jan. 1, 2000, 100 Phil. 100, 122 SCRA 100-A'

        Args:
            cat (str): The shorthand code for docket category
            num (str): The serial identifier of the docket category
            date (str): The date of `cat` + `num`
            phil (str | None, optional): Phil. Reports. Defaults to None.
            scra (str | None, optional): Supreme Court Reports Annotated. Defaults to None.
            offg (str | None, optional): Official Gazette. Defaults to None.

        Returns:
            str | None: The combination of citation bits.
        """  # noqa: E501
        bits = [
            phil.title().split() if phil else None,
            scra.upper().split() if scra else None,
            offg.upper().split() if offg else None,
        ]
        cased_bits = [
            f"{bit[0].upper()} {bit[1]} {bit[2].upper()}" for bit in bits if bit
        ]
        reports = ", ".join(cased_bits) if any(bits) else None
        dt = datetime.date.fromisoformat(date).strftime("%b. %-d, %Y")
        match cat:
            case "gr":
                prefix = "G.R."
            case "am":
                prefix = "A.M."
            case "ac":
                prefix = "A.C."
            case "bm":
                prefix = "B.M."
            case "udk":
                prefix = "UDK"
            case "jib":
                prefix = "JIB-FPI"
            case "oca":
                prefix = "OCA IPI"
            case "pet":
                prefix = "P.E.T."
            case _:
                return None
        docket = f"{prefix} No. {num.upper()}"
        bits = [bit for bit in [docket, dt, reports] if bit]
        return ", ".join(bits)


class CountedCitation(Citation):
    mentions: int = Field(default=1, description="Get count via Citation __eq__")

    def __repr__(self) -> str:
        return f"{str(self)}: {self.mentions}"

    @model_serializer
    def ser_model(self) -> dict[str, str | datetime.date | int | None]:
        return {
            "cat": self.serialize_cat(self.docket_category),
            "num": self.serialize_num(self.docket_serial),
            "date": self.serialize_dt(self.docket_date),
            "phil": self.serialize_phil(self.phil),
            "scra": self.serialize_scra(self.scra),
            "offg": self.serialize_offg(self.offg),
            "mentions": self.mentions,
        }

    @classmethod
    def from_source(cls, text: str) -> list[Self]:
        """Computes mentions of `counted_dockets()` vis-a-vis `counted_reports()` and
        count the number of unique items, taking into account the Citation
        structure and the use of __eq__ re: what is considered unique.

        Examples:
            >>> source = "374 Phil. 1, 10-11 (1999) 1111 SCRA 1111; G.R. No. 147033, April 30, 2003; G.R. No. 147033, April 30, 2003, 374 Phil. 1, 600; ABC v. XYZ, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449;  XXX, G.R. No. 31711, Sept. 30, 1971, 35 SCRA 190; Hello World, 1111 SCRA 1111; Y v. Z, 35 SCRA 190; 1 Off. Gaz. 41 Bar Matter No. 803, Jan. 1, 2000 Bar Matter No. 411, Feb. 1, 2000 Bar Matter No. 412, Jan. 1, 2000, 1111 SCRA 1111; 374 Phil. 1"
            >>> len(CountedCitation.from_source(source))
            5

        Args:
            text (str): Text to Evaluate.

        Returns:
            list[Self]: Unique citations with their counts.
        """  # noqa: E501
        all_reports = cls.counted_reports(text)  # includes reports in docket_reports
        if drs := cls.counted_docket_reports(text):
            for dr in drs:
                for report in all_reports:
                    if report == dr:  # uses Citation __eq__
                        balance = 0
                        if report.mentions > dr.mentions:
                            balance = report.mentions - dr.mentions
                        dr.mentions = dr.mentions + balance
                        report.mentions = 0
            return drs + [report for report in all_reports if report.mentions > 0]
        return all_reports

    @classmethod
    def from_repr_format(cls, repr_texts: list[str]) -> Iterator[Self]:
        """Generate their pydantic counterparts from `<cat> <id>: <mentions>` format.

        Examples:
            >>> repr_texts = ['BM No. 412, Jan 01, 2000, 1111 SCRA 1111: 3', 'GR No. 147033, Apr 30, 2003, 374 Phil. 1: 1']
            >>> results = list(CountedCitation.from_repr_format(repr_texts))
            >>> len(results)
            2
            >>> results[0].model_dump()
            {'cat': 'bm', 'num': '412', 'date': '2000-01-01', 'phil': None, 'scra': '1111 scra 1111', 'offg': None, 'mentions': 3}
            >>> results[1].model_dump()
            {'cat': 'gr', 'num': '147033', 'date': '2003-04-30', 'phil': '374 phil. 1', 'scra': None, 'offg': None, 'mentions': 1}

        Args:
            repr_texts (str): list of texts having `__repr__` format of a `CountedRule`

        Yields:
            Iterator[Self]: Instances of CountedCitation.
        """  # noqa: E501
        for text in repr_texts:
            counted_bits = text.split(":")
            if len(counted_bits) == 2:
                if cite := cls.extract_citation(counted_bits[0].strip()):
                    citation = cls(
                        cat=cite.docket_category,
                        num=cite.docket_serial,
                        date=cite.docket_date,
                        phil=cite.phil,
                        scra=cite.scra,
                        offg=cite.offg,
                    )
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
            cite = Citation(phil=report.phil, scra=report.scra, offg=report.offg)
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
        a `seen` list. Will populate unique records with missing values.
        """

        seen: list[cls] = []
        for obj in CitableDocument.get_docketed_reports(text=text):
            cite = Citation(
                cat=obj.category,
                num=obj.serial_text,
                date=obj.docket_date,
                phil=obj.phil,
                scra=obj.scra,
                offg=obj.offg,
            )
            if cite not in seen:
                seen_citation = cls(
                    cat=cite.docket_category,
                    num=cite.docket_serial,
                    date=cite.docket_date,
                    phil=cite.phil,
                    scra=cite.scra,
                    offg=cite.offg,
                )
                seen.append(seen_citation)
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

        if not self.scra and other.scra:
            self.scra = other.scra

        if not self.phil and other.phil:
            self.phil = other.phil

        if not self.offg and other.offg:
            self.offg = other.offg
