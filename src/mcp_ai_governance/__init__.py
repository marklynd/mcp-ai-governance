"""AI governance and compliance mapping exposed as MCP tools.

The public Python API mirrors the MCP tool surface, so the logic can be reused
directly (in a notebook, a batch job or a test) without going through a client.
"""

from __future__ import annotations

__version__ = "0.1.0"

from .evidence import EvidenceChecklist, evidence_checklist
from .mapping import MappingResult, map_control
from .readiness import ReadinessResult, question_catalogue, score_readiness
from .risk import RiskClassification, classify_risk_tier
from .roadmap import Roadmap, generate_roadmap

__all__ = [
    "EvidenceChecklist",
    "MappingResult",
    "ReadinessResult",
    "RiskClassification",
    "Roadmap",
    "__version__",
    "classify_risk_tier",
    "evidence_checklist",
    "generate_roadmap",
    "map_control",
    "question_catalogue",
    "score_readiness",
]
