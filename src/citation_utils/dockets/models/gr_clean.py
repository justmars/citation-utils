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

_NUMBER_PREFIX_PATTERN = re.compile(r"^nos?\.\s*", re.I)
_LEGACY_PREFIXED_PATTERN = re.compile(LEGACY_PREFIXED, re.X)
_L_LOOKALIKE_PATTERN = re.compile(r"^l\s*-\s*[il]\s*(?=\d)", re.I)
_I_PREFIX_PATTERN = re.compile(r"^i\.?\s*-\s*", re.I)
_L_NUMBER_PREFIX_PATTERN = re.compile(r"^l\s*-\s*no\.?\s*", re.I)
_SPACED_L_PREFIX_PATTERN = re.compile(r"^l\s+(?=\d)", re.I)


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
    value = _NUMBER_PREFIX_PATTERN.sub("", text.strip())

    # These are deliberately narrow repairs for the legacy GR prefix.  They
    # run before generic serial normalization so that the original ``L`` is
    # not discarded by a permissive category prefix matcher.
    if match := _L_LOOKALIKE_PATTERN.match(value):
        return "L-1" + value[match.end() :]
    if match := _I_PREFIX_PATTERN.match(value):
        return "L-" + value[match.end() :]
    if match := _L_NUMBER_PREFIX_PATTERN.match(value):
        return "L-" + value[match.end() :]
    if match := _SPACED_L_PREFIX_PATTERN.match(value):
        return "L-" + value[match.end() :]
    if match := _LEGACY_PREFIXED_PATTERN.match(value):
        return "L-" + value.removeprefix(match.group()).strip()
    return None
