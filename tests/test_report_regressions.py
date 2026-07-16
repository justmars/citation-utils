from citation_utils import CitableDocument, Citation


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
