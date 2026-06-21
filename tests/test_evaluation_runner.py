import json
import tempfile
import unittest
from pathlib import Path

from test_guardian.models.evaluation import EvaluationFixture, EvaluationReport
from test_guardian.models.failure import FailureAnalysisResult
from test_guardian.models.pipeline import PipelineResult
from test_guardian.models.requirements import ExtractedRequirement
from test_guardian.models.routing import RouteTarget, RoutingResult
from test_guardian.models.test_audit import TestAuditResult, TestBugReason
from test_guardian.services.evaluation_runner import (
    EvaluationRunner,
    evaluate_failure_types,
    evaluate_reason_types,
    generate_report,
    load_dataset,
)


class FakePipeline:
    def __init__(self, results: list[PipelineResult]) -> None:
        self.results = results
        self.calls = []

    def run(self, **kwargs) -> PipelineResult:
        self.calls.append(kwargs)
        return self.results[len(self.calls) - 1]


class EvaluationRunnerTests(unittest.TestCase):
    def test_load_dataset(self) -> None:
        fixtures = load_dataset(Path("tests") / "fixtures" / "test_guardian_eval.json")

        self.assertEqual(len(fixtures), 25)
        self.assertIsInstance(fixtures[0], EvaluationFixture)

    def test_accuracy_calculation(self) -> None:
        fixtures = [
            self._fixture("CODE_BUG"),
            self._fixture("TEST_BUG", "WRONG_ASSERTION"),
            self._fixture("TEST_BUG", "WRONG_EXCEPTION"),
        ]
        results = [
            self._result("CODE_BUG"),
            self._result("TEST_BUG", "WRONG_ASSERTION"),
            self._result("TEST_BUG", "WRONG_INPUT"),
        ]

        self.assertEqual(evaluate_failure_types(fixtures, results), (3, 0))
        self.assertEqual(evaluate_reason_types(fixtures, results), (1, 1))

    def test_empty_dataset_report(self) -> None:
        report = generate_report([], [])

        self.assertEqual(report.total_cases, 0)
        self.assertEqual(report.failure_accuracy, 0.0)
        self.assertEqual(report.reason_accuracy, 0.0)
        self.assertEqual(report.failure_correct, 0)
        self.assertEqual(report.failure_incorrect, 0)
        self.assertEqual(report.reason_correct, 0)
        self.assertEqual(report.reason_incorrect, 0)

    def test_generate_report(self) -> None:
        fixtures = [
            self._fixture("CODE_BUG"),
            self._fixture("TEST_BUG", "WRONG_ASSERTION"),
            self._fixture("TEST_BUG", "WRONG_EXCEPTION"),
        ]
        results = [
            self._result("TEST_BUG", "WRONG_ASSERTION"),
            self._result("TEST_BUG", "WRONG_ASSERTION"),
            self._result("TEST_BUG", "WRONG_INPUT"),
        ]

        report = generate_report(fixtures, results)

        self.assertIsInstance(report, EvaluationReport)
        self.assertEqual(report.total_cases, 3)
        self.assertEqual(report.failure_correct, 2)
        self.assertEqual(report.failure_incorrect, 1)
        self.assertAlmostEqual(report.failure_accuracy, 2 / 3)
        self.assertEqual(report.reason_correct, 1)
        self.assertEqual(report.reason_incorrect, 1)
        self.assertEqual(report.reason_accuracy, 0.5)

    def test_runner_loads_dataset_and_generates_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            dataset_path = Path(temp_dir) / "dataset.json"
            dataset_path.write_text(
                json.dumps(
                    [
                        self._fixture("CODE_BUG").model_dump(mode="json"),
                        self._fixture(
                            "TEST_BUG",
                            "OUTDATED_TEST",
                        ).model_dump(mode="json"),
                    ]
                ),
                encoding="utf-8",
            )
            pipeline = FakePipeline(
                [
                    self._result("CODE_BUG"),
                    self._result("TEST_BUG", "OUTDATED_TEST"),
                ]
            )

            report = EvaluationRunner(
                pipeline=pipeline,
                dataset_path=dataset_path,
            ).run()

        self.assertEqual(report.total_cases, 2)
        self.assertEqual(report.failure_accuracy, 1.0)
        self.assertEqual(report.reason_accuracy, 1.0)
        self.assertEqual(len(pipeline.calls), 2)

    def _fixture(
        self,
        failure_type: str,
        reason_type: str | None = None,
    ) -> EvaluationFixture:
        return EvaluationFixture(
            requirement="discount = 10%",
            source_code="def discount(): return 10",
            test_code="assert discount() == 20",
            ci_log="AssertionError",
            expected_failure_type=failure_type,
            expected_reason_type=reason_type,
        )

    def _result(
        self,
        failure_type: str,
        reason_type: str | None = None,
    ) -> PipelineResult:
        test_audit = None
        if reason_type is not None:
            test_audit = TestAuditResult(
                reason_type=TestBugReason(reason_type),
                confidence=0.9,
                reason="Expected reason.",
            )

        return PipelineResult(
            requirement=ExtractedRequirement(
                feature="Discount",
                requirement="discount = 10%",
                sources=["README.md"],
            ),
            failure_analysis=FailureAnalysisResult(
                failure_type=failure_type,
                confidence=0.9,
                reason="Expected failure.",
            ),
            routing=RoutingResult(
                target=(
                    RouteTarget.CODING_AGENT
                    if failure_type == "CODE_BUG"
                    else RouteTarget.TEST_AUDITOR
                ),
                reason="Expected route.",
            ),
            test_audit=test_audit,
        )


if __name__ == "__main__":
    unittest.main()
