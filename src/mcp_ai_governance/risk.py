"""EU AI Act risk-tier classification.

Classifies a described use case into the four practical tiers of Regulation
(EU) 2024/1689:

``prohibited``
    Matches an Art. 5 practice. The correct answer is do not build it.
``high-risk``
    Falls in an Annex III area under Art. 6(2), or is a safety component of a
    product covered by Annex I under Art. 6(1). Triggers the full Art. 9-15
    requirement set plus conformity assessment.
``limited-risk``
    Triggers an Art. 50 transparency obligation but no Annex III area.
``minimal-risk``
    No specific obligation beyond Art. 4 AI literacy and whatever other law
    already applies.

The classifier is deliberately **conservative**: it reports the highest tier
any rule triggers, and it reports every rule that fired rather than only the
winner, so a reviewer can disagree with a specific trigger without discarding
the whole answer.

This is not legal advice. Art. 6(3) allows a system that falls in an Annex III
area to be treated as not high-risk where it performs only a narrow procedural
task or does not materially influence a decision. That derogation depends on
facts a text classifier cannot see, so it is surfaced as a caveat rather than
applied automatically.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from .knowledge.eu_ai_act import (
    ANNEX_III_AREAS,
    APPLICATION_DATES,
    PENALTY_BANDS,
    PROHIBITED_PRACTICES,
    TRANSPARENCY_TRIGGERS,
    PracticeRule,
)
from .text import find_phrases

MAX_USE_CASE_CHARS: Final[int] = 4000

TIER_ORDER: Final[tuple[str, ...]] = (
    "minimal-risk",
    "limited-risk",
    "high-risk",
    "prohibited",
)

TIER_SUMMARY: Final[dict[str, str]] = {
    "prohibited": (
        "The described practice appears to fall under Art. 5. Placing it on the "
        "EU market or putting it into service is banned; prohibitions have "
        "applied since 2 February 2025."
    ),
    "high-risk": (
        "The use case appears to fall in an Annex III area under Art. 6(2). "
        "Art. 9-15 requirements, Art. 17 quality management, Art. 43 conformity "
        "assessment, Art. 49 registration and Art. 72-73 post-market duties apply."
    ),
    "limited-risk": (
        "No Annex III area matched, but Art. 50 transparency obligations appear "
        "to apply. Disclosure and content-marking duties, not the full high-risk "
        "regime."
    ),
    "minimal-risk": (
        "No prohibited practice, Annex III area or Art. 50 trigger matched. "
        "Art. 4 AI literacy still applies, as does all other law such as the GDPR."
    ),
}

#: Obligations to work through once a tier is assigned.
TIER_OBLIGATIONS: Final[dict[str, tuple[str, ...]]] = {
    "prohibited": (
        "Stop the initiative and record the decision. There is no compliance path.",
        "Check whether an adjacent lawful design exists, for example replacing inferred emotion with an explicit user-declared preference.",
        "Confirm the Art. 5 analysis with counsel; several prohibitions have narrow statutory carve-outs.",
    ),
    "high-risk": (
        "Art. 9: establish a continuous risk management system across the lifecycle.",
        "Art. 10: apply data governance to training, validation and testing data.",
        "Art. 11 and Annex IV: draw up technical documentation before market placement.",
        "Art. 12: enable automatic event logging for the life of the system.",
        "Art. 13: provide instructions for use and known limitations to deployers.",
        "Art. 14: design effective human oversight, including a stop function.",
        "Art. 15: demonstrate accuracy, robustness and cybersecurity.",
        "Art. 17: operate a documented quality management system (providers).",
        "Art. 26: deployers use the system per instructions with competent oversight.",
        "Art. 27: check whether a fundamental rights impact assessment is required.",
        "Art. 43, 47, 48, 49: conformity assessment, declaration, CE marking, EU database registration.",
        "Art. 72 and 73: post-market monitoring plan and serious-incident reporting.",
    ),
    "limited-risk": (
        "Art. 50(1): tell people they are interacting with an AI system, unless it is obvious.",
        "Art. 50(2): mark synthetic audio, image, video and text in a machine-readable format.",
        "Art. 50(3): inform people exposed to emotion recognition or biometric categorisation.",
        "Art. 50(4): disclose deep fake content as artificially generated or manipulated.",
        "Art. 4: ensure staff operating the system have sufficient AI literacy.",
    ),
    "minimal-risk": (
        "Art. 4: ensure staff operating the system have sufficient AI literacy.",
        "Re-run this classification whenever the use case expands; scope creep is the usual route from minimal to high risk.",
        "Confirm that no other regime applies, in particular the GDPR, sectoral financial rules or product safety law.",
    ),
}

DISCLAIMER: Final[str] = (
    "Deterministic keyword classification against Art. 5, Annex III and Art. 50 "
    "of Regulation (EU) 2024/1689. It is a triage aid for a qualified reviewer, "
    "not a legal determination. Annex I product-safety high-risk classification "
    "under Art. 6(1) is not detected automatically."
)


@dataclass(frozen=True)
class Trigger:
    """A rule that fired during classification.

    Attributes:
        code: Rule identifier.
        label: What the rule describes.
        citation: The article or annex point.
        matched_phrases: Phrases in the use case that fired the rule.
        confidence: Strength of the evidence, 0 to 0.95.
        caveats: Statutory carve-outs that may defeat the trigger.
    """

    code: str
    label: str
    citation: str
    matched_phrases: tuple[str, ...]
    confidence: float
    caveats: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        payload: dict[str, Any] = {
            "code": self.code,
            "criterion": self.label,
            "citation": self.citation,
            "matched_phrases": list(self.matched_phrases),
            "confidence": self.confidence,
        }
        if self.caveats:
            payload["caveats"] = self.caveats
        return payload


@dataclass(frozen=True)
class RiskClassification:
    """The complete result of a ``classify_risk_tier`` call."""

    use_case: str
    tier: str
    confidence: float
    reasoning: str
    triggers: tuple[Trigger, ...]
    obligations: tuple[str, ...]
    caveats: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "use_case": self.use_case,
            "tier": self.tier,
            "confidence": self.confidence,
            "summary": TIER_SUMMARY[self.tier],
            "reasoning": self.reasoning,
            "triggered_criteria": [trigger.to_dict() for trigger in self.triggers],
            "obligations": list(self.obligations),
            "penalty_exposure": PENALTY_BANDS[self.tier],
            "key_dates": dict(APPLICATION_DATES),
            "caveats": list(self.caveats),
            "regulation": "Regulation (EU) 2024/1689",
            "disclaimer": DISCLAIMER,
        }


def _evaluate(use_case: str, rules: tuple[PracticeRule, ...]) -> list[Trigger]:
    """Return the triggers fired by ``rules`` against ``use_case``."""
    triggers: list[Trigger] = []
    for rule in rules:
        hits = find_phrases(use_case, rule.signals)
        if not hits:
            continue
        # Longer phrases are much less likely to be coincidental, so a single
        # four-word match is treated as stronger than two one-word matches.
        strength = sum(
            1.0 + 0.65 * (hit.word_count - 1) for hit in hits
        )
        confidence = round(min(0.95, 0.42 + 0.16 * strength), 2)
        triggers.append(
            Trigger(
                code=rule.code,
                label=rule.label,
                citation=rule.citation,
                matched_phrases=tuple(hit.phrase for hit in hits),
                confidence=confidence,
                caveats=rule.caveats,
            )
        )
    triggers.sort(key=lambda trigger: (-trigger.confidence, trigger.code))
    return triggers


def classify_risk_tier(use_case: str) -> RiskClassification:
    """Classify an AI use case against the EU AI Act risk tiers.

    Args:
        use_case: Plain-language description of what the system does, to whom,
            and in what setting. More context produces a better classification;
            "a chatbot" is not enough to distinguish limited from high risk.

    Returns:
        A :class:`RiskClassification`.

    Raises:
        TypeError: If ``use_case`` is not a string.
        ValueError: If it is empty or longer than 4000 characters.
    """
    if not isinstance(use_case, str):
        raise TypeError("use_case must be a string")
    cleaned = use_case.strip()
    if not cleaned:
        raise ValueError("use_case must not be empty")
    if len(cleaned) > MAX_USE_CASE_CHARS:
        raise ValueError(
            f"use_case must be at most {MAX_USE_CASE_CHARS} characters "
            f"(received {len(cleaned)})"
        )

    prohibited = _evaluate(cleaned, PROHIBITED_PRACTICES)
    annex_iii = _evaluate(cleaned, ANNEX_III_AREAS)
    transparency = _evaluate(cleaned, TRANSPARENCY_TRIGGERS)

    caveats: list[str] = []
    if prohibited:
        tier = "prohibited"
        primary = prohibited
        reasoning = (
            f"The description matches {len(prohibited)} Art. 5 prohibited "
            f"practice rule(s), the strongest being {prohibited[0].citation} "
            f"({prohibited[0].label.lower()}). A prohibited practice outranks "
            "every other classification."
        )
        caveats.append(
            "Several Art. 5 prohibitions have narrow statutory exceptions. "
            "Confirm with counsel before concluding the practice is banned in "
            "your specific circumstances."
        )
    elif annex_iii:
        tier = "high-risk"
        primary = annex_iii
        reasoning = (
            f"The description falls in {len(annex_iii)} Annex III area(s), the "
            f"strongest being {annex_iii[0].citation} "
            f"({annex_iii[0].label.lower()}), which makes it high-risk under "
            "Art. 6(2)."
        )
        caveats.append(
            "Art. 6(3) allows an Annex III system to be treated as not high-risk "
            "where it performs a narrow procedural task, improves a completed "
            "human activity, detects decision patterns without replacing human "
            "assessment, or is purely preparatory. Assess and document that "
            "derogation explicitly; it must be registered before market placement."
        )
    elif transparency:
        tier = "limited-risk"
        primary = transparency
        reasoning = (
            f"No prohibited practice or Annex III area matched, but "
            f"{len(transparency)} Art. 50 transparency trigger(s) fired, the "
            f"strongest being {transparency[0].citation}."
        )
    else:
        tier = "minimal-risk"
        primary = []
        reasoning = (
            "No Art. 5 practice, Annex III area or Art. 50 trigger matched the "
            "description. Note that a thin description is the most common reason "
            "for a minimal-risk result; state the decision the system influences "
            "and the people it affects, then re-run."
        )

    if tier != "prohibited" and transparency and tier == "high-risk":
        caveats.append(
            "Art. 50 transparency obligations also appear to apply and are "
            "cumulative with the high-risk regime, not an alternative to it."
        )

    caveats.append(
        "Annex I high-risk classification under Art. 6(1), which covers AI used "
        "as a safety component of a regulated product such as machinery, medical "
        "devices or vehicles, is not detected by this tool. Check it manually."
    )
    caveats.append(
        "Obligations differ by role. Confirm whether you are the provider, "
        "deployer, importer or distributor under Art. 3 before acting on this."
    )

    all_triggers = tuple(prohibited + annex_iii + transparency)
    confidence = primary[0].confidence if primary else 0.5

    return RiskClassification(
        use_case=cleaned,
        tier=tier,
        confidence=confidence,
        reasoning=reasoning,
        triggers=all_triggers,
        obligations=TIER_OBLIGATIONS[tier],
        caveats=tuple(caveats),
    )
