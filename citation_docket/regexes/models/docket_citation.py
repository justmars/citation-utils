import abc
from collections.abc import Iterator
from typing import Self

from citation_report import Report

from .docket_model import Docket


class DocketReportCitation(Docket, Report, abc.ABC):
    """Note `Report` is defined in a separate library `citation-report`.

    The `DocketReportCitation` abstract class makes sure that all of the
    fields of a [Docket][docket-model] object alongside all of the fields of a `Report`
    object will be utilized. It also mandates the implementation of a`cls.search()`
    method.
    """

    ...

    @classmethod
    @abc.abstractmethod
    def search(cls, raw: str) -> Iterator[Self]:
        raise NotImplementedError(
            "Each docket citation must have a search method that produces an"
            " Iterator of the class instance."
        )
