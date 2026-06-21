"""Test patch proposal agent interfaces."""

from typing import Protocol

from test_guardian.models.requirements import ExtractedRequirement
from test_guardian.models.test_audit import TestAuditResult
from test_guardian.models.test_patch import TestPatchProposal


class TestPatchAgent(Protocol):
    """Contract for generating test patch proposals without modifying files."""

    def generate(
        self,
        requirement: ExtractedRequirement,
        test_audit: TestAuditResult,
        test_code: str,
    ) -> TestPatchProposal:
        """Generate a structured test patch proposal."""
