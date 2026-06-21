import unittest

from pydantic import ValidationError

from test_guardian.models.failure import FailureAnalysisResult, FailureType
from test_guardian.models.requirements import RequirementInput


class RequirementInputTests(unittest.TestCase):
    def test_requires_at_least_one_source(self) -> None:
        with self.assertRaises(ValidationError):
            RequirementInput()

    def test_accepts_readme_source(self) -> None:
        model = RequirementInput(readme="  # Checkout  ")

        self.assertEqual(model.readme, "# Checkout")
        self.assertIsNone(model.issue)


class FailureAnalysisResultTests(unittest.TestCase):
    def test_confidence_must_be_between_zero_and_one(self) -> None:
        with self.assertRaises(ValidationError):
            FailureAnalysisResult(
                failure_type=FailureType.CODE_BUG,
                confidence=1.1,
                reason="Too confident.",
            )

    def test_serializes_failure_type_as_string(self) -> None:
        result = FailureAnalysisResult(
            failure_type=FailureType.TEST_BUG,
            confidence=0.8,
            reason="Broken test fixture.",
        )

        self.assertEqual(result.model_dump()["failure_type"], FailureType.TEST_BUG)
        self.assertEqual(result.model_dump(mode="json")["failure_type"], "TEST_BUG")


if __name__ == "__main__":
    unittest.main()
