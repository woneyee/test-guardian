"""Evaluation runner for labeled Test Guardian fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from pydantic import ValidationError

from test_guardian.models.evaluation import EvaluationFixture, EvaluationReport
from test_guardian.models.failure import FailureType
from test_guardian.models.pipeline import PipelineResult
from test_guardian.models.requirements import RequirementInput

DEFAULT_DATASET_PATH = Path("tests") / "fixtures" / "test_guardian_eval.json"


class PipelineLike(Protocol):
    """Minimal pipeline contract needed by the evaluation runner."""

    def run(
        self,
        *,
        requirement_input: RequirementInput,
        source_code: str,
        test_code: str,
        ci_log: str,
    ) -> PipelineResult:
        """Run one fixture through the pipeline."""


class EvaluationRunner:
    """Run labeled fixtures through a pipeline and produce an EvaluationReport."""

    def __init__(
        self,
        *,
        pipeline: PipelineLike,
        dataset_path: Path | str = DEFAULT_DATASET_PATH,
    ) -> None:
        self._pipeline = pipeline
        self._dataset_path = Path(dataset_path)

    def run(self) -> EvaluationReport:
        fixtures = load_dataset(self._dataset_path)
        results = [
            self._pipeline.run(
                requirement_input=RequirementInput(readme=fixture.requirement),
                source_code=fixture.source_code,
                test_code=fixture.test_code,
                ci_log=fixture.ci_log,
            )
            for fixture in fixtures
        ]

        return generate_report(fixtures, results)


def load_dataset(dataset_path: Path | str = DEFAULT_DATASET_PATH) -> list[EvaluationFixture]:
    path = Path(dataset_path)
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Evaluation dataset must be a JSON array.")

    fixtures: list[EvaluationFixture] = []
    errors: list[str] = []

    for index, record in enumerate(records):
        try:
            fixtures.append(EvaluationFixture.model_validate(record))
        except ValidationError as error:
            errors.append(f"{path.name}[{index}]: {error}")

    if errors:
        raise ValueError("\n".join(errors))

    return fixtures


def evaluate_failure_types(
    fixtures: list[EvaluationFixture],
    results: list[PipelineResult],
) -> tuple[int, int]:
    _validate_equal_lengths(fixtures, results)

    correct = sum(
        fixture.expected_failure_type == result.failure_analysis.failure_type
        for fixture, result in zip(fixtures, results)
    )
    return correct, len(fixtures) - correct


def evaluate_reason_types(
    fixtures: list[EvaluationFixture],
    results: list[PipelineResult],
) -> tuple[int, int]:
    _validate_equal_lengths(fixtures, results)

    test_bug_pairs = [
        (fixture, result)
        for fixture, result in zip(fixtures, results)
        if fixture.expected_failure_type == FailureType.TEST_BUG
    ]
    correct = sum(
        result.test_audit is not None
        and fixture.expected_reason_type == result.test_audit.reason_type
        for fixture, result in test_bug_pairs
    )
    return correct, len(test_bug_pairs) - correct


def generate_report(
    fixtures: list[EvaluationFixture],
    results: list[PipelineResult],
) -> EvaluationReport:
    _validate_equal_lengths(fixtures, results)

    total_cases = len(fixtures)
    failure_correct, failure_incorrect = evaluate_failure_types(fixtures, results)
    reason_correct, reason_incorrect = evaluate_reason_types(fixtures, results)
    total_test_bug_cases = reason_correct + reason_incorrect

    failure_accuracy = failure_correct / total_cases if total_cases else 0.0
    reason_accuracy = (
        reason_correct / total_test_bug_cases if total_test_bug_cases else 0.0
    )

    return EvaluationReport(
        total_cases=total_cases,
        failure_accuracy=failure_accuracy,
        reason_accuracy=reason_accuracy,
        failure_correct=failure_correct,
        failure_incorrect=failure_incorrect,
        reason_correct=reason_correct,
        reason_incorrect=reason_incorrect,
    )


def _validate_equal_lengths(
    fixtures: list[EvaluationFixture],
    results: list[PipelineResult],
) -> None:
    if len(fixtures) != len(results):
        raise ValueError("Fixture and result counts must match.")
