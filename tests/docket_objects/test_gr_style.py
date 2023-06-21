import pytest

from citation_docket.regexes import constructed_gr


@pytest.mark.parametrize(
    "data, phrase, docket_date, formerly, pp, report_date",
    [
        (
            "G.R. No. 224466 (Formerly UDK-15574), Feb. 16, 2019",
            "G.R. No. 224466 ",
            "Feb. 16, 2019",
            "(Formerly UDK-15574), ",
            None,
            None,
        ),
        (
            "G.R. No. 97920, p. 17, January 20, 1997",
            "G.R. No. 97920, ",
            "January 20, 1997",
            None,
            "p. 17, ",
            None,
        ),
        (
            "G.R. No. 104666, pp. 11-12, February 12, 1997",
            "G.R. No. 104666, ",
            "February 12, 1997",
            None,
            "pp. 11-12, ",
            None,
        ),
        (
            (  # noqa: E501
                "See <i>People v. Hirang</i>, G.R. No. 223528, 223529, 223530,"
                " 11 January 2017;"
            ),
            "G.R. No. 223528, 223529, 223530, ",
            "11 January 2017",
            None,
            None,
            None,
        ),
        (
            (  # noqa: E501
                "People v. De la Cruz, G.R. Nos. 91865-66 and G.R. Nos."
                " 92439-40, 6 July 1993"
            ),
            "G.R. Nos. 91865-66 and G.R. Nos. 92439-40, ",
            "6 July 1993",
            None,
            None,
            None,
        ),
        (
            (  # noqa: E501
                "Bangayan, Jr. v. Bangayan, G.R. Nos. 172777 and 172792,"
                " October 19, 2011, 659 SCRA 590, 597."
            ),
            "G.R. Nos. 172777 and 172792, ",
            "October 19, 2011",
            None,
            None,
            ", 659 SCRA 590",
        ),
        (
            (  # noqa: E501
                "Osmeña v. Commission on Elections, G.R. No. 100318, 100308,"
                " 100417,100420, July 30, 1991, 199 SCRA 750"
            ),
            "G.R. No. 100318, 100308, 100417,100420, ",
            "July 30, 1991",
            None,
            None,
            ", 199 SCRA 750",
        ),
        (
            (  # noqa: E501
                "Soriano III v. Yuzon, G.R. Nos. L-74910, L-75075, L-75094,"
                " L-76397, L-79459, and L-79520, 10 August 1988, 164 SCRA 226."
            ),
            "G.R. Nos. L-74910, L-75075, L-75094, L-76397, L-79459, and L-79520, ",
            "10 August 1988",
            None,
            None,
            ", 164 SCRA 226",
        ),
        (
            (  # noqa: E501
                "Republic v. Sandiganbayan, G.R. Nos. 108292, 108368,"
                " 108548-49, and 108550, 10 September 1993, 226 SCRA 314."
            ),
            "G.R. Nos. 108292, 108368, 108548-49, and 108550, ",
            "10 September 1993",
            None,
            None,
            ", 226 SCRA 314",
        ),
        (
            (  # noqa: E501
                "<i>Bagong Alyansang Makabayan v. Zamora,</i> G.R. Nos."
                " 138570, 138572, 138587, 138680, 138698, October 10, 2000,"
                " 342 SCRA 449"
            ),
            "G.R. Nos. 138570, 138572, 138587, 138680, 138698, ",
            "October 10, 2000",
            None,
            None,
            ", 342 SCRA 449",
        ),
    ],
)
def test_match_full(data, phrase, docket_date, formerly, pp, report_date):
    assert (match := constructed_gr.pattern.search(data))
    assert match.group("gr_phrase") == phrase
    assert match.group("docket_date") == docket_date
    assert match.group("formerly") == formerly
    assert match.group("pp") == pp
    assert match.group("opt_report") == report_date
