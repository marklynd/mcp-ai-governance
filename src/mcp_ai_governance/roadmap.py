"""Turn a gap list into a sequenced remediation roadmap.

Sequencing is driven by two things rather than severity alone, because severity
alone produces roadmaps that cannot be executed:

* **Severity** sets the baseline urgency.
* **Prerequisite themes** pull work earlier regardless of severity. You cannot
  run a risk assessment on an inventory you do not have, and you cannot enforce
  a policy that does not exist. Inventory, policy and accountability work is
  therefore promoted into the earliest phase it is eligible for, and dependent
  work is annotated with what it waits on.

Owners are **role names**, not people. Effort is a rough person-week band
derived from the theme and severity, intended for sizing a plan, not for
costing a statement of work.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final

from .mapping import detect_themes

MAX_GAPS: Final[int] = 60
MAX_GAP_CHARS: Final[int] = 600

SEVERITIES: Final[tuple[str, ...]] = ("critical", "high", "medium", "low")
_SEVERITY_RANK: Final[dict[str, int]] = {name: i for i, name in enumerate(SEVERITIES)}


@dataclass(frozen=True)
class Phase:
    """One phase of the roadmap.

    Attributes:
        key: Stable identifier.
        name: Display name.
        window: Calendar window relative to programme start.
        intent: What this phase is for, in one sentence.
    """

    key: str
    name: str
    window: str
    intent: str


PHASES: Final[tuple[Phase, ...]] = (
    Phase(
        "phase_1",
        "Stabilise",
        "Days 0-30",
        "Stop the bleeding and establish the minimum you need to make any other decision.",
    ),
    Phase(
        "phase_2",
        "Establish",
        "Days 31-90",
        "Stand up the core controls an auditor or regulator will ask for first.",
    ),
    Phase(
        "phase_3",
        "Operationalise",
        "Days 91-180",
        "Move controls from documented to routinely executed and evidenced.",
    ),
    Phase(
        "phase_4",
        "Optimise",
        "Days 181-365",
        "Measure control effectiveness and improve on a cycle.",
    ),
)

_PHASE_INDEX: Final[dict[str, Phase]] = {phase.key: phase for phase in PHASES}

_SEVERITY_TO_PHASE: Final[dict[str, str]] = {
    "critical": "phase_1",
    "high": "phase_2",
    "medium": "phase_3",
    "low": "phase_4",
}

#: Themes that other work depends on. Gaps in these themes are promoted one
#: phase earlier so the dependent work has something to build on.
PREREQUISITE_THEMES: Final[frozenset[str]] = frozenset(
    {"inventory", "policy", "accountability", "purpose_scope"}
)

#: Themes that only make sense once the prerequisites exist. Annotated with a
#: dependency note rather than delayed, so the plan stays honest about ordering.
DEPENDENT_THEMES: Final[frozenset[str]] = frozenset(
    {"conformity", "monitoring", "testing_evaluation", "impact_assessment"}
)

#: Accountable role for each theme. Role names, deliberately not people.
THEME_OWNERS: Final[dict[str, str]] = {
    "accountability": "Head of AI Governance",
    "policy": "Head of AI Governance",
    "inventory": "AI Programme Manager",
    "risk_assessment": "AI Risk Lead",
    "impact_assessment": "AI Risk Lead",
    "data_governance": "Chief Data Officer",
    "privacy": "Data Protection Officer",
    "bias_fairness": "Model Evaluation Lead",
    "transparency": "Product Owner",
    "documentation": "AI Programme Manager",
    "human_oversight": "Business Process Owner",
    "testing_evaluation": "Model Evaluation Lead",
    "monitoring": "MLOps Lead",
    "logging": "Platform Engineering Lead",
    "security": "CISO",
    "resilience": "Platform Engineering Lead",
    "incident_response": "Incident Response Manager",
    "third_party": "Vendor Risk Manager",
    "training_awareness": "Learning and Development Lead",
    "lifecycle": "Engineering Lead",
    "feedback": "Customer Experience Lead",
    "conformity": "Internal Audit Lead",
    "purpose_scope": "Product Owner",
}

DEFAULT_OWNER: Final[str] = "Head of AI Governance"

#: Baseline effort in person-weeks for a medium-severity gap in each theme.
THEME_BASE_EFFORT: Final[dict[str, float]] = {
    "accountability": 2.0,
    "policy": 3.0,
    "inventory": 4.0,
    "risk_assessment": 4.0,
    "impact_assessment": 3.0,
    "data_governance": 8.0,
    "privacy": 5.0,
    "bias_fairness": 5.0,
    "transparency": 3.0,
    "documentation": 3.0,
    "human_oversight": 4.0,
    "testing_evaluation": 8.0,
    "monitoring": 6.0,
    "logging": 5.0,
    "security": 6.0,
    "resilience": 5.0,
    "incident_response": 3.0,
    "third_party": 4.0,
    "training_awareness": 3.0,
    "lifecycle": 5.0,
    "feedback": 3.0,
    "conformity": 4.0,
    "purpose_scope": 2.0,
}

DEFAULT_BASE_EFFORT: Final[float] = 4.0

_SEVERITY_EFFORT_MULTIPLIER: Final[dict[str, float]] = {
    "critical": 1.4,
    "high": 1.2,
    "medium": 1.0,
    "low": 0.7,
}


@dataclass(frozen=True)
class RoadmapItem:
    """One remediation action derived from a gap."""

    gap_id: str
    description: str
    phase: str
    severity: str
    owner_role: str
    supporting_roles: tuple[str, ...]
    effort_person_weeks: float
    effort_band: str
    themes: tuple[str, ...]
    depends_on: tuple[str, ...]
    first_deliverable: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "gap_id": self.gap_id,
            "action": self.description,
            "phase": self.phase,
            "severity": self.severity,
            "owner_role": self.owner_role,
            "supporting_roles": list(self.supporting_roles),
            "effort_person_weeks": self.effort_person_weeks,
            "effort_band": self.effort_band,
            "themes": list(self.themes),
            "depends_on": list(self.depends_on),
            "first_deliverable": self.first_deliverable,
        }


@dataclass(frozen=True)
class Roadmap:
    """The complete result of a ``generate_roadmap`` call."""

    items: tuple[RoadmapItem, ...]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation grouped by phase."""
        phases: list[dict[str, Any]] = []
        for phase in PHASES:
            in_phase = [item for item in self.items if item.phase == phase.key]
            if not in_phase:
                continue
            phases.append(
                {
                    "phase": phase.key,
                    "name": phase.name,
                    "window": phase.window,
                    "intent": phase.intent,
                    "item_count": len(in_phase),
                    "effort_person_weeks": round(
                        sum(item.effort_person_weeks for item in in_phase), 1
                    ),
                    "owner_roles": sorted({item.owner_role for item in in_phase}),
                    "items": [item.to_dict() for item in in_phase],
                }
            )
        return {
            "phases": phases,
            "total_items": len(self.items),
            "total_effort_person_weeks": round(
                sum(item.effort_person_weeks for item in self.items), 1
            ),
            "owner_summary": _owner_summary(self.items),
            "notes": list(self.notes),
        }


