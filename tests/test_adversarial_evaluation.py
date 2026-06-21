import unittest

from test_guardian.models.adversarial import (
    AdversarialCategory,
    AdversarialEvaluationResult,
    AdversarialRequirement,
)
from test_guardian.models.failure import FailureAnalysisResult
from test_guardian.models.pipeline import PipelineResult
from test_guardian.models.requirements import ExtractedRequirement
from test_guardian.models.routing import RouteTarget, RoutingResult
from test_guardian.models.test_audit import TestAuditResult, TestBugReason
from test_guardian.models.test_patch import PatchType, TestPatchProposal
from test_guardian.evaluation.adversarial import (
    AdversarialEvaluationRunner,
    BugInjector,
    generate_adversarial_report,
    load_requirements,
)


class FakeCodeGenerator:
    def generate(self, requirement: str) -> str:
        return "def service(): return 'ACCEPTED'"


class FakeTestGenerator:
    def generate(self, requirement: str, source_code: str) -> str:
        return "def test_service():\n    assert service() == 'ACCEPTED'"


class FakePipeline:
    def __init__(self, reason_type: TestBugReason) -> None:
        self.reason_type = reason_type
        self.calls = []

    def run(self, **kwargs) -> PipelineResult:
        self.calls.append(kwargs)
        return PipelineResult(
            requirement=ExtractedRequirement(
                feature="Generated",
                requirement=kwargs["requirement_input"].readme,
                sources=["README.md"],
            ),
            failure_analysis=FailureAnalysisResult(
                failure_type="TEST_BUG",
                confidence=0.9,
                reason="The generated test is faulty.",
            ),
            routing=RoutingResult(
                target=RouteTarget.TEST_AUDITOR,
                reason="TEST_BUG failures are routed to the test auditor.",
            ),
            test_audit=TestAuditResult(
                reason_type=self.reason_type,
                confidence=0.9,
                reason="Expected reason.",
            ),
        )


class FakePatchAgent:
    def __init__(self, patch_type: PatchType) -> None:
        self.patch_type = patch_type
        self.calls = []

    def generate(self, requirement, test_audit, test_code: str) -> TestPatchProposal:
        self.calls.append((requirement, test_audit, test_code))
        return TestPatchProposal(
            patch_type=self.patch_type,
            confidence=0.9,
            before=test_code,
            after=test_code.replace("COMPLETED", "ACCEPTED"),
            justification="Expected patch.",
        )


class AdversarialEvaluationTests(unittest.TestCase):
    def test_load_requirements_returns_twenty_cases(self) -> None:
        requirements = load_requirements()

        self.assertEqual(len(requirements), 20)
        self.assertEqual(
            sum(item.category == AdversarialCategory.ASYNC for item in requirements),
            5,
        )
        self.assertEqual(
            sum(item.category == AdversarialCategory.MOCK for item in requirements),
            5,
        )
        self.assertEqual(
            sum(item.category == AdversarialCategory.EXCEPTION for item in requirements),
            5,
        )
        self.assertEqual(
            sum(item.category == AdversarialCategory.FIXTURE_STATE for item in requirements),
            5,
        )

    def test_bug_injector_injects_wrong_assertion(self) -> None:
        faulty = BugInjector().inject(
            "assert status == 'ACCEPTED'",
            TestBugReason.WRONG_ASSERTION,
        )

        self.assertIn("COMPLETED", faulty)

    def test_runner_generates_successful_result(self) -> None:
        requirement = AdversarialRequirement(
            category=AdversarialCategory.ASYNC,
            requirement="Return ACCEPTED immediately.",
            expected_reason_type=TestBugReason.WRONG_ASSERTION,
        )
        patch_agent = FakePatchAgent(PatchType.ASSERTION_FIX)
        runner = AdversarialEvaluationRunner(
            pipeline=FakePipeline(TestBugReason.WRONG_ASSERTION),
            patch_agent=patch_agent,
            code_generator=FakeCodeGenerator(),
            test_generator=FakeTestGenerator(),
            requirements=[requirement],
        )

        report = runner.run()

        self.assertEqual(report.total_cases, 1)
        self.assertEqual(report.failure_accuracy, 1.0)
        self.assertEqual(report.reason_accuracy, 1.0)
        self.assertEqual(report.patch_accuracy, 1.0)
        self.assertTrue(report.results[0].success)
        self.assertEqual(len(patch_agent.calls), 1)

    def test_generate_report_calculates_accuracy(self) -> None:
        results = [
            AdversarialEvaluationResult(
                requirement="A",
                expected_reason_type=TestBugReason.WRONG_ASSERTION,
                predicted_failure_type="TEST_BUG",
                predicted_reason_type="WRONG_ASSERTION",
                patch_type="ASSERTION_FIX",
                success=True,
            ),
            AdversarialEvaluationResult(
                requirement="B",
                expected_reason_type=TestBugReason.WRONG_EXCEPTION,
                predicted_failure_type="CODE_BUG",
                predicted_reason_type=None,
                patch_type=None,
                success=False,
            ),
        ]

        report = generate_adversarial_report(results)

        self.assertEqual(report.total_cases, 2)
        self.assertEqual(report.failure_accuracy, 0.5)
        self.assertEqual(report.reason_accuracy, 0.5)
        self.assertEqual(report.patch_accuracy, 0.5)


if __name__ == "__main__":
    unittest.main()
