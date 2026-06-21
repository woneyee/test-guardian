"""Backward-compatible analyzer interface imports."""

from test_guardian.agents.base import Analyzer, FailureAnalyzer, RequirementExtractor

__all__ = [
    "Analyzer",
    "FailureAnalyzer",
    "RequirementExtractor",
]
