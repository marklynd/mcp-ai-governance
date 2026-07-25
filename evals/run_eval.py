#!/usr/bin/env python3
"""Score the control-mapping tool against the labelled eval set.

Usage::

    python evals/run_eval.py
    python evals/run_eval.py --top-k 3 --threshold 0.80
    python evals/run_eval.py --json > results.json

Metrics reported, per framework and overall:

``hit@1``
    Fraction of cases where the top-ranked control is in the gold set. This is
    the metric that matters if a downstream agent takes the first result.
``hit@k``
    Fraction of cases where any gold control appears in the top k. This is the
    metric that matters if a human reads the shortlist.
``MRR``
    Mean reciprocal rank of the first gold control. Sensitive to *where* in the
    list the right answer lands, so it separates "correct but ranked third"
    from "correct and ranked first".
``no-result rate``
    Fraction of evaluated cases that returned nothing at all above the
    confidence threshold. Tracked separately because a silent empty result is a
    different failure from a wrong result.

Cases whose expectation for a framework is ``null`` are excluded from that
framework's metrics. Those are deliberate statements that the encoded subset
has no good answer, and counting them as failures would punish honesty.

Exits non-zero if ``--threshold`` is given and overall hit@k falls below it,
so this can run as a CI gate.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from mcp_ai_governance.mapping import map_control  # noqa: E402

DEFAULT_EVAL_SET = Path(__file__).resolve().parent / "mapping_eval_set.json"


@dataclass
class FrameworkStats:
    """Accumulated results for one framework."""

    evaluated: int = 0
    hit_at_1: int = 0
    hit_at_k: int = 0
    reciprocal_ranks: list[float] = field(default_factory=list)
    empty: int = 0
    misses: list[dict[str, Any]] = field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        """Return the computed metrics for this framework."""
        if self.evaluated == 0:
            return {
                "evaluated": 0,
                "hit@1": None,
                "hit@k": None,
                "mrr": None,
                "no_result_rate": None,
            }
        return {
            "evaluated": self.evaluated,
            "hit@1": round(self.hit_at_1 / self.evaluated, 3),
            "hit@k": round(self.hit_at_k / self.evaluated, 3),
            "mrr": round(sum(self.reciprocal_ranks) / self.evaluated, 3),
            "no_result_rate": round(self.empty / self.evaluated, 3),
        }


def load_eval_set(path: Path) -> dict[str, Any]:
    """Load and minimally validate the eval set file."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Eval set not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Eval set is not valid JSON: {exc}") from exc

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise SystemExit("Eval set must contain a non-empty 'cases' array")
    for index, case in enumerate(cases):
        if not isinstance(case.get("description"), str):
            raise SystemExit(f"Case {index} is missing a string 'description'")
        if not isinstance(case.get("expected"), dict):
            raise SystemExit(f"Case {index} is missing an 'expected' object")
    return payload


def evaluate(
    cases: Sequence[dict[str, Any]],
    top_k: int,
    min_confidence: float,
) -> tuple[dict[str, FrameworkStats], FrameworkStats]:
    """Run every case and accumulate per-framework and overall statistics."""
    per_framework: dict[str, FrameworkStats] = {}
    overall = FrameworkStats()

    for case in cases:
        expected: dict[str, Any] = case["expected"]
        frameworks = [key for key, value in expected.items() if value is not None]
        if not frameworks:
            continue

        result = map_control(
            description=case["description"],
            frameworks=list(expected.keys()),
            top_k=top_k,
            min_confidence=min_confidence,
        )

        for framework_key in frameworks:
            gold = set(expected[framework_key])
            stats = per_framework.setdefault(framework_key, FrameworkStats())
            predicted = [
                match.control.id for match in result.mappings.get(framework_key, ())
            ]

            stats.evaluated += 1
            overall.evaluated += 1
            if not predicted:
                stats.empty += 1
                overall.empty += 1

            rank = next(
                (i + 1 for i, control_id in enumerate(predicted) if control_id in gold),
                None,
            )
            if rank == 1:
                stats.hit_at_1 += 1
                overall.hit_at_1 += 1
            if rank is not None:
                stats.hit_at_k += 1
                overall.hit_at_k += 1
                stats.reciprocal_ranks.append(1.0 / rank)
                overall.reciprocal_ranks.append(1.0 / rank)
            else:
                stats.reciprocal_ranks.append(0.0)
                overall.reciprocal_ranks.append(0.0)
                miss = {
                    "case": case.get("id", case["description"][:40]),
                    "framework": framework_key,
                    "expected_any_of": sorted(gold),
                    "predicted": predicted,
                }
                stats.misses.append(miss)
                overall.misses.append(miss)

    return per_framework, overall


