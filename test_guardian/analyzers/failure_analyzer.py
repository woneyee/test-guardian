"""OpenAI-backed failure responsibility analyzer."""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

from test_guardian.models.failure import (
    FailureAnalysisInput,
    FailureAnalysisResult,
)

DEFAULT_MODEL = "gpt-4.1-mini"

_INSTRUCTIONS = """\
You are a failure responsibility analyzer for a TDD/CI repair system.

Classify the failed test responsibility as exactly one of:
- CODE_BUG: the implementation likely violates the stated requirement.
- TEST_BUG: the test likely violates the stated requirement, is invalid, or is unrunnable.

Return only the structured result. The confidence must be between 0 and 1.
The reason should be concise and grounded in the requirement, source code, test code, and CI log.
"""


class OpenAIFailureAnalyzer:
    """Classify failure responsibility with OpenAI structured output."""

    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str | None = None,
    ) -> None:
        self._client = client or OpenAI()
        self._model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    def analyze(self, input_data: FailureAnalysisInput) -> FailureAnalysisResult:
        response = self._client.responses.parse(
            model=self._model,
            instructions=_INSTRUCTIONS,
            input=_format_input(input_data),
            text_format=FailureAnalysisResult,
            temperature=0,
        )

        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("OpenAI response did not include parsed failure analysis.")

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
