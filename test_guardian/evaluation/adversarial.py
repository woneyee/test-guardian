"""Adversarial evaluation runner for generated test-bug cases."""

from __future__ import annotations

import os
from typing import Any, Protocol

from openai import OpenAI

from test_guardian.agents.failure_analyzer.openai import DEFAULT_MODEL
from test_guardian.models.adversarial import (
    AdversarialCategory,
    AdversarialEvaluationReport,
    AdversarialEvaluationResult,
    AdversarialRequirement,
    GeneratedSourceCode,
    GeneratedTestCode,
)
from test_guardian.models.failure import FailureType
from test_guardian.models.pipeline import PipelineResult
from test_guardian.models.requirements import RequirementInput
from test_guardian.models.test_audit import TestBugReason
from test_guardian.models.test_patch import PatchType, TestPatchProposal

_CODE_GENERATOR_INSTRUCTIONS = """\
Generate concise Python implementation code for the requirement.
Return only structured output with source_code.
"""

_TEST_GENERATOR_INSTRUCTIONS = """\
Generate concise pytest test code for the requirement and source code.
Return only structured output with test_code.
"""

_REASON_TO_PATCH_TYPE = {
    TestBugReason.WRONG_ASSERTION: PatchType.ASSERTION_FIX,
    TestBugReason.WRONG_EXCEPTION: PatchType.EXCEPTION_FIX,
    TestBugReason.WRONG_INPUT: PatchType.INPUT_FIX,
    TestBugReason.OUTDATED_TEST: PatchType.REQUIREMENT_SYNC,
}


class CodeGenerator(Protocol):
    """Contract for generating source code from a requirement."""

    def generate(self, requirement: str) -> str:
        """Generate source code."""


class TestGenerator(Protocol):
    """Contract for generating tests from a requirement and source code."""

    def generate(self, requirement: str, source_code: str) -> str:
        """Generate test code."""


class PipelineLike(Protocol):
    """Minimal pipeline contract used by adversarial evaluation."""

    def run(
        self,
        *,
        requirement_input: RequirementInput,
        source_code: str,
        test_code: str,
        ci_log: str,
    ) -> PipelineResult:
        """Run one generated case through Test Guardian."""


class TestPatchAgentLike(Protocol):
    """Minimal patch-agent contract used by adversarial evaluation."""

    def generate(
        self,
        requirement,
        test_audit,
        test_code: str,
    ) -> TestPatchProposal:
        """Generate a test patch proposal."""


