"""MCP server exposing AI governance and compliance mapping as tools.

Run over stdio::

    python -m mcp_ai_governance

or::

    mcp-ai-governance

Every tool is pure and deterministic. There is no network access, no API key
and no persistent state, so the server can be pointed at a client and used
immediately.

Error handling convention: tools validate their inputs and raise ``ValueError``
or ``TypeError`` with a message that names the offending argument and the valid
range. FastMCP surfaces those as MCP tool errors, which is what a calling model
needs in order to retry correctly.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import __version__
from .evidence import evidence_checklist as _evidence_checklist
from .knowledge import (
    ALL_FRAMEWORK_KEYS,
    FRAMEWORKS,
    control_ids,
    coverage_summary,
)
from .mapping import DEFAULT_MIN_CONFIDENCE, DEFAULT_TOP_K
from .mapping import map_control as _map_control
from .readiness import question_catalogue
from .readiness import score_readiness as _score_readiness
from .risk import classify_risk_tier as _classify_risk_tier
from .roadmap import generate_roadmap as _generate_roadmap
from .roadmap import phase_reference

INSTRUCTIONS = """\
AI governance tooling over an encoded subset of the NIST AI Risk Management
Framework 1.0, ISO/IEC 42001:2023, the EU AI Act (Regulation (EU) 2024/1689)
and NIST CSF 2.0.

Use map_control to place a described practice against framework controls,
classify_risk_tier to triage a use case against the EU AI Act, score_readiness
to assess an organisation, generate_roadmap to sequence the resulting gaps, and
evidence_checklist to prepare for an audit of a specific control.

The tools compose: the 'gaps' array returned by score_readiness can be passed
straight into generate_roadmap, and any control_id returned by map_control can
be passed straight into evidence_checklist.

