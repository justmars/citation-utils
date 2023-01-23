import pytest

from citation_docket.regexes.models.gr_clean import (
    LEGACY_PREFIXED,
    gr_prefix_clean,
    remove_prefix_regex,
)


@pytest.mark.parametrize(
    "raw, result",
    [
        ("No. L-26353", "26353"),
        ("L -4618", "4618"),
        ("L 12271", "12271"),
        ("L- 59592", "59592"),
        ("L-26353", "26353"),
        ("I -5458", "5458"),
        ("I-19555", "19555"),
        ("I.-12735", "12735"),
    ],
)
def test_prefix_clean(raw, result):
    assert result == remove_prefix_regex(LEGACY_PREFIXED, raw)


@pytest.mark.parametrize(
    "raw, result",
    [
        ("No. L-I9863", "L-19863"),  # note change from I9 to 19
        ("L-I 1438", "L-11438"),  # change from I 14 to 114
        ("L-L8432", "L-18432"),  # change from L8 to 18
        ("No. L-26353", "L-26353"),
        ("L -4618", "L-4618"),
        ("L 12271", "L-12271"),
        ("L- 59592", "L-59592"),
        ("L-26353", "L-26353"),
        ("I -5458", "L-5458"),
        ("I-19555", "L-19555"),
        ("I.-12735", "L-12735"),
        ("I-47629", "L-47629"),
    ],
)
def test_gr_prefix_clean(raw, result):
    assert result == gr_prefix_clean(raw)
