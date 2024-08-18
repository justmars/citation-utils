from collections import namedtuple
from enum import Enum


class Point(namedtuple("Point", ["x", "y"])):
    """
    Based on two letters, get valid options and patterns
    """

    __slots__ = ()

    @property
    def permuted(self):
        return [
            "".join([self.x, self.y]),  # gr
            "".join([self.x, r"\.", self.y]),  # g.r
            "".join([self.x, self.y, r"\."]),  # gr.
            "".join([self.x, r"\.", self.y, r"\."]),  # g.r.
        ]


NUMBER_KEYWORD = r"""
    \b
    No # Number
    s? # the letter s, optional
    \.? # optional .
    \s*
"""


class Key(Enum):
    GR = Point("g", "r").permuted
    AM = Point("a", "m").permuted + [r"Adm\.\sMatter", r"Admin\sMatter"]
    BM = Point("b", "m").permuted + [r"Bar\sMatter"]
    AC = Point("a", "c").permuted + [
        r"A\.C\.\s\-\sCBD",
        r"A\.C\.\sCBD",
        r"Adm\.\sCase",
        r"Admin\sCase",
    ]


class Num(Enum):
    GR = Key.AM.value + Key.AC.value + Key.BM.value
    AM = Key.GR.value + Key.AC.value + Key.BM.value
    AC = Key.GR.value + Key.AM.value + Key.BM.value
    BM = Key.GR.value + Key.AM.value + Key.AC.value

    @property
    def allowed(self):
        """
        Prevent capture of "Nos" word when not preceded by the
        intended docket type. Get excluded raw literals combined
        as negative lookbehinds for keyword "Nos".
        """
        ex_list = [rf"(?<!{e}\s)" for e in self.value]
        pre_num = "".join(ex_list)
        return rf"{pre_num}{NUMBER_KEYWORD}"
