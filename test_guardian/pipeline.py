"""MVP pipeline runner."""

from test_guardian.analyzers.base import FailureAnalyzer, RequirementExtractor
from test_guardian.auditors.base import TestAuditor
from test_guardian.models.failure import FailureAnalysisInput, FailureType
from test_guardian.models.pipeline import PipelineResult
from test_guardian.models.requirements import RequirementInput
from test_guardian.routers.base import FailureRouter


class GuardianPipeline:
    """Orchestrate requirement extraction, failure analysis, routing, and audit."""

    def __init__(
        self,
        *,
        requirement_extractor: RequirementExtractor,
        failure_analyzer: FailureAnalyzer,
        router: FailureRouter,
        test_auditor: TestAuditor,
    ) -> None:
        self._requirement_extractor = requirement_extractor
        self._failure_analyzer = failure_analyzer
        self._router = router
        self._test_auditor = test_auditor

    def run(
        self,
        *,
        requirement_input: RequirementInput,
        source_code: str,
        test_code: str,
        ci_log: str,
    ) -> PipelineResult:
        requirement = self._requirement_extractor.extract(requirement_input)
        failure_input = FailureAnalysisInput(
            requirement=requirement,
            source_code=source_code,
            test_code=test_code,
            ci_log=ci_log,
        )
        failure_analysis = self._failure_analyzer.analyze(failure_input)
        routing = self._router.route(failure_analysis)

        test_audit = None
        if failure_analysis.failure_type == FailureType.TEST_BUG:
            test_audit = self._test_auditor.audit(failure_input)

        return PipelineResult(
            requirement=requirement,
            failure_analysis=failure_analysis,
            routing=routing,
            test_audit=test_audit,
        )
