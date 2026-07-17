import json
from datetime import date
from pathlib import Path

import pytest

from citation_utils import (
    CitableDocument,
    Citation,
    CitationGR,
    CountedCitation,
    Docket,
    extract_docket_meta,
)
from citation_utils.dockets import DocketCategory
from citation_utils.dockets.constructed_gr import constructed_gr

FIXTURES = json.loads(
    (Path(__file__).parent / "fixtures" / "citation_regressions.json").read_text()
)


def compact(citation):
    return {
        key: value for key, value in citation.model_dump().items() if value is not None
    }


@pytest.mark.parametrize("fixture", FIXTURES["normalization"])
def test_observed_serial_errors_normalize_to_one_canonical_docket(fixture):
    citation = Citation.extract_citation(fixture["source"])

    assert citation is not None
    assert compact(citation) == fixture["expected"]
    assert citation.set_slug() == "-".join(fixture["expected"].values())


@pytest.mark.parametrize("fixture", FIXTURES["ownership"])
def test_category_ownership_prevents_phantom_gr_matches(fixture):
    citations = list(Citation.extract_citations(fixture["source"]))

    assert [compact(citation) for citation in citations] == fixture["expected"]


@pytest.mark.parametrize("fixture", FIXTURES["rejected"])
def test_malformed_serials_are_not_extracted(fixture):
    assert list(Citation.extract_citations(fixture["source"])) == []


@pytest.mark.parametrize("fixture", FIXTURES["statutory"])
def test_statutory_exclusion_is_an_exact_canonical_serial_match(fixture):
    citations = list(CitableDocument.get_docketed_reports(fixture["source"]))

    assert bool(citations) is not fixture["excluded"]
    assert (
        len(list(CitableDocument.get_docketed_reports(fixture["source"], False))) == 1
    )


@pytest.mark.parametrize("fixture", FIXTURES["reports"])
def test_qualified_official_gazette_forms_survive_normalization(fixture):
    citation = Citation.extract_citation(fixture["source"])

    assert citation is not None
    assert compact(citation) == fixture["expected"]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "100 SCRA 1; G.R. No. 1, Jan. 1, 2000, 100 SCRA 1",
            [
                {
                    "cat": "gr",
                    "num": "1",
                    "date": "2000-01-01",
                    "scra": "100 scra 1",
                    "mentions": 2,
                }
            ],
        ),
        (
            "G.R. No. 1, Jan. 1, 2000, 100 SCRA 1; 100 SCRA 1",
            [
                {
                    "cat": "gr",
                    "num": "1",
                    "date": "2000-01-01",
                    "scra": "100 scra 1",
                    "mentions": 2,
                }
            ],
        ),
        (
            (
                "G.R. No. 1, Jan. 1, 2000, 100 SCRA 1; "
                "G.R. No. 2, Jan. 2, 2000, 100 SCRA 1; 100 SCRA 1"
            ),
            [
                {
                    "cat": "gr",
                    "num": "1",
                    "date": "2000-01-01",
                    "scra": "100 scra 1",
                    "mentions": 1,
                },
                {
                    "cat": "gr",
                    "num": "2",
                    "date": "2000-01-02",
                    "scra": "100 scra 1",
                    "mentions": 1,
                },
                {"scra": "100 scra 1", "mentions": 1},
            ],
        ),
    ],
)
def test_aggregation_keeps_source_order_and_counts_true_occurrences(source, expected):
    citations = CountedCitation.from_source(source)

    assert [compact(citation) for citation in citations] == expected


def test_report_first_occurrence_keeps_its_position_when_later_linked_to_one_docket():
    citations = list(
        Citation.extract_citations(
            "100 SCRA 1; G.R. No. 1, Jan. 1, 2000, 100 SCRA 1; G.R. No. 2, Jan. 2, 2000"
        )
    )

    assert [citation.docket_serial for citation in citations] == ["1", "2"]
    assert citations[0].scra == "100 SCRA 1"


def test_extraction_is_unique_while_counting_retains_duplicate_source_mentions():
    source = (
        "100 SCRA 1; 100 SCRA 1; G.R. No. 1, Jan. 1, 2000; G.R. No. 1, Jan. 1, 2000"
    )

    assert len(list(Citation.extract_citations(source))) == 2
    assert [citation.mentions for citation in CountedCitation.from_source(source)] == [
        2,
        2,
    ]


