"""Evaluation runner models."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from test_guardian.models.failure import FailureType
from test_guardian.models.test_audit import TestBugReason


class EvaluationFixture(BaseModel):
    """Single labeled evaluation case."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    requirement: str = Field(min_length=1)
    source_code: str = Field(min_length=1)
    test_code: str = Field(min_length=1)
    ci_log: str = Field(min_length=1)
    expected_failure_type: FailureType
    expected_reason_type: TestBugReason | None = None

    @model_validator(mode="after")
    def validate_reason_type_matches_failure_type(self) -> "EvaluationFixture":
        if self.expected_failure_type == FailureType.CODE_BUG:
            if self.expected_reason_type is not None:
                raise ValueError("CODE_BUG fixtures must not define expected_reason_type.")
            return self

        if self.expected_reason_type is None:
            raise ValueError("TEST_BUG fixtures must define expected_reason_type.")
        return self


class EvaluationReport(BaseModel):
    """Aggregate evaluation metrics for Test Guardian."""

    model_config = ConfigDict(extra="forbid")

    total_cases: int = Field(ge=0)
    failure_accuracy: Annotated[float, Field(ge=0.0, le=1.0)]
    reason_accuracy: Annotated[float, Field(ge=0.0, le=1.0)]
    failure_correct: int = Field(ge=0)
    failure_incorrect: int = Field(ge=0)
    reason_correct: int = Field(ge=0)
    reason_incorrect: int = Field(ge=0)
