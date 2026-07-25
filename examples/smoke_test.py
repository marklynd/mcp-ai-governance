#!/usr/bin/env python3
"""Import the server, list its tools, and exercise one call per tool.

Runs without a client and without a transport, so it is the fastest way to
confirm an install is working::

    python examples/smoke_test.py

Exits non-zero if any tool fails to import, register or execute.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from mcp_ai_governance import __version__, server  # noqa: E402


def _preview(payload: Any, limit: int = 220) -> str:
    """Return a truncated one-line JSON preview of ``payload``."""
    text = json.dumps(payload, separators=(",", ":"))
    return text if len(text) <= limit else text[:limit] + "..."


CALLS: dict[str, Callable[[], Any]] = {
    "map_control": lambda: server.map_control(
        "A named reviewer must approve every AI-drafted customer email before it "
        "is sent, and can reject it."
    ),
    "classify_risk_tier": lambda: server.classify_risk_tier(
        "A model that ranks job applicants and produces a shortlist for recruiters."
    ),
    "score_readiness": lambda: server.score_readiness(
        {
            "governance": {"ai_policy": 1, "system_inventory": 0, "oversight_gates": 2},
            "data": {"data_quality": 2, "lineage_provenance": 1},
        }
    ),
    "generate_roadmap": lambda: server.generate_roadmap(
        [
            {"id": "g1", "description": "No AI system inventory exists.", "severity": "critical"},
            {"id": "g2", "description": "No production monitoring for model drift.", "severity": "high"},
        ]
    ),
    "evidence_checklist": lambda: server.evidence_checklist("Art. 14"),
    "list_frameworks": server.list_frameworks,
    "list_readiness_questions": server.list_readiness_questions,
}


def main() -> int:
    """Run the smoke test. Returns a process exit code."""
    print(f"mcp-ai-governance {__version__}")
    print(f"server name: {server.mcp.name}")
    print()

    registered = list(server.registered_tool_names())
    print(f"Registered tools ({len(registered)}):")
    for name in registered:
        print(f"  - {name}")
    print()

    missing = set(registered) - set(CALLS)
    if missing:
        print(f"FAIL: no smoke call defined for: {', '.join(sorted(missing))}")
        return 1

    failures = 0
    for name in registered:
        try:
            result = CALLS[name]()
        except Exception as exc:  # noqa: BLE001 - the point is to report anything
            print(f"  FAIL {name}: {type(exc).__name__}: {exc}")
            failures += 1
            continue
        print(f"  OK   {name}: {_preview(result)}")

    print()
    if failures:
        print(f"{failures} tool(s) failed.")
        return 1
    print(f"All {len(registered)} tools imported, registered and executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
