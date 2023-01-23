import re

import pytest

from citation_docket.regexes.constructed_bm import required

BM_PATTERN = re.compile(required, re.X | re.I)


@pytest.mark.parametrize(
    "data",
    [
        "BAR MATTER No. 810",
        "B.M. No. 3288",
        "BAR MATTER NO. 1628",
        "Bar Matter No. 68",
        "B.M. NO. 1370",
    ],
)
def test_match_bm_phrase(data):
    assert BM_PATTERN.fullmatch(data)