def _owner_summary(items: Sequence[RoadmapItem]) -> list[dict[str, Any]]:
    """Return per-owner totals so a reader can spot an overloaded role."""
    totals: dict[str, dict[str, Any]] = {}
    for item in items:
        entry = totals.setdefault(
            item.owner_role, {"owner_role": item.owner_role, "items": 0, "effort_person_weeks": 0.0}
        )
        entry["items"] += 1
        entry["effort_person_weeks"] = round(
            entry["effort_person_weeks"] + item.effort_person_weeks, 1
        )
    return sorted(
        totals.values(),
        key=lambda entry: (-entry["effort_person_weeks"], entry["owner_role"]),
    )


def _effort_band(person_weeks: float) -> str:
    if person_weeks <= 3.0:
        return "S"
    if person_weeks <= 7.0:
        return "M"
    if person_weeks <= 14.0:
        return "L"
    return "XL"


def _shift_phase(phase_key: str, steps: int) -> str:
    """Return the phase ``steps`` positions earlier, clamped to the first phase."""
    order = [phase.key for phase in PHASES]
    index = max(0, order.index(phase_key) - steps)
    return order[index]


def _normalise_gap(raw: Any, position: int) -> dict[str, Any]:
    """Coerce one gap entry into a validated dictionary."""
    if isinstance(raw, str):
        gap: dict[str, Any] = {"description": raw}
    elif isinstance(raw, Mapping):
        gap = dict(raw)
    else:
        raise ValueError(
            f"Gap at position {position} must be a string or an object, "
            f"received {type(raw).__name__}"
        )

    description = gap.get("description") or gap.get("title") or gap.get("gap")
    if not isinstance(description, str) or not description.strip():
        raise ValueError(
            f"Gap at position {position} needs a non-empty 'description' "
            "(or 'title') field"
        )
    description = description.strip()
    if len(description) > MAX_GAP_CHARS:
        raise ValueError(
            f"Gap at position {position} description must be at most "
            f"{MAX_GAP_CHARS} characters (received {len(description)})"
        )

    severity = str(gap.get("severity", "medium")).strip().lower()
    if severity not in _SEVERITY_RANK:
        raise ValueError(
            f"Gap at position {position} has severity {severity!r}; "
            f"valid values are {', '.join(SEVERITIES)}"
        )

    gap_id = gap.get("id") or gap.get("gap_id") or f"gap-{position + 1}"
    return {
        "id": str(gap_id),
        "description": description,
        "severity": severity,
        "dimension": gap.get("dimension"),
    }


