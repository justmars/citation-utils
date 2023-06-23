import re

import pytest

from citation_utils.dockets.constructed_ac import required

AC_PATTERN = re.compile(required, re.X | re.I)


@pytest.mark.parametrize(
    "data",
    [
        "AC No. 561",
        "A.C. No. L-363",
        "AC No. CBD-174",
        "A.C. No. P-88-198",
        "A.C. CBD No. 167",
        "Adm. Case No. 1701-CFI",
        "ADM CASE No. 783-MJ",
        "Adm. Case No. 203-CJ",
        "A.C. No. 11599",
    ],
)
def test_match_am_phrase(data):
    assert AC_PATTERN.fullmatch(data)
