import unittest
from types import SimpleNamespace

from test_guardian.auditors.test_auditor import OpenAITestAuditor
from test_guardian.models.failure import FailureAnalysisInput
from test_guardian.models.requirements import ExtractedRequirement
from test_guardian.models.test_audit import TestAuditResult, TestBugReason


class FakeResponses:
    def __init__(self, parsed: TestAuditResult | None) -> None:
        self.parsed = parsed
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_parsed=self.parsed)


class FakeClient:
    def __init__(self, parsed: TestAuditResult | None) -> None:
        self.responses = FakeResponses(parsed)


class OpenAITestAuditorTests(unittest.TestCase):
    def test_audits_wrong_assertion(self) -> None:
        result = self._audit(
            TestAuditResult(
                reason_type=TestBugReason.WRONG_ASSERTION,
                confidence=0.92,
                reason="The test expects a value inconsistent with the requirement.",
            )
        )

        self.assertEqual(result.reason_type, TestBugReason.WRONG_ASSERTION)

    def test_audits_wrong_exception(self) -> None:
        result = self._audit(
            TestAuditResult(
                reason_type=TestBugReason.WRONG_EXCEPTION,
                confidence=0.88,
                reason="The test expects TypeError instead of the required ValueError.",
            )
        )

        self.assertEqual(result.reason_type, TestBugReason.WRONG_EXCEPTION)

    def test_audits_wrong_input(self) -> None:
        result = self._audit(
            TestAuditResult(
                reason_type=TestBugReason.WRONG_INPUT,
                confidence=0.86,
                reason="The test uses input outside the supported requirement range.",
            )
        )

        self.assertEqual(result.reason_type, TestBugReason.WRONG_INPUT)

    def test_audits_outdated_test(self) -> None:
        result = self._audit(
            TestAuditResult(
                reason_type=TestBugReason.OUTDATED_TEST,
                confidence=0.9,
                reason="The test follows the old tax rate instead of the updated issue.",
            )
        )

        self.assertEqual(result.reason_type, TestBugReason.OUTDATED_TEST)

    def test_uses_openai_structured_output_contract(self) -> None:
        expected = TestAuditResult(
            reason_type=TestBugReason.WRONG_ASSERTION,
            confidence=0.92,
            reason="The assertion contradicts the requirement.",
        )
        client = FakeClient(expected)
        auditor = OpenAITestAuditor(client=client, model="gpt-test")

        auditor.audit(self._input())

        call = client.responses.calls[0]
        self.assertEqual(call["model"], "gpt-test")
        self.assertEqual(call["text_format"], TestAuditResult)
        self.assertEqual(call["temperature"], 0)
        self.assertIn("WRONG_ASSERTION", call["instructions"])
        self.assertIn("WRONG_EXCEPTION", call["instructions"])
        self.assertIn("WRONG_INPUT", call["instructions"])
        self.assertIn("OUTDATED_TEST", call["instructions"])
        self.assertIn("discount = 10%", call["input"])
        self.assertIn("AssertionError", call["input"])

    def test_raises_when_openai_response_is_not_parsed(self) -> None:
        auditor = OpenAITestAuditor(client=FakeClient(None))

        with self.assertRaises(ValueError):
            auditor.audit(self._input())

    def _audit(self, expected: TestAuditResult) -> TestAuditResult:
        auditor = OpenAITestAuditor(client=FakeClient(expected), model="gpt-test")
        return auditor.audit(self._input())

    def _input(self) -> FailureAnalysisInput:
        return FailureAnalysisInput(
            requirement=ExtractedRequirement(
                feature="Discount",
                requirement="discount = 10%",
                sources=["README.md"],
            ),
            source_code="def discount(): return 10",
            test_code="assert discount() == 20",
            ci_log="AssertionError: expected 20 got 10",
        )


if __name__ == "__main__":
    unittest.main()
