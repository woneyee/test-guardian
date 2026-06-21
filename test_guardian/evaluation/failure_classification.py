"""Evaluation runner for 4-class FailureAnalyzer classification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from pydantic import ValidationError

from test_guardian.models.failure import (
    ExperimentalFailureAnalysisResult,
    ExperimentalFailureType,
    FailureAnalysisInput,
)
from test_guardian.models.failure_evaluation import (
    FailureClassificationCaseResult,
    FailureClassificationFixture,
    FailureClassificationReport,
)
from test_guardian.models.requirements import ExtractedRequirement

DEFAULT_FAILURE_CLASSIFICATION_DATASET_PATH = (
    Path("tests") / "fixtures" / "failure_classification_eval.json"
)


class FailureAnalyzerLike(Protocol):
    """Minimal FailureAnalyzer contract used by the evaluation runner."""

    def analyze(self, input_data: FailureAnalysisInput) -> ExperimentalFailureAnalysisResult:
        """Analyze one failure fixture."""


class FailureClassificationEvaluationRunner:
    """Run labeled fixtures through a FailureAnalyzer and score predictions."""

    def __init__(
        self,
        *,
        analyzer: FailureAnalyzerLike,
        dataset_path: Path | str = DEFAULT_FAILURE_CLASSIFICATION_DATASET_PATH,
        limit: int | None = None,
    ) -> None:
        self._analyzer = analyzer
        self._dataset_path = Path(dataset_path)
        self._limit = limit

    def run(self) -> FailureClassificationReport:
        fixtures = load_failure_classification_dataset(self._dataset_path)
        if self._limit is not None:
            if self._limit < 0:
                raise ValueError("limit must be greater than or equal to 0")
            fixtures = fixtures[: self._limit]
        results = [
            self._evaluate_fixture(index, fixture)
            for index, fixture in enumerate(fixtures, start=1)
        ]
        return generate_failure_classification_report(results)

    def _evaluate_fixture(
        self,
        index: int,
        fixture: FailureClassificationFixture,
    ) -> FailureClassificationCaseResult:
        analysis = self._analyzer.analyze(
            FailureAnalysisInput(
                requirement=ExtractedRequirement(
                    feature=f"Failure classification case {index}",
                    requirement=fixture.requirement,
                    sources=["failure_classification_eval.json"],
                ),
                source_code=fixture.source_code,
                test_code=fixture.test_code,
                ci_log=fixture.ci_log,
            )
        )
        return FailureClassificationCaseResult(
            expected_failure_type=fixture.expected_failure_type,
            predicted_failure_type=analysis.failure_type,
            confidence=analysis.confidence,
            reason=analysis.reason,
            correct=fixture.expected_failure_type == analysis.failure_type,
        )


def load_failure_classification_dataset(
    dataset_path: Path | str = DEFAULT_FAILURE_CLASSIFICATION_DATASET_PATH,
) -> list[FailureClassificationFixture]:
    path = Path(dataset_path)
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Failure classification dataset must be a JSON array.")

    fixtures: list[FailureClassificationFixture] = []
    errors: list[str] = []

    for index, record in enumerate(records):
        try:
            fixtures.append(FailureClassificationFixture.model_validate(record))
        except ValidationError as error:
            errors.append(f"{path.name}[{index}]: {error}")

    if errors:
        raise ValueError("\n".join(errors))

    return fixtures


def generate_failure_classification_report(
    results: list[FailureClassificationCaseResult],
) -> FailureClassificationReport:
    total_cases = len(results)
    correct = sum(result.correct for result in results)
    by_type = {
        failure_type: {"total": 0, "correct": 0}
        for failure_type in ExperimentalFailureType
    }

    for result in results:
        bucket = by_type[result.expected_failure_type]
        bucket["total"] += 1
        if result.correct:
            bucket["correct"] += 1

    return FailureClassificationReport(
        total_cases=total_cases,
        accuracy=correct / total_cases if total_cases else 0.0,
        correct=correct,
        incorrect=total_cases - correct,
        by_type=by_type,
        results=results,
    )
