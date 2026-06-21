"""Test audit models."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from test_guardian.models.common import StrictStrEnum


class TestBugReason(StrictStrEnum):
    """Supported test-bug reason types for the MVP Test Auditor."""

    WRONG_ASSERTION = "WRONG_ASSERTION"
    WRONG_EXCEPTION = "WRONG_EXCEPTION"
    WRONG_INPUT = "WRONG_INPUT"
    OUTDATED_TEST = "OUTDATED_TEST"


class TestAuditResult(BaseModel):
    """Structured result produced by a Test Auditor."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    reason_type: TestBugReason
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    reason: str = Field(min_length=1)
