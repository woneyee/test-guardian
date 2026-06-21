"""Compare FailureAnalyzer prompt V1 and experimental prompt V2."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from test_guardian.agents.failure_analyzer.openai import (
    OpenAIFailureAnalyzerExperimentalV1,
    OpenAIFailureAnalyzerV2,
)
from test_guardian.models.failure import ExperimentalFailureType
from test_guardian.models.failure_evaluation import FailureClassificationReport
from test_guardian.evaluation.failure_classification import (
    DEFAULT_FAILURE_CLASSIFICATION_DATASET_PATH,
    FailureClassificationEvaluationRunner,
)


def main(
    argv: Sequence[str] | None = None,
    *,
    v1_runner: FailureClassificationEvaluationRunner | None = None,
    v2_runner: FailureClassificationEvaluationRunner | None = None,
) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        dataset_path = Path(args.dataset)
        if not dataset_path.exists():
            raise FileNotFoundError(str(dataset_path))
        if args.limit is not None and args.limit < 0:
            raise ValueError("--limit must be greater than or equal to 0")

        active_v1 = v1_runner or FailureClassificationEvaluationRunner(
            analyzer=OpenAIFailureAnalyzerExperimentalV1(),
            dataset_path=dataset_path,
            limit=args.limit,
        )
        active_v2 = v2_runner or FailureClassificationEvaluationRunner(
            analyzer=OpenAIFailureAnalyzerV2(),
            dataset_path=dataset_path,
            limit=args.limit,
        )
        v1_report = active_v1.run()
        v2_report = active_v2.run()
    except (FileNotFoundError, ValueError) as error:
        print(_format_error(error), file=sys.stderr)
        return 1

    if args.json:
        print(
            json.dumps(
                {
                    "v1": v1_report.model_dump(mode="json"),
                    "v2": v2_report.model_dump(mode="json"),
                    "delta_accuracy": v2_report.accuracy - v1_report.accuracy,
                },
                indent=2,
            )
        )
    else:
        print(format_comparison_report(v1_report, v2_report))
    return 0


def format_comparison_report(
    v1_report: FailureClassificationReport,
    v2_report: FailureClassificationReport,
) -> str:
    lines = [
        "==================================",
        "",
        "Failure Analyzer Prompt Comparison",
        "",
        f"Total Cases: {v2_report.total_cases}",
        "",
        f"Prompt V1 Accuracy: {v1_report.accuracy:.2%}",
        f"Prompt V2 Accuracy: {v2_report.accuracy:.2%}",
        f"Delta: {v2_report.accuracy - v1_report.accuracy:+.2%}",
        "",
        "Accuracy by Failure Type",
    ]

    for failure_type in ExperimentalFailureType:
        lines.append(
            f"- {failure_type}: "
            f"V1 {_type_accuracy(v1_report, failure_type):.2%} "
            f"({ _type_correct(v1_report, failure_type) }/{ _type_total(v1_report, failure_type) }) | "
            f"V2 {_type_accuracy(v2_report, failure_type):.2%} "
            f"({ _type_correct(v2_report, failure_type) }/{ _type_total(v2_report, failure_type) })"
        )

    lines.extend(
        [
            "",
            "==================================",
        ]
    )
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare FailureAnalyzer prompt V1 and experimental prompt V2."
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
        help="Maximum number of cases to run for each prompt",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full comparison report as JSON",
    )
    return parser


def _type_total(
    report: FailureClassificationReport,
    failure_type: ExperimentalFailureType,
) -> int:
    return report.by_type.get(failure_type, {}).get("total", 0)


def _type_correct(
    report: FailureClassificationReport,
    failure_type: ExperimentalFailureType,
) -> int:
    return report.by_type.get(failure_type, {}).get("correct", 0)


def _type_accuracy(
    report: FailureClassificationReport,
    failure_type: ExperimentalFailureType,
) -> float:
    total = _type_total(report, failure_type)
    return _type_correct(report, failure_type) / total if total else 0.0


def _format_error(error: BaseException) -> str:
    if isinstance(error, FileNotFoundError):
        return f"File not found: {error.filename or error}"
    return str(error)


if __name__ == "__main__":
    raise SystemExit(main())
