import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import evaluate
from test_guardian.models.evaluation import EvaluationReport


class FakeRunner:
    def __init__(self, report: EvaluationReport) -> None:
        self.report = report
        self.calls = 0

    def run(self) -> EvaluationReport:
        self.calls += 1
        return self.report


class EvaluateCliTests(unittest.TestCase):
    def test_file_not_found(self) -> None:
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = evaluate.main(["--dataset", "missing-dataset.json"])

        self.assertEqual(exit_code, 1)
        self.assertIn("File not found: missing-dataset.json", stderr.getvalue())

    def test_successful_execution(self) -> None:
        runner = FakeRunner(
            EvaluationReport(
                total_cases=25,
                failure_accuracy=0.96,
                reason_accuracy=0.95,
                failure_correct=24,
                failure_incorrect=1,
                reason_correct=19,
                reason_incorrect=1,
            )
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            dataset = Path(temp_dir) / "dataset.json"
            dataset.write_text("[]", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = evaluate.main(
                    ["--dataset", str(dataset)],
                    runner=runner,
                )

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertEqual(runner.calls, 1)
        self.assertIn("Test Guardian Evaluation", output)
        self.assertIn("Total Cases: 25", output)
        self.assertIn("Failure Accuracy: 96.00%", output)
        self.assertIn("Reason Accuracy: 95.00%", output)


if __name__ == "__main__":
    unittest.main()
