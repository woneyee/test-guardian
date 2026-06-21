"""Pydantic data contracts for the Test Guardian MVP."""

from test_guardian.models.adversarial import (
    AdversarialCategory,
    AdversarialEvaluationReport,
    AdversarialEvaluationResult,
    AdversarialRequirement,
    GeneratedSourceCode,
    GeneratedTestCode,
)
from test_guardian.models.evaluation import EvaluationFixture, EvaluationReport
from test_guardian.models.failure import (
    ExperimentalFailureAnalysisResult,
    ExperimentalFailureType,
    FailureAnalysisInput,
    FailureAnalysisResult,
    FailureType,
)
from test_guardian.models.failure_evaluation import (
    FailureClassificationCaseResult,
    FailureClassificationFixture,
    FailureClassificationReport,
)
from test_guardian.models.pipeline import PipelineResult
from test_guardian.models.requirements import ExtractedRequirement, RequirementInput
from test_guardian.models.routing import RouteTarget, RoutingResult
from test_guardian.models.test_audit import TestAuditResult, TestBugReason
from test_guardian.models.test_patch import PatchType, TestPatchProposal

__all__ = [
    "AdversarialCategory",
    "AdversarialEvaluationReport",
    "AdversarialEvaluationResult",
    "AdversarialRequirement",
    "EvaluationFixture",
    "EvaluationReport",
    "ExperimentalFailureAnalysisResult",
    "ExperimentalFailureType",
    "ExtractedRequirement",
    "FailureAnalysisInput",
    "FailureAnalysisResult",
    "FailureClassificationCaseResult",
    "FailureClassificationFixture",
    "FailureClassificationReport",
    "FailureType",
    "GeneratedSourceCode",
    "GeneratedTestCode",
    "PatchType",
    "PipelineResult",
    "RequirementInput",
    "RouteTarget",
    "RoutingResult",
    "TestAuditResult",
    "TestBugReason",
    "TestPatchProposal",
]
