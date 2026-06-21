"""Backward-compatible failure classification evaluation imports."""

from test_guardian.evaluation.failure_classification import (
    FailureClassificationEvaluationRunner,
    generate_failure_classification_report,
    load_failure_classification_dataset,
)

__all__ = [
    "FailureClassificationEvaluationRunner",
    "generate_failure_classification_report",
    "load_failure_classification_dataset",
]
