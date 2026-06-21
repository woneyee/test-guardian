import unittest

from test_guardian.analyzers.requirement_extractor import SimpleRequirementExtractor
from test_guardian.models.requirements import RequirementInput


class SimpleRequirementExtractorTests(unittest.TestCase):
    def test_extracts_feature_and_requirement_section(self) -> None:
        extractor = SimpleRequirementExtractor()

        result = extractor.extract(
            RequirementInput(
                readme="""
                # Price Calculator

                ## Requirements
                - Calculate discounts from the configured percentage.

                ## Notes
                Internal notes should not be preferred.
                """,
            )
        )

        self.assertEqual(result.feature, "Price Calculator")
        self.assertEqual(
            result.requirement,
            "Calculate discounts from the configured percentage.",
        )
        self.assertEqual(result.sources, ["README.md"])

    def test_combines_readme_and_issue_sources(self) -> None:
        extractor = SimpleRequirementExtractor()

        result = extractor.extract(
            RequirementInput(
                readme="# Checkout",
                issue="## Expected Behavior\nReturn the final payable amount.",
            )
        )

        self.assertEqual(result.feature, "Checkout")
        self.assertEqual(result.requirement, "Return the final payable amount.")
        self.assertEqual(result.sources, ["README.md", "Issue.md"])


if __name__ == "__main__":
    unittest.main()
