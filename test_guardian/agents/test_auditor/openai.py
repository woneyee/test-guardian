"""OpenAI-backed Test Auditor implementation."""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

from test_guardian.agents.failure_analyzer.openai import DEFAULT_MODEL
from test_guardian.models.failure import FailureAnalysisInput
from test_guardian.models.test_audit import TestAuditResult

_INSTRUCTIONS = """\
You are a Test Auditor for a TDD/CI repair system.

Analyze a failure that has already been classified as TEST_BUG.
Classify the concrete test bug reason as exactly one of:
- WRONG_ASSERTION: the test expects an incorrect result.
- WRONG_EXCEPTION: the test validates the wrong exception type or exception behavior.
- WRONG_INPUT: the test uses input outside the requirement's allowed scope.
- OUTDATED_TEST: the test is stale after a requirement change.

Return only the structured result. The confidence must be between 0 and 1.
The reason should be concise and grounded in the requirement, source code, test code, and CI log.
Do not generate patches or rewritten tests.
"""


class OpenAITestAuditor:
    """Audit TEST_BUG failures with OpenAI structured output."""

    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str | None = None,
    ) -> None:
        self._client = client or OpenAI()
        self._model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    def audit(self, input_data: FailureAnalysisInput) -> TestAuditResult:
        response = self._client.responses.parse(
            model=self._model,
            instructions=_INSTRUCTIONS,
            input=_format_input(input_data),
            text_format=TestAuditResult,
            temperature=0,
        )

        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("OpenAI response did not include parsed test audit.")

        return parsed


def _format_input(input_data: FailureAnalysisInput) -> str:
    requirement = input_data.requirement

    return f"""\
Requirement:
Feature: {requirement.feature}
Requirement: {requirement.requirement}
Sources: {", ".join(requirement.sources) if requirement.sources else "N/A"}

Source Code:
{input_data.source_code}

Test Code:
{input_data.test_code}

CI Log:
{input_data.ci_log}
"""
