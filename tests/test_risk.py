"""Tests for EU AI Act risk-tier classification."""

from __future__ import annotations

import pytest

from mcp_ai_governance.risk import TIER_OBLIGATIONS, classify_risk_tier


class TestValidation:
    def test_rejects_non_string(self) -> None:
        with pytest.raises(TypeError, match="use_case must be a string"):
            classify_risk_tier(None)  # type: ignore[arg-type]

    def test_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            classify_risk_tier("  ")

    def test_rejects_oversized(self) -> None:
        with pytest.raises(ValueError, match="at most 4000 characters"):
            classify_risk_tier("x" * 4001)


class TestProhibited:
    @pytest.mark.parametrize(
        "use_case,citation",
        [
            (
                "A system that assigns citizens a social credit score used to deny "
                "them access to unrelated services.",
                "Art. 5(1)(c)",
            ),
            (
                "A tool that performs untargeted scraping of facial images from the "
                "internet to build a facial recognition database.",
                "Art. 5(1)(e)",
            ),
            (
                "Software that infers employee emotions from webcam video during "
                "meetings for the HR team.",
                "Art. 5(1)(f)",
            ),
            (
                "A model that predicts who will commit a crime based on personality "
                "traits, for use in predictive policing.",
                "Art. 5(1)(d)",
            ),
        ],
    )
    def test_article_5_practices_are_prohibited(
        self, use_case: str, citation: str
    ) -> None:
        result = classify_risk_tier(use_case)
        assert result.tier == "prohibited"
        assert citation in {trigger.citation for trigger in result.triggers}

    def test_prohibited_outranks_annex_iii(self) -> None:
        result = classify_risk_tier(
            "A recruitment tool that screens CVs and also assigns applicants a "
            "social credit score."
        )
        assert result.tier == "prohibited"

    def test_prohibited_advises_stopping(self) -> None:
        result = classify_risk_tier("a social scoring system for citizens")
        assert any("Stop the initiative" in item for item in result.obligations)


class TestHighRisk:
    @pytest.mark.parametrize(
        "use_case,citation",
        [
            (
                "A model that ranks job applicants and produces a shortlist for "
                "recruiters.",
                "Annex III, point 4",
            ),
            (
                "A model that scores loan applicants for creditworthiness at a "
                "retail bank.",
                "Annex III, point 5",
            ),
            (
                "A system used for exam proctoring and cheating detection at a "
                "university.",
                "Annex III, point 3",
            ),
            (
                "A tool that helps a judge draft a sentencing recommendation.",
                "Annex III, point 8",
            ),
            (
                "A model that triages visa applications for an immigration agency.",
                "Annex III, point 7",
            ),
        ],
    )
    def test_annex_iii_areas_are_high_risk(self, use_case: str, citation: str) -> None:
        result = classify_risk_tier(use_case)
        assert result.tier == "high-risk"
        assert citation in {trigger.citation for trigger in result.triggers}

    def test_high_risk_surfaces_the_article_6_3_derogation(self) -> None:
        result = classify_risk_tier("a model that ranks job applicants for recruiters")
        assert any("Art. 6(3)" in caveat for caveat in result.caveats)

    def test_high_risk_obligations_span_articles_9_to_15(self) -> None:
        obligations = " ".join(TIER_OBLIGATIONS["high-risk"])
        for article in ("Art. 9", "Art. 10", "Art. 12", "Art. 14", "Art. 15"):
            assert article in obligations


class TestLimitedRisk:
    def test_chatbot_is_limited_risk(self) -> None:
        result = classify_risk_tier(
            "An internal chatbot that answers HR policy questions for staff."
        )
        assert result.tier == "limited-risk"
        assert any(t.citation.startswith("Art. 50") for t in result.triggers)

    def test_image_generation_is_limited_risk(self) -> None:
        result = classify_risk_tier(
            "A tool that will generate images from text prompts for the marketing "
            "team."
        )
        assert result.tier == "limited-risk"

    def test_deepfake_is_limited_risk(self) -> None:
        result = classify_risk_tier(
            "A feature that produces a deepfake of a public figure for a satirical "
            "video."
        )
        assert result.tier == "limited-risk"


class TestMinimalRisk:
    def test_unremarkable_use_case_is_minimal(self) -> None:
        result = classify_risk_tier(
            "A model that forecasts warehouse stock levels from historical sales."
        )
        assert result.tier == "minimal-risk"
        assert result.triggers == ()

    def test_minimal_risk_explains_thin_descriptions(self) -> None:
        result = classify_risk_tier("a model")
        assert "thin description" in result.reasoning


class TestOutputContract:
    def test_always_returns_caveats_and_disclaimer(self) -> None:
        for use_case in (
            "a social scoring system",
            "a CV screening model",
            "a customer service chatbot",
            "a stock forecasting model",
        ):
            payload = classify_risk_tier(use_case).to_dict()
            assert payload["caveats"]
            assert "not a legal determination" in payload["disclaimer"]
            assert payload["penalty_exposure"]
            assert payload["key_dates"]["general_application"] == "2026-08-02"

    def test_annex_i_limitation_is_always_disclosed(self) -> None:
        result = classify_risk_tier("a stock forecasting model")
        assert any("Annex I" in caveat for caveat in result.caveats)

    def test_is_deterministic(self) -> None:
        use_case = "a model that ranks job applicants"
        assert classify_risk_tier(use_case).to_dict() == classify_risk_tier(
            use_case
        ).to_dict()

    def test_is_json_serialisable(self) -> None:
        import json

        json.dumps(classify_risk_tier("a CV screening tool").to_dict())

    def test_confidence_is_bounded(self) -> None:
        result = classify_risk_tier(
            "recruitment recruitment hiring decision job applicant candidate ranking"
        )
        assert 0.0 <= result.confidence <= 0.95
