"""Routing models for failure responsibility results."""

from pydantic import BaseModel, ConfigDict, Field

from test_guardian.models.common import StrictStrEnum


class RouteTarget(StrictStrEnum):
    """Supported specialized-agent targets for the MVP router."""

    CODING_AGENT = "coding_agent"
    TEST_AUDITOR = "test_auditor"


class RoutingResult(BaseModel):
    """Decision produced by the failure router."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    target: RouteTarget
    reason: str = Field(min_length=1)
