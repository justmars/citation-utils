from citation_utils.formatting import get_docket_slug_from_text, make_citation_string


def test_stable_formatting_helpers() -> None:
    assert (
        get_docket_slug_from_text("G.R. No. 138570, Oct. 10, 2000")
        == "gr-138570-2000-10-10"
    )
    assert make_citation_string(
        "gr", "111", "2000-01-01", "100 phil. 100", "122 scra 100-a"
    ) == "G.R. No. 111, Jan. 1, 2000, 100 Phil. 100, 122 SCRA 100-A"
