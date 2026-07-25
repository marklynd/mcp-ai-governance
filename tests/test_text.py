"""Tests for the normalisation and phrase-matching primitives."""

from __future__ import annotations

import pytest

from mcp_ai_governance.text import find_phrases, normalise, tokenise


class TestNormalise:
    def test_lowercases_and_strips_punctuation(self) -> None:
        assert normalise("Human-Oversight, REQUIRED!") == "human oversight required"

    def test_folds_british_and_american_spellings(self) -> None:
        assert normalise("categorisation") == normalise("categorization")
        assert normalise("behaviour") == normalise("behavior")

    def test_collapses_whitespace(self) -> None:
        assert normalise("  a\n\tb  ") == "a b"


class TestTokenise:
    @pytest.mark.parametrize(
        "surface_forms",
        [
            ("approve", "approves", "approved"),
            ("monitor", "monitors", "monitoring", "monitored"),
            ("log", "logs", "logging", "logged"),
            ("use", "uses"),
            ("review", "reviews", "reviewer", "reviewers"),
            ("test", "tests", "testing", "tested"),
        ],
    )
    def test_inflections_converge_to_one_stem(self, surface_forms: tuple[str, ...]) -> None:
        stems = {tokenise(form) for form in surface_forms}
        assert len(stems) == 1, f"{surface_forms} produced {stems}"

    def test_short_words_are_left_alone(self) -> None:
        assert tokenise("ai") == ("ai",)
        assert tokenise("log") == ("log",)

    def test_stop_words_are_retained(self) -> None:
        # Regression: dropping stop words collapsed "must approve" to "approve",
        # which then fired on "an approved policy".
        assert "must" in tokenise("must approve the output")


class TestFindPhrases:
    def test_matches_across_inflection_and_punctuation(self) -> None:
        hits = find_phrases(
            "We are Monitoring, continuously, for drift.", ["monitor", "drift"]
        )
        assert {hit.phrase for hit in hits} == {"monitor", "drift"}

    def test_requires_contiguous_word_order(self) -> None:
        assert find_phrases("assessment of the impact", ["impact assessment"]) == []
        assert find_phrases("an impact assessment", ["impact assessment"]) != []

    def test_longer_phrases_sort_first(self) -> None:
        hits = find_phrases(
            "a human oversight process with oversight", ["oversight", "human oversight"]
        )
        assert hits[0].phrase == "human oversight"

    def test_synonymous_phrases_are_counted_once(self) -> None:
        # "reject" and "reject the" reduce to different needles, but two phrases
        # that reduce to the SAME needle must not both score.
        hits = find_phrases("we reject it", ["reject", "reject"])
        assert len(hits) == 1

    def test_repeated_occurrences_are_counted(self) -> None:
        hits = find_phrases("drift and more drift and drift", ["drift"])
        assert hits[0].occurrences == 3

    def test_no_match_returns_empty(self) -> None:
        assert find_phrases("nothing relevant here", ["quantum tunnelling"]) == []

    def test_empty_phrase_is_ignored(self) -> None:
        assert find_phrases("some text", ["", "   "]) == []
