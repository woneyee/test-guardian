"""Failure classification evaluation models."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from test_guardian.models.failure import ExperimentalFailureType


class FailureClassificationFixture(BaseModel):
    """Single labeled failure-classification evaluation case."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    requirement: str = Field(min_length=1)
    source_code: str = Field(min_length=1)
    test_code: str = Field(min_length=1)
    ci_log: str = Field(min_length=1)
    expected_failure_type: ExperimentalFailureType


class FailureClassificationCaseResult(BaseModel):
    """Prediction result for one failure-classification fixture."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    expected_failure_type: ExperimentalFailureType
    predicted_failure_type: ExperimentalFailureType
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    reason: str = Field(min_length=1)
    correct: bool


class FailureClassificationReport(BaseModel):
    """Aggregate metrics for FailureAnalyzer classification accuracy."""

    model_config = ConfigDict(extra="forbid")

    total_cases: int = Field(ge=0)
    accuracy: Annotated[float, Field(ge=0.0, le=1.0)]
    correct: int = Field(ge=0)
    incorrect: int = Field(ge=0)
    by_type: dict[ExperimentalFailureType, dict[str, int]] = Field(default_factory=dict)
    results: list[FailureClassificationCaseResult] = Field(default_factory=list)
