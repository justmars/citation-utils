import re

import pytest

from citation_docket.regexes.constructed_oca import required

OCA_PATTERN = re.compile(required, re.X | re.I)


@pytest.mark.parametrize(
    "data",
    [
        "A.M. OCA IPI No. 10-25-SB-J",
        "OCA IPI NO. 14-220-CA-J",
        "A.M. OCA I.P.I. No. 07-108-CA-J",
        "A.M. OCA IPI No. 04-1606-MTJ",
        "A.M. OCA IPI No. 09-3210-RTJ",
        "A.M. OCA I.P.I. No. 10-3492-RTJ",
        "A.M. OCA IPI No. 02-1321-P",
        "A.M. OCA IPI No. 09-3243-RTJ",
        "A.M. OCA IPI NO. 06-11-392-METC",
        "OCA I.P.I. NO. 11-3589-RTJ",
    ],
)
def test_match_oca_phrase(data):
    assert OCA_PATTERN.fullmatch(data)
