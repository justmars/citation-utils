import abc
from collections.abc import Callable, Iterator
from typing import Any, Self

from citation_report import Report
from pydantic import PrivateAttr

from .constructor import CitationConstructor
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
        if self.ids:
            return f"{self.category.name} No. {self.ids}, {self.formatted_date}"
        return None

    @property
    def _report(self):
        return self.qualified_volpubpage or None

    def __str__(self) -> str:
        if self._docket and self._report:
            return f"{self._docket}, {self._report}"
        if self._docket:
            return self._docket
        if self._report:
            return self._report
        return "No citation."

    def __repr__(self) -> str:
        if self._docket and self._report:
            return f"<DocketReport: {self._docket} | {self._report}>"
        if self._docket:
            return f"<DocketReport: {self._docket}>"
        if self._report:
            return f"<DocketReport: {self._report}>"
        return "<DocketReport: improper citation>"

    @classmethod
    @abc.abstractmethod
    def search(cls, raw: str) -> Iterator[Self]:
        raise NotImplementedError("Search method must produce Iterator of instance.")

    _source_span: tuple[int, int] = PrivateAttr(default=(-1, -1))
    _explicit_category: bool = PrivateAttr(default=True)

    @classmethod
    def from_detected(
        cls, result: dict[str, Any], *, explicit_category: bool = True
    ) -> Self:
        """Build a public model while retaining extraction-only metadata."""
        data = dict(result)
        start = data.pop("_source_start", -1)
        end = data.pop("_source_end", -1)
        instance = cls(**data)
        instance._source_span = (start, end)
        instance._explicit_category = explicit_category
        return instance

    @classmethod
    def _search_with_constructor(
        cls,
        text: str,
        constructor: CitationConstructor,
        *,
        category_is_explicit: Callable[[dict[str, Any]], bool] | None = None,
    ) -> Iterator[Self]:
        """Build citations detected by a docket-specific constructor."""
        for result in constructor.detect_with_spans(text):
            explicit_category = (
                category_is_explicit(result)
                if category_is_explicit is not None
                else True
            )
            yield cls.from_detected(result, explicit_category=explicit_category)
