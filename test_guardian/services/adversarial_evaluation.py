"""Backward-compatible adversarial evaluation imports."""

from test_guardian.evaluation.adversarial import (
    AdversarialEvaluationRunner,
    BugInjector,
    OpenAICodeGenerator,
    OpenAITestGenerator,
    generate_adversarial_report,
    load_requirements,
)

__all__ = [
    "AdversarialEvaluationRunner",
    "BugInjector",
    "OpenAICodeGenerator",
    "OpenAITestGenerator",
    "generate_adversarial_report",
    "load_requirements",
]
