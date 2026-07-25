"""Framework knowledge base for the AI governance MCP server.

Everything in this package is static, offline reference data. No network calls
and no API keys are required at any point.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from typing import Final

from . import eu_ai_act, iso_42001, nist_ai_rmf, nist_csf
from .base import Control, Framework
from .themes import ALL_THEME_IDS, THEMES, Theme

FRAMEWORKS: Final[Mapping[str, Framework]] = {
    nist_ai_rmf.FRAMEWORK_KEY: nist_ai_rmf.FRAMEWORK,
    iso_42001.FRAMEWORK_KEY: iso_42001.FRAMEWORK,
    eu_ai_act.FRAMEWORK_KEY: eu_ai_act.FRAMEWORK,
    nist_csf.FRAMEWORK_KEY: nist_csf.FRAMEWORK,
}

#: Frameworks returned by ``map_control`` when the caller does not narrow the set.
DEFAULT_FRAMEWORKS: Final[tuple[str, ...]] = (
    nist_ai_rmf.FRAMEWORK_KEY,
    iso_42001.FRAMEWORK_KEY,
    eu_ai_act.FRAMEWORK_KEY,
)

ALL_FRAMEWORK_KEYS: Final[tuple[str, ...]] = tuple(FRAMEWORKS)


def iter_controls(framework_keys: tuple[str, ...] | None = None) -> Iterator[Control]:
    """Yield every control in the requested frameworks.

    Args:
        framework_keys: Framework keys to include. ``None`` means all.

    Raises:
        KeyError: If a requested framework key is unknown.
    """
    keys = framework_keys if framework_keys is not None else ALL_FRAMEWORK_KEYS
    for key in keys:
        yield from FRAMEWORKS[key].controls


_CONTROL_INDEX: Final[dict[str, Control]] = {
    control.id: control for control in iter_controls()
}


def _normalise_control_id(raw: str) -> str:
    """Return a comparison key for a control identifier.

    Tolerates the punctuation and casing variants people actually type:
    ``govern-1.1``, ``GOVERN 1.1``, ``art14``, ``Article 14``, ``a.6.2.4``.
    """
    text = raw.strip().lower()
    text = re.sub(r"^article\b", "art", text)
    # Collapse every separator style (space, dot, hyphen, underscore) to a
    # single dot so "Art. 14", "art 14" and "art-14" agree, while keeping the
    # component boundaries that stop "A.1.1" colliding with "A.11".
    text = re.sub(r"[^a-z0-9]+", ".", text)
    return text.strip(".")


_NORMALISED_INDEX: Final[dict[str, Control]] = {
    _normalise_control_id(control_id): control
    for control_id, control in _CONTROL_INDEX.items()
}


def find_control(control_id: str) -> Control | None:
    """Return the control matching ``control_id``, or ``None``.

    Matching is tolerant of case, spacing and separator style. ``"art 14"``,
    ``"Art. 14"`` and ``"Article 14"`` all resolve to the same EU AI Act
    article.
    """
    if not isinstance(control_id, str):
        raise TypeError("control_id must be a string")
    return _NORMALISED_INDEX.get(_normalise_control_id(control_id))


def control_ids() -> tuple[str, ...]:
    """Return every encoded control identifier, in framework order."""
    return tuple(_CONTROL_INDEX)


def coverage_summary() -> list[dict[str, str | int]]:
    """Return a per-framework description of what is and is not encoded."""
    return [
        {
            "framework": framework.key,
            "name": framework.name,
            "version": framework.version,
            "controls_encoded": len(framework.controls),
            "source": framework.source,
            "coverage": framework.coverage,
        }
        for framework in FRAMEWORKS.values()
    ]


__all__ = [
    "ALL_FRAMEWORK_KEYS",
    "ALL_THEME_IDS",
    "Control",
    "DEFAULT_FRAMEWORKS",
    "FRAMEWORKS",
    "Framework",
    "THEMES",
    "Theme",
    "control_ids",
    "coverage_summary",
    "eu_ai_act",
    "find_control",
    "iso_42001",
    "iter_controls",
    "nist_ai_rmf",
    "nist_csf",
]
