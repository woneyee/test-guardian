import unittest

from test_guardian.models.failure import FailureAnalysisInput, FailureAnalysisResult
from test_guardian.models.pipeline import PipelineResult
from test_guardian.models.requirements import ExtractedRequirement, RequirementInput
from test_guardian.models.routing import RouteTarget, RoutingResult
from test_guardian.models.test_audit import TestAuditResult, TestBugReason
from test_guardian.pipeline import GuardianPipeline


class FakeRequirementExtractor:
    def __init__(self, requirement: ExtractedRequirement) -> None:
        self.requirement = requirement
        self.calls = []

    def extract(self, input_data: RequirementInput) -> ExtractedRequirement:
        self.calls.append(input_data)
        return self.requirement


class FakeFailureAnalyzer:
    def __init__(self, result: FailureAnalysisResult) -> None:
        self.result = result
        self.calls: list[FailureAnalysisInput] = []

    def analyze(self, input_data: FailureAnalysisInput) -> FailureAnalysisResult:
        self.calls.append(input_data)
        return self.result


class FakeRouter:
    def __init__(self, result: RoutingResult) -> None:
        self.result = result
        self.calls: list[FailureAnalysisResult] = []

    def route(self, analysis: FailureAnalysisResult) -> RoutingResult:
        self.calls.append(analysis)
        return self.result


class FakeTestAuditor:
    def __init__(self, result: TestAuditResult) -> None:
        self.result = result
        self.calls: list[FailureAnalysisInput] = []

    def audit(self, input_data: FailureAnalysisInput) -> TestAuditResult:
        self.calls.append(input_data)
        return self.result


class GuardianPipelineTests(unittest.TestCase):
    def test_code_bug_path_does_not_call_test_auditor(self) -> None:
        pipeline, auditor = self._pipeline(
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

        result = pipeline.run(
            requirement_input=RequirementInput(readme="# Discount"),
            source_code="def discount(): return 0",
            test_code="assert discount() == 10",
            ci_log="AssertionError",
        )

        self.assertIsInstance(result, PipelineResult)
        self.assertEqual(result.failure_analysis.failure_type, "CODE_BUG")
        self.assertEqual(result.routing.target, RouteTarget.CODING_AGENT)
        self.assertIsNone(result.test_audit)
        self.assertEqual(auditor.calls, [])

    def test_test_bug_path_calls_test_auditor(self) -> None:
        pipeline, auditor = self._pipeline(
            failure_analysis=FailureAnalysisResult(
                failure_type="TEST_BUG",
                confidence=0.87,
                reason="Test contradicts the requirement.",
            ),
            routing=RoutingResult(
                target=RouteTarget.TEST_AUDITOR,
                reason="TEST_BUG failures are routed to the test auditor.",
            ),
        )

        result = pipeline.run(
            requirement_input=RequirementInput(readme="# Discount"),
            source_code="def discount(): return 10",
            test_code="assert discount() == 20",
            ci_log="AssertionError",
        )

        self.assertIsInstance(result, PipelineResult)
        self.assertEqual(result.failure_analysis.failure_type, "TEST_BUG")
        self.assertEqual(result.routing.target, RouteTarget.TEST_AUDITOR)
        self.assertIsNotNone(result.test_audit)
        self.assertEqual(result.test_audit.reason_type, TestBugReason.WRONG_ASSERTION)
        self.assertEqual(len(auditor.calls), 1)

    def _pipeline(
        self,
        *,
        failure_analysis: FailureAnalysisResult,
        routing: RoutingResult,
    ) -> tuple[GuardianPipeline, FakeTestAuditor]:
        requirement = ExtractedRequirement(
            feature="Discount",
            requirement="discount = 10%",
            sources=["README.md"],
        )
        auditor = FakeTestAuditor(
            TestAuditResult(
                reason_type=TestBugReason.WRONG_ASSERTION,
                confidence=0.92,
                reason="The test expects the wrong value.",
            )
        )

        return (
            GuardianPipeline(
                requirement_extractor=FakeRequirementExtractor(requirement),
                failure_analyzer=FakeFailureAnalyzer(failure_analysis),
                router=FakeRouter(routing),
                test_auditor=auditor,
            ),
            auditor,
        )


if __name__ == "__main__":
    unittest.main()
