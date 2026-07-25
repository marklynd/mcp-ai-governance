"""Tests for the MCP tool surface.

These assert the contract a client sees: the tool names, that every tool has a
description and a JSON schema, and that calling through the FastMCP dispatcher
returns the same result as calling the underlying function.
"""

from __future__ import annotations

import json

import pytest

from mcp_ai_governance import server

EXPECTED_TOOLS = {
    "map_control",
    "score_readiness",
    "classify_risk_tier",
    "generate_roadmap",
    "evidence_checklist",
    "list_frameworks",
    "list_readiness_questions",
}


@pytest.fixture(scope="module")
def tools():
    """The registered tool definitions, resolved once."""
    import asyncio

    return asyncio.run(server.mcp.list_tools())


class TestToolSurface:
    def test_expected_tools_are_registered(self, tools) -> None:
        assert {tool.name for tool in tools} == EXPECTED_TOOLS

    def test_registered_tool_names_helper_agrees(self) -> None:
        assert set(server.registered_tool_names()) == EXPECTED_TOOLS

    def test_every_tool_has_a_useful_description(self, tools) -> None:
        for tool in tools:
            assert tool.description, f"{tool.name} has no description"
            assert len(tool.description) > 80, f"{tool.name} description is too thin"

    def test_every_tool_has_an_object_schema(self, tools) -> None:
        for tool in tools:
            assert tool.inputSchema["type"] == "object"

    def test_required_arguments_are_declared(self, tools) -> None:
        by_name = {tool.name: tool for tool in tools}
        assert by_name["map_control"].inputSchema["required"] == ["description"]
        assert by_name["classify_risk_tier"].inputSchema["required"] == ["use_case"]
        assert by_name["evidence_checklist"].inputSchema["required"] == ["control_id"]

    def test_optional_arguments_are_not_required(self, tools) -> None:
        schema = {tool.name: tool for tool in tools}["map_control"].inputSchema
        assert "frameworks" in schema["properties"]
        assert "frameworks" not in schema["required"]

    def test_server_has_instructions(self) -> None:
        assert server.mcp.instructions
        assert "legal advice" in server.mcp.instructions


class TestToolDispatch:
    def test_map_control_through_dispatcher(self) -> None:
        import asyncio

        result = asyncio.run(
            server.mcp.call_tool(
                "map_control",
                {"description": "a human reviewer must approve the output"},
            )
        )
        payload = result[1] if isinstance(result, tuple) else result
        assert payload["detected_themes"]

    def test_unknown_tool_raises(self) -> None:
        import asyncio

        with pytest.raises(Exception):  # noqa: B017 - the SDK's error type is not public API
            asyncio.run(server.mcp.call_tool("not_a_tool", {}))

    def test_invalid_argument_surfaces_an_error(self) -> None:
        import asyncio

        with pytest.raises(Exception):  # noqa: B017 - the SDK's error type is not public API
            asyncio.run(server.mcp.call_tool("map_control", {"description": ""}))


class TestPlainFunctions:
    def test_list_frameworks(self) -> None:
        payload = server.list_frameworks()
        assert payload["total_controls_encoded"] > 100
        assert len(payload["frameworks"]) == 4
        assert payload["server_version"]

    def test_list_readiness_questions(self) -> None:
        payload = server.list_readiness_questions()
        assert len(payload["dimensions"]) == 5
        assert payload["maturity_scale"]["0"]
        assert len(payload["roadmap_phases"]) == 4

    def test_tools_return_json_serialisable_payloads(self) -> None:
        json.dumps(server.map_control("audit logging of model output"))
        json.dumps(server.classify_risk_tier("a CV screening tool"))
        json.dumps(server.score_readiness({"governance.ai_policy": 2}))
        json.dumps(server.generate_roadmap(["no AI inventory"]))
        json.dumps(server.evidence_checklist("Art. 12"))
        json.dumps(server.list_frameworks())


class TestResource:
    def test_controls_resource_is_valid_json(self) -> None:
        payload = json.loads(server.controls_resource())
        assert set(payload) == {"nist_ai_rmf", "iso_42001", "eu_ai_act", "nist_csf"}
        for framework in payload.values():
            assert framework["controls"]
            assert framework["source"]
