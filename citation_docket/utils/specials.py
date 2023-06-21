import re

old_sp = r"""
(?:
    ^r
    \s*
    gnos?\.?\s+ # RGNo. 39202, R GNo. 37505
)|
(?:
    ^reg.*gen.*nos?\.?\s+ # REGISTRO GENERAL No. 4312, REGISTER GENEREL No. 3877
)
"""
OLD_SPANISH = re.compile(old_sp, re.X | re.I)


def remove_prefix(text: str):
    """Based on the `regex` passed, remove this from the start of the `text`"""
    match = OLD_SPANISH.search(text)
    if not match:
        return None
    return {"cat": "gr", "idx": text.strip().removeprefix(match.group())}
