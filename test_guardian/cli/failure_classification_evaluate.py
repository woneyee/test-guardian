"""Command-line evaluation for 4-class FailureAnalyzer accuracy."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from test_guardian.agents.failure_analyzer.openai import OpenAIFailureAnalyzerExperimentalV1
from test_guardian.models.failure_evaluation import FailureClassificationReport
from test_guardian.evaluation.failure_classification import (
    DEFAULT_FAILURE_CLASSIFICATION_DATASET_PATH,
    FailureClassificationEvaluationRunner,
)


def main(
    argv: Sequence[str] | None = None,
    *,
    runner: FailureClassificationEvaluationRunner | None = None,
) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        dataset_path = Path(args.dataset)
        if not dataset_path.exists():
            raise FileNotFoundError(str(dataset_path))
        if args.limit is not None and args.limit < 0:
            raise ValueError("--limit must be greater than or equal to 0")

        active_runner = runner or FailureClassificationEvaluationRunner(
            analyzer=OpenAIFailureAnalyzerExperimentalV1(),
            dataset_path=dataset_path,
            limit=args.limit,
        )
        report = active_runner.run()
    except (FileNotFoundError, ValueError) as error:
        print(_format_error(error), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report.model_dump(mode="json"), indent=2))
    else:
        print(format_report(report))
    return 0


def format_report(report: FailureClassificationReport) -> str:
    lines = [
        "==================================",
        "",
        "Failure Classification Evaluation",
        "",
        f"Total Cases: {report.total_cases}",
        "",
        f"Accuracy: {report.accuracy:.2%}",
        f"Correct: {report.correct}",
        f"Incorrect: {report.incorrect}",
        "",
        "By Type:",
    ]

    for failure_type, metrics in report.by_type.items():
        total = metrics["total"]
        correct = metrics["correct"]
        accuracy = correct / total if total else 0.0
        lines.append(f"- {failure_type}: {correct}/{total} ({accuracy:.2%})")

    lines.extend(["", "=================================="])
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate OpenAIFailureAnalyzer on 4-class fixtures."
    )
    parser.add_argument(
        "--dataset",
        default=str(DEFAULT_FAILURE_CLASSIFICATION_DATASET_PATH),
        help="Failure classification dataset path",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of failure classification cases to run",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full evaluation report as JSON",
    )
    return parser


def _format_error(error: BaseException) -> str:
    if isinstance(error, FileNotFoundError):
        return f"File not found: {error.filename or error}"
    return str(error)


if __name__ == "__main__":
    raise SystemExit(main())