def _print_report(
    payload: dict[str, Any],
    per_framework: dict[str, FrameworkStats],
    overall: FrameworkStats,
    top_k: int,
) -> None:
    """Print a human-readable report to stdout."""
    print("=" * 74)
    print(f"Control mapping evaluation - {payload['name']}")
    print(f"{len(payload['cases'])} cases, top_k={top_k}")
    print("=" * 74)
    print()
    header = f"{'framework':<16}{'n':>5}{'hit@1':>9}{f'hit@{top_k}':>9}{'MRR':>9}{'empty':>9}"
    print(header)
    print("-" * len(header))
    for framework_key in sorted(per_framework):
        summary = per_framework[framework_key].summary()
        print(
            f"{framework_key:<16}{summary['evaluated']:>5}"
            f"{summary['hit@1']:>9.3f}{summary['hit@k']:>9.3f}"
            f"{summary['mrr']:>9.3f}{summary['no_result_rate']:>9.3f}"
        )
    print("-" * len(header))
    summary = overall.summary()
    print(
        f"{'OVERALL':<16}{summary['evaluated']:>5}"
        f"{summary['hit@1']:>9.3f}{summary['hit@k']:>9.3f}"
        f"{summary['mrr']:>9.3f}{summary['no_result_rate']:>9.3f}"
    )
    print()

    skipped = sum(
        1
        for case in payload["cases"]
        for value in case["expected"].values()
        if value is None
    )
    if skipped:
        print(
            f"{skipped} framework expectations are null (no good answer in the "
            "encoded subset) and were excluded from scoring."
        )
        print()

    if overall.misses:
        print(f"Misses ({len(overall.misses)}):")
        for miss in overall.misses:
            predicted = ", ".join(miss["predicted"]) or "(nothing returned)"
            print(f"  [{miss['framework']}] {miss['case']}")
            print(f"      expected any of: {', '.join(miss['expected_any_of'])}")
            print(f"      predicted:       {predicted}")
        print()
    else:
        print("No misses.")
        print()


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--eval-set",
        type=Path,
        default=DEFAULT_EVAL_SET,
        help="Path to the labelled eval set JSON file.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Results per framework to consider when computing hit@k (default 3).",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.30,
        help="Confidence floor passed to map_control (default 0.30).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Fail with a non-zero exit code if overall hit@k is below this.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of the printed report.",
    )
    args = parser.parse_args(argv)

    if args.top_k < 1:
        parser.error("--top-k must be at least 1")

    payload = load_eval_set(args.eval_set)
    per_framework, overall = evaluate(
        payload["cases"], top_k=args.top_k, min_confidence=args.min_confidence
    )

    if args.json:
        print(
            json.dumps(
                {
                    "eval_set": payload["name"],
                    "cases": len(payload["cases"]),
                    "top_k": args.top_k,
                    "min_confidence": args.min_confidence,
                    "per_framework": {
                        key: stats.summary() for key, stats in per_framework.items()
                    },
                    "overall": overall.summary(),
                    "misses": overall.misses,
                },
                indent=2,
            )
        )
    else:
        _print_report(payload, per_framework, overall, args.top_k)

    if args.threshold is not None:
        achieved = overall.summary()["hit@k"] or 0.0
        if achieved < args.threshold:
            print(
                f"FAIL: overall hit@{args.top_k} {achieved:.3f} is below the "
                f"threshold {args.threshold:.3f}",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
