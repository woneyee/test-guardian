"""Command-line adversarial evaluation runner."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from test_guardian.cli.run import _build_pipeline
from test_guardian.models.adversarial import AdversarialEvaluationReport
from test_guardian.agents.test_patch_agent.openai import OpenAITestPatchAgent
from test_guardian.evaluation.adversarial import (
    AdversarialEvaluationRunner,
    OpenAICodeGenerator,
    OpenAITestGenerator,
    load_requirements,
)


def main(
    argv: Sequence[str] | None = None,
    *,
    runner: AdversarialEvaluationRunner | None = None,
) -> int:
    parser = argparse.ArgumentParser(description="Run adversarial Test Guardian evaluation.")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of adversarial cases to run",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full evaluation report as JSON",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-case evaluation details after the summary",
    )
    args = parser.parse_args(argv)

    try:
        if args.limit is not None and args.limit < 0:
            raise ValueError("--limit must be greater than or equal to 0")

        active_runner = runner or AdversarialEvaluationRunner(
            pipeline=_build_pipeline(),
            patch_agent=OpenAITestPatchAgent(),
            code_generator=OpenAICodeGenerator(),
            test_generator=OpenAITestGenerator(),
            requirements=_limited_requirements(args.limit),
        )
        report = active_runner.run()
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report.model_dump(mode="json"), indent=2))
    else:
        print(format_report(report, verbose=args.verbose))
    return 0


def _limited_requirements(limit: int | None):
    requirements = load_requirements()
    if limit is None:
        return requirements
    return requirements[:limit]


def format_report(
    report: AdversarialEvaluationReport,
    *,
    verbose: bool = False,
) -> str:
    lines = [
        "==================================",
        "",
        "Adversarial Evaluation",
        "",
        f"Total Cases: {report.total_cases}",
        "",
        f"Failure Accuracy: {report.failure_accuracy:.0%}",
        "",
        f"Reason Accuracy: {report.reason_accuracy:.0%}",
        "",
        f"Patch Accuracy: {report.patch_accuracy:.0%}",
        "",
        "==================================",
    ]

    if verbose:
        lines.extend(_format_case_details(report))

    return "\n".join(lines)


def _format_case_details(report: AdversarialEvaluationReport) -> list[str]:
    lines = ["", "Case Details", ""]

    for index, result in enumerate(report.results, start=1):
        lines.extend(
        [
                f"[{index}] success={result.success}",
                f"Requirement: {result.requirement}",
                f"Expected Reason: {result.expected_reason_type}",
                f"Predicted Failure: {result.predicted_failure_type}",
                f"Predicted Reason: {result.predicted_reason_type}",
                f"Patch Type: {result.patch_type}",
            "",
        ]
    )

    return lines


if __name__ == "__main__":
    raise SystemExit(main())
