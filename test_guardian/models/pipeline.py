"""Pipeline runner models."""

from pydantic import BaseModel, ConfigDict

from test_guardian.models.failure import FailureAnalysisResult
from test_guardian.models.requirements import ExtractedRequirement
from test_guardian.models.routing import RoutingResult
from test_guardian.models.test_audit import TestAuditResult


class PipelineResult(BaseModel):
    """Single result object returned by the Guardian pipeline."""

    model_config = ConfigDict(extra="forbid")

    requirement: ExtractedRequirement
    failure_analysis: FailureAnalysisResult
    routing: RoutingResult
    test_audit: TestAuditResult | None = None