def _first_deliverable(themes: Sequence[str], description: str) -> str:
    """Return a concrete first artefact for the owner to produce."""
    templates = {
        "inventory": "A populated inventory record for every AI system currently in use, with a named owner per row.",
        "policy": "A one-page approved policy statement with scope, prohibited uses and an escalation route.",
        "accountability": "A RACI covering build, run, approve and audit for AI systems.",
        "risk_assessment": "A completed risk assessment for the two highest-exposure systems, using a repeatable template.",
        "impact_assessment": "A completed impact assessment for one system, with affected groups named.",
        "data_governance": "A data lineage diagram and quality thresholds for one production pipeline.",
        "privacy": "A record of processing and lawful basis for the personal data used by one system.",
        "bias_fairness": "A subgroup performance report for one production model.",
        "human_oversight": "A written oversight procedure naming who reviews what, with a recorded decision per review.",
        "testing_evaluation": "An automated evaluation suite that runs in CI and blocks release on regression.",
        "monitoring": "A production dashboard with alert thresholds and a named on-call owner.",
        "logging": "An append-only log of model inputs, outputs and decisions with a stated retention period.",
        "security": "A threat model for one AI system covering prompt injection, data exfiltration and model abuse.",
        "incident_response": "An AI incident runbook, exercised once end to end.",
        "third_party": "A completed vendor assessment for the largest AI supplier, including exit provisions.",
        "training_awareness": "A role-based AI literacy curriculum with completion tracking.",
        "transparency": "User-facing disclosure copy and a model or system card for one deployed system.",
        "documentation": "Technical documentation for one system, structured to survive an external request.",
        "lifecycle": "A documented promotion path from development to production with named gates.",
        "conformity": "An internal audit plan with scope, cadence and evidence requests.",
        "feedback": "A working channel for users to report and appeal AI outcomes, with response targets.",
        "resilience": "A tested fallback path for when the model is unavailable or degraded.",
        "purpose_scope": "A written intended-use statement including out-of-scope uses.",
    }
    for theme in themes:
        if theme in templates:
            return templates[theme]
    return (
        "A one-page written definition of the practice, its owner and how it "
        f"will be evidenced, covering: {description}"
    )