All output is decision support for a qualified reviewer.
It is not legal advice and it is not a compliance determination.
"""

mcp: FastMCP = FastMCP(
    "ai-governance",
    instructions=INSTRUCTIONS,
)


@mcp.tool()
def map_control(
    description: str,
    frameworks: list[str] | None = None,
    top_k: int = DEFAULT_TOP_K,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
) -> dict[str, Any]:
    """Map a control or practice description onto governance framework controls.

    Give it a description of what a control actually does and it returns the
    NIST AI RMF subcategories, ISO/IEC 42001 clauses and EU AI Act articles a
    reviewer would expect to see cited, each with a confidence score and the
    specific phrases that drove the match.

    Describe behaviour rather than naming a tool. "A reviewer approves every
    AI-drafted customer email before it is sent, and can reject it" maps well;
    "we use the approvals service" does not.

    Args:
        description: Free-text description of the control, practice or
            capability. 1 to 4000 characters.
        frameworks: Framework keys to map against. Defaults to
            ["nist_ai_rmf", "iso_42001", "eu_ai_act"]. Valid keys are
            "nist_ai_rmf", "iso_42001", "eu_ai_act" and "nist_csf".
        top_k: Maximum matches per framework, 1 to 10. Defaults to 3.
        min_confidence: Drop matches below this confidence, 0.0 to 1.0.
            Defaults to 0.3.

    Returns:
        The detected governance themes, per-framework mappings with confidence,
        matched signals and rationale, plus any notes about weak coverage.

    Raises:
        ValueError: If the description is empty or too long, a framework key is
            unknown, or a numeric argument is out of range.
    """
    return _map_control(
        description=description,
        frameworks=frameworks,
        top_k=top_k,
        min_confidence=min_confidence,
    ).to_dict()


@mcp.tool()
def score_readiness(answers: dict[str, Any]) -> dict[str, Any]:
    """Score an organisation's AI readiness across five weighted dimensions.

    The dimensions are strategy, data, platform, talent and governance. Each has
    five questions answered on a 0 to 4 maturity scale, where 0 is absent,
    2 is a repeatable but undocumented practice, and 4 is measured and audited.

    Dimensions you do not answer are excluded from the overall score and
    reported, rather than being silently scored as zero.

    Args:
        answers: Maturity levels keyed by question. Accepts nested form
            ({"governance": {"ai_policy": 3}}) or dotted form
            ({"governance.ai_policy": 3}), and the two may be mixed. Call
            list_readiness_questions for the full key list.

    Returns:
        Overall score and tier, per-dimension scores with coverage, the two
        weakest dimensions, and a gaps array that can be passed directly into
        generate_roadmap.

    Raises:
        ValueError: If answers is empty, contains an unknown key, or contains a
            value outside the 0 to 4 scale.
    """
    return _score_readiness(answers).to_dict()


@mcp.tool()
def classify_risk_tier(use_case: str) -> dict[str, Any]:
    """Classify an AI use case against the EU AI Act risk tiers.

    Returns one of prohibited, high-risk, limited-risk or minimal-risk, with the
    specific Art. 5 practice, Annex III area or Art. 50 trigger that fired, the
    obligations that follow, the penalty band and the relevant application dates.

    The classification is conservative: it reports the highest tier any rule
    triggers and lists every rule that fired, so a reviewer can dispute an
    individual trigger without discarding the result.

    Describe who the system affects and what decision it influences. "A model
    that ranks job applicants and produces a shortlist for recruiters" gets a
    correct answer; "an HR tool" does not.

    Args:
        use_case: Plain-language description of the system, its users, the
            decision it influences and the setting. 1 to 4000 characters.

    Returns:
        Tier, confidence, reasoning, triggered criteria with citations,
        obligations, penalty exposure, key dates and caveats.

    Raises:
        ValueError: If the use case is empty or longer than 4000 characters.
    """
    return _classify_risk_tier(use_case).to_dict()


@mcp.tool()
def generate_roadmap(gaps: list[Any]) -> dict[str, Any]:
    """Sequence a list of governance gaps into a phased remediation roadmap.

    Produces four phases (0-30, 31-90, 91-180 and 181-365 days) with an
    accountable role, a supporting role, a person-week effort band and a
    concrete first deliverable per item. Inventory, policy, accountability and
    scope gaps are promoted earlier because dependent work cannot be evidenced
    without them.

    Args:
        gaps: Gap entries. Each may be a plain string, or an object with
            "description" (or "title") and optionally "id", "severity"
            (critical, high, medium or low) and "dimension". The gaps array
            returned by score_readiness can be passed through unchanged.
            1 to 60 entries.

    Returns:
        Phases with their items, total and per-phase effort, and a per-owner
        summary that makes an overloaded role visible.

    Raises:
        ValueError: If the list is empty, longer than 60 entries, contains a
            malformed entry, an unknown severity or a duplicate id.
    """
    return _generate_roadmap(gaps).to_dict()


@mcp.tool()
def evidence_checklist(control_id: str) -> dict[str, Any]:
    """List the evidence an auditor would request for a specific control.

    Evidence is split by kind - documents, records produced by the control
    operating, system artefacts and interviews - because the usual audit failure
    is having every document and no records.

    Args:
        control_id: A control identifier from any encoded framework, for example
            "GOVERN 1.6", "A.6.2.8", "Art. 14" or "MEASURE 2.11". Matching
            tolerates case and punctuation.

    Returns:
        The control detail, the evidence list with the reason each item is
        requested, likely auditor questions, common failure modes for this kind
        of control, and sampling guidance.

    Raises:
        ValueError: If the control id is empty or does not match an encoded
            control.
    """
    return _evidence_checklist(control_id).to_dict()


@mcp.tool()
def list_frameworks() -> dict[str, Any]:
    """Describe the encoded frameworks and how much of each is covered.

    Call this before relying on a negative result. A framework returning no
    match may mean the practice is genuinely out of its scope, or that the
    encoded subset does not reach it, and this tool tells you which.

    Returns:
        Per-framework name, version, source citation, number of encoded controls
        and an honest coverage statement.
    """
    return {
        "frameworks": coverage_summary(),
        "framework_keys": list(ALL_FRAMEWORK_KEYS),
        "total_controls_encoded": len(control_ids()),
        "server_version": __version__,
    }


@mcp.tool()
def list_readiness_questions() -> dict[str, Any]:
    """Return the readiness question bank and the maturity scale.

    Use this to render an assessment, or to build a valid answers object for
    score_readiness.

    Returns:
        The five dimensions with their weights and questions, and the meaning of
        each point on the 0 to 4 maturity scale.
    """
    from .readiness import MATURITY_SCALE

    return {
        "dimensions": question_catalogue(),
        "maturity_scale": {str(k): v for k, v in MATURITY_SCALE.items()},
        "roadmap_phases": phase_reference(),
    }


@mcp.resource("governance://controls")
def controls_resource() -> str:
    """Every encoded control across all four frameworks, as JSON."""
    payload = {
        framework.key: {
            "name": framework.name,
            "version": framework.version,
            "source": framework.source,
            "coverage": framework.coverage,
            "controls": [
                {
                    "id": control.id,
                    "title": control.title,
                    "group": control.group,
                    "themes": list(control.themes),
                    "citation": control.citation,
                }
                for control in framework.controls
            ],
        }
        for framework in FRAMEWORKS.values()
    }
    return json.dumps(payload, indent=2)


def registered_tool_names() -> Sequence[str]:
    """Return the names of the tools registered on this server.

    Exposed for the smoke test and for anyone who wants to assert the tool
    surface in CI without starting a transport.
    """
    import asyncio

    async def _collect() -> list[str]:
        return [tool.name for tool in await mcp.list_tools()]

    return asyncio.run(_collect())


def main() -> None:
    """Run the server over stdio. Entry point for the console script."""
    mcp.run()


if __name__ == "__main__":  # pragma: no cover - process entry point
    main()
