"""Backward-compatible evaluation runner imports."""

from test_guardian.evaluation.evaluation_runner import (
    EvaluationRunner,
    evaluate_failure_types,
    evaluate_reason_types,
    generate_report,
    load_dataset,
)

__all__ = [
    "EvaluationRunner",
    "evaluate_failure_types",
    "evaluate_reason_types",
    "generate_report",
    "load_dataset",
]
