import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import run
from test_guardian.models.failure import FailureAnalysisResult
from test_guardian.models.pipeline import PipelineResult
from test_guardian.models.requirements import ExtractedRequirement
from test_guardian.models.routing import RouteTarget, RoutingResult


class FakePipeline:
    def __init__(self) -> None:
        self.calls = []

    def run(self, **kwargs) -> PipelineResult:
        self.calls.append(kwargs)
        return PipelineResult(
            requirement=ExtractedRequirement(
                feature="Discount",
                requirement="discount = 10%",
                sources=["README.md", "Issue.md"],
            ),
            failure_analysis=FailureAnalysisResult(
                failure_type="CODE_BUG",
                confidence=0.91,
                reason="Implementation violates the requirement.",
            ),
            routing=RoutingResult(
                target=RouteTarget.CODING_AGENT,
                reason="CODE_BUG failures are routed to the coding agent.",
            ),
        )


class RunCliTests(unittest.TestCase):
    def test_missing_arguments(self) -> None:
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = run.main([])

        self.assertEqual(exit_code, 1)
        self.assertIn("Missing required argument", stderr.getvalue())

    def test_file_not_found(self) -> None:
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = run.main(
                [
                    "--readme",
                    "missing-readme.md",
                    "--issue",
                    "missing-issue.md",
                    "--source",
                    "missing-source.py",
                    "--test",
                    "missing-test.py",
                    "--log",
                    "missing.log",
                ],
                pipeline=FakePipeline(),
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("File not found: missing-readme.md", stderr.getvalue())

    def test_successful_execution(self) -> None:
        pipeline = FakePipeline()

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            readme = self._write(root, "README.md", "# Discount")
            issue = self._write(root, "ISSUE.md", "discount = 10%")
            source = self._write(root, "calculator.py", "def discount(): return 0")
            test = self._write(root, "test_calculator.py", "assert discount() == 10")
            log = self._write(root, "ci.log", "AssertionError")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = run.main(
                    [
                        "--readme",
                        str(readme),
                        "--issue",
                        str(issue),
                        "--source",
                        str(source),
                        "--test",
                        str(test),
                        "--log",
                        str(log),
                    ],
                    pipeline=pipeline,
                )

        payload = json.loads(stdout.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["failure_analysis"]["failure_type"], "CODE_BUG")
        self.assertEqual(payload["routing"]["target"], "coding_agent")
        self.assertEqual(len(pipeline.calls), 1)

    def _write(self, root: Path, name: str, content: str) -> Path:
        path = root / name
        path.write_text(content, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
