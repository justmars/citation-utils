from citation_utils import CitableDocument


def test_occurrences_preserve_order_spans_raw_text_and_duplicates() -> None:
    text = "G.R. No. 1, January 2, 2024; G.R. No. 1, January 2, 2024, 900 Phil. 1"
    occurrences = list(CitableDocument(text).iter_occurrences())

    assert len(occurrences) == 2
    assert [item.start for item in occurrences] == sorted(
        item.start for item in occurrences
    )
    assert all(text[item.start : item.end] == item.raw_text for item in occurrences)
    assert occurrences[0].occurrence_key != occurrences[1].occurrence_key
    assert occurrences[1].phil == "900 Phil. 1"
