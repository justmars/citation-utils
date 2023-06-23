import re
from collections.abc import Iterator
from typing import Any

from citation_date import DOCKET_DATE_REGEX, decode_date
from citation_report import REPORT_REGEX, get_publisher_label
from pydantic import BaseModel, Field

from .misc import cull_extra, formerly, pp


class CitationConstructor(BaseModel):
    """Prefatorily, regex strings are defined so that a
    `re.Pattern` object can take advantage of the "group_name"
    assigned in the string.

    These are the docket styles with regex strings predefined:

    1. General Register
    2. Administrative Matter
    3. Administrative Case
    4. Bar Matter
    5. Office of the Court Administrator
    6. Presidential Electoral Tribunal
    7. Judicial Integrity Board
    8. Undocketed Case

    The CitationConstructor formalizes the assigned group names into
    their respective fields.

    Relatedly, it takes advantage of
    the `citation_date` and the `citation_report` libraries in
    generating the main `@pattern` since the regex strings above
    are only concerned with the `key` `num` `id` formula part
    of the docket, e.g. `GR` `No.` `123`... but not the accompanying
    date and report.
    """

    label: str = Field(
        ...,
        title="Docket Label",
        description="e.g. General Register, Administrative Matter",
    )
    short_category: str = Field(
        ..., title="Docket Category Shorthand", description="e.g. GR, AM"
    )
    group_name: str = Field(
        ...,
        title="Regex Group Name",
        description=(
            "e.g. 'gr_test_phrase' identifies that portion of the"
            "Match object that should be associated with the label."
        ),
    )
    init_name: str = Field(
        ...,
        title="Regex Initial Group Name",
        description="e.g. gr_mid, am_init; see .regexes for other group names",
    )
    docket_regex: str = Field(
        ...,
        title="Regex Expression Proper",
        description=(
            "The full regex expression which includes the groupnames referred to above."
        ),
    )
    key_regex: str = Field(
        ...,
        title="Regex Key",
        description="Regex portion to get the serial ids",
    )
    num_regex: str = Field(
        ...,
        title="Regex Num",
        description="Regex portion for the num keyword to get the serial ids",
    )

    @property
    def pattern(self) -> re.Pattern:
        """Construct the regex string and generate a full Pattern object from:

        1. `docket_regex`,
        2. `docket_date` defined in the citation-date library
        3. an optional `REPORT_REGEX` defined in the citation-report library

        Returns:
            Pattern: Combination of Docket and Report styles.
        """
        return re.compile(
            "".join(
                [
                    rf"{self.docket_regex}",
                    rf"(?P<extra_phrase>{formerly}?{pp}?){DOCKET_DATE_REGEX}",
                    rf"(?P<opt_report>\,\s*{REPORT_REGEX})?",
                ]
            ),
            re.I | re.X,
        )

    @property
    def key_num_pattern(self) -> re.Pattern:
        """Unlike full @pattern, this regex compiled object is limited to
        just the key and number elements, e.g. "GR No. 123" or "BP Blg. 45"
        """
        regex = rf"{self.key_regex}({self.num_regex})?"
        return re.compile(regex, re.I | re.X)

    def detect(self, raw: str) -> Iterator[dict[str, Any]]:
        """Logic: if `self.init_name` Match group exists, get entire
        regex based on `self.group_name`, extract subgroups which will
        consist of `Docket` and `Report` parts.

        Args:
            raw (str): Text to evaluate

        Yields:
            Iterator[dict[str, Any]]: A dict that can fill up a Docket + Report pydantic BaseModel
        """  # noqa: E501
        for match in self.pattern.finditer(raw):
            if match.group(self.init_name):
                if ctx := match.group(self.group_name).strip(", "):
                    raw_id = cull_extra(self.key_num_pattern.sub("", ctx))
                    ids = raw_id.strip("()[] .,;")
                    raw_date = match.group("docket_date")
                    date_found = decode_date(raw_date, True)
                    if ids and date_found:
                        yield dict(
                            context=ctx,
                            short_category=self.short_category,
                            category=self.label,
                            ids=ids,
                            docket_date=date_found,
                            publisher=get_publisher_label(match),
                            volpubpage=match.group("volpubpage"),
                            volume=match.group("volume"),
                            page=match.group("page"),
                        )
