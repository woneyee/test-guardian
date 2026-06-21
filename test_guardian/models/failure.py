"""Failure analysis models."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from test_guardian.models.common import StrictStrEnum
from test_guardian.models.requirements import ExtractedRequirement


class FailureType(StrictStrEnum):
    """Production failure responsibility classes."""

    CODE_BUG = "CODE_BUG"
    TEST_BUG = "TEST_BUG"


class ExperimentalFailureType(StrictStrEnum):
    """Experimental failure responsibility classes for evaluation only."""

    CODE_BUG = "CODE_BUG"
    TEST_BUG = "TEST_BUG"
    BOTH = "BOTH"
    UNKNOWN = "UNKNOWN"


class FailureAnalysisInput(BaseModel):
    """Inputs required to classify a test failure."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    requirement: ExtractedRequirement
    source_code: str = Field(min_length=1)
    test_code: str = Field(min_length=1)
    ci_log: str = Field(min_length=1)


class FailureAnalysisResult(BaseModel):
    """Structured result produced by a failure analyzer."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    failure_type: FailureType
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    reason: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)


class ExperimentalFailureAnalysisResult(BaseModel):
    """Structured result produced by experimental failure analyzers."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    failure_type: ExperimentalFailureType
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    reason: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)
