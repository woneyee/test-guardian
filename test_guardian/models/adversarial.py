"""Adversarial evaluation models."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from test_guardian.models.common import StrictStrEnum
from test_guardian.models.failure import FailureType
from test_guardian.models.test_audit import TestBugReason
from test_guardian.models.test_patch import PatchType


class AdversarialCategory(StrictStrEnum):
    """Supported adversarial evaluation categories."""

    ASYNC = "Async"
    MOCK = "Mock"
    EXCEPTION = "Exception"
    FIXTURE_STATE = "Fixture / State"


class AdversarialRequirement(BaseModel):
    """Requirement and expected injected bug for one adversarial case."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    category: AdversarialCategory
    requirement: str = Field(min_length=1)
    expected_reason_type: TestBugReason


class GeneratedSourceCode(BaseModel):
    """Structured source-code generation output."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_code: str = Field(min_length=1)


class GeneratedTestCode(BaseModel):
    """Structured test-code generation output."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    test_code: str = Field(min_length=1)


class AdversarialEvaluationResult(BaseModel):
    """Single adversarial evaluation result."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    requirement: str
    expected_reason_type: TestBugReason
    predicted_failure_type: FailureType
    predicted_reason_type: TestBugReason | None = None
    patch_type: PatchType | None = None
    success: bool


class AdversarialEvaluationReport(BaseModel):
    """Aggregate adversarial evaluation metrics."""

    model_config = ConfigDict(extra="forbid")

    total_cases: int = Field(ge=0)
    failure_accuracy: Annotated[float, Field(ge=0.0, le=1.0)]
    reason_accuracy: Annotated[float, Field(ge=0.0, le=1.0)]
    patch_accuracy: Annotated[float, Field(ge=0.0, le=1.0)]
    failure_correct: int = Field(ge=0)
    reason_correct: int = Field(ge=0)
    patch_correct: int = Field(ge=0)
    results: list[AdversarialEvaluationResult] = Field(default_factory=list)
