import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import failure_classification_evaluate
from test_guardian.models.failure_evaluation import FailureClassificationReport


class FakeRunner:
    def __init__(self, report: FailureClassificationReport) -> None:
        self.report = report
        self.calls = 0

    def run(self) -> FailureClassificationReport:
        self.calls += 1
        return self.report


class FailureClassificationEvaluateCliTests(unittest.TestCase):
    def test_file_not_found(self) -> None:
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = failure_classification_evaluate.main(
                ["--dataset", "missing.json"]
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("File not found: missing.json", stderr.getvalue())

    def test_successful_execution(self) -> None:
        runner = FakeRunner(self._report())

        with tempfile.TemporaryDirectory() as temp_dir:
            dataset = Path(temp_dir) / "dataset.json"
            dataset.write_text("[]", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = failure_classification_evaluate.main(
                    ["--dataset", str(dataset)],
                    runner=runner,
                )

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertEqual(runner.calls, 1)
        self.assertIn("Failure Classification Evaluation", output)
        self.assertIn("Accuracy: 75.00%", output)
        self.assertIn("- CODE_BUG: 1/1 (100.00%)", output)

    def test_json_output(self) -> None:
        runner = FakeRunner(self._report())

        with tempfile.TemporaryDirectory() as temp_dir:
            dataset = Path(temp_dir) / "dataset.json"
            dataset.write_text("[]", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = failure_classification_evaluate.main(
                    ["--dataset", str(dataset), "--json"],
                    runner=runner,
                )

        payload = json.loads(stdout.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["total_cases"], 4)
        self.assertEqual(payload["accuracy"], 0.75)

    def _report(self) -> FailureClassificationReport:
        return FailureClassificationReport(
            total_cases=4,
            accuracy=0.75,
            correct=3,
            incorrect=1,
            by_type={
                "CODE_BUG": {"total": 1, "correct": 1},
                "TEST_BUG": {"total": 1, "correct": 0},
                "BOTH": {"total": 1, "correct": 1},
                "UNKNOWN": {"total": 1, "correct": 1},
            },
            results=[],
        )


if __name__ == "__main__":
    unittest.main()
