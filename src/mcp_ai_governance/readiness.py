"""Five-dimension enterprise AI readiness scoring.

The model is a weighted maturity assessment: 25 questions across five
dimensions, each answered on a 0 to 4 maturity scale. Dimension scores are the
mean of the answered questions rescaled to 0-100; the overall score is the
weighted mean of the dimensions that were actually assessed.

Two design decisions are worth calling out because they are the ones a reviewer
usually probes:

* **Unanswered dimensions are excluded, not zeroed.** Scoring an unassessed
  dimension as zero silently converts "we did not ask" into "they have
  nothing", which is the most common way readiness scores mislead. Weights are
  renormalised over the assessed dimensions and the omission is reported.
* **Weights are explicit and visible in the output.** Governance and data carry
  the most weight because they are the dimensions that most often block a
  deployment from reaching production, and the caller should be able to argue
  with that choice rather than discover it.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final

MIN_LEVEL: Final[int] = 0
MAX_LEVEL: Final[int] = 4

#: Human-readable meaning of each point on the maturity scale.
MATURITY_SCALE: Final[dict[int, str]] = {
    0: "Absent - not done at all",
    1: "Ad hoc - happens sometimes, depends on individuals",
    2: "Repeatable - a consistent practice exists but is not documented or enforced",
    3: "Defined - documented, owned and applied consistently",
    4: "Optimised - measured, audited and improved on a cycle",
}


@dataclass(frozen=True)
class Question:
    """One assessment question.

    Attributes:
        key: Identifier, unique within its dimension.
        prompt: The statement the respondent rates from 0 to 4.
        weight: Relative weight within the dimension.
    """

    key: str
    prompt: str
    weight: float = 1.0


@dataclass(frozen=True)
class Dimension:
    """One of the five readiness dimensions.

    Attributes:
        key: Identifier used in the answers mapping.
        label: Display name.
        weight: Share of the overall score, before renormalisation.
        questions: The questions that make up the dimension.
    """

    key: str
    label: str
    weight: float
    questions: tuple[Question, ...]


DIMENSIONS: Final[tuple[Dimension, ...]] = (
    Dimension(
        key="strategy",
        label="Strategy",
        weight=0.18,
        questions=(
            Question(
                "executive_sponsorship",
                "A named executive owns the AI agenda and is accountable for its outcomes.",
                1.2,
            ),
            Question(
                "use_case_portfolio",
                "AI use cases are prioritised against business value in a maintained pipeline.",
            ),
            Question(
                "funding_model",
                "AI work has a durable funding line rather than one-off project budgets.",
                0.8,
            ),
            Question(
                "value_measurement",
                "Realised business value of deployed AI is measured after go-live, not just projected.",
                1.1,
            ),
            Question(
                "operating_model",
                "A defined operating model states who builds, who runs and who approves AI systems.",
            ),
        ),
    ),
    Dimension(
        key="data",
        label="Data",
        weight=0.22,
        questions=(
            Question(
                "data_inventory",
                "The data assets available for AI are catalogued with owners.",
            ),
            Question(
                "data_quality",
                "Data quality is measured against defined thresholds before data reaches a model.",
                1.2,
            ),
            Question(
                "access_control",
                "Data is classified and access is granted on least privilege.",
                1.1,
            ),
            Question(
                "lineage_provenance",
                "Lineage and provenance are recorded end to end for data used in training and retrieval.",
                1.1,
            ),
            Question(
                "privacy_controls",
                "Personal data used by AI systems has a lawful basis and documented privacy controls.",
                1.2,
            ),
        ),
    ),
    Dimension(
        key="platform",
        label="Platform",
        weight=0.18,
        questions=(
            Question(
                "environments",
                "Separate, reproducible development, test and production environments exist for AI workloads.",
            ),
            Question(
                "lifecycle_tooling",
                "Models, prompts and agent configurations are versioned in a registry with a promotion path.",
                1.1,
            ),
            Question(
                "observability",
                "Production AI systems emit logs, traces, quality metrics and cost telemetry.",
                1.2,
            ),
            Question(
                "evaluation_harness",
                "A repeatable automated evaluation harness runs before every release.",
                1.3,
            ),
            Question(
                "platform_security",
                "AI-specific security controls exist, covering secrets, tenant isolation and prompt injection.",
                1.2,
            ),
        ),
    ),
    Dimension(
        key="talent",
        label="Talent",
        weight=0.17,
        questions=(
            Question(
                "core_skills",
                "The organisation has enough in-house engineering and data science depth to run its AI systems.",
                1.2,
            ),
            Question(
                "workforce_literacy",
                "Staff who use AI tools have completed role-appropriate AI literacy training.",
                1.1,
            ),
            Question(
                "role_clarity",
                "AI roles and career paths are defined rather than absorbed into existing job descriptions.",
                0.8,
            ),
            Question(
                "partner_strategy",
                "A deliberate build, buy and partner strategy governs where external help is used.",
                0.9,
            ),
            Question(
                "enablement",
                "Internal enablement such as a community of practice or centre of excellence is active.",
                0.8,
            ),
        ),
    ),
    Dimension(
        key="governance",
        label="Governance",
        weight=0.25,
        questions=(
            Question(
                "ai_policy",
                "An approved AI policy defines acceptable and prohibited uses.",
                1.1,
            ),
            Question(
                "risk_process",
                "A documented AI risk and impact assessment runs before a system is approved.",
                1.3,
            ),
            Question(
                "system_inventory",
                "A maintained inventory covers every AI system in use, including third-party and embedded AI.",
                1.2,
            ),
            Question(
                "oversight_gates",
                "Consequential AI actions require a human decision that is recorded.",
                1.3,
            ),
            Question(
                "monitoring_incidents",
                "Deployed AI is monitored and there is a tested process for AI incidents.",
                1.2,
            ),
        ),
    ),
)

_DIMENSION_INDEX: Final[dict[str, Dimension]] = {dim.key: dim for dim in DIMENSIONS}

TIER_BANDS: Final[tuple[tuple[float, str, str], ...]] = (
    (25.0, "Ad hoc", "AI activity is uncontrolled. Treat any production use as unmanaged risk."),
    (45.0, "Developing", "Foundations are being laid but coverage is patchy and person-dependent."),
    (65.0, "Defined", "Practices are documented and applied. Consistency and evidence are the gap."),
    (85.0, "Managed", "Controls are measured and enforced. Focus shifts to efficiency and scale."),
    (101.0, "Optimising", "Controls are audited and improved on a cycle. Suitable for regulated deployment."),
)

#: Answers at or below this level are emitted as gaps.
GAP_THRESHOLD: Final[int] = 2


@dataclass(frozen=True)
class QuestionResult:
    """The scored result for a single question."""

    key: str
    dimension: str
    prompt: str
    level: int
    weight: float

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "key": f"{self.dimension}.{self.key}",
            "prompt": self.prompt,
            "level": self.level,
            "level_meaning": MATURITY_SCALE[self.level],
            "weight": self.weight,
        }


@dataclass(frozen=True)
class DimensionResult:
    """The scored result for one dimension."""

    key: str
    label: str
    weight: float
    score: float | None
    answered: tuple[QuestionResult, ...]
    unanswered: tuple[str, ...]

    @property
    def assessed(self) -> bool:
        """Whether at least one question in this dimension was answered."""
        return self.score is not None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "dimension": self.key,
            "label": self.label,
            "weight": self.weight,
            "score": self.score,
            "assessed": self.assessed,
            "coverage": f"{len(self.answered)}/{len(self.answered) + len(self.unanswered)}",
            "answers": [answer.to_dict() for answer in self.answered],
            "unanswered": list(self.unanswered),
        }


@dataclass(frozen=True)
class ReadinessResult:
    """The complete result of a ``score_readiness`` call."""

    overall_score: float
    tier: str
    tier_description: str
    dimensions: tuple[DimensionResult, ...]
    weakest_dimensions: tuple[str, ...]
    gaps: tuple[dict[str, Any], ...]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "overall_score": self.overall_score,
            "tier": self.tier,
            "tier_description": self.tier_description,
            "dimensions": [dimension.to_dict() for dimension in self.dimensions],
            "weakest_dimensions": list(self.weakest_dimensions),
            "gaps": [dict(gap) for gap in self.gaps],
            "maturity_scale": {str(k): v for k, v in MATURITY_SCALE.items()},
            "notes": list(self.notes),
        }


def question_catalogue() -> list[dict[str, Any]]:
    """Return the full question bank, for callers that want to render a survey."""
    return [
        {
            "dimension": dimension.key,
            "label": dimension.label,
            "weight": dimension.weight,
            "questions": [
                {
                    "key": f"{dimension.key}.{question.key}",
                    "prompt": question.prompt,
                    "weight": question.weight,
                }
                for question in dimension.questions
            ],
        }
        for dimension in DIMENSIONS
    ]


def _valid_keys() -> list[str]:
    return [
        f"{dimension.key}.{question.key}"
        for dimension in DIMENSIONS
        for question in dimension.questions
    ]


def _coerce_level(value: Any, key: str) -> int:
    """Return ``value`` as a validated maturity level."""
    if isinstance(value, bool):
        raise ValueError(
            f"Answer for {key!r} must be an integer 0-4, not a boolean"
        )
    if isinstance(value, float) and not value.is_integer():
        raise ValueError(
            f"Answer for {key!r} must be a whole number 0-4 (received {value})"
        )
    if not isinstance(value, (int, float)):
        raise ValueError(
            f"Answer for {key!r} must be a number 0-4 (received {type(value).__name__})"
        )
    level = int(value)
    if not MIN_LEVEL <= level <= MAX_LEVEL:
        raise ValueError(
            f"Answer for {key!r} must be between {MIN_LEVEL} and {MAX_LEVEL} "
            f"(received {level})"
        )
    return level


def _flatten(answers: Mapping[str, Any]) -> dict[tuple[str, str], int]:
    """Normalise the accepted answer shapes into ``(dimension, question) -> level``.

    Accepted shapes, which may be mixed in one call:

    * nested - ``{"governance": {"ai_policy": 3}}``
    * dotted - ``{"governance.ai_policy": 3}``
    """
    flat: dict[tuple[str, str], int] = {}
    unknown: list[str] = []

    for raw_key, raw_value in answers.items():
        if not isinstance(raw_key, str):
            raise ValueError(f"Answer keys must be strings (received {raw_key!r})")
        if isinstance(raw_value, Mapping):
            dimension = _DIMENSION_INDEX.get(raw_key)
            if dimension is None:
                unknown.append(raw_key)
                continue
            valid = {question.key for question in dimension.questions}
            for question_key, value in raw_value.items():
                if question_key not in valid:
                    unknown.append(f"{raw_key}.{question_key}")
                    continue
                flat[(raw_key, question_key)] = _coerce_level(
                    value, f"{raw_key}.{question_key}"
                )
            continue

        if "." not in raw_key:
            unknown.append(raw_key)
            continue
        dimension_key, _, question_key = raw_key.partition(".")
        dimension = _DIMENSION_INDEX.get(dimension_key)
        if dimension is None or question_key not in {
            question.key for question in dimension.questions
        }:
            unknown.append(raw_key)
            continue
        flat[(dimension_key, question_key)] = _coerce_level(raw_value, raw_key)

    if unknown:
        raise ValueError(
            "Unknown answer key(s): "
            + ", ".join(sorted(unknown))
            + ". Valid keys are: "
            + ", ".join(_valid_keys())
        )
    return flat


def _tier_for(score: float) -> tuple[str, str]:
    for upper, label, description in TIER_BANDS:
        if score < upper:
            return label, description
    return TIER_BANDS[-1][1], TIER_BANDS[-1][2]  # pragma: no cover - unreachable


def _gap_severity(level: int, dimension_weight: float) -> str:
    """Return a severity label for an under-performing answer."""
    if level == 0:
        return "critical" if dimension_weight >= 0.20 else "high"
    if level == 1:
        return "high" if dimension_weight >= 0.20 else "medium"
    return "medium" if dimension_weight >= 0.20 else "low"


def score_readiness(answers: Mapping[str, Any]) -> ReadinessResult:
    """Score an organisation's AI readiness across five dimensions.

    Args:
        answers: Maturity levels from 0 to 4. Keys may be nested
            (``{"data": {"data_quality": 2}}``) or dotted
            (``{"data.data_quality": 2}``); both forms may be mixed.

    Returns:
        A :class:`ReadinessResult` whose ``gaps`` field can be passed straight
        into :func:`mcp_ai_governance.roadmap.generate_roadmap`.

    Raises:
        TypeError: If ``answers`` is not a mapping.
        ValueError: If it is empty, contains unknown keys, or contains a value
            outside the 0 to 4 maturity scale.
    """
    if not isinstance(answers, Mapping):
        raise TypeError(
            "answers must be a mapping of question keys to maturity levels 0-4"
        )
    if not answers:
        raise ValueError(
            "answers must not be empty. Valid keys are: " + ", ".join(_valid_keys())
        )

    flat = _flatten(answers)
    if not flat:
        raise ValueError(
            "No valid answers were supplied. Valid keys are: " + ", ".join(_valid_keys())
        )

    results: list[DimensionResult] = []
    gaps: list[dict[str, Any]] = []

    for dimension in DIMENSIONS:
        answered: list[QuestionResult] = []
        unanswered: list[str] = []
        for question in dimension.questions:
            level = flat.get((dimension.key, question.key))
            if level is None:
                unanswered.append(f"{dimension.key}.{question.key}")
                continue
            answered.append(
                QuestionResult(
                    key=question.key,
                    dimension=dimension.key,
                    prompt=question.prompt,
                    level=level,
                    weight=question.weight,
                )
            )
            if level <= GAP_THRESHOLD:
                gaps.append(
                    {
                        "id": f"{dimension.key}.{question.key}",
                        "dimension": dimension.key,
                        "description": question.prompt,
                        "current_level": level,
                        "severity": _gap_severity(level, dimension.weight),
                    }
                )

        if answered:
            weighted = sum(item.level * item.weight for item in answered)
            total_weight = sum(item.weight for item in answered)
            score: float | None = round(weighted / total_weight / MAX_LEVEL * 100, 1)
        else:
            score = None

        results.append(
            DimensionResult(
                key=dimension.key,
                label=dimension.label,
                weight=dimension.weight,
                score=score,
                answered=tuple(answered),
                unanswered=tuple(unanswered),
            )
        )

    # Pair each assessed dimension with its non-optional score once, so the
    # rest of this function does not have to keep re-proving that an assessed
    # dimension has a score.
    scored: list[tuple[DimensionResult, float]] = [
        (result, result.score) for result in results if result.score is not None
    ]
    weight_total = sum(result.weight for result, _ in scored)
    overall = round(
        sum(score * result.weight for result, score in scored) / weight_total, 1
    )
    tier, tier_description = _tier_for(overall)

    ranked = sorted(scored, key=lambda pair: (pair[1], pair[0].key))
    weakest = tuple(result.key for result, _ in ranked[:2])

    notes: list[str] = []
    unassessed = [result.key for result in results if not result.assessed]
    if unassessed:
        notes.append(
            "Not assessed, and excluded from the overall score rather than "
            f"scored as zero: {', '.join(unassessed)}. Weights were renormalised "
            "over the assessed dimensions."
        )
    partial = [result.key for result, _ in scored if result.unanswered]
    if partial:
        notes.append(
            "Partially answered dimensions, scored on the answered questions "
            f"only: {', '.join(partial)}."
        )

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps.sort(key=lambda gap: (severity_rank[gap["severity"]], gap["id"]))

    return ReadinessResult(
        overall_score=overall,
        tier=tier,
        tier_description=tier_description,
        dimensions=tuple(results),
        weakest_dimensions=weakest,
        gaps=tuple(gaps),
        notes=tuple(notes),
    )


def dimension_keys() -> Sequence[str]:
    """Return the five dimension keys in scoring order."""
    return tuple(dimension.key for dimension in DIMENSIONS)
