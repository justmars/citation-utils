import re

import pytest

from citation_utils.dockets import formerly

FORMERLY_PATTERN = re.compile(formerly, re.X)


@pytest.mark.parametrize(
    "original, matched_result",
    [
        (
            "A.M. No. MTJ-01-1381. (Formerly OCA I.P.I No. 97-426-MTJ)",
            ". (Formerly OCA I.P.I No. 97-426-MTJ)",
        ),
        (
            "G.R. Nos. 201225-26 (From CTA-EB Nos. 649 & 651)",
            " (From CTA-EB Nos. 649 & 651)",
        ),
        (
            "G.R. NO. 168174 (FORMERLY G.R. NOS. 156174-76)",
            " (FORMERLY G.R. NOS. 156174-76)",
        ),
        (
            "A.M. No. P-11-2896 [Formerly OCA I.P.I. No. 08-2977-P]",
            " [Formerly OCA I.P.I. No. 08-2977-P]",
        ),
        (
            "G.R. No. 227795 (Formerly UDK-15556)",
            " (Formerly UDK-15556)",
        ),
        (
            "A.M. No. RTJ-10-2255  (Formerly OCA I.P.I. No. 10-3335-RTJ)",
            "  (Formerly OCA I.P.I. No. 10-3335-RTJ)",
        ),
        (
            "A.M. No. P-12-3027 [Formerly OCA I.P.I. No. 11-3584-P]",
            " [Formerly OCA I.P.I. No. 11-3584-P]",
        ),
    ],
)
def test_match_formerly(original, matched_result):
    match = FORMERLY_PATTERN.search(original)
    assert match
    assert match.group(0) == matched_result