class OpenAICodeGenerator:
    """Generate source code with OpenAI structured output."""

    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str | None = None,
    ) -> None:
        self._client = client or OpenAI()
        self._model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    def generate(self, requirement: str) -> str:
        response = self._client.responses.parse(
            model=self._model,
            instructions=_CODE_GENERATOR_INSTRUCTIONS,
            input=requirement,
            text_format=GeneratedSourceCode,
            temperature=0,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("OpenAI response did not include parsed source code.")
        return parsed.source_code


class OpenAITestGenerator:
    """Generate pytest code with OpenAI structured output."""

    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str | None = None,
    ) -> None:
        self._client = client or OpenAI()
        self._model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    def generate(self, requirement: str, source_code: str) -> str:
        response = self._client.responses.parse(
            model=self._model,
            instructions=_TEST_GENERATOR_INSTRUCTIONS,
            input=f"Requirement:\n{requirement}\n\nSource Code:\n{source_code}",
            text_format=GeneratedTestCode,
            temperature=0,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("OpenAI response did not include parsed test code.")
        return parsed.test_code


class BugInjector:
    """Inject deterministic test bugs without modifying files."""

    def inject(self, test_code: str, reason_type: TestBugReason) -> str:
        if reason_type == TestBugReason.WRONG_ASSERTION:
            return _replace_first(
                test_code,
                [
                    ("ACCEPTED", "COMPLETED"),
                    ("== 8", "== 10"),
                    ("== 10", "== 20"),
                    ("user_id", "id"),
                ],
                "\nassert result == 'WRONG_EXPECTATION'",
            )

        if reason_type == TestBugReason.WRONG_EXCEPTION:
            return _replace_first(
                test_code,
                [
                    ("ValueError", "TypeError"),
                    ("PermissionError", "ValueError"),
                    ("LookupError", "KeyError"),
                ],
                "\nwith pytest.raises(TypeError):\n    pass",
            )

        if reason_type == TestBugReason.WRONG_INPUT:
            return _replace_first(
                test_code,
                [
                    ("ACTIVE", "None"),
                    ("100", "1000"),
                    ("valid_user", "None"),
                    ("5", "500"),
                ],
                "\ninvalid_input = None",
            )

        return _replace_first(
            test_code,
            [
                ("== 8", "== 10"),
                ("user_id", "id"),
                ("threshold = 75", "threshold = 50"),
            ],
            "\n# stale expectation from previous requirement",
        )


class AdversarialEvaluationRunner:
    """Generate, inject, run, and score adversarial test-bug cases."""

    def __init__(
        self,
        *,
        pipeline: PipelineLike,
        patch_agent: TestPatchAgentLike,
        code_generator: CodeGenerator,
        test_generator: TestGenerator,
        bug_injector: BugInjector | None = None,
        requirements: list[AdversarialRequirement] | None = None,
    ) -> None:
        self._pipeline = pipeline
        self._patch_agent = patch_agent
        self._code_generator = code_generator
        self._test_generator = test_generator
        self._bug_injector = bug_injector or BugInjector()
        self._requirements = requirements or load_requirements()

    def run(self) -> AdversarialEvaluationReport:
        results = [self._run_case(requirement) for requirement in self._requirements]
        return generate_adversarial_report(results)

    def _run_case(
        self,
        requirement: AdversarialRequirement,
    ) -> AdversarialEvaluationResult:
        source_code = self._code_generator.generate(requirement.requirement)
        test_code = self._test_generator.generate(requirement.requirement, source_code)
        faulty_test_code = self._bug_injector.inject(
            test_code,
            requirement.expected_reason_type,
        )
        pipeline_result = self._pipeline.run(
            requirement_input=RequirementInput(readme=requirement.requirement),
            source_code=source_code,
            test_code=faulty_test_code,
            ci_log=_synthetic_ci_log(requirement.expected_reason_type),
        )

        patch_type = None
        if pipeline_result.test_audit is not None:
            proposal = self._patch_agent.generate(
                pipeline_result.requirement,
                pipeline_result.test_audit,
                faulty_test_code,
            )
            patch_type = proposal.patch_type

        predicted_reason_type = (
            pipeline_result.test_audit.reason_type
            if pipeline_result.test_audit is not None
            else None
        )
        expected_patch_type = _REASON_TO_PATCH_TYPE[requirement.expected_reason_type]
        success = (
            pipeline_result.failure_analysis.failure_type == FailureType.TEST_BUG
            and predicted_reason_type == requirement.expected_reason_type
            and patch_type == expected_patch_type
        )

        return AdversarialEvaluationResult(
            requirement=requirement.requirement,
            expected_reason_type=requirement.expected_reason_type,
            predicted_failure_type=pipeline_result.failure_analysis.failure_type,
            predicted_reason_type=predicted_reason_type,
            patch_type=patch_type,
            success=success,
        )


def load_requirements() -> list[AdversarialRequirement]:
    """Load the default 20 adversarial requirements."""

    cases: list[tuple[AdversarialCategory, TestBugReason, str]] = []
    categories = [
        AdversarialCategory.ASYNC,
        AdversarialCategory.MOCK,
        AdversarialCategory.EXCEPTION,
        AdversarialCategory.FIXTURE_STATE,
    ]
    reasons = [
        TestBugReason.WRONG_ASSERTION,
        TestBugReason.WRONG_EXCEPTION,
        TestBugReason.WRONG_INPUT,
        TestBugReason.OUTDATED_TEST,
        TestBugReason.WRONG_ASSERTION,
    ]

    for category in categories:
        for index, reason_type in enumerate(reasons, start=1):
            cases.append(
                (
                    category,
                    reason_type,
                    _requirement_text(category, index),
                )
            )

    return [
        AdversarialRequirement(
            category=category,
            requirement=requirement,
            expected_reason_type=reason_type,
        )
        for category, reason_type, requirement in cases
    ]


def generate_adversarial_report(
    results: list[AdversarialEvaluationResult],
) -> AdversarialEvaluationReport:
    total_cases = len(results)
    failure_correct = sum(
        result.predicted_failure_type == FailureType.TEST_BUG for result in results
    )
    reason_correct = sum(
        result.predicted_reason_type == result.expected_reason_type
        for result in results
    )
    patch_correct = sum(
        result.patch_type == _REASON_TO_PATCH_TYPE[result.expected_reason_type]
        for result in results
    )

    return AdversarialEvaluationReport(
        total_cases=total_cases,
        failure_accuracy=failure_correct / total_cases if total_cases else 0.0,
        reason_accuracy=reason_correct / total_cases if total_cases else 0.0,
        patch_accuracy=patch_correct / total_cases if total_cases else 0.0,
        failure_correct=failure_correct,
        reason_correct=reason_correct,
        patch_correct=patch_correct,
        results=results,
    )


def _replace_first(
    test_code: str,
    replacements: list[tuple[str, str]],
    fallback_suffix: str,
) -> str:
    for before, after in replacements:
        if before in test_code:
            return test_code.replace(before, after, 1)
    return test_code.rstrip() + fallback_suffix


def _synthetic_ci_log(reason_type: TestBugReason) -> str:
    if reason_type == TestBugReason.WRONG_EXCEPTION:
        return "E   ValueError: expected exception type did not match"
    if reason_type == TestBugReason.WRONG_INPUT:
        return "E   ValueError: input outside supported range"
    return "AssertionError: generated test expectation failed"


def _requirement_text(category: AdversarialCategory, index: int) -> str:
    prefix = f"{category} case {index}."
    if category == AdversarialCategory.ASYNC:
        return (
            f"{prefix} Implement an asynchronous email service that returns "
            "ACCEPTED immediately without waiting for completion."
        )
    if category == AdversarialCategory.MOCK:
        return (
            f"{prefix} Implement a service that calls an injected dependency once "
            "and returns user_id in the response."
        )
    if category == AdversarialCategory.EXCEPTION:
        return (
            f"{prefix} Implement validation that raises ValueError for invalid "
            "input and preserves successful results."
        )
    return (
        f"{prefix} Implement fixture-safe state handling where each test gets "
        "isolated ACTIVE user state."
    )