def generate_roadmap(gaps: Iterable[Any]) -> Roadmap:
    """Sequence a list of gaps into a phased remediation roadmap.

    Args:
        gaps: Gap entries. Each may be a plain string, or an object with
            ``description`` (or ``title``), and optionally ``id``, ``severity``
            (``critical``, ``high``, ``medium`` or ``low``) and ``dimension``.
            The ``gaps`` field of a ``score_readiness`` result can be passed
            through unchanged.

    Returns:
        A :class:`Roadmap`.

    Raises:
        TypeError: If ``gaps`` is not a sequence of gap entries.
        ValueError: If the list is empty, too long, or an entry is malformed.
    """
    if isinstance(gaps, (str, bytes, Mapping)):
        raise TypeError(
            "gaps must be a list of gap entries, not a single string or object"
        )
    try:
        raw_gaps = list(gaps)
    except TypeError as exc:  # pragma: no cover - defensive
        raise TypeError("gaps must be an iterable of gap entries") from exc

    if not raw_gaps:
        raise ValueError("gaps must contain at least one entry")
    if len(raw_gaps) > MAX_GAPS:
        raise ValueError(
            f"gaps must contain at most {MAX_GAPS} entries (received {len(raw_gaps)})"
        )

    normalised = [_normalise_gap(raw, index) for index, raw in enumerate(raw_gaps)]

    seen_ids: set[str] = set()
    for gap in normalised:
        if gap["id"] in seen_ids:
            raise ValueError(f"Duplicate gap id {gap['id']!r}")
        seen_ids.add(gap["id"])

    # First pass: theme detection and base phase assignment.
    staged: list[dict[str, Any]] = []
    for gap in normalised:
        themes = tuple(theme.theme_id for theme in detect_themes(gap["description"]))
        phase = _SEVERITY_TO_PHASE[gap["severity"]]
        if any(theme in PREREQUISITE_THEMES for theme in themes):
            phase = _shift_phase(phase, 1)
        staged.append({**gap, "themes": themes, "phase": phase})

    # Second pass: dependency annotation. Dependent work points at the
    # prerequisite gaps that must land first.
    prerequisite_ids = tuple(
        entry["id"]
        for entry in staged
        if any(theme in PREREQUISITE_THEMES for theme in entry["themes"])
    )

    items: list[RoadmapItem] = []
    for entry in staged:
        themes = entry["themes"]
        owner = next(
            (THEME_OWNERS[theme] for theme in themes if theme in THEME_OWNERS),
            DEFAULT_OWNER,
        )
        supporting = tuple(
            dict.fromkeys(
                THEME_OWNERS[theme]
                for theme in themes
                if theme in THEME_OWNERS and THEME_OWNERS[theme] != owner
            )
        )[:2]
        base = next(
            (THEME_BASE_EFFORT[theme] for theme in themes if theme in THEME_BASE_EFFORT),
            DEFAULT_BASE_EFFORT,
        )
        effort = round(base * _SEVERITY_EFFORT_MULTIPLIER[entry["severity"]], 1)
        depends_on = (
            tuple(gap_id for gap_id in prerequisite_ids if gap_id != entry["id"])
            if any(theme in DEPENDENT_THEMES for theme in themes)
            else ()
        )
        items.append(
            RoadmapItem(
                gap_id=entry["id"],
                description=entry["description"],
                phase=entry["phase"],
                severity=entry["severity"],
                owner_role=owner,
                supporting_roles=supporting,
                effort_person_weeks=effort,
                effort_band=_effort_band(effort),
                themes=themes,
                depends_on=depends_on,
                first_deliverable=_first_deliverable(themes, entry["description"]),
            )
        )

    order = {phase.key: index for index, phase in enumerate(PHASES)}
    items.sort(
        key=lambda item: (
            order[item.phase],
            _SEVERITY_RANK[item.severity],
            -item.effort_person_weeks,
            item.gap_id,
        )
    )

    notes: list[str] = []
    untyped = [item.gap_id for item in items if not item.themes]
    if untyped:
        notes.append(
            "No governance theme could be detected for these gaps, so ownership "
            f"defaulted to {DEFAULT_OWNER} and effort to a generic baseline: "
            + ", ".join(untyped)
            + ". Rewriting them to describe the practice rather than the "
            "system name will produce a better assignment."
        )
    if prerequisite_ids:
        notes.append(
            "Inventory, policy, accountability and scope gaps were promoted one "
            "phase earlier because dependent work cannot be evidenced without "
            "them."
        )
    notes.append(
        "Effort figures are person-week planning bands derived from the gap "
        "theme and severity. They are for sizing a plan, not for costing a "
        "statement of work."
    )

    return Roadmap(items=tuple(items), notes=tuple(notes))


def phase_reference() -> list[dict[str, str]]:
    """Return the phase definitions, for callers rendering a plan template."""
    return [
        {
            "phase": phase.key,
            "name": phase.name,
            "window": phase.window,
            "intent": phase.intent,
        }
        for phase in PHASES
    ]


def phase_by_key(key: str) -> Phase:
    """Return the phase with ``key``.

    Raises:
        KeyError: If no such phase exists.
    """
    return _PHASE_INDEX[key]
