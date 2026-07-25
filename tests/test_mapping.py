"""Tests for the control mapping engine."""

from __future__ import annotations

import pytest

from mcp_ai_governance.mapping import (
    DEFAULT_FRAMEWORKS,
    detect_themes,
    map_control,
)


def matched_ids(result, framework: str) -> list[str]:
    """Return the control ids matched for one framework."""
    return [match.control.id for match in result.mappings[framework]]


class TestValidation:
    def test_rejects_non_string_description(self) -> None:
        with pytest.raises(TypeError, match="description must be a string"):
            map_control(123)  # type: ignore[arg-type]

    def test_rejects_empty_description(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            map_control("   ")

    def test_rejects_oversized_description(self) -> None:
        with pytest.raises(ValueError, match="at most 4000 characters"):
            map_control("x" * 4001)

    def test_rejects_unknown_framework(self) -> None:
        with pytest.raises(ValueError, match="Unknown framework key"):
            map_control("human review", frameworks=["iso_9001"])

    def test_rejects_framework_string_instead_of_list(self) -> None:
        with pytest.raises(ValueError, match="not a single string"):
            map_control("human review", frameworks="eu_ai_act")  # type: ignore[arg-type]

    def test_rejects_empty_framework_list(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            map_control("human review", frameworks=[])

    @pytest.mark.parametrize("top_k", [0, -1, 11])
    def test_rejects_out_of_range_top_k(self, top_k: int) -> None:
        with pytest.raises(ValueError, match="top_k must be between"):
            map_control("human review", top_k=top_k)

    def test_rejects_boolean_top_k(self) -> None:
        with pytest.raises(TypeError, match="top_k must be an integer"):
            map_control("human review", top_k=True)  # type: ignore[arg-type]

    @pytest.mark.parametrize("value", [-0.1, 1.1])
    def test_rejects_out_of_range_min_confidence(self, value: float) -> None:
        with pytest.raises(ValueError, match="min_confidence must be between"):
            map_control("human review", min_confidence=value)


class TestThemeDetection:
    def test_detects_the_obvious_theme(self) -> None:
        themes = {theme.theme_id for theme in detect_themes("we run bias testing")}
        assert "bias_fairness" in themes

    def test_returns_strongest_theme_first(self) -> None:
        themes = detect_themes(
            "an approved AI policy naming prohibited uses, and one audit log entry"
        )
        assert themes[0].strength >= themes[-1].strength

    def test_no_theme_for_contentless_text(self) -> None:
        assert detect_themes("the quick brown fox") == ()

    def test_qualified_approval_phrase_does_not_fire_on_approved_policy(self) -> None:
        # Regression: "must approve" once collapsed to "approve" and fired here.
        themes = {
            theme.theme_id for theme in detect_themes("an approved written AI policy")
        }
        assert "human_oversight" not in themes
        assert "policy" in themes


class TestMapping:
    def test_maps_human_oversight_across_frameworks(self) -> None:
        result = map_control(
            "A named reviewer must approve every AI-drafted customer email before "
            "it is sent, and can reject it."
        )
        assert "Art. 14" in matched_ids(result, "eu_ai_act")
        assert any(
            control_id.startswith(("MAP", "MANAGE", "GOVERN"))
            for control_id in matched_ids(result, "nist_ai_rmf")
        )
        assert matched_ids(result, "iso_42001")

    def test_maps_logging_to_article_12(self) -> None:
        result = map_control(
            "Every model inference is written to an immutable audit log retained "
            "for seven years."
        )
        assert matched_ids(result, "eu_ai_act")[0] == "Art. 12"
        assert "A.6.2.8" in matched_ids(result, "iso_42001")

    def test_maps_inventory_to_govern_1_6(self) -> None:
        result = map_control(
            "We maintain a central inventory of every AI system in use, including "
            "shadow AI on employee laptops."
        )
        assert matched_ids(result, "nist_ai_rmf")[0] == "GOVERN 1.6"

    def test_maps_bias_testing_to_measure_2_11(self) -> None:
        result = map_control(
            "We measure subgroup performance and fairness metrics before release."
        )
        assert matched_ids(result, "nist_ai_rmf")[0] == "MEASURE 2.11"

    def test_defaults_to_the_three_ai_frameworks(self) -> None:
        result = map_control("human oversight of model output")
        assert tuple(result.mappings) == DEFAULT_FRAMEWORKS

    def test_framework_selection_is_honoured_and_deduplicated(self) -> None:
        result = map_control(
            "incident response runbook", frameworks=["nist_csf", "nist_csf"]
        )
        assert tuple(result.mappings) == ("nist_csf",)

    def test_top_k_caps_results_per_framework(self) -> None:
        result = map_control("documented policy and procedures", top_k=1)
        for matches in result.mappings.values():
            assert len(matches) <= 1

    def test_min_confidence_filters(self) -> None:
        permissive = map_control("documented policy", min_confidence=0.0, top_k=10)
        strict = map_control("documented policy", min_confidence=0.9, top_k=10)
        permissive_total = sum(len(v) for v in permissive.mappings.values())
        strict_total = sum(len(v) for v in strict.mappings.values())
        assert strict_total < permissive_total

    def test_confidence_is_bounded(self) -> None:
        result = map_control(
            "human oversight human oversight human oversight approval gate override",
            min_confidence=0.0,
        )
        for matches in result.mappings.values():
            for match in matches:
                assert 0.0 <= match.confidence <= 0.95

    def test_results_are_ordered_by_score(self) -> None:
        result = map_control("bias fairness testing of subgroups", top_k=5)
        scores = [match.raw_score for match in result.mappings["nist_ai_rmf"]]
        assert scores == sorted(scores, reverse=True)

    def test_is_deterministic(self) -> None:
        description = "vendor due diligence for a foundation model provider"
        first = map_control(description).to_dict()
        second = map_control(description).to_dict()
        assert first == second

    def test_case_and_punctuation_do_not_change_the_result(self) -> None:
        plain = map_control("we maintain an ai system inventory")
        shouty = map_control("WE MAINTAIN AN AI SYSTEM INVENTORY!!!")
        assert matched_ids(plain, "nist_ai_rmf") == matched_ids(shouty, "nist_ai_rmf")

    def test_every_match_carries_a_rationale_and_citation(self) -> None:
        result = map_control("post-deployment monitoring for model drift")
        for matches in result.mappings.values():
            for match in matches:
                assert match.rationale.startswith("Mapped to")
                assert match.control.citation


class TestNotes:
    def test_notes_when_nothing_is_detected(self) -> None:
        result = map_control("the quick brown fox jumps over the lazy dog")
        assert any("No governance themes" in note for note in result.notes)
        assert all(not matches for matches in result.mappings.values())

    def test_notes_when_a_framework_has_no_coverage(self) -> None:
        result = map_control(
            "the carbon footprint of model training is measured",
            frameworks=["nist_ai_rmf", "eu_ai_act"],
        )
        if not result.mappings["eu_ai_act"]:
            assert any("No match above the confidence" in n for n in result.notes)


class TestSerialisation:
    def test_to_dict_is_json_serialisable_and_complete(self) -> None:
        import json

        payload = map_control("human oversight before release").to_dict()
        json.dumps(payload)
        assert set(payload) >= {
            "description",
            "detected_themes",
            "mappings",
            "frameworks",
            "notes",
            "disclaimer",
        }
        assert "not legal advice" in payload["disclaimer"]
