"""Shared types for the framework knowledge modules."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from .themes import ALL_THEME_IDS


@dataclass(frozen=True)
class Control:
    """One addressable requirement inside a governance framework.

    Attributes:
        id: Canonical identifier as printed in the source document, for example
            ``"GOVERN 1.1"``, ``"A.6.2.4"`` or ``"Art. 14"``.
        title: Short paraphrase of the requirement. These are summaries written
            for this project, not verbatim quotations of the standards.
        framework: Framework key, one of the keys of ``knowledge.FRAMEWORKS``.
        group: Parent grouping (function, clause or chapter) for display.
        themes: Theme identifiers from ``knowledge.themes`` that this control
            addresses. Drives the mapping engine.
        signals: Extra control-specific phrases that are strong evidence for
            this control beyond its themes.
        citation: Human-readable pointer to the source document and section.
    """

    id: str
    title: str
    framework: str
    group: str
    themes: tuple[str, ...]
    signals: tuple[str, ...] = field(default=())
    citation: str = ""

    def __post_init__(self) -> None:
        """Validate theme references on construction."""
        unknown = set(self.themes) - ALL_THEME_IDS
        if unknown:
            raise ValueError(
                f"Control {self.id!r} references unknown themes: {sorted(unknown)}"
            )
        if not self.themes:
            raise ValueError(f"Control {self.id!r} must declare at least one theme")


@dataclass(frozen=True)
class Framework:
    """A governance framework and its encoded control subset.

    Attributes:
        key: Stable short key used in tool arguments and results.
        name: Full published name.
        version: Published version or year.
        source: Citation for the authoritative source document.
        coverage: Honest description of how much of the framework is encoded.
        controls: The encoded controls.
    """

    key: str
    name: str
    version: str
    source: str
    coverage: str
    controls: tuple[Control, ...]

    def by_id(self) -> dict[str, Control]:
        """Return a mapping of control id to control."""
        return {control.id: control for control in self.controls}


def assert_unique_ids(controls: Iterable[Control]) -> tuple[Control, ...]:
    """Return ``controls`` as a tuple, raising if any identifier repeats."""
    materialised = tuple(controls)
    seen: set[str] = set()
    for control in materialised:
        if control.id in seen:
            raise ValueError(f"Duplicate control id {control.id!r}")
        seen.add(control.id)
    return materialised
