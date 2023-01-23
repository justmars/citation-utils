import pytest

from citation_docket.regexes import constructed_am


@pytest.mark.parametrize(
    "data, phrase, formerly, pp, options",
    [
        (
            (  # noqa: E501
                "A.M. No. O.C.A.-00-01 (Formerly O.C.A. I.P.I. No. 99-02-OCA)"
                " July 28, 1997"
            ),
            "A.M. No. O.C.A.-00-01 ",
            "(Formerly O.C.A. I.P.I. No. 99-02-OCA) ",
            None,
            None,
        ),
        (
            (  # noqa: E501
                "A.M. Nos. 07-115-CA-J and CA-08-46-J (Formerly OCA IPI No."
                " 08-131-CA-J) July 28, 1997"
            ),
            "A.M. Nos. 07-115-CA-J and CA-08-46-J ",
            "(Formerly OCA IPI No. 08-131-CA-J) ",
            None,
            None,
        ),
        (
            "A.M No. P-96-1173, July 28, 1997, 28 SCRA 81",
            "A.M No. P-96-1173, ",
            None,
            None,
            ", 28 SCRA 81",
        ),
        (
            "A.M. No. 2008-23-SC, September 30, 2014, 737 SCRA 176, 191-192.",
            "A.M. No. 2008-23-SC, ",
            None,
            None,
            ", 737 SCRA 176",
        ),
        (
            "A.M. Nos. P-13-3116 & P-13-3112, November 12, 2013, 709 SCRA 254",
            "A.M. Nos. P-13-3116 & P-13-3112, ",
            None,
            None,
            ", 709 SCRA 254",
        ),
        (
            (
                "A.M. RTJ 00-1593 (Formerly OCA IPI NO. 98-544-RTJ), October"
                " 16, 2000"
            ),
            "A.M. RTJ 00-1593 ",
            "(Formerly OCA IPI NO. 98-544-RTJ), ",
            None,
            None,
        ),
        (
            (  # noqa: E501
                "A.M. No. P-04-1786 (Formerly OCA I.P.I. No. 02-1341-P), 13"
                " February 2006, 482 SCRA 265, 275-276"
            ),
            "A.M. No. P-04-1786 ",
            "(Formerly OCA I.P.I. No. 02-1341-P), ",
            None,
            ", 482 SCRA 265",
        ),
        (
            (
                "A.M. RTJ-12-2317 (Formerly OCA I.P.I. No. 10-3378-RTJ), Jan"
                " 1, 2000"
            ),
            "A.M. RTJ-12-2317 ",
            "(Formerly OCA I.P.I. No. 10-3378-RTJ), ",
            None,
            None,
        ),
    ],
)
def test_match_full(data, phrase, formerly, pp, options):
    assert (match := constructed_am.pattern.search(data))
    assert match.group("am_phrase") == phrase
    assert match.group("formerly") == formerly
    assert match.group("pp") == pp
    assert match.group("opt_report") == options
