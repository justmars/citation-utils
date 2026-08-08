from __future__ import annotations

import datetime as dt
from collections.abc import Iterator
from typing import Self

import pytest

from citation_utils import (
    Citation,
    CitationAC,
    CitationAM,
    CitationBM,
    CitationGR,
    CitationJIB,
    CitationOCA,
    CitationPET,
    CitationUDK,
    CountedCitation,
    Docket,
    DocketCategory,
)
from citation_utils.dockets.models.docket_citation import DocketReportCitation
from citation_utils.special import extract_docket_meta


class ConcreteDocketReport(DocketReportCitation):
    @classmethod
    def search(cls, raw: str) -> Iterator[Self]:
        if raw:
            yield cls(
                context=raw,
                category=DocketCategory.GR,
                ids="1",
                docket_date=dt.date(2000, 1, 1),
            )


@pytest.mark.parametrize(
    ("citation_type", "text", "category", "ids"),
    [
        (
            CitationAC,
            "A.C. No. P-88-198, February 25, 1992, 206 SCRA 491.",
            "AC",
            "P-88-198",
        ),
        (
            CitationAM,
            "A.M. No. P-88-198, February 25, 1992, 206 SCRA 491.",
            "AM",
            "P-88-198",
        ),
        (CitationBM, "B.M. No. 1678, December 17, 2007", "BM", "1678"),
        (
            CitationGR,
            "G.R. No. 138570, October 10, 2000, 342 SCRA 449",
            "GR",
            "138570",
        ),
        (
            CitationJIB,
            "JIB FPI No. 21-018-MTJ. August 17, 2022",
            "JIB",
            "21-018-MTJ",
        ),
        (
            CitationOCA,
            "AM OCA IPI No. P-07-2403, Feb. 06, 2008",
            "OCA",
            "P-07-2403",
        ),
        (
            CitationPET,
            "P.E.T. Case No. 001, February 13, 1996",
            "PET",
            "001",
        ),
        (CitationUDK, "UDK 16915, February 15, 2022", "UDK", "16915"),
    ],
)
def test_docket_searches_share_detection_without_changing_results(
    citation_type: type[DocketReportCitation],
    text: str,
    category: str,
    ids: str,
) -> None:
    citation = next(citation_type.search(text))

    assert citation.category.name == category
    assert citation.ids == ids
    assert citation._source_span[0] == 0
    assert citation._source_span[1] > len(citation.context)
    assert citation._explicit_category is True


@pytest.mark.parametrize(
    "text",
    ["L-3243, January 1, 2000", ", Nos. 123, January 1, 2000"],
)
def test_gr_search_preserves_implicit_category_detection(text: str) -> None:
    citation = next(CitationGR.search(text))

    assert citation.category is DocketCategory.GR
    assert citation._explicit_category is False


def test_docket_report_display_variants_and_detection_metadata() -> None:
    docket = ConcreteDocketReport(
        context="docket",
        category=DocketCategory.GR,
        ids="1",
        docket_date=dt.date(2000, 1, 1),
    )
    report = ConcreteDocketReport(
        context="report",
        category=DocketCategory.GR,
        ids="",
        docket_date=dt.date(2000, 1, 1),
        volume="1",
        publisher="Phil.",
        page="2",
    )
    combined = ConcreteDocketReport(
        context="combined",
        category=DocketCategory.GR,
        ids="1",
        docket_date=dt.date(2000, 1, 1),
        volume="1",
        publisher="Phil.",
        page="2",
    )
    empty = ConcreteDocketReport(
        context="empty",
        category=DocketCategory.GR,
        ids="",
        docket_date=dt.date(2000, 1, 1),
    )

    assert str(docket).startswith("GR No. 1")
    assert repr(docket).startswith("<DocketReport: GR No. 1")
    assert str(report) == "1 Phil. 2"
    assert repr(report) == "<DocketReport: 1 Phil. 2>"
    assert "1 Phil. 2" in str(combined)
    assert " | 1 Phil. 2>" in repr(combined)
    assert str(empty) == "No citation."
    assert repr(empty) == "<DocketReport: improper citation>"

    detected = ConcreteDocketReport.from_detected(
        {
            "context": "detected",
            "category": DocketCategory.GR,
            "ids": "2",
            "docket_date": dt.date(2000, 1, 2),
            "_source_start": 3,
            "_source_end": 9,
        },
        explicit_category=False,
    )
    assert detected._source_span == (3, 9)
    assert detected._explicit_category is False
    assert list(ConcreteDocketReport.search("source"))


