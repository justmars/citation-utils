import pytest

from citation_docket.regexes import constructed_ac


@pytest.mark.parametrize(
    "data, init, phrase, formerly, pp, options",
    [
        (
            "A.C. No. 10179 (Formerly CBD 11-2985), March 04, 2014",
            "A.C. No. ",
            "A.C. No. 10179 ",
            "(Formerly CBD 11-2985), ",
            None,
            None,
        ),
        (
            "A.C. No. 10138 (Formerly CBD Case No. 06-1876), June 16, 2015",
            "A.C. No. ",
            "A.C. No. 10138 ",
            "(Formerly CBD Case No. 06-1876), ",
            None,
            None,
        ),
        (
            "A.C. No. 8392 [ Formerly CBD Case No. 08-2175], January 1, 2020",
            "A.C. No. ",
            "A.C. No. 8392 ",
            "[ Formerly CBD Case No. 08-2175], ",
            None,
            None,
        ),
        (
            "A.C. No. 7250 [Formerly CBD Case No. 05-1448], 13 February 2006",
            "A.C. No. ",
            "A.C. No. 7250 ",
            "[Formerly CBD Case No. 05-1448], ",
            None,
            None,
        ),
        (
            "A.C. No. P-88-198, February 25, 1992, 206 SCRA 491.",
            "A.C. No. ",
            "A.C. No. P-88-198, ",
            None,
            None,
            ", 206 SCRA 491",
        ),
        (
            "Admin. Case No. 561, April 27, 1967, 19 SCRA 815",
            "Admin. Case No. ",
            "Admin. Case No. 561, ",
            None,
            None,
            ", 19 SCRA 815",
        ),
    ],
)
def test_match_full(data, init, phrase, formerly, pp, options):
    assert (match := constructed_ac.pattern.search(data))
    assert match.group("ac_phrase") == phrase
    assert match.group("formerly") == formerly
    assert match.group("pp") == pp
    assert match.group("opt_report") == options
