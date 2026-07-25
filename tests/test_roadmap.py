"""Tests for roadmap sequencing."""

from __future__ import annotations

import pytest

from mcp_ai_governance.readiness import score_readiness
from mcp_ai_governance.roadmap import PHASES, generate_roadmap, phase_by_key


class TestValidation:
    def test_rejects_a_bare_string(self) -> None:
        with pytest.raises(TypeError, match="not a single string"):
            generate_roadmap("we have no policy")  # type: ignore[arg-type]

    def test_rejects_a_bare_object(self) -> None:
        with pytest.raises(TypeError, match="not a single string or object"):
            generate_roadmap({"description": "no policy"})  # type: ignore[arg-type]

    def test_rejects_empty_list(self) -> None:
        with pytest.raises(ValueError, match="at least one entry"):
            generate_roadmap([])

    def test_rejects_too_many_gaps(self) -> None:
        with pytest.raises(ValueError, match="at most 60 entries"):
            generate_roadmap([f"gap {i}" for i in range(61)])

    def test_rejects_entry_without_description(self) -> None:
        with pytest.raises(ValueError, match="needs a non-empty 'description'"):
            generate_roadmap([{"severity": "high"}])

    def test_rejects_unknown_severity(self) -> None:
        with pytest.raises(ValueError, match="valid values are"):
            generate_roadmap([{"description": "no policy", "severity": "urgent"}])

    def test_rejects_duplicate_ids(self) -> None:
        with pytest.raises(ValueError, match="Duplicate gap id"):
            generate_roadmap(
                [
                    {"id": "g1", "description": "no policy"},
                    {"id": "g1", "description": "no inventory"},
                ]
            )

    def test_rejects_oversized_description(self) -> None:
        with pytest.raises(ValueError, match="at most 600 characters"):
            generate_roadmap([{"description": "x" * 601}])

    def test_rejects_wrong_entry_type(self) -> None:
        with pytest.raises(ValueError, match="must be a string or an object"):
            generate_roadmap([42])


class TestSequencing:
    def test_severity_drives_the_phase(self) -> None:
        roadmap = generate_roadmap(
            [
                {"id": "c", "description": "no bias testing", "severity": "critical"},
                {"id": "l", "description": "no bias testing", "severity": "low"},
            ]
        )
        by_id = {item.gap_id: item.phase for item in roadmap.items}
        order = [phase.key for phase in PHASES]
        assert order.index(by_id["c"]) < order.index(by_id["l"])

    def test_prerequisite_themes_are_promoted(self) -> None:
        promoted = generate_roadmap(
            [{"description": "there is no AI system inventory", "severity": "medium"}]
        )
        normal = generate_roadmap(
            [{"description": "there is no bias testing", "severity": "medium"}]
        )
        order = [phase.key for phase in PHASES]
        assert order.index(promoted.items[0].phase) < order.index(normal.items[0].phase)
        assert any("promoted one" in note for note in promoted.notes)

    def test_dependent_work_points_at_prerequisites(self) -> None:
        roadmap = generate_roadmap(
            [
                {"id": "inv", "description": "no AI system inventory"},
                {"id": "mon", "description": "no production monitoring for drift"},
            ]
        )
        monitoring = next(item for item in roadmap.items if item.gap_id == "mon")
        assert "inv" in monitoring.depends_on

    def test_a_gap_never_depends_on_itself(self) -> None:
        roadmap = generate_roadmap(
            [{"id": "solo", "description": "no AI policy and no impact assessment"}]
        )
        assert "solo" not in roadmap.items[0].depends_on

    def test_items_are_ordered_by_phase_then_severity(self) -> None:
        roadmap = generate_roadmap(
            [
                {"id": "a", "description": "no bias testing", "severity": "low"},
                {"id": "b", "description": "no bias testing", "severity": "critical"},
                {"id": "c", "description": "no bias testing", "severity": "high"},
            ]
        )
        assert [item.gap_id for item in roadmap.items] == ["b", "c", "a"]


