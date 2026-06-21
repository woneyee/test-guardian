import unittest
from types import SimpleNamespace

from pydantic import ValidationError

from test_guardian.models.requirements import ExtractedRequirement
from test_guardian.models.test_audit import TestAuditResult, TestBugReason
from test_guardian.models.test_patch import PatchType, TestPatchProposal
from test_guardian.agents.test_patch_agent.openai import OpenAITestPatchAgent


class FakeResponses:
    def __init__(self, parsed: TestPatchProposal | None) -> None:
        self.parsed = parsed
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_parsed=self.parsed)


class FakeClient:
    def __init__(self, parsed: TestPatchProposal | None) -> None:
        self.responses = FakeResponses(parsed)


class OpenAITestPatchAgentTests(unittest.TestCase):
    def test_generates_assertion_fix_for_wrong_assertion(self) -> None:
        result = self._generate(
            reason_type=TestBugReason.WRONG_ASSERTION,
            proposal=TestPatchProposal(
                patch_type=PatchType.ASSERTION_FIX,
                confidence=0.91,
                before="assert discount() == 20",
                after="assert discount() == 10",
                justification="Requirement specifies 10.",
            ),
        )

        self.assertEqual(result.patch_type, PatchType.ASSERTION_FIX)

    def test_generates_exception_fix_for_wrong_exception(self) -> None:
        result = self._generate(
            reason_type=TestBugReason.WRONG_EXCEPTION,
            proposal=TestPatchProposal(
                patch_type=PatchType.EXCEPTION_FIX,
                confidence=0.88,
                before="with pytest.raises(TypeError):",
                after="with pytest.raises(ValueError):",
                justification="Requirement specifies ValueError.",
            ),
        )

        self.assertEqual(result.patch_type, PatchType.EXCEPTION_FIX)

    def test_generates_input_fix_for_wrong_input(self) -> None:
        result = self._generate(
            reason_type=TestBugReason.WRONG_INPUT,
            proposal=TestPatchProposal(
                patch_type=PatchType.INPUT_FIX,
                confidence=0.86,
                before="calculate(1000)",
                after="calculate(100)",
                justification="Requirement allows only values from 1 to 100.",
            ),
        )

        self.assertEqual(result.patch_type, PatchType.INPUT_FIX)

    def test_generates_requirement_sync_for_outdated_test(self) -> None:
        result = self._generate(
            reason_type=TestBugReason.OUTDATED_TEST,
            proposal=TestPatchProposal(
                patch_type=PatchType.REQUIREMENT_SYNC,
                confidence=0.9,
                before="assert tax() == 10",
                after="assert tax() == 8",
                justification="Issue changed the tax requirement to 8.",
            ),
        )

        self.assertEqual(result.patch_type, PatchType.REQUIREMENT_SYNC)

    def test_uses_openai_structured_output_contract(self) -> None:
        proposal = TestPatchProposal(
            patch_type=PatchType.ASSERTION_FIX,
            confidence=0.91,
            before="assert discount() == 20",
            after="assert discount() == 10",
            justification="Requirement specifies 10.",
        )
        client = FakeClient(proposal)
        agent = OpenAITestPatchAgent(client=client, model="gpt-test")

        agent.generate(
            self._requirement(),
            self._audit(TestBugReason.WRONG_ASSERTION),
            "assert discount() == 20",
        )

        call = client.responses.calls[0]
        self.assertEqual(call["model"], "gpt-test")
        self.assertEqual(call["text_format"], TestPatchProposal)
        self.assertEqual(call["temperature"], 0)
        self.assertIn("ASSERTION_FIX", call["instructions"])
        self.assertIn("EXCEPTION_FIX", call["instructions"])
        self.assertIn("INPUT_FIX", call["instructions"])
        self.assertIn("REQUIREMENT_SYNC", call["instructions"])
        self.assertIn("WRONG_ASSERTION -> ASSERTION_FIX", call["instructions"])
        self.assertIn("discount = 10", call["input"])
        self.assertIn("assert discount() == 20", call["input"])

    def test_raises_when_openai_response_is_not_parsed(self) -> None:
        agent = OpenAITestPatchAgent(client=FakeClient(None))

        with self.assertRaises(ValueError):
            agent.generate(
                self._requirement(),
                self._audit(TestBugReason.WRONG_ASSERTION),
                "assert discount() == 20",
            )

    def test_missing_required_field_is_rejected_by_output_model(self) -> None:
        with self.assertRaises(ValidationError):
            TestPatchProposal.model_validate(
                {
                    "patch_type": "ASSERTION_FIX",
                    "confidence": 0.91,
                    "before": "assert discount() == 20",
                    "after": "assert discount() == 10",
                }
            )

    def _generate(
        self,
        *,
        reason_type: TestBugReason,
        proposal: TestPatchProposal,
    ) -> TestPatchProposal:
        agent = OpenAITestPatchAgent(client=FakeClient(proposal), model="gpt-test")
        return agent.generate(
            self._requirement(),
            self._audit(reason_type),
            proposal.before,
        )

    def _requirement(self) -> ExtractedRequirement:
        return ExtractedRequirement(
            feature="Discount",
            requirement="discount = 10",
            sources=["README.md"],
        )

    def _audit(self, reason_type: TestBugReason) -> TestAuditResult:
        return TestAuditResult(
            reason_type=reason_type,
            confidence=0.92,
            reason=f"Audited as {reason_type}.",
        )


if __name__ == "__main__":
    unittest.main()
