import importlib
from types import ModuleType


def assert_star_exports(module_name: str, expected: list[str]) -> None:
    module: ModuleType = importlib.import_module(module_name)
    namespace: dict[str, object] = {}
    exec(f"from {module_name} import *", namespace)

    assert module.__all__ == expected
    assert [name for name in namespace if name != "__builtins__"] == expected


def test_root_facade_preserves_its_star_import_contract() -> None:
    assert_star_exports(
        "citation_utils",
        [
            "dockets",
            "identity",
            "document",
            "citation",
            "Citation",
            "CountedCitation",
            "DOCKET_DATE_FORMAT",
            "CitationAC",
            "CitationAM",
            "CitationBM",
            "CitationGR",
            "CitationJIB",
            "CitationOCA",
            "CitationPET",
            "CitationUDK",
            "Docket",
            "DocketCategory",
            "Num",
            "ac_key",
            "ac_phrases",
            "am_key",
            "am_phrases",
            "bm_key",
            "bm_phrases",
            "cull_extra",
            "formerly",
            "gr_key",
            "gr_phrases",
            "is_statutory_rule",
            "jib_key",
            "jib_phrases",
            "l_key",
            "oca_key",
            "oca_phrases",
            "pet_key",
            "pet_phrases",
            "pp",
            "udk_key",
            "udk_phrases",
            "CitableDocument",
            "CitationOccurrence",
            "special",
            "extract_docket_meta",
        ],
    )


def test_docket_facade_preserves_its_star_import_contract() -> None:
    assert_star_exports(
        "citation_utils.dockets",
        [
            "models",
            "constructed_ac",
            "CitationAC",
            "ac_key",
            "ac_phrases",
            "constructed_am",
            "CitationAM",
            "am_key",
            "am_phrases",
            "constructed_bm",
            "CitationBM",
            "bm_key",
            "bm_phrases",
            "constructed_gr",
            "CitationGR",
            "gr_key",
            "gr_phrases",
            "l_key",
            "constructed_jib",
            "CitationJIB",
            "jib_key",
            "jib_phrases",
            "constructed_oca",
            "CitationOCA",
            "oca_key",
            "oca_phrases",
            "constructed_pet",
            "CitationPET",
            "pet_key",
            "pet_phrases",
            "constructed_udk",
            "CitationUDK",
            "udk_key",
            "udk_phrases",
            "DOCKET_DATE_FORMAT",
            "CitationConstructor",
            "Docket",
            "DocketCategory",
            "DocketReportCitation",
            "Num",
            "cull_extra",
            "formerly",
            "gr_prefix_clean",
            "is_statutory_rule",
            "pp",
            "DocketReport",
        ],
    )


def test_docket_model_facades_preserve_their_star_import_contracts() -> None:
    assert_star_exports(
        "citation_utils.dockets.models",
        [
            "docket_category",
            "gr_clean",
            "docket_model",
            "misc",
            "constructor",
            "CitationConstructor",
            "DocketCategory",
            "docket_citation",
            "DocketReportCitation",
            "DB_SERIAL_NUM",
            "DOCKET_DATE_FORMAT",
            "Docket",
            "docket_rules",
            "is_statutory_rule",
            "gr_prefix_clean",
            "cull_extra",
            "formerly",
            "pp",
            "Num",
        ],
    )
    assert_star_exports(
        "citation_utils.dockets.models.misc",
        [
            "extra",
            "cull_extra",
            "formerly",
            "pp",
            "num",
            "NUMBER_KEYWORD",
            "Num",
        ],
    )