class TestAssignment:
    @pytest.mark.parametrize(
        "description,owner",
        [
            ("data lineage and provenance are not recorded", "Chief Data Officer"),
            ("there is no threat model or penetration test", "CISO"),
            ("no incident response runbook exists", "Incident Response Manager"),
            ("vendor due diligence is not performed", "Vendor Risk Manager"),
            ("no AI literacy training programme", "Learning and Development Lead"),
        ],
    )
    def test_owner_matches_the_dominant_theme(self, description: str, owner: str) -> None:
        roadmap = generate_roadmap([description])
        assert roadmap.items[0].owner_role == owner

    def test_untyped_gaps_fall_back_and_are_flagged(self) -> None:
        roadmap = generate_roadmap(["the frobnicator is not wibbled"])
        assert roadmap.items[0].owner_role == "Head of AI Governance"
        assert roadmap.items[0].themes == ()
        assert any("No governance theme" in note for note in roadmap.notes)

    def test_severity_scales_effort(self) -> None:
        critical = generate_roadmap(
            [{"description": "no bias testing", "severity": "critical"}]
        )
        low = generate_roadmap([{"description": "no bias testing", "severity": "low"}])
        assert (
            critical.items[0].effort_person_weeks > low.items[0].effort_person_weeks
        )

    def test_effort_band_tracks_effort(self) -> None:
        roadmap = generate_roadmap(
            [{"description": "no evaluation harness or testing", "severity": "critical"}]
        )
        assert roadmap.items[0].effort_band in {"S", "M", "L", "XL"}

    def test_every_item_has_a_concrete_first_deliverable(self) -> None:
        roadmap = generate_roadmap(
            ["no AI inventory", "no human oversight", "no incident runbook"]
        )
        for item in roadmap.items:
            assert len(item.first_deliverable) > 20

    def test_supporting_roles_exclude_the_owner(self) -> None:
        roadmap = generate_roadmap(
            ["no data lineage, no privacy controls and no security threat model"]
        )
        item = roadmap.items[0]
        assert item.owner_role not in item.supporting_roles


class TestOutput:
    def test_phases_are_grouped_with_totals(self) -> None:
        payload = generate_roadmap(
            [
                {"description": "no AI policy", "severity": "critical"},
                {"description": "no drift monitoring", "severity": "medium"},
            ]
        ).to_dict()
        assert payload["total_items"] == 2
        assert payload["total_effort_person_weeks"] > 0
        for phase in payload["phases"]:
            assert phase["item_count"] == len(phase["items"])
            assert phase["window"]

    def test_owner_summary_aggregates_effort(self) -> None:
        payload = generate_roadmap(
            ["no data lineage", "no data quality thresholds"]
        ).to_dict()
        cdo = next(
            entry
            for entry in payload["owner_summary"]
            if entry["owner_role"] == "Chief Data Officer"
        )
        assert cdo["items"] == 2

    def test_empty_phases_are_omitted(self) -> None:
        payload = generate_roadmap(
            [{"description": "no bias testing", "severity": "low"}]
        ).to_dict()
        assert len(payload["phases"]) == 1

    def test_is_json_serialisable(self) -> None:
        import json

        json.dumps(generate_roadmap(["no AI policy"]).to_dict())

    def test_effort_caveat_is_always_present(self) -> None:
        roadmap = generate_roadmap(["no AI policy"])
        assert any("not for costing" in note for note in roadmap.notes)


class TestComposition:
    def test_readiness_gaps_feed_straight_into_the_roadmap(self) -> None:
        readiness = score_readiness(
            {
                "governance": {
                    "ai_policy": 0,
                    "risk_process": 1,
                    "system_inventory": 0,
                    "oversight_gates": 2,
                    "monitoring_incidents": 1,
                },
                "data": {"data_quality": 1, "lineage_provenance": 0},
            }
        )
        roadmap = generate_roadmap(list(readiness.gaps))
        assert len(roadmap.items) == len(readiness.gaps)
        assert {item.gap_id for item in roadmap.items} == {
            gap["id"] for gap in readiness.gaps
        }


class TestPhaseHelpers:
    def test_phase_lookup(self) -> None:
        assert phase_by_key("phase_1").name == "Stabilise"

    def test_unknown_phase_raises(self) -> None:
        with pytest.raises(KeyError):
            phase_by_key("phase_9")
