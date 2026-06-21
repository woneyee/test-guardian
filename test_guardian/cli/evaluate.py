"""Command-line evaluation runner for Test Guardian."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from test_guardian.cli.run import _build_pipeline
from test_guardian.models.evaluation import EvaluationReport
from test_guardian.evaluation.evaluation_runner import (
    DEFAULT_DATASET_PATH,
    EvaluationRunner,
)


def main(
    argv: Sequence[str] | None = None,
    *,
    runner: EvaluationRunner | None = None,
) -> int:
    parser = _build_parser()

    try:
        args = parser.parse_args(argv)
        dataset_path = Path(args.dataset)
        if not dataset_path.exists():
            raise FileNotFoundError(str(dataset_path))

        active_runner = runner or EvaluationRunner(
            pipeline=_build_pipeline(),
            dataset_path=dataset_path,
        )
        report = active_runner.run()
    except (FileNotFoundError, ValueError) as error:
        print(_format_error(error), file=sys.stderr)
        return 1

    print(format_report(report))
    return 0


def format_report(report: EvaluationReport) -> str:
    return "\n".join(
        [
            "================================",
            "",
            "Test Guardian Evaluation",
            "",
            f"Total Cases: {report.total_cases}",
            "",
            f"Failure Accuracy: {report.failure_accuracy:.2%}",
            f"Failure Correct: {report.failure_correct}",
            f"Failure Incorrect: {report.failure_incorrect}",
            "",
            f"Reason Accuracy: {report.reason_accuracy:.2%}",
            f"Reason Correct: {report.reason_correct}",
            f"Reason Incorrect: {report.reason_incorrect}",
            "",
            "================================",
        ]
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate Test Guardian fixtures.")
    parser.add_argument(
        "--dataset",
        default=str(DEFAULT_DATASET_PATH),
        help="Evaluation dataset path",
    )
    return parser


def _format_error(error: BaseException) -> str:
    if isinstance(error, FileNotFoundError):
        return f"File not found: {error.filename or error}"
    return str(error)


if __name__ == "__main__":
    raise SystemExit(main())
