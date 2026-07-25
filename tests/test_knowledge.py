"""Integrity tests for the encoded framework knowledge base.

These are the tests that stop the knowledge base rotting: every control must
have a resolvable identifier, valid themes, and a citation, and the framework
structure must match what the source documents actually contain.
"""

from __future__ import annotations

import pytest

from mcp_ai_governance.knowledge import (
    ALL_FRAMEWORK_KEYS,
    ALL_THEME_IDS,
    FRAMEWORKS,
    THEMES,
    control_ids,
    coverage_summary,
    find_control,
    iter_controls,
)
from mcp_ai_governance.knowledge.base import Control
from mcp_ai_governance.knowledge.eu_ai_act import (
    ANNEX_III_AREAS,
    PENALTY_BANDS,
    PROHIBITED_PRACTICES,
    TRANSPARENCY_TRIGGERS,
)


class TestStructuralIntegrity:
    def test_control_ids_are_globally_unique(self) -> None:
        ids = control_ids()
        assert len(ids) == len(set(ids))

    def test_every_control_has_citation_and_themes(self) -> None:
        for control in iter_controls():
            assert control.citation, f"{control.id} has no citation"
            assert control.themes, f"{control.id} has no themes"
            assert control.title.strip(), f"{control.id} has no title"

    def test_every_theme_reference_is_valid(self) -> None:
        for control in iter_controls():
            unknown = set(control.themes) - ALL_THEME_IDS
            assert not unknown, f"{control.id} references unknown themes {unknown}"

    def test_every_theme_is_used_by_at_least_one_control(self) -> None:
        used = {theme for control in iter_controls() for theme in control.themes}
        assert used == ALL_THEME_IDS, f"Unused themes: {sorted(ALL_THEME_IDS - used)}"

    def test_every_theme_has_signals(self) -> None:
        for theme in THEMES.values():
            assert theme.signals, f"Theme {theme.id} has no signal phrases"

    def test_control_rejects_unknown_theme(self) -> None:
        with pytest.raises(ValueError, match="unknown themes"):
            Control(
                id="X.1",
                title="t",
                framework="nist_ai_rmf",
                group="g",
                themes=("not_a_real_theme",),
            )

    def test_control_rejects_empty_themes(self) -> None:
        with pytest.raises(ValueError, match="at least one theme"):
            Control(id="X.1", title="t", framework="nist_ai_rmf", group="g", themes=())


class TestFrameworkContent:
    def test_all_four_frameworks_present(self) -> None:
        assert set(ALL_FRAMEWORK_KEYS) == {
            "nist_ai_rmf",
            "iso_42001",
            "eu_ai_act",
            "nist_csf",
        }

    def test_ai_rmf_has_the_four_core_functions(self) -> None:
        prefixes = {
            control.id.split()[0] for control in FRAMEWORKS["nist_ai_rmf"].controls
        }
        assert prefixes == {"GOVERN", "MAP", "MEASURE", "MANAGE"}

    def test_ai_rmf_encodes_all_72_subcategories(self) -> None:
        # NIST AI RMF 1.0 has 72 subcategories across the four functions.
        assert len(FRAMEWORKS["nist_ai_rmf"].controls) == 72

    @pytest.mark.parametrize(
        "control_id",
        ["GOVERN 1.1", "GOVERN 6.2", "MAP 5.2", "MEASURE 2.11", "MANAGE 4.3"],
    )
    def test_known_ai_rmf_subcategories_exist(self, control_id: str) -> None:
        assert find_control(control_id) is not None

    def test_iso_42001_covers_clauses_four_to_ten(self) -> None:
        clause_numbers = {
            control.id.split(".")[0]
            for control in FRAMEWORKS["iso_42001"].controls
            if control.id[0].isdigit()
        }
        assert clause_numbers == {"4", "5", "6", "7", "8", "9", "10"}

    def test_iso_42001_annex_a_groups(self) -> None:
        annex_groups = {
            ".".join(control.id.split(".")[:2])
            for control in FRAMEWORKS["iso_42001"].controls
            if control.id.startswith("A.")
        }
        assert annex_groups == {
            "A.2",
            "A.3",
            "A.4",
            "A.5",
            "A.6",
            "A.7",
            "A.8",
            "A.9",
            "A.10",
        }

    @pytest.mark.parametrize(
        "article", ["Art. 5", "Art. 6", "Art. 14", "Art. 50", "Art. 53", "Art. 99"]
    )
    def test_key_eu_articles_exist(self, article: str) -> None:
        assert find_control(article) is not None

    def test_eu_transparency_is_article_50_not_the_proposal_number(self) -> None:
        # Art. 52 was the 2021 proposal's transparency article. In the adopted
        # regulation it is Art. 50, and citing 52 is a common sourcing error.
        art_50 = find_control("Art. 50")
        assert art_50 is not None
        assert "transparency" in art_50.title.lower()
        assert find_control("Art. 52") is None

    def test_csf_functions(self) -> None:
        functions = {control.group for control in FRAMEWORKS["nist_csf"].controls}
        assert functions == {
            "GOVERN",
            "IDENTIFY",
            "PROTECT",
            "DETECT",
            "RESPOND",
            "RECOVER",
        }


