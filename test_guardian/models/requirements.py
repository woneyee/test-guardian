"""Requirement extraction models."""

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RequirementInput(BaseModel):
    """Natural-language project material used to derive a requirement."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    readme: str | None = None
    issue: str | None = None

    @model_validator(mode="after")
    def require_at_least_one_source(self) -> "RequirementInput":
        if not self.readme and not self.issue:
            raise ValueError("At least one requirement source is required.")
        return self


class ExtractedRequirement(BaseModel):
    """Normalized feature requirement passed to failure analysis."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    feature: str = Field(min_length=1)
    requirement: str = Field(min_length=1)
    sources: list[str] = Field(default_factory=list)
