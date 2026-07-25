"""Control-to-framework mapping engine.

Given a free-text description of a control, practice or capability, this module
resolves it to the framework controls that a reviewer would expect to see cited,
with a confidence score and an explanation of why.

Algorithm
---------
1. **Theme detection.** The description is matched against the signal phrases of
   each theme in :mod:`mcp_ai_governance.knowledge.themes`. A theme's strength is
   the sum of its hits, weighted so that longer phrases count for more, then
   capped so no single theme can dominate.
2. **Control scoring.** Each candidate control accumulates:

   * *direct evidence* - hits on the control's own signal phrases, which are the
     strongest indicator available;
   * *thematic evidence* - the strength of each shared theme, discounted by that
     theme's **specificity within its framework**. A theme carried by one control
     is discriminative; a theme carried by fifteen is not, and is discounted by
     ``1 / sqrt(n)``;
   * *agreement bonus* - extra credit when a control matches more than one theme
     found in the description, because multi-theme agreement is much less likely
     to be coincidental.
3. **Confidence.** The raw score is squashed through ``1 - exp(-raw / SCALE)``,
   which is monotonic, bounded and saturates gently. It is a calibrated ranking
   signal, not a probability.

Everything is deterministic. The same description always produces the same
mapping.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Final

from .knowledge import (
    ALL_FRAMEWORK_KEYS,
    DEFAULT_FRAMEWORKS,
    FRAMEWORKS,
    THEMES,
    Control,
)
from .text import PhraseHit, find_phrases

#: Weight applied to a one-word hit on a control's own signal list.
DIRECT_SIGNAL_WEIGHT: Final[float] = 1.25

#: Weight applied to a one-word hit on a theme's signal list.
THEME_SIGNAL_WEIGHT: Final[float] = 0.70

#: Extra credit per additional word in a matched phrase, as a multiplier.
PHRASE_LENGTH_BONUS: Final[float] = 0.6

#: A single phrase counts at most this many times, so repetition cannot inflate.
MAX_OCCURRENCES_COUNTED: Final[int] = 2

#: Ceiling on any one theme's strength, so a keyword-stuffed description cannot
#: push a single theme far beyond the others.
THEME_STRENGTH_CAP: Final[float] = 2.2

#: Floor on the specificity discount. Without it, themes that are deliberately
#: broad (documentation, risk assessment) would suppress correct matches below
#: the reporting threshold rather than merely ranking them lower.
MIN_THEME_SPECIFICITY: Final[float] = 0.45

#: Credit added for each theme beyond the first that a control shares with the
#: description.
MULTI_THEME_AGREEMENT_BONUS: Final[float] = 0.45

#: Denominator of the confidence squashing function. Larger means more
#: conservative confidence.
CONFIDENCE_SCALE: Final[float] = 1.7

#: Confidence below this is treated as noise and dropped.
DEFAULT_MIN_CONFIDENCE: Final[float] = 0.30

#: Maximum controls returned per framework unless the caller asks for more.
DEFAULT_TOP_K: Final[int] = 3

MAX_TOP_K: Final[int] = 10
MAX_DESCRIPTION_CHARS: Final[int] = 4000

DISCLAIMER: Final[str] = (
    "Deterministic keyword and theme mapping over an encoded subset of each "
    "framework. It is decision support for a qualified reviewer, not a "
    "compliance determination and not legal advice."
)


def _length_weighted(hits: Iterable[PhraseHit], base_weight: float) -> float:
    """Return the summed weight of ``hits`` at ``base_weight`` per single word."""
    total = 0.0
    for hit in hits:
        occurrences = min(hit.occurrences, MAX_OCCURRENCES_COUNTED)
        length_factor = 1.0 + PHRASE_LENGTH_BONUS * (hit.word_count - 1)
        total += base_weight * length_factor * occurrences
    return total


def _build_theme_specificity() -> dict[tuple[str, str], float]:
    """Return ``(framework_key, theme_id) -> specificity`` in ``(0, 1]``.

    A theme used by one control in a framework has specificity 1.0. A theme used
    by nine would have 1/3, floored at :data:`MIN_THEME_SPECIFICITY`. Computed
    once at import time.
    """
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for framework in FRAMEWORKS.values():
        for control in framework.controls:
            for theme_id in control.themes:
                counts[(framework.key, theme_id)] += 1
    return {
        key: max(MIN_THEME_SPECIFICITY, 1.0 / math.sqrt(count))
        for key, count in counts.items()
    }


_THEME_SPECIFICITY: Final[Mapping[tuple[str, str], float]] = _build_theme_specificity()


@dataclass(frozen=True)
class ThemeMatch:
    """A governance theme detected in a description.

    Attributes:
        theme_id: Identifier from the theme vocabulary.
        label: Human-readable theme name.
        strength: Capped evidence strength, higher means clearer signal.
        evidence: The phrases that triggered the theme, most specific first.
    """

    theme_id: str
    label: str
    strength: float
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "theme_id": self.theme_id,
            "label": self.label,
            "strength": round(self.strength, 3),
            "evidence": list(self.evidence),
        }


@dataclass(frozen=True)
class ControlMatch:
    """A framework control matched to a description.

    Attributes:
        control: The matched control.
        confidence: Squashed score in ``[0, 0.95]``.
        raw_score: Pre-squash score, exposed for debugging and evaluation.
        matched_signals: Control-specific phrases found in the description.
        matched_themes: Theme identifiers shared with the description.
        rationale: One-sentence explanation suitable for showing to a reviewer.
    """

    control: Control
    confidence: float
    raw_score: float
    matched_signals: tuple[str, ...]
    matched_themes: tuple[str, ...]
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "control_id": self.control.id,
            "title": self.control.title,
            "group": self.control.group,
            "confidence": self.confidence,
            "raw_score": round(self.raw_score, 3),
            "matched_signals": list(self.matched_signals),
            "matched_themes": list(self.matched_themes),
            "rationale": self.rationale,
            "citation": self.control.citation,
        }


@dataclass(frozen=True)
class MappingResult:
    """The complete result of a ``map_control`` call."""

    description: str
    themes: tuple[ThemeMatch, ...]
    mappings: Mapping[str, tuple[ControlMatch, ...]]
    notes: tuple[str, ...] = field(default=())

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "description": self.description,
            "detected_themes": [theme.to_dict() for theme in self.themes],
            "mappings": {
                framework_key: [match.to_dict() for match in matches]
                for framework_key, matches in self.mappings.items()
            },
            "frameworks": {
                framework_key: {
                    "name": FRAMEWORKS[framework_key].name,
                    "version": FRAMEWORKS[framework_key].version,
                    "source": FRAMEWORKS[framework_key].source,
                }
                for framework_key in self.mappings
            },
            "notes": list(self.notes),
            "disclaimer": DISCLAIMER,
        }


def detect_themes(description: str) -> tuple[ThemeMatch, ...]:
    """Return the themes present in ``description``, strongest first."""
    matches: list[ThemeMatch] = []
    for theme in THEMES.values():
        hits = find_phrases(description, theme.signals)
        if not hits:
            continue
        strength = min(
            _length_weighted(hits, THEME_SIGNAL_WEIGHT), THEME_STRENGTH_CAP
        )
        matches.append(
            ThemeMatch(
                theme_id=theme.id,
                label=theme.label,
                strength=strength,
                evidence=tuple(hit.phrase for hit in hits),
            )
        )
    matches.sort(key=lambda match: (-match.strength, match.theme_id))
    return tuple(matches)


def _score_control(
    description: str,
    control: Control,
    theme_strengths: Mapping[str, float],
) -> ControlMatch | None:
    """Score one control against a description, or return ``None`` if unrelated."""
    direct_hits = find_phrases(description, control.signals)
    direct_score = _length_weighted(direct_hits, DIRECT_SIGNAL_WEIGHT)

    shared_themes = [
        theme_id for theme_id in control.themes if theme_id in theme_strengths
    ]
    thematic_score = 0.0
    for theme_id in shared_themes:
        specificity = _THEME_SPECIFICITY.get((control.framework, theme_id), 1.0)
        thematic_score += theme_strengths[theme_id] * specificity

    if direct_score == 0.0 and thematic_score == 0.0:
        return None

    agreement_bonus = MULTI_THEME_AGREEMENT_BONUS * max(0, len(shared_themes) - 1)
    raw = direct_score + thematic_score + agreement_bonus
    confidence = round(min(0.95, 1.0 - math.exp(-raw / CONFIDENCE_SCALE)), 2)

    return ControlMatch(
        control=control,
        confidence=confidence,
        raw_score=raw,
        matched_signals=tuple(hit.phrase for hit in direct_hits),
        matched_themes=tuple(shared_themes),
        rationale=_build_rationale(control, direct_hits, shared_themes),
    )


def _build_rationale(
    control: Control,
    direct_hits: Sequence[PhraseHit],
    shared_themes: Sequence[str],
) -> str:
    """Return a short human-readable justification for a match."""
    parts: list[str] = []
    if direct_hits:
        quoted = ", ".join(f'"{hit.phrase}"' for hit in direct_hits[:3])
        parts.append(f"the description uses {quoted}, which is specific to this control")
    if shared_themes:
        labels = ", ".join(THEMES[theme_id].label.lower() for theme_id in shared_themes[:3])
        parts.append(f"it addresses {labels}")
    if not parts:  # pragma: no cover - guarded by the caller
        return f"Matched {control.id}."
    return f"Mapped to {control.id} because " + " and ".join(parts) + "."


def _validate_frameworks(frameworks: Sequence[str] | None) -> tuple[str, ...]:
    """Validate and normalise the requested framework keys."""
    if frameworks is None:
        return DEFAULT_FRAMEWORKS
    if isinstance(frameworks, str):
        raise ValueError(
            "frameworks must be a list of framework keys, not a single string. "
            f"Valid keys: {', '.join(ALL_FRAMEWORK_KEYS)}"
        )
    if not frameworks:
        raise ValueError(
            f"frameworks must not be empty. Valid keys: {', '.join(ALL_FRAMEWORK_KEYS)}"
        )
    unknown = [key for key in frameworks if key not in FRAMEWORKS]
    if unknown:
        raise ValueError(
            f"Unknown framework key(s): {', '.join(sorted(unknown))}. "
            f"Valid keys: {', '.join(ALL_FRAMEWORK_KEYS)}"
        )
    seen: list[str] = []
    for key in frameworks:
        if key not in seen:
            seen.append(key)
    return tuple(seen)


def map_control(
    description: str,
    frameworks: Sequence[str] | None = None,
    top_k: int = DEFAULT_TOP_K,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
) -> MappingResult:
    """Map a control description onto framework controls.

    Args:
        description: Free-text description of a control, practice or capability.
        frameworks: Framework keys to map against. Defaults to NIST AI RMF,
            ISO/IEC 42001 and the EU AI Act.
        top_k: Maximum matches returned per framework, 1 to 10.
        min_confidence: Matches below this confidence are dropped, 0.0 to 1.0.

    Returns:
        A :class:`MappingResult`.

    Raises:
        TypeError: If ``description`` is not a string.
        ValueError: If the description is empty or too long, if a framework key
            is unknown, or if ``top_k`` or ``min_confidence`` is out of range.
    """
    if not isinstance(description, str):
        raise TypeError("description must be a string")
    cleaned = description.strip()
    if not cleaned:
        raise ValueError("description must not be empty")
    if len(cleaned) > MAX_DESCRIPTION_CHARS:
        raise ValueError(
            f"description must be at most {MAX_DESCRIPTION_CHARS} characters "
            f"(received {len(cleaned)})"
        )
    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise TypeError("top_k must be an integer")
    if not 1 <= top_k <= MAX_TOP_K:
        raise ValueError(f"top_k must be between 1 and {MAX_TOP_K} (received {top_k})")
    if not isinstance(min_confidence, (int, float)) or isinstance(min_confidence, bool):
        raise TypeError("min_confidence must be a number")
    if not 0.0 <= float(min_confidence) <= 1.0:
        raise ValueError(
            f"min_confidence must be between 0.0 and 1.0 (received {min_confidence})"
        )

    framework_keys = _validate_frameworks(frameworks)
    themes = detect_themes(cleaned)
    theme_strengths = {theme.theme_id: theme.strength for theme in themes}

    mappings: dict[str, tuple[ControlMatch, ...]] = {}
    for framework_key in framework_keys:
        scored = [
            match
            for control in FRAMEWORKS[framework_key].controls
            if (match := _score_control(cleaned, control, theme_strengths)) is not None
            and match.confidence >= min_confidence
        ]
        scored.sort(key=lambda match: (-match.raw_score, match.control.id))
        mappings[framework_key] = tuple(scored[:top_k])

    notes: list[str] = []
    if not themes:
        notes.append(
            "No governance themes were detected. Describe the control in terms "
            "of what it does (for example 'a reviewer approves the output before "
            "it reaches a customer') rather than naming a product or team."
        )
    empty = [key for key, matches in mappings.items() if not matches]
    if empty and themes:
        names = ", ".join(FRAMEWORKS[key].name for key in empty)
        notes.append(
            f"No match above the confidence threshold in: {names}. This may mean "
            "the framework genuinely does not cover the practice, or that the "
            "encoded subset does not reach it."
        )

    return MappingResult(
        description=cleaned,
        themes=themes,
        mappings=mappings,
        notes=tuple(notes),
    )
