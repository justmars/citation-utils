import abc
from collections.abc import Iterator
from typing import Self

from citation_report import Report
from pydantic import PrivateAttr

from .docket_category import DocketCategory
from .docket_model import Docket


class DocketReportCitation(Docket, Report, abc.ABC):
    """Note `Report` is defined in a separate library `citation-report`.

    The `DocketReportCitation` abstract class makes sure that all of the
    fields of a `Docket` object alongside all of the fields of a `Report`
    object will be utilized. It also mandates the implementation of a`cls.search()`
    method.
    """

    @property
    def _docket(self):
        if self.first_id:
            return f"{self.category.name} No. {self.serial_text}, {self.formatted_date}"
        elif self.ids:
            return f"{self.category.name} No. {self.ids}, {self.formatted_date}"
        return None

    @property
    def _report(self):
        return self.qualified_volpubpage or None

    def __str__(self) -> str:
        if self._docket and self._report:
            return f"{self._docket}, {self._report}"
        elif self._docket:
            return self._docket
        elif self._report:
            return self._report
        return "No citation."

    def __repr__(self) -> str:
        if self._docket and self._report:
            return f"<DocketReport: {self._docket} | {self._report}>"
        elif self._docket:
            return f"<DocketReport: {self._docket}>"
        elif self._report:
            return f"<DocketReport: {self._report}>"
        return "<DocketReport: improper citation>"

    @classmethod
    @abc.abstractmethod
    def search(cls, raw: str) -> Iterator[Self]:
        raise NotImplementedError("Search method must produce Iterator of instance.")

    _source_span: tuple[int, int] = PrivateAttr(default=(-1, -1))
    _explicit_category: bool = PrivateAttr(default=True)

    @classmethod
    def from_detected(cls, result: dict, *, explicit_category: bool = True) -> Self:
        """Build a public model while retaining extraction-only metadata."""
        data = dict(result)
        start = data.pop("_source_start", -1)
        end = data.pop("_source_end", -1)
        instance = cls(**data)
        instance._source_span = (start, end)
        instance._explicit_category = explicit_category
        return instance
