import unittest

from test_guardian.models.failure import FailureAnalysisResult, FailureType
from test_guardian.models.routing import RouteTarget
from test_guardian.agents.router.simple import SimpleFailureRouter


class SimpleFailureRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = SimpleFailureRouter()

    def test_routes_code_bug_to_coding_agent(self) -> None:
        result = self.router.route(
            FailureAnalysisResult(
                failure_type=FailureType.CODE_BUG,
                confidence=0.9,
                reason="The implementation violates the requirement.",
            )
        )

        self.assertEqual(result.target, RouteTarget.CODING_AGENT)
        self.assertEqual(result.model_dump(mode="json")["target"], "coding_agent")
        self.assertIn("CODE_BUG", result.reason)

    def test_routes_test_bug_to_test_auditor(self) -> None:
        result = self.router.route(
            FailureAnalysisResult(
                failure_type=FailureType.TEST_BUG,
                confidence=0.85,
                reason="The test contradicts the requirement.",
            )
        )

        self.assertEqual(result.target, RouteTarget.TEST_AUDITOR)
        self.assertEqual(result.model_dump(mode="json")["target"], "test_auditor")
        self.assertIn("TEST_BUG", result.reason)

    def test_analysis_result_routes_to_coding_agent(self) -> None:
        analysis = FailureAnalysisResult(
            failure_type="CODE_BUG",
            confidence=0.91,
            reason="Requirement and test align.",
        )

        result = self.router.route(analysis)

        self.assertEqual(result.target, RouteTarget.CODING_AGENT)

    def test_analysis_result_routes_to_test_auditor(self) -> None:
        analysis = FailureAnalysisResult(
            failure_type="TEST_BUG",
            confidence=0.87,
            reason="Source matches requirement.",
        )

        result = self.router.route(analysis)

        self.assertEqual(result.target, RouteTarget.TEST_AUDITOR)

    def test_router_ignores_confidence(self) -> None:
        low_confidence = FailureAnalysisResult(
            failure_type="CODE_BUG",
            confidence=0.01,
            reason="Low confidence but still classified as CODE_BUG.",
        )
        high_confidence = FailureAnalysisResult(
            failure_type="CODE_BUG",
            confidence=0.99,
            reason="High confidence and classified as CODE_BUG.",
        )

        self.assertEqual(
            self.router.route(low_confidence).target,
            RouteTarget.CODING_AGENT,
        )
        self.assertEqual(
            self.router.route(high_confidence).target,
            RouteTarget.CODING_AGENT,
        )


if __name__ == "__main__":
    unittest.main()
