"""OpenAI-backed failure responsibility analyzer."""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

from test_guardian.models.failure import (
    ExperimentalFailureAnalysisResult,
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

_EXPERIMENTAL_V1_INSTRUCTIONS = """\
You are a failure responsibility analyzer for a TDD/CI repair system.

Classify the failed test responsibility as exactly one of:
- CODE_BUG: the implementation likely violates the stated requirement.
- TEST_BUG: the test likely violates the stated requirement, is invalid, or is unrunnable.
- BOTH: both the implementation and the test likely violate the stated requirement.
- UNKNOWN: there is not enough information to determine responsibility.

Return only the structured result. The confidence must be between 0 and 1.
The reason should be concise and grounded in the requirement, source code, test code, and CI log.
"""

_V2_INSTRUCTIONS = """\
You are a failure responsibility analyzer for a TDD/CI repair system.

Before selecting the final failure_type, internally answer these two questions:

1. Does the source code violate the requirement?
   Answer exactly one of: YES, NO, UNKNOWN.

2. Does the test code violate the requirement?
   Answer exactly one of: YES, NO, UNKNOWN.

Then apply this routing logic:

- Source=YES and Test=NO -> CODE_BUG
- Source=NO and Test=YES -> TEST_BUG
- Source=YES and Test=YES -> BOTH
- Source=UNKNOWN and Test=UNKNOWN -> UNKNOWN

Additional guidance:
- If source code and test code agree with each other but both contradict the requirement, choose BOTH.
- If the CI log or requirement is too vague to determine either side, choose UNKNOWN.
- If only one side can be determined and the other side is UNKNOWN, choose UNKNOWN unless the evidence strongly proves a single responsible side.
- Do not collapse BOTH into CODE_BUG or TEST_BUG just because one side appears more directly involved in the CI failure.

Return only the structured result. The confidence must be between 0 and 1.
The reason should briefly mention the internal Source/Test answers and be grounded in the requirement, source code, test code, and CI log.
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


class OpenAIFailureAnalyzerExperimentalV1:
    """Experimental 4-class prompt-v1 failure analyzer."""

    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str | None = None,
    ) -> None:
        self._client = client or OpenAI()
        self._model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    def analyze(self, input_data: FailureAnalysisInput) -> ExperimentalFailureAnalysisResult:
        response = self._client.responses.parse(
            model=self._model,
            instructions=_EXPERIMENTAL_V1_INSTRUCTIONS,
            input=_format_input(input_data),
            text_format=ExperimentalFailureAnalysisResult,
            temperature=0,
        )

        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("OpenAI response did not include parsed failure analysis.")

        return parsed


class OpenAIFailureAnalyzerV2:
    """Experimental prompt-v2 failure analyzer with explicit source/test checks."""

    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str | None = None,
    ) -> None:
        self._client = client or OpenAI()
        self._model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    def analyze(self, input_data: FailureAnalysisInput) -> ExperimentalFailureAnalysisResult:
        response = self._client.responses.parse(
            model=self._model,
            instructions=_V2_INSTRUCTIONS,
            input=_format_input(input_data),
            text_format=ExperimentalFailureAnalysisResult,
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
