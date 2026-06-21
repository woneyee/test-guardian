import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import failure_classification_evaluate_v2
from test_guardian.models.failure_evaluation import FailureClassificationReport


class FakeRunner:
    def __init__(self, report: FailureClassificationReport) -> None:
        self.report = report
        self.calls = 0

    def run(self) -> FailureClassificationReport:
        self.calls += 1
        return self.report


class FailureClassificationEvaluateV2Tests(unittest.TestCase):
    def test_file_not_found(self) -> None:
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = failure_classification_evaluate_v2.main(
                ["--dataset", "missing.json"]
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("File not found: missing.json", stderr.getvalue())

    def test_successful_comparison(self) -> None:
        v1 = FakeRunner(self._report(accuracy=0.5, both_correct=1, unknown_correct=1))
        v2 = FakeRunner(self._report(accuracy=0.75, both_correct=2, unknown_correct=2))

        with tempfile.TemporaryDirectory() as temp_dir:
            dataset = Path(temp_dir) / "dataset.json"
            dataset.write_text("[]", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = failure_classification_evaluate_v2.main(
                    ["--dataset", str(dataset)],
                    v1_runner=v1,
                    v2_runner=v2,
                )

        output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertEqual(v1.calls, 1)
        self.assertEqual(v2.calls, 1)
        self.assertIn("Failure Analyzer Prompt Comparison", output)
        self.assertIn("Prompt V1 Accuracy: 50.00%", output)
        self.assertIn("Prompt V2 Accuracy: 75.00%", output)
        self.assertIn("Delta: +25.00%", output)

    def test_json_output(self) -> None:
        v1 = FakeRunner(self._report(accuracy=0.5, both_correct=1, unknown_correct=1))
        v2 = FakeRunner(self._report(accuracy=0.75, both_correct=2, unknown_correct=2))

        with tempfile.TemporaryDirectory() as temp_dir:
            dataset = Path(temp_dir) / "dataset.json"
            dataset.write_text("[]", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = failure_classification_evaluate_v2.main(
                    ["--dataset", str(dataset), "--json"],
                    v1_runner=v1,
                    v2_runner=v2,
                )

        payload = json.loads(stdout.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["v1"]["accuracy"], 0.5)
        self.assertEqual(payload["v2"]["accuracy"], 0.75)
        self.assertEqual(payload["delta_accuracy"], 0.25)

    def _report(
        self,
        *,
        accuracy: float,
        both_correct: int,
        unknown_correct: int,
    ) -> FailureClassificationReport:
        return FailureClassificationReport(
            total_cases=4,
            accuracy=accuracy,
            correct=int(accuracy * 4),
            incorrect=4 - int(accuracy * 4),
            by_type={
                "CODE_BUG": {"total": 1, "correct": 1},
                "TEST_BUG": {"total": 1, "correct": 1},
                "BOTH": {"total": 1, "correct": both_correct},
                "UNKNOWN": {"total": 1, "correct": unknown_correct},
            },
            results=[],
        )


if __name__ == "__main__":
    unittest.main()
