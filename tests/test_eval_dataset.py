import json
import unittest
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from test_guardian.models.failure import FailureType
from test_guardian.models.test_audit import TestBugReason

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "test_guardian_eval.json"


class EvaluationFixture(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    requirement: str = Field(min_length=1)
    source_code: str = Field(min_length=1)
    test_code: str = Field(min_length=1)
    ci_log: str = Field(min_length=1)
    expected_failure_type: FailureType
    expected_reason_type: TestBugReason | None = None

    @model_validator(mode="after")
    def validate_reason_type_matches_failure_type(self) -> "EvaluationFixture":
        if self.expected_failure_type == FailureType.CODE_BUG:
            if self.expected_reason_type is not None:
                raise ValueError("CODE_BUG fixtures must not define expected_reason_type.")
            return self

        if self.expected_reason_type is None:
            raise ValueError("TEST_BUG fixtures must define expected_reason_type.")
        return self


class EvaluationDatasetTests(unittest.TestCase):
    def test_all_fixtures_are_schema_valid(self) -> None:
        fixtures = _load_fixtures()

        self.assertEqual(len(fixtures), 25)
        self.assertEqual(_count_code_bugs(fixtures), 5)
        self.assertEqual(_count_reason(fixtures, TestBugReason.WRONG_ASSERTION), 5)
        self.assertEqual(_count_reason(fixtures, TestBugReason.WRONG_EXCEPTION), 5)
        self.assertEqual(_count_reason(fixtures, TestBugReason.WRONG_INPUT), 5)
        self.assertEqual(_count_reason(fixtures, TestBugReason.OUTDATED_TEST), 5)


def _load_fixtures() -> list[EvaluationFixture]:
    fixtures: list[EvaluationFixture] = []
    errors: list[str] = []

    records = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise AssertionError(f"{FIXTURE_PATH.name}: expected top-level JSON array")

    for index, record in enumerate(records):
        try:
            fixtures.append(EvaluationFixture.model_validate(record))
        except ValidationError as error:
            errors.append(f"{FIXTURE_PATH.name}[{index}]: {error}")

    if errors:
        raise AssertionError("\n".join(errors))

    return fixtures


def _count_code_bugs(fixtures: list[EvaluationFixture]) -> int:
    return sum(
        fixture.expected_failure_type == FailureType.CODE_BUG
        for fixture in fixtures
    )


def _count_reason(
    fixtures: list[EvaluationFixture],
    reason_type: TestBugReason,
) -> int:
    return sum(fixture.expected_reason_type == reason_type for fixture in fixtures)


if __name__ == "__main__":
    unittest.main()
