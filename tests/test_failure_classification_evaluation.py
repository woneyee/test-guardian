import tempfile
import unittest
from pathlib import Path

from test_guardian.models.failure import (
    ExperimentalFailureAnalysisResult,
    ExperimentalFailureType,
    FailureAnalysisInput,
)
from test_guardian.models.failure_evaluation import (
    FailureClassificationCaseResult,
    FailureClassificationFixture,
)
from test_guardian.evaluation.failure_classification import (
    FailureClassificationEvaluationRunner,
    generate_failure_classification_report,
    load_failure_classification_dataset,
)


class FakeFailureAnalyzer:
    def __init__(self, predictions: list[ExperimentalFailureType]) -> None:
        self.predictions = predictions
        self.calls: list[FailureAnalysisInput] = []

    def analyze(self, input_data: FailureAnalysisInput) -> ExperimentalFailureAnalysisResult:
        self.calls.append(input_data)
        prediction = self.predictions[len(self.calls) - 1]
        return ExperimentalFailureAnalysisResult(
            failure_type=prediction,
            confidence=0.9,
            reason=f"Predicted {prediction}.",
        )


class FailureClassificationEvaluationTests(unittest.TestCase):
    def test_loads_dataset_with_expected_distribution(self) -> None:
        fixtures = load_failure_classification_dataset()

        self.assertEqual(len(fixtures), 32)
        self.assertEqual(_count(fixtures, ExperimentalFailureType.CODE_BUG), 8)
        self.assertEqual(_count(fixtures, ExperimentalFailureType.TEST_BUG), 8)
        self.assertEqual(_count(fixtures, ExperimentalFailureType.BOTH), 8)
        self.assertEqual(_count(fixtures, ExperimentalFailureType.UNKNOWN), 8)

    def test_runner_scores_predictions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            dataset_path = Path(temp_dir) / "dataset.json"
            dataset_path.write_text(
                """
                [
                  {
                    "requirement": "Requirement A",
                    "source_code": "def a(): pass",
                    "test_code": "def test_a(): pass",
                    "ci_log": "AssertionError",
                    "expected_failure_type": "CODE_BUG"
                  },
                  {
                    "requirement": "Requirement B",
                    "source_code": "def b(): pass",
                    "test_code": "def test_b(): pass",
                    "ci_log": "AssertionError",
                    "expected_failure_type": "TEST_BUG"
                  }
                ]
                """,
                encoding="utf-8",
            )
            analyzer = FakeFailureAnalyzer(
                [ExperimentalFailureType.CODE_BUG, ExperimentalFailureType.UNKNOWN]
            )
            report = FailureClassificationEvaluationRunner(
                analyzer=analyzer,
                dataset_path=dataset_path,
            ).run()

        self.assertEqual(report.total_cases, 2)
        self.assertEqual(report.correct, 1)
        self.assertEqual(report.incorrect, 1)
        self.assertEqual(report.accuracy, 0.5)
        self.assertEqual(len(analyzer.calls), 2)

    def test_generate_report_handles_empty_results(self) -> None:
        report = generate_failure_classification_report([])

        self.assertEqual(report.total_cases, 0)
        self.assertEqual(report.accuracy, 0.0)
        self.assertEqual(report.correct, 0)
        self.assertEqual(report.incorrect, 0)

    def test_generate_report_counts_by_type(self) -> None:
        report = generate_failure_classification_report(
            [
                _case(ExperimentalFailureType.CODE_BUG, ExperimentalFailureType.CODE_BUG),
                _case(ExperimentalFailureType.TEST_BUG, ExperimentalFailureType.CODE_BUG),
                _case(ExperimentalFailureType.BOTH, ExperimentalFailureType.BOTH),
                _case(ExperimentalFailureType.UNKNOWN, ExperimentalFailureType.UNKNOWN),
            ]
        )

        self.assertEqual(report.total_cases, 4)
        self.assertEqual(report.correct, 3)
        self.assertEqual(report.by_type[ExperimentalFailureType.CODE_BUG]["correct"], 1)
        self.assertEqual(report.by_type[ExperimentalFailureType.TEST_BUG]["correct"], 0)
        self.assertEqual(report.by_type[ExperimentalFailureType.BOTH]["correct"], 1)
        self.assertEqual(report.by_type[ExperimentalFailureType.UNKNOWN]["correct"], 1)


def _count(
    fixtures: list[FailureClassificationFixture],
    failure_type: ExperimentalFailureType,
) -> int:
    return sum(fixture.expected_failure_type == failure_type for fixture in fixtures)


def _case(
    expected: ExperimentalFailureType,
    predicted: ExperimentalFailureType,
) -> FailureClassificationCaseResult:
    return FailureClassificationCaseResult(
        expected_failure_type=expected,
        predicted_failure_type=predicted,
        confidence=0.9,
        reason="Expected reason.",
        correct=expected == predicted,
    )


if __name__ == "__main__":
    unittest.main()
