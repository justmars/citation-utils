import pytest

from citation_docket.simple_matcher import (
    is_docket,
    simple_two_letter_docket_category,
)


@pytest.mark.parametrize(
    "raw, group_name",
    [
        ("G.  R. No. 123", "gr"),
        ("a.c124", "ac"),
    ],
)
def test_get_docket_category(raw, group_name):
    assert simple_two_letter_docket_category(raw) == group_name


@pytest.mark.parametrize(
    "raw, res",
    [
        (
            "gr 1241-sc Sep. 1, 1981",  # includes dashes
            {
                "docket_cat": "gr",
                "docket_idx": "1241-SC",
                "docket_dated": "1981-09-01",
            },
        ),
        (
            "am 124, Sep. 1, 1981",  # notice the comma in between
            {
                "docket_cat": "am",
                "docket_idx": "124",
                "docket_dated": "1981-09-01",
            },
        ),
        (
            "ac ac-2142-12, 12/4/2000",  # only initial cat included, diff. date format
            {
                "docket_cat": "ac",
                "docket_idx": "AC-2142-12",
                "docket_dated": "2000-12-04",
            },
        ),
        (
            "G.R. No. 192813, 12/4/2000",  # g.r. converted to gr; see ignored "No."
            {
                "docket_cat": "gr",
                "docket_idx": "192813",
                "docket_dated": "2000-12-04",
            },
        ),
    ],
)
def test_get_docket_defined(raw, res):
    assert is_docket(raw) == res
