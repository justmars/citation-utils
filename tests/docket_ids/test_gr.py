import re

import pytest

from citation_docket.regexes import gr_phrases


@pytest.mark.parametrize(
    "item",
    [
        "Angara v. Electoral Commission, 63 Phil. 139,",  # prevented l. 139
        "CA G.R. No. 30720-R, October 8, 1962",
        "Banaria vs. Banaria, et al., C.A. No. 4142, May 31, 1950",
        "Del Fierro and Padilla, C.A. G.R. No. 3599-R, July 27, 1950.",
        "Republic v. Escaño, CA-G.R. No. 33045-R, 27 July 1964 as cited",
        (
            "Joven v. Caoili, A.M. No. P-17-3754 (Formerly OCA IPI No."
            " 14-4285-P), September 26, 2017, 840 SCRA 552, 559."
        ),
        "Adm. Matter No. P- 236, July 29, 1977, 78 SCRA 83, 86, 87",
        (
            "See Notice of Resolution in Santos Ventura Hocorma Foundation,"
            " Inc. v. Funk, A.C. No. 9094, January 13, 2014."
        ),
        "Adarne v. Aldaba, Adm. Case No. 801, 27 June 1978, 83 SCRA 734.",
        (
            "Re: Petition of Al Argosino To Take The Lawyer's Oath, B.M. No."
            " 712, March 19, 1997"
        ),
    ],
)
def test_other_dockets_fail_proper_gr_pattern(item):
    pattern = re.compile(gr_phrases, re.X | re.I)
    assert not pattern.search(item)


@pytest.mark.parametrize(
    "item",
    [
        "G.R. L-No. 5110",
        "G.R. No. 5110",
        "GR 100",
        "L-3243",
        "L-No. 5110",
        "L 5110",
        ", No. 32435",
        "G.R. No. 100909",
        "G.R. No. 223528, 223529, 223530",
        "G.R. Nos. 172777 and 172792,",
        "G.R. No. 100318, 100308, 100417,100420, ",
        "G.R. Nos. L-74910, L-75075, L-75094, L-76397, L-79459, and L-79520",
    ],
)
def test_pass_gr_pattern(item):
    pattern = re.compile(gr_phrases, re.X | re.I)
    assert pattern.fullmatch(item)
