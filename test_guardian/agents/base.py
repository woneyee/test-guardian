"""Analyzer interfaces for the Test Guardian MVP."""

from typing import Protocol, TypeVar

from test_guardian.models.failure import FailureAnalysisInput, FailureAnalysisResult
from test_guardian.models.requirements import ExtractedRequirement, RequirementInput

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class Analyzer(Protocol[InputT, OutputT]):
    """Generic analyzer contract."""

    def analyze(self, input_data: InputT) -> OutputT:
        """Analyze typed input and return typed output."""


class RequirementExtractor(Protocol):
    """Contract for normalizing natural-language requirements."""

    def extract(self, input_data: RequirementInput) -> ExtractedRequirement:
        """Extract a normalized requirement."""


class FailureAnalyzer(Protocol):
    """Contract for classifying failure responsibility."""

    def analyze(self, input_data: FailureAnalysisInput) -> FailureAnalysisResult:
        """Classify a failure as a code bug or test bug."""
