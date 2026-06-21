import unittest
from types import SimpleNamespace

from test_guardian.agents.failure_analyzer.openai import (
    DEFAULT_MODEL,
    OpenAIFailureAnalyzer,
    OpenAIFailureAnalyzerV2,
)
from test_guardian.models.failure import (
    ExperimentalFailureAnalysisResult,
    ExperimentalFailureType,
    FailureAnalysisInput,
    FailureAnalysisResult,
    FailureType,
)
from test_guardian.models.requirements import ExtractedRequirement


class FakeResponses:
    def __init__(self, parsed: FailureAnalysisResult | None) -> None:
        self.parsed = parsed
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_parsed=self.parsed)


class FakeClient:
    def __init__(self, parsed: FailureAnalysisResult | None) -> None:
        self.responses = FakeResponses(parsed)


class OpenAIFailureAnalyzerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.requirement = ExtractedRequirement(
            feature="Price Calculator",
            requirement="Calculate discounts from the configured percentage.",
            sources=["README.md"],
        )

    def test_returns_structured_openai_result(self) -> None:
        expected = FailureAnalysisResult(
            failure_type=FailureType.TEST_BUG,
            confidence=0.88,
            reason="The test expects behavior outside the stated requirement.",
        )
        client = FakeClient(expected)
        analyzer = OpenAIFailureAnalyzer(client=client, model="gpt-test")

        result = analyzer.analyze(self._input())

        self.assertEqual(result, expected)
        self.assertEqual(result.failure_type, FailureType.TEST_BUG)

    def test_uses_openai_structured_output_contract(self) -> None:
        expected = FailureAnalysisResult(
            failure_type=FailureType.CODE_BUG,
            confidence=0.74,
            reason="The implementation returns the undiscounted amount.",
        )
        client = FakeClient(expected)
        analyzer = OpenAIFailureAnalyzer(client=client, model="gpt-test")

        analyzer.analyze(self._input())

        call = client.responses.calls[0]
        self.assertEqual(call["model"], "gpt-test")
        self.assertEqual(call["text_format"], FailureAnalysisResult)
        self.assertEqual(call["temperature"], 0)
        self.assertIn("CODE_BUG", call["instructions"])
        self.assertIn("TEST_BUG", call["instructions"])
        self.assertNotIn("BOTH", call["instructions"])
        self.assertNotIn("UNKNOWN", call["instructions"])
        self.assertIn("Calculate discounts", call["input"])
        self.assertIn("AssertionError", call["input"])

    def test_uses_default_model_when_model_not_provided(self) -> None:
        expected = FailureAnalysisResult(
            failure_type=FailureType.CODE_BUG,
            confidence=0.74,
            reason="The implementation returns the undiscounted amount.",
        )
        client = FakeClient(expected)
        analyzer = OpenAIFailureAnalyzer(client=client)

        analyzer.analyze(self._input())

        self.assertEqual(client.responses.calls[0]["model"], DEFAULT_MODEL)

    def test_raises_when_openai_response_is_not_parsed(self) -> None:
        analyzer = OpenAIFailureAnalyzer(client=FakeClient(None))

        with self.assertRaises(ValueError):
            analyzer.analyze(self._input())

    def test_v2_prompt_uses_explicit_source_and_test_checks(self) -> None:
        expected = ExperimentalFailureAnalysisResult(
            failure_type=ExperimentalFailureType.BOTH,
            confidence=0.74,
            reason="Source=YES and Test=YES.",
        )
        client = FakeClient(expected)
        analyzer = OpenAIFailureAnalyzerV2(client=client, model="gpt-test")

        analyzer.analyze(self._input())

        call = client.responses.calls[0]
        self.assertEqual(call["text_format"], ExperimentalFailureAnalysisResult)
        self.assertIn("Does the source code violate the requirement?", call["instructions"])
        self.assertIn("Does the test code violate the requirement?", call["instructions"])
        self.assertIn("Source=YES and Test=YES -> BOTH", call["instructions"])
        self.assertIn("Source=UNKNOWN and Test=UNKNOWN -> UNKNOWN", call["instructions"])

    def _input(self) -> FailureAnalysisInput:
        return FailureAnalysisInput(
            requirement=self.requirement,
            source_code="def calculate_total(price): return price",
            test_code="assert calculate_total(100) == 90",
            ci_log="AssertionError: expected 90 got 100",
        )


if __name__ == "__main__":
    unittest.main()
