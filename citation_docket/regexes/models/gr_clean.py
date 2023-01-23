import re

LEGACY_PREFIXED = r"""
    ^ # start
    (?:
        (?:
            No # shorthand for number
            s? # plural option
            \. # period
            \s+ # space/s
        )? # number
        (?:
            (?:
                L
                \s* # L-26353
                -? # L 12271
                \s* # L- 59592
            )|
            (?:
                I\s- # I -5458
            )|
            (?:
                I- # I-19555
            )|
            (?:
                I\.- # I.-12735
            )
        )
    )
    (?=\w+) # excluded alphanumeric character
"""

LEGACY_PREFIXED_LOOKALIKE = r"""
    ^ # start
    (?:
        (?:
            No # shorthand for number
            s? # plural option
            \. # period
            \s+ # space/s
        )? # number
        (?:
            L
            \s* # L-26353
            -? # L 12271
            \s* # L- 59592
        )|
        (?:
            I\s- # I -5458
        )|
        (?:
            I- # I-19555
        )|
        (?:
            I\.- # I.-12735
        )
    )
    [ILl] # necessary after the group
    \s?
"""


def remove_prefix_regex(regex_to_match: str, text: str):
    """Based on the `regex` passed, remove this from the start of the `text`"""
    match = re.search(regex_to_match, text, re.VERBOSE)
    if not match:
        return None
    return text.strip().removeprefix(match.group())


def replace_prefix_regex(regex_to_match: str, text: str, std: str):
    """Based on the `regex` passed, replace this from the start of the `text`
    with a standardized variant `std`."""
    match = re.search(regex_to_match, text, re.VERBOSE)
    if not match:
        return None
    return std + text.strip().removeprefix(match.group()).strip()


def gr_prefix_clean(text: str) -> str | None:
    """The GR (General Register) docket ID makes use of `L-xxx` as a prefix
    in some of its serialized ids.

    Since most legal documents are parsed via OCR, the translation is often
    errneous resulting in an L-`I`9863 instead of being L-`1`9863.

    This also deals with cases involving inconsistent formatting, e.g.
    `No. L-12414`.

    If the regex patterns find the inconsistencies described above, clean
    the prefix.

    Examples:
        >>> inconsistent_text = "No. L-I9863"
        >>> gr_prefix_clean(inconsistent_text)
        'L-19863'

    Args:
        text (str): Raw docket serial ID that ought to be cleaned, e.g. ``L-I`
            or `No. L-`.

    Returns:
        str | None: The cleaned GR docket ID, if detected.
    """
    regex1, prefix1 = LEGACY_PREFIXED_LOOKALIKE, "L-1"  # L-I9863
    regex2, prefix2 = LEGACY_PREFIXED, "L-"  # improper L- formatted cases
    if cleaned1 := replace_prefix_regex(regex1, text, prefix1):
        return cleaned1
    elif cleaned2 := replace_prefix_regex(regex2, text, prefix2):
        return cleaned2
    return None