class TestControlLookup:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("Art. 14", "Art. 14"),
            ("art 14", "Art. 14"),
            ("Article 14", "Art. 14"),
            ("art-14", "Art. 14"),
            ("  ART. 14  ", "Art. 14"),
            ("govern 1.6", "GOVERN 1.6"),
            ("GOVERN-1.6", "GOVERN 1.6"),
            ("a.6.2.8", "A.6.2.8"),
            ("measure 2.11", "MEASURE 2.11"),
            ("gv.sc", "GV.SC"),
        ],
    )
    def test_tolerant_matching(self, raw: str, expected: str) -> None:
        control = find_control(raw)
        assert control is not None
        assert control.id == expected

    def test_unknown_returns_none(self) -> None:
        assert find_control("GOVERN 99.9") is None

    def test_component_boundaries_are_preserved(self) -> None:
        # "A.1.1" style ids must not collide with "A.11" style ids.
        assert find_control("a611") is None

    def test_non_string_raises(self) -> None:
        with pytest.raises(TypeError):
            find_control(14)  # type: ignore[arg-type]


class TestEuReferenceData:
    def test_prohibited_practices_cover_article_5_points(self) -> None:
        citations = {rule.citation for rule in PROHIBITED_PRACTICES}
        assert citations == {f"Art. 5(1)({letter})" for letter in "abcdefgh"}

    def test_annex_iii_has_eight_areas(self) -> None:
        assert len(ANNEX_III_AREAS) == 8
        assert {rule.citation for rule in ANNEX_III_AREAS} == {
            f"Annex III, point {n}" for n in range(1, 9)
        }

    def test_transparency_triggers_cite_article_50(self) -> None:
        for rule in TRANSPARENCY_TRIGGERS:
            assert rule.citation.startswith("Art. 50(")

    def test_every_rule_has_signals(self) -> None:
        for rule in PROHIBITED_PRACTICES + ANNEX_III_AREAS + TRANSPARENCY_TRIGGERS:
            assert rule.signals, f"{rule.code} has no signals"

    def test_penalty_bands_cover_every_tier(self) -> None:
        assert set(PENALTY_BANDS) == {
            "prohibited",
            "high-risk",
            "limited-risk",
            "minimal-risk",
        }


class TestCoverageSummary:
    def test_reports_every_framework_with_honest_fields(self) -> None:
        summary = coverage_summary()
        assert len(summary) == len(ALL_FRAMEWORK_KEYS)
        for entry in summary:
            assert entry["coverage"]
            assert entry["source"]
            assert entry["controls_encoded"] > 0
