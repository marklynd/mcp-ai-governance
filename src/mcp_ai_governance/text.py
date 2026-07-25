"""Deterministic text normalisation and phrase matching.

The mapping engine is intentionally rule-based rather than model-based. That
buys three things that matter for a governance tool: the output is identical
for identical input, every match can be explained by pointing at the phrase
that caused it, and the server runs with no API key and no network access.

The normaliser is deliberately small. It lower-cases, strips punctuation,
folds a handful of British/American spelling pairs, and applies a conservative
suffix-stripping rule so that "monitoring", "monitors" and "monitored" match
the signal "monitor". It is not a linguistic stemmer and does not try to be.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from functools import lru_cache
from typing import Final

_WORD_SPLIT: Final[re.Pattern[str]] = re.compile(r"[^a-z0-9]+")

# Folded before tokenising so that either spelling matches either signal list.
_SPELLING_FOLD: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (re.compile(r"\bis(ation|ations)\b"), r"iz\1"),
    (re.compile(r"([a-z]+)isation\b"), r"\1ization"),
    (re.compile(r"([a-z]+)isations\b"), r"\1izations"),
    (re.compile(r"([a-z]+)ise\b"), r"\1ize"),
    (re.compile(r"([a-z]+)ised\b"), r"\1ized"),
    (re.compile(r"([a-z]+)ises\b"), r"\1izes"),
    (re.compile(r"([a-z]+)ising\b"), r"\1izing"),
    (re.compile(r"\bbehaviour"), "behavior"),
    (re.compile(r"\blabelling\b"), "labeling"),
    (re.compile(r"\bmodelling\b"), "modeling"),
    (re.compile(r"\bcatalogue\b"), "catalog"),
    (re.compile(r"\bprogramme\b"), "program"),
    (re.compile(r"\bjudgement\b"), "judgment"),
    (re.compile(r"\bharmonised\b"), "harmonized"),
    (re.compile(r"\bauthorisation\b"), "authorization"),
)

_IRREGULAR_STEMS: Final[dict[str, str]] = {
    # Doubled-consonant verbs the suffix rules below would over-truncate.
    "logging": "log",
    "logged": "log",
    "mapping": "map",
    "mapped": "map",
    "flagging": "flag",
    "flagged": "flag",
    "data": "data",
    "criteria": "criterion",
    "analyses": "analysis",
    "analysis": "analysis",
    "bias": "bias",
    "biases": "bias",
    "policies": "policy",
    "policy": "policy",
    "process": "process",
    "processes": "process",
    "access": "access",
    "business": "business",
    "class": "class",
    "loss": "loss",
    "less": "less",
    "status": "status",
    "risk": "risk",
    "risks": "risk",
    "logs": "log",
    "needs": "need",
    "series": "series",
}


#: ``(suffix, replacement, minimum length of the resulting stem)``, tried in
#: order. The first rule whose result is long enough wins.
_SUFFIX_RULES: Final[tuple[tuple[str, str, int], ...]] = (
    ("ies", "y", 4),
    ("ing", "", 4),
    ("ers", "", 4),
    ("ed", "", 4),
    ("er", "", 4),
    ("es", "", 5),
    # Minimum 3 so that four-letter plurals reduce correctly: without it "uses"
    # stayed "uses" while "use" stayed "use", and the two never matched.
    ("s", "", 3),
)

#: How many times the suffix rules are applied. Two passes are needed because a
#: single pass stops at the first matching suffix: "triggered" would reduce to
#: "trigger" while "trigger" reduced to "trigg", and the two never met.
_SUFFIX_PASSES: Final[int] = 2


def _stem(token: str) -> str:
    """Return a conservative stem for ``token``.

    Suffixes are only removed when the remaining stem stays at least four or
    five characters long, which keeps short domain words such as "log", "use"
    and "data" intact. A trailing silent "e" is then dropped so that the three
    surface forms of a verb converge: "approve", "approves" and "approved" all
    reduce to "approv".

    This is not a linguistic stemmer. Forms it cannot unify (for example
    "documentation" against "documented") are handled by listing both surface
    forms in the knowledge base, which keeps the behaviour inspectable.
    """
    if token in _IRREGULAR_STEMS:
        return _IRREGULAR_STEMS[token]
    if len(token) <= 3:
        return token
    stem = token
    for _ in range(_SUFFIX_PASSES):
        if len(stem) <= 3:
            break
        for suffix, replacement, min_stem in _SUFFIX_RULES:
            if stem.endswith(suffix):
                candidate = stem[: -len(suffix)] + replacement
                if len(candidate) >= min_stem:
                    stem = candidate
                    break
        else:
            break
    if len(stem) > 4 and stem.endswith("e"):
        stem = stem[:-1]
    return stem


@lru_cache(maxsize=4096)
def normalise(text: str) -> str:
    """Lower-case, fold spellings and collapse punctuation to single spaces."""
    lowered = text.lower()
    for pattern, replacement in _SPELLING_FOLD:
        lowered = pattern.sub(replacement, lowered)
    return " ".join(part for part in _WORD_SPLIT.split(lowered) if part)


@lru_cache(maxsize=4096)
def tokenise(text: str) -> tuple[str, ...]:
    """Return the stemmed token sequence for ``text``.

    Stop words are deliberately **kept**. An earlier version dropped them, which
    silently collapsed qualified signal phrases into bare ones: "must approve"
    became "approve" and then fired on "an approved policy". Keeping every token
    makes phrase matching stricter and, more importantly, makes the knowledge
    base mean exactly what it says.
    """
    return tuple(_stem(token) for token in normalise(text).split() if token)


@lru_cache(maxsize=8192)
def phrase_tokens(phrase: str) -> tuple[str, ...]:
    """Return the token sequence for a signal phrase.

    Uses the same tokenisation as document text, so a phrase matches exactly
    the word sequence it spells out, modulo inflection and punctuation.
    """
    return tokenise(phrase)


@dataclass(frozen=True)
class PhraseHit:
    """A signal phrase found in a piece of text.

    Attributes:
        phrase: The signal phrase as written in the knowledge base.
        word_count: Number of tokens in the phrase after normalisation.
        occurrences: How many times it appeared.
    """

    phrase: str
    word_count: int
    occurrences: int


def _count_subsequence(haystack: Sequence[str], needle: Sequence[str]) -> int:
    """Return the number of non-overlapping occurrences of ``needle``."""
    if not needle or len(needle) > len(haystack):
        return 0
    count = 0
    index = 0
    limit = len(haystack) - len(needle)
    while index <= limit:
        if tuple(haystack[index : index + len(needle)]) == tuple(needle):
            count += 1
            index += len(needle)
        else:
            index += 1
    return count


def find_phrases(text: str, phrases: Iterable[str]) -> list[PhraseHit]:
    """Return every phrase from ``phrases`` that occurs in ``text``.

    Matching is on the stemmed token sequence, so word order matters but
    inflection, punctuation and casing do not.

    Args:
        text: Free-text description to search.
        phrases: Candidate signal phrases.

    Returns:
        Hits sorted by descending phrase length, so that the most specific
        evidence appears first in rationales.

    Phrases that reduce to the same token sequence are counted once. Without
    this, "approve" and "approved by" (whose stop word is dropped, leaving the
    same single stem) would each score, double-counting one piece of evidence
    and skewing the theme ranking.
    """
    tokens = tokenise(text)
    by_needle: dict[tuple[str, ...], str] = {}
    for phrase in phrases:
        needle = phrase_tokens(phrase)
        if not needle:
            continue
        existing = by_needle.get(needle)
        if existing is None or len(phrase) < len(existing):
            by_needle[needle] = phrase

    hits: list[PhraseHit] = []
    for needle, phrase in by_needle.items():
        occurrences = _count_subsequence(tokens, needle)
        if occurrences:
            hits.append(
                PhraseHit(phrase=phrase, word_count=len(needle), occurrences=occurrences)
            )
    hits.sort(key=lambda hit: (-hit.word_count, hit.phrase))
    return hits
