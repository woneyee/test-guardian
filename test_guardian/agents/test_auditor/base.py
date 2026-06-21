"""Test auditor interfaces for the Test Guardian MVP."""

from typing import Protocol

from test_guardian.models.failure import FailureAnalysisInput
from test_guardian.models.test_audit import TestAuditResult


class TestAuditor(Protocol):
    """Contract for analyzing the concrete cause of a test bug."""

    def audit(self, input_data: FailureAnalysisInput) -> TestAuditResult:
        """Audit a TEST_BUG failure and return a structured reason."""
