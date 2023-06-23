import re

import pytest

from citation_utils.dockets.constructed_am import required

AM_PATTERN = re.compile(required, re.X | re.I)


@pytest.mark.parametrize(
    "data",
    [
        "A. M. No. 08-19-SB-J",
        "A.M. No. 08-19-SB-J",
        "A.M. No. 336",
        "A.M. No. P-04-1786",
        "A.M. No. 2008-23-SC",
        "A.M. Nos. P-13-3116",
        "Adm. Matter No. P-236",
        "A.M. No. 96-MTC",
        "A.M. No. P-96-1173",
        "A.M. No. P-96-1173,",
        "A.M. No. P-96-1173, and",
        "A.M. No. P-96-1173, and,",
        "A.M. No. P-96-1173 and,",
        "A.M. No. SDC-97-2-P",
        "A.M. MTJ-00-1255",
        "Administrative Matter No. P-274",
        "Administrative Matter No. 6998-MJ",
        "ADM MATTER NO. 573-MJ",
        "ADM MAT. NO. 1513-MJ",
        "Adm. Matter No. 1037-CJ",
        "AM No. 866-CJ",
        "A. M No. 340-MJ",
        "A.M. RTJ-00-1569",
        "A.M. MTJ-99-1199",
        "A.M. P-01-1473",
        "A.M. P-99-1343",
        "A.M. P-01-1480",
        "A.M. MTJ-00-1262",
        "A. M. RTJ-00-1550",
        "A.M. RTJ-99-1511",
        "A.M. 99-9-141-MTCC",
        "A.M. P-94-1072",
        "A.M. SB-95-6-P",
        "A.M. SDC-97-2-P",
        "A.M. MTJ-98-1147",
        "A.M. MTJ-95-1051",
        "A.M. MTJ-93-850",
        "A.M. RTJ-96-1353",
        "A.M. RTJ-94-1266",
        "A.M. MTJ-96-1099",
        "Adm. Matter Nos. 2367-CAR &",
    ],  # should match but presently isn't: Adm. Matter Nos. 2367-CAR & 2373-CAR
)
def test_match_am_phrase(data):
    assert AM_PATTERN.fullmatch(data)