def test_dangling_repeated_am_key_without_serial_is_not_extracted():
    source = "A.M. No. 123 and A.M. No. , Jan 1, 2020"

    assert list(Citation.extract_citations(source)) == []


def test_date_preflight_keeps_case_insensitive_us_and_day_first_dates():
    sources = [
        "G.R. No. 123, jan. 1, 2000",
        "G.R. No. 123, 1 Jan. 2000",
    ]

    assert [
        next(CitableDocument.get_docketed_reports(source)).serial_text
        for source in sources
    ] == ["123", "123"]


@pytest.mark.parametrize(
    ("source", "context", "ids", "docket_date"),
    [
        ("G.R. No. 123, Jan. 1, 2000", "G.R. No. 123", "123", "2000-01-01"),
        ("G.R. No. 123, 1 Jan. 2000", "G.R. No. 123", "123", "2000-01-01"),
        (
            "G.R. Nos. 223528, 223529, 223530, 11 January 2017",
            "G.R. Nos. 223528, 223529, 223530",
            "223528, 223529, 223530",
            "2017-01-11",
        ),
    ],
)
def test_gr_date_order_and_multiple_id_results_are_stable(
    source, context, ids, docket_date
):
    citation = next(CitationGR.search(source))

    assert citation.context == context
    assert citation.ids == ids
    assert citation.docket_date.isoformat() == docket_date


@pytest.mark.parametrize(
    "source",
    [
        (
            "NLRC Case Nos. I-05-1083-97 to I-05-1109-97; consolidated "
            "NLRC Case Nos. I-05-1087-97, I-05-1088-97, I-05-1091-97, "
            "I-05-1092-97, I-05-1096-97, I-05-1097-97, and I-05-1109-97."
        ),
        (
            "Civil Cases Nos. 4247-L, 2395-L, 2367-L, 2812-L, 4160-L, "
            "4550-L, 4470-L, 4475-L, 4442-L, 4362-L, 4377-L, 4394-L, "
            "2581-L, 268-L, 2799-L, 4641-L, 2995-L, 3025-L, 3031-L, "
            "3090-L, 3042-L, 2520-L, 4669-L, 4649-L, and 4693-L."
        ),
    ],
)
def test_gr_search_rejects_long_date_less_legacy_shaped_number_lists(source):
    assert list(CitationGR.search(source)) == []


def test_constructor_patterns_are_cached_and_invalidate_when_the_source_changes():
    original = constructed_gr.docket_regex
    cached = constructed_gr.pattern
    assert constructed_gr.pattern is cached

    try:
        constructed_gr.docket_regex = original + "(?:)"
        assert constructed_gr.pattern is not cached
    finally:
        constructed_gr.docket_regex = original


def test_model_round_trip_equality_and_rendering_are_safe_and_structural():
    citation = Citation(
        cat="gr", num="L-I9863", date="1964-04-29", offg="47 O.G. Supp. 43"
    )

    assert Citation(**citation.model_dump()) == citation
    assert citation != None  # noqa: E711
    assert Docket.clean_serial("L-I9863", "gr") == "l-19863"
    docket = Docket(
        context="", category=DocketCategory.GR, ids="1", docket_date=date(2000, 1, 1)
    )
    assert docket != None  # noqa: E711
    assert (
        Citation.make_citation_string(
            "gr", "L-I9863", "1964-04-29", offg="47 o.g. supp. 43"
        )
        == "G.R. No. L-19863, Apr. 29, 1964, 47 O.G. Supp. 43"
    )


def test_derived_properties_do_not_become_stale_after_model_mutation():
    citation = Citation()

    assert citation.is_docket is False
    citation.docket_category = DocketCategory.GR
    citation.docket_serial = "1"
    citation.docket_date = "2000-01-01"
    assert citation.is_docket is True
    assert citation.display_date == "Jan. 01, 2000"


def test_make_citation_string_rejects_malformed_reports_and_unknown_categories():
    assert Citation.make_citation_string("unknown", "1", "2000-01-01") is None
    with pytest.raises(ValueError, match="Invalid scra report"):
        Citation.make_citation_string("gr", "1", "2000-01-01", scra="not a report")


def test_docket_metadata_uses_the_same_canonical_serial_as_citation_extraction():
    metadata = extract_docket_meta("G.R. No. L-I9863. April 29, 1964")

    assert metadata is not None
    assert metadata["ids"] == "l-19863"
