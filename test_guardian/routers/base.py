"""Router interfaces for the Test Guardian MVP."""

from typing import Protocol

from test_guardian.models.failure import FailureAnalysisResult
from test_guardian.models.routing import RoutingResult


class FailureRouter(Protocol):
    """Contract for routing failure analysis results to specialized agents."""

    def route(self, analysis: FailureAnalysisResult) -> RoutingResult:
        """Route the failure analysis result to the next agent target."""
