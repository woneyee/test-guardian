"""OpenAI-backed TestPatchAgent implementation."""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

from test_guardian.agents.failure_analyzer.openai import DEFAULT_MODEL
from test_guardian.models.requirements import ExtractedRequirement
from test_guardian.models.test_audit import TestAuditResult
from test_guardian.models.test_patch import TestPatchProposal

_INSTRUCTIONS = """\
You are a TestPatchAgent for a TDD/CI repair system.

Generate a test patch proposal for a failure that has already been audited as a test bug.
Do not modify files. Do not produce a git patch. Return only a structured proposal.

Choose exactly one patch_type:
- ASSERTION_FIX: fix an incorrect expected value or assertion.
- EXCEPTION_FIX: fix an incorrect expected exception type or exception assertion.
- INPUT_FIX: fix test input that is outside the requirement's allowed scope.
- REQUIREMENT_SYNC: update a stale test to match a changed requirement.

Mapping rules:
- WRONG_ASSERTION -> ASSERTION_FIX
- WRONG_EXCEPTION -> EXCEPTION_FIX
- WRONG_INPUT -> INPUT_FIX
- OUTDATED_TEST -> REQUIREMENT_SYNC

The before field should contain the relevant existing test code snippet.
The after field should contain the proposed replacement snippet.
The justification should be concise and grounded in the requirement and test audit.
The confidence must be between 0 and 1.
"""


class OpenAITestPatchAgent:
    """Generate test patch proposals with OpenAI structured output."""

    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str | None = None,
    ) -> None:
        self._client = client or OpenAI()
        self._model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    def generate(
        self,
        requirement: ExtractedRequirement,
        test_audit: TestAuditResult,
        test_code: str,
    ) -> TestPatchProposal:
        response = self._client.responses.parse(
            model=self._model,
            instructions=_INSTRUCTIONS,
            input=_format_input(requirement, test_audit, test_code),
            text_format=TestPatchProposal,
            temperature=0,
        )

        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("OpenAI response did not include parsed test patch proposal.")

        return parsed


def _format_input(
    requirement: ExtractedRequirement,
    test_audit: TestAuditResult,
    test_code: str,
) -> str:
    return f"""\
Requirement:
Feature: {requirement.feature}
Requirement: {requirement.requirement}
Sources: {", ".join(requirement.sources) if requirement.sources else "N/A"}

Test Audit:
Reason Type: {test_audit.reason_type}
Confidence: {test_audit.confidence}
Reason: {test_audit.reason}

Test Code:
{test_code}
"""
