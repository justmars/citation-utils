from citation_utils import CitableDocument, Citation
from citation_utils.document import _SpanIndex


def test_footnote_markers_do_not_change_docketed_report_pages():
    raw = "G.R. No. 147033, April 30, 2003, 374 Phil. 1²"

    document = CitableDocument(raw)
    assert len(document.docketed_reports) == 1
    assert document.docketed_reports[0].page == "1"
    assert document.docketed_reports[0].qualified_volpubpage == "374 Phil. 1"
    assert document.undocketed_reports == set()

    direct = list(CitableDocument.get_docketed_reports(raw))
    assert len(direct) == 1
    assert direct[0].page == "1"

    citations = list(Citation.extract_citations(raw))
    assert len(citations) == 1
    assert citations[0].phil == "374 Phil. 1"


def test_statutory_dockets_can_be_included_explicitly():
    raw = "Bar Matter No. 803, Jan. 1, 2000"

    assert list(CitableDocument.get_docketed_reports(raw)) == []
    assert len(list(CitableDocument.get_docketed_reports(raw, False))) == 1


def test_document_properties_are_lazy_and_cached():
    document = CitableDocument("G.R. No. 1, Jan. 1, 2000, 100 SCRA 1")

    assert set(document.__dict__) == {"text"}
    assert document.reports is document.reports
    assert document.docketed_reports is document.docketed_reports
    assert document.undocketed_reports is document.undocketed_reports


def test_missing_report_group_is_skipped_without_span_zip_failure(monkeypatch):
    monkeypatch.setattr("citation_report.main.get_publisher_label", lambda match: None)

    document = CitableDocument("100 SCRA 1")
    assert document.reports == []
    assert list(document.iter_parts()) == []


def test_span_index_requires_one_interval_to_contain_the_full_span():
    index = _SpanIndex.from_spans([(0, 5), (5, 10)])

    assert index.contains_span(0, 5)
    assert not index.contains_span(4, 6)


def test_span_index_handles_nested_overlapping_and_equal_start_intervals():
    nested = _SpanIndex.from_spans([(0, 10), (3, 6)])
    overlapping = _SpanIndex.from_spans([(0, 5), (3, 8)])
    equal_start = _SpanIndex.from_spans([(0, 5), (0, 10)])

    assert nested.contains_span(3, 9)
    assert not overlapping.contains_span(2, 7)
    assert equal_start.contains_span(0, 9)
