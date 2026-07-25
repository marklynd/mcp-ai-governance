"""Tests for evidence checklists."""

from __future__ import annotations

import pytest

from mcp_ai_governance.evidence import (
    COMMON_FAILURES,
    EVIDENCE_KINDS,
    THEME_EVIDENCE,
    EvidenceItem,
    evidence_checklist,
)
from mcp_ai_governance.knowledge import ALL_THEME_IDS, iter_controls


class TestValidation:
    def test_rejects_non_string(self) -> None:
        with pytest.raises(TypeError, match="control_id must be a string"):
            evidence_checklist(14)  # type: ignore[arg-type]

    def test_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            evidence_checklist("  ")

    def test_unknown_control_error_is_actionable(self) -> None:
        with pytest.raises(ValueError) as excinfo:
            evidence_checklist("GOVERN 42.9")
        message = str(excinfo.value)
        assert "Unknown control id" in message
        assert "controls are encoded" in message
        assert "governance://controls" in message


class TestLookup:
    @pytest.mark.parametrize("raw", ["Art. 14", "art 14", "Article 14", "ART-14"])
    def test_tolerant_control_ids(self, raw: str) -> None:
        assert evidence_checklist(raw).control.id == "Art. 14"


class TestContent:
    def test_every_encoded_control_produces_evidence(self) -> None:
        for control in iter_controls():
            checklist = evidence_checklist(control.id)
            assert checklist.items, f"{control.id} produced no evidence items"

    def test_evidence_spans_documents_and_records(self) -> None:
        # The point of the tool: a policy on its own is not evidence.
        checklist = evidence_checklist("Art. 14")
        kinds = {item.kind for item in checklist.items}
        assert "document" in kinds
        assert "record" in kinds

    def test_control_specific_overrides_are_included(self) -> None:
        items = " ".join(item.item for item in evidence_checklist("Art. 14").items)
        assert "stop function" in items

    def test_conformity_override_names_the_declaration(self) -> None:
        items = " ".join(item.item for item in evidence_checklist("Art. 43").items)
        assert "declaration of conformity" in items.lower()

    def test_iso_soa_override(self) -> None:
        items = " ".join(item.item for item in evidence_checklist("6.1.3").items)
        assert "Statement of Applicability" in items

    def test_common_failures_are_surfaced_where_known(self) -> None:
        checklist = evidence_checklist("Art. 14")
        assert any("rubber-stamping" in failure for failure in checklist.common_failures)

    def test_no_duplicate_evidence_items(self) -> None:
        for control_id in ("Art. 14", "MANAGE 4.1", "A.6.2.8"):
            items = [item.item for item in evidence_checklist(control_id).items]
            assert len(items) == len(set(items))

    def test_auditor_questions_and_sampling_guidance_present(self) -> None:
        payload = evidence_checklist("GOVERN 1.6").to_dict()
        assert payload["auditor_questions"]
        assert "sample" in payload["sampling_guidance"]


class TestDataIntegrity:
    def test_every_theme_has_an_evidence_template(self) -> None:
        missing = ALL_THEME_IDS - set(THEME_EVIDENCE)
        assert not missing, f"Themes without evidence templates: {sorted(missing)}"

    def test_evidence_kinds_are_valid(self) -> None:
        for items in THEME_EVIDENCE.values():
            for item in items:
                assert item.kind in EVIDENCE_KINDS
                assert item.why

    def test_failure_notes_reference_known_themes(self) -> None:
        assert set(COMMON_FAILURES) <= ALL_THEME_IDS

    def test_invalid_evidence_kind_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="Unknown evidence kind"):
            EvidenceItem(kind="vibes", item="x", why="y")


class TestSerialisation:
    def test_is_json_serialisable_and_grouped_by_kind(self) -> None:
        import json

        payload = evidence_checklist("MEASURE 2.11").to_dict()
        json.dumps(payload)
        assert payload["control_id"] == "MEASURE 2.11"
        assert payload["framework"] == "nist_ai_rmf"
        assert payload["citation"]
        for kind, values in payload["evidence_by_kind"].items():
            assert kind in EVIDENCE_KINDS
            assert values
