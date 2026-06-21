import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import adversarial_evaluate
from test_guardian.models.adversarial import (
    AdversarialEvaluationReport,
    AdversarialEvaluationResult,
    AdversarialRequirement,
)
from test_guardian.models.test_audit import TestBugReason


class FakeRunner:
    def __init__(self, report: AdversarialEvaluationReport) -> None:
        self.report = report
        self.calls = 0

    def run(self) -> AdversarialEvaluationReport:
        self.calls += 1
        return self.report


class AdversarialEvaluateCliTests(unittest.TestCase):
    def test_successful_execution(self) -> None:
        runner = FakeRunner(
            self._report()
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = adversarial_evaluate.main([], runner=runner)

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertEqual(runner.calls, 1)
        self.assertIn("Adversarial Evaluation", output)
        self.assertIn("Total Cases: 20", output)
        self.assertIn("Failure Accuracy: 95%", output)
        self.assertIn("Reason Accuracy: 90%", output)
        self.assertIn("Patch Accuracy: 90%", output)

    def test_json_output(self) -> None:
        runner = FakeRunner(self._report())

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = adversarial_evaluate.main(["--json"], runner=runner)

        payload = json.loads(stdout.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["total_cases"], 20)
        self.assertEqual(payload["failure_accuracy"], 0.95)
        self.assertEqual(payload["results"][0]["predicted_failure_type"], "TEST_BUG")
        self.assertEqual(payload["results"][0]["patch_type"], "ASSERTION_FIX")

    def test_verbose_output_includes_case_details(self) -> None:
        runner = FakeRunner(self._report())

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = adversarial_evaluate.main(["--verbose"], runner=runner)

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("Case Details", output)
        self.assertIn("[1] success=True", output)
        self.assertIn("Expected Reason: WRONG_ASSERTION", output)
        self.assertIn("Patch Type: ASSERTION_FIX", output)

    def test_limit_slices_requirements(self) -> None:
        requirements = [
            AdversarialRequirement(
                category="Async",
                requirement=f"Requirement {index}",
                expected_reason_type=TestBugReason.WRONG_ASSERTION,
            )
            for index in range(5)
        ]

        with patch.object(adversarial_evaluate, "load_requirements", return_value=requirements):
            limited = adversarial_evaluate._limited_requirements(3)

        self.assertEqual(len(limited), 3)
        self.assertEqual(limited[0].requirement, "Requirement 0")
        self.assertEqual(limited[-1].requirement, "Requirement 2")

    def _report(self) -> AdversarialEvaluationReport:
        return AdversarialEvaluationReport(
            total_cases=20,
            failure_accuracy=0.95,
            reason_accuracy=0.9,
            patch_accuracy=0.9,
            failure_correct=19,
            reason_correct=18,
            patch_correct=18,
            results=[
                AdversarialEvaluationResult(
                    requirement="Return ACCEPTED immediately.",
                    expected_reason_type="WRONG_ASSERTION",
                    predicted_failure_type="TEST_BUG",
                    predicted_reason_type="WRONG_ASSERTION",
                    patch_type="ASSERTION_FIX",
                    success=True,
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
