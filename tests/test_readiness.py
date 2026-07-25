"""Tests for readiness scoring."""

from __future__ import annotations

import pytest

from mcp_ai_governance.readiness import (
    DIMENSIONS,
    MAX_LEVEL,
    dimension_keys,
    question_catalogue,
    score_readiness,
)


def full_answers(level: int) -> dict[str, dict[str, int]]:
    """Return every question answered at ``level``."""
    return {
        dimension.key: {question.key: level for question in dimension.questions}
        for dimension in DIMENSIONS
    }


class TestValidation:
    def test_rejects_non_mapping(self) -> None:
        with pytest.raises(TypeError, match="answers must be a mapping"):
            score_readiness(["governance", 3])  # type: ignore[arg-type]

    def test_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            score_readiness({})

    def test_rejects_unknown_dimension(self) -> None:
        with pytest.raises(ValueError, match="Unknown answer key"):
            score_readiness({"culture": {"vibes": 3}})

    def test_rejects_unknown_question(self) -> None:
        with pytest.raises(ValueError, match="Unknown answer key"):
            score_readiness({"governance": {"not_a_question": 3}})

    def test_rejects_bare_dimension_key_without_question(self) -> None:
        with pytest.raises(ValueError, match="Unknown answer key"):
            score_readiness({"governance": 60})

    @pytest.mark.parametrize("value", [-1, 5, 99])
    def test_rejects_out_of_range_level(self, value: int) -> None:
        with pytest.raises(ValueError, match="must be between 0 and 4"):
            score_readiness({"governance.ai_policy": value})

    def test_rejects_boolean_level(self) -> None:
        with pytest.raises(ValueError, match="not a boolean"):
            score_readiness({"governance.ai_policy": True})

    def test_rejects_fractional_level(self) -> None:
        with pytest.raises(ValueError, match="whole number"):
            score_readiness({"governance.ai_policy": 2.5})

    def test_error_message_lists_valid_keys(self) -> None:
        with pytest.raises(ValueError) as excinfo:
            score_readiness({"nonsense": 1})
        assert "governance.ai_policy" in str(excinfo.value)


class TestInputShapes:
    def test_nested_and_dotted_forms_agree(self) -> None:
        nested = score_readiness({"governance": {"ai_policy": 3, "risk_process": 2}})
        dotted = score_readiness(
            {"governance.ai_policy": 3, "governance.risk_process": 2}
        )
        assert nested.overall_score == dotted.overall_score

    def test_forms_may_be_mixed(self) -> None:
        result = score_readiness(
            {"governance": {"ai_policy": 3}, "data.data_quality": 4}
        )
        assessed = {d.key for d in result.dimensions if d.assessed}
        assert assessed == {"governance", "data"}


class TestScoring:
    def test_all_zero_scores_zero(self) -> None:
        result = score_readiness(full_answers(0))
        assert result.overall_score == 0.0
        assert result.tier == "Ad hoc"

    def test_all_max_scores_one_hundred(self) -> None:
        result = score_readiness(full_answers(MAX_LEVEL))
        assert result.overall_score == 100.0
        assert result.tier == "Optimising"

    def test_midpoint_scores_fifty(self) -> None:
        result = score_readiness(full_answers(2))
        assert result.overall_score == 50.0

    def test_score_is_monotonic_in_maturity(self) -> None:
        scores = [score_readiness(full_answers(level)).overall_score for level in range(5)]
        assert scores == sorted(scores)
        assert len(set(scores)) == 5

    def test_dimension_scores_are_zero_to_one_hundred(self) -> None:
        result = score_readiness(full_answers(3))
        for dimension in result.dimensions:
            assert dimension.score is not None
            assert 0.0 <= dimension.score <= 100.0

    def test_question_weights_matter(self) -> None:
        # evaluation_harness carries a higher weight than role_clarity, so
        # scoring it low must hurt more than scoring an equally sized but
        # lighter question low.
        heavy_low = score_readiness(
            {"platform": {"evaluation_harness": 0, "environments": 4}}
        )
        light_low = score_readiness(
            {"platform": {"evaluation_harness": 4, "environments": 0}}
        )
        assert heavy_low.overall_score < light_low.overall_score


class TestPartialAssessment:
    def test_unassessed_dimensions_are_excluded_not_zeroed(self) -> None:
        result = score_readiness({"governance": {"ai_policy": 4}})
        assert result.overall_score == 100.0
        unassessed = [d.key for d in result.dimensions if not d.assessed]
        assert set(unassessed) == set(dimension_keys()) - {"governance"}
        assert any("excluded from the overall score" in n for n in result.notes)

    def test_coverage_is_reported(self) -> None:
        result = score_readiness({"data": {"data_quality": 3, "privacy_controls": 2}})
        data = next(d for d in result.dimensions if d.key == "data")
        assert data.to_dict()["coverage"] == "2/5"
        assert len(data.unanswered) == 3


class TestGapsAndWeakest:
    def test_low_answers_become_gaps(self) -> None:
        result = score_readiness(full_answers(0))
        assert len(result.gaps) == sum(len(d.questions) for d in DIMENSIONS)
        for gap in result.gaps:
            assert gap["severity"] in {"critical", "high", "medium", "low"}
            assert "." in gap["id"]

    def test_high_answers_produce_no_gaps(self) -> None:
        assert score_readiness(full_answers(4)).gaps == ()

    def test_gaps_are_sorted_by_severity(self) -> None:
        result = score_readiness(full_answers(0))
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        ranks = [order[gap["severity"]] for gap in result.gaps]
        assert ranks == sorted(ranks)

    def test_governance_zero_is_critical(self) -> None:
        result = score_readiness({"governance": {"ai_policy": 0}})
        assert result.gaps[0]["severity"] == "critical"

    def test_weakest_dimensions_are_the_two_lowest(self) -> None:
        answers = full_answers(4)
        answers["talent"] = dict.fromkeys(answers["talent"], 0)
        answers["data"] = dict.fromkeys(answers["data"], 1)
        result = score_readiness(answers)
        assert set(result.weakest_dimensions) == {"talent", "data"}


class TestSerialisation:
    def test_to_dict_is_json_serialisable(self) -> None:
        import json

        payload = score_readiness(full_answers(2)).to_dict()
        json.dumps(payload)
        assert set(payload) >= {
            "overall_score",
            "tier",
            "dimensions",
            "weakest_dimensions",
            "gaps",
            "maturity_scale",
        }

    def test_question_catalogue_covers_every_dimension(self) -> None:
        catalogue = question_catalogue()
        assert [entry["dimension"] for entry in catalogue] == list(dimension_keys())
        assert all(len(entry["questions"]) == 5 for entry in catalogue)

    def test_dimension_weights_sum_to_one(self) -> None:
        assert round(sum(d.weight for d in DIMENSIONS), 6) == 1.0
