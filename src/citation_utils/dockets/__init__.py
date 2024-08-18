from .constructed_ac import (
    CitationAC,
    ac_key,
    ac_phrases,
    constructed_ac,
)
from .constructed_am import (
    CitationAM,
    am_key,
    am_phrases,
    constructed_am,
)
from .constructed_bm import (
    CitationBM,
    bm_key,
    bm_phrases,
    constructed_bm,
)
from .constructed_gr import (
    CitationGR,
    constructed_gr,
    gr_key,
    gr_phrases,
    l_key,
)
from .constructed_jib import (
    CitationJIB,
    constructed_jib,
    jib_key,
    jib_phrases,
)
from .constructed_oca import (
    CitationOCA,
    constructed_oca,
    oca_key,
    oca_phrases,
)
from .constructed_pet import (
    CitationPET,
    constructed_pet,
    pet_key,
    pet_phrases,
)
from .constructed_udk import (
    CitationUDK,
    constructed_udk,
    udk_key,
    udk_phrases,
)
from .models import (
    DOCKET_DATE_FORMAT,
    CitationConstructor,
    Docket,
    DocketCategory,
    DocketReportCitation,
    Num,
    cull_extra,
    formerly,
    gr_prefix_clean,
    is_statutory_rule,
    pp,
)

DocketReport = (
    CitationAC
    | CitationAM
    | CitationOCA
    | CitationBM
    | CitationGR
    | CitationPET
    | CitationJIB
    | CitationUDK
)
