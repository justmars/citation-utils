import re

import pytest

from citation_utils.dockets.constructed_pet import required

PET_PATTERN = re.compile(required, re.X | re.I)


@pytest.mark.parametrize(
    "data",
    [
        "PET No. 1",
        "P.E.T. No. 1",
        "P.E.T No. 3",
        "P.ET No.4",
    ],
)
def test_match_pet_phrase(data):
    assert PET_PATTERN.fullmatch(data)
