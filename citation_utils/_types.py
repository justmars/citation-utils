from .dockets import (
    CitationAC,
    CitationAM,
    CitationBM,
    CitationGR,
    CitationJIB,
    CitationOCA,
    CitationPET,
    CitationUDK,
)

DocketReportCitationType = (
    CitationAC
    | CitationAM
    | CitationOCA
    | CitationBM
    | CitationGR
    | CitationPET
    | CitationJIB
    | CitationUDK
)  # noqa: E501

SEARCHABLE_CITATIONS = (
    CitationAC,
    CitationAM,
    CitationOCA,
    CitationBM,
    CitationGR,
    CitationPET,
    CitationUDK,
    CitationJIB,
)
"""Each object implements a `cls.search()` method which is utilized to generate matching citation types."""  # noqa: E501
