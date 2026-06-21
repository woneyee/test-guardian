"""Simple deterministic failure router."""

from test_guardian.models.failure import FailureAnalysisResult, FailureType
from test_guardian.models.routing import RouteTarget, RoutingResult


class SimpleFailureRouter:
    """Route CODE_BUG to coding agent and TEST_BUG to test auditor."""

    def route(self, analysis: FailureAnalysisResult) -> RoutingResult:
        if analysis.failure_type == FailureType.CODE_BUG:
            return RoutingResult(
                target=RouteTarget.CODING_AGENT,
                reason="CODE_BUG failures are routed to the coding agent.",
            )

        return RoutingResult(
            target=RouteTarget.TEST_AUDITOR,
            reason="TEST_BUG failures are routed to the test auditor.",
        )