def test_docket_normalization_and_comparison_branches() -> None:
    docket = Docket(
        context="raw",
        category=DocketCategory.GR,
        ids="Nos. L 123, 456",
        docket_date=dt.date(2000, 1, 1),
    )
    same = Docket(
        context="other",
        category=DocketCategory.GR,
        ids="l-123",
        docket_date=dt.date(2000, 1, 1),
    )
    assert docket == same
    assert docket != object()
    assert docket.slug == "GR-l-123-2000-01-01"
    assert Docket.clean_serial("A.C. CBD 12") == "accbd12"
    assert Docket.clean_serial("bad !") is None
    assert Docket.check_serial_num("123") is True


def test_citation_serialization_display_and_failure_branches() -> None:
    empty = Citation()
    assert "Bad citation" in str(empty)
    assert empty != object()
    assert empty.model_dump() == {
        "cat": None,
        "num": None,
        "date": None,
        "phil": None,
        "scra": None,
        "offg": None,
    }
    assert empty.set_slug() is None
    assert empty.make_docket_row() is None
    assert empty.display_date is None
    assert empty.get_docket_display() is None

    citation = Citation.from_docket_row(
        "gr", "1", "2000-01-01", "1 Phil. 2", None, None
    )
    assert citation.is_docket
    assert citation.set_slug() == "gr-1-2000-01-01"
    assert citation.make_docket_row()["id"] == "gr-1-2000-01-01"
    assert citation.display_date == "Jan. 01, 2000"
    assert Citation.get_docket_slug_from_text("not a citation") is None
    assert Citation.get_report(None) is None
    assert Citation.get_report("not a report") is None
    assert Citation._set_report("1 Phil. 2").phil == "1 Phil. 2"
    assert Citation._set_report("not a report") is None
    assert Citation._set_docket_report("not a citation") is None

    for category in ("gr", "am", "ac", "bm", "udk", "jib", "oca", "pet"):
        assert Citation.make_citation_string(category, "1", "2000-01-01")
    with pytest.raises(ValueError, match="Invalid cat"):
        Citation.make_citation_string("gr", "bad !", "2000-01-01")
    with pytest.raises(ValueError, match="Invalid phil report"):
        Citation.make_citation_string("gr", "1", "2000-01-01", phil="not a report")


def test_counted_citation_merge_and_repr_failure_paths() -> None:
    target = CountedCitation()
    target.add_values(
        Citation(
            cat="gr",
            num="1",
            date="2000-01-01",
            phil="1 Phil. 2",
            scra="2 SCRA 3",
            offg="3 O.G. 4",
        )
    )
    assert target.model_dump() == {
        "cat": "gr",
        "num": "1",
        "date": "2000-01-01",
        "phil": "1 phil. 2",
        "scra": "2 scra 3",
        "offg": "3 o.g. 4",
        "mentions": 1,
    }
    assert list(CountedCitation.from_repr_format(["invalid", "also invalid: 2"])) == []


def test_special_metadata_rejects_unparseable_inputs() -> None:
    assert extract_docket_meta("not metadata") is None
    assert extract_docket_meta(". December 5, 2022") is None
    assert extract_docket_meta("G.R. No. bad!. December 5, 2022") is None
