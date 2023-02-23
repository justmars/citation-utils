__version__ = "0.1.2"

from .__main__ import (
    DocketReportCitationType,
    extract_docket_from_data,
    extract_dockets,
)
from .regexes import (
    DOCKET_DATE_FORMAT,
    CitationAdministrativeCase,
    CitationAdministrativeMatter,
    CitationBarMatter,
    CitationGeneralRegister,
    Docket,
    DocketCategory,
    Num,
    ShortDocketCategory,
    ac_key,
    ac_phrases,
    am_key,
    am_phrases,
    bm_key,
    bm_phrases,
    cull_extra,
    formerly,
    gr_key,
    gr_phrases,
    l_key,
    pp,
)
from .simple_matcher import is_docket, setup_docket_field
