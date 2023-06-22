from .regexes import (
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

CITATION_OPTIONS = (
    CitationAC,
    CitationAM,
    CitationOCA,
    CitationBM,
    CitationGR,
    CitationPET,
    CitationUDK,
    CitationJIB,
)
