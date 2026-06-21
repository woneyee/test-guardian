"""Test patch proposal models."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from test_guardian.models.common import StrictStrEnum


class PatchType(StrictStrEnum):
    """Supported test patch proposal types for the MVP."""

    ASSERTION_FIX = "ASSERTION_FIX"
    EXCEPTION_FIX = "EXCEPTION_FIX"
    INPUT_FIX = "INPUT_FIX"
    REQUIREMENT_SYNC = "REQUIREMENT_SYNC"


class TestPatchProposal(BaseModel):
    """Structured test patch proposal produced by a TestPatchAgent."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    patch_type: PatchType
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    before: str = Field(min_length=1)
    after: str = Field(min_length=1)
    justification: str = Field(min_length=1)
