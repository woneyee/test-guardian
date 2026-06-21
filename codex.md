# Test Guardian 작업 정리

## 현재 목표

Test Guardian은 테스트 실패를 무조건 구현 코드 버그로 보지 않고, 실패 책임을 분석한 뒤 적절한 후속 처리 대상으로 라우팅하는 MVP 시스템이다.

현재 구현 범위는 다음 흐름이다.

```text
RequirementExtractor
-> FailureAnalyzer
-> Router
-> if TEST_BUG: TestAuditor
-> PipelineResult
-> EvaluationRunner
```

## 구현된 구성

### Requirement Extractor

- 구현체: `SimpleRequirementExtractor`
- 입력: `RequirementInput`
- 출력: `ExtractedRequirement`
- 역할:
  - README / Issue 텍스트에서 기능명과 요구사항을 추출한다.
  - 요구사항 출처를 `sources`에 기록한다.

### Failure Analyzer

- 구현체: `OpenAIFailureAnalyzer`
- 입력: `FailureAnalysisInput`
- 출력: `FailureAnalysisResult`
- OpenAI structured output을 사용한다.
- 지원 실패 유형:
  - `CODE_BUG`
  - `TEST_BUG`
- 출력 필드:
  - `failure_type`
  - `confidence`
  - `reason`
  - `evidence`

### Router

- 인터페이스: `FailureRouter`
- 구현체: `SimpleFailureRouter`
- 입력: `FailureAnalysisResult`
- 출력: `RoutingResult`
- 라우팅 규칙:
  - `CODE_BUG -> coding_agent`
  - `TEST_BUG -> test_auditor`
- 현재 결정:
  - `confidence`는 라우팅에 사용하지 않는다.

### Test Auditor

- 인터페이스: `TestAuditor`
- 구현체: `OpenAITestAuditor`
- 입력: `FailureAnalysisInput`
- 출력: `TestAuditResult`
- OpenAI structured output을 사용한다.
- 지원 테스트 버그 이유:
  - `WRONG_ASSERTION`
  - `WRONG_EXCEPTION`
  - `WRONG_INPUT`
  - `OUTDATED_TEST`
- 제외:
  - 테스트 패치 생성은 하지 않는다.
  - 테스트 수정은 하지 않는다.

### Pipeline Runner

- 구현체: `GuardianPipeline`
- 출력: `PipelineResult`
- 연결 컴포넌트:
  - `RequirementExtractor`
  - `FailureAnalyzer`
  - `FailureRouter`
  - `TestAuditor`
- 동작:
  - `CODE_BUG`이면 `TestAuditor`를 실행하지 않는다.
  - `TEST_BUG`이면 `TestAuditor`를 실행한다.

### Evaluation Dataset

- 위치: `tests/fixtures/test_guardian_eval.json`
- 총 25개 fixture
- 구성:
  - 5 `CODE_BUG`
  - 5 `WRONG_ASSERTION`
  - 5 `WRONG_EXCEPTION`
  - 5 `WRONG_INPUT`
  - 5 `OUTDATED_TEST`
- 각 fixture 필드:
  - `requirement`
  - `source_code`
  - `test_code`
  - `ci_log`
  - `expected_failure_type`
  - `expected_reason_type`

### Evaluation Runner

- 모델: `EvaluationReport`
- 구현체: `EvaluationRunner`
- 기본 dataset 경로:
  - `tests/fixtures/test_guardian_eval.json`
- 제공 함수:
  - `load_dataset`
  - `evaluate_failure_types`
  - `evaluate_reason_types`
  - `generate_report`
- 계산 지표:
  - `failure_accuracy = failure_correct / total_cases`
  - `reason_accuracy = reason_correct / total_test_bug_cases`

## 주요 모델

- `RequirementInput`
- `ExtractedRequirement`
- `FailureAnalysisInput`
- `FailureAnalysisResult`
- `RoutingResult`
- `TestAuditResult`
- `PipelineResult`
- `EvaluationFixture`
- `EvaluationReport`

## 테스트 현황

현재 단위 테스트는 다음 범위를 검증한다.

- Pydantic 모델 검증
- Requirement Extractor
- OpenAI Failure Analyzer structured output 계약
- Router 라우팅 규칙
- Analyzer 결과 객체 -> Router 계약
- Router가 `confidence`를 무시한다는 정책
- OpenAI Test Auditor structured output 계약
- Pipeline Runner의 `CODE_BUG` / `TEST_BUG` 경로
- Evaluation Dataset schema validation
- Evaluation Runner dataset loading / accuracy calculation / empty dataset / report generation

마지막 확인 기준:

```text
py -3.12 -m unittest discover -s tests

Ran 29 tests
OK
```

## 현재 결정된 사항

- MVP Failure Type은 `CODE_BUG`, `TEST_BUG`만 지원한다.
- Test Auditor reason type은 4개만 지원한다.
- Router는 confidence를 사용하지 않는다.
- OpenAI 기반 컴포넌트는 structured output을 사용한다.
- Unit test에서는 실제 OpenAI API를 호출하지 않고 fake client / fake pipeline을 사용한다.
- Evaluation Runner는 CI나 CLI가 아니라 서비스 레이어로만 구현한다.

## 아직 구현하지 않은 것

- LangGraph workflow
- CodingAgent
- TestPatchAgent
- Code patch generation
- Test patch generation
- Re-test loop
- CLI argument parsing
- CI integration
- GitHub Actions 연동
- Low confidence human review routing
- `BOTH_WRONG`, `UNKNOWN`, `ENV_BUG`, `FLAKY_TEST`, `REQUIREMENT_CONFLICT` 같은 확장 failure type

## 다음 후보 작업

1. 실제 OpenAI API key가 있는 환경에서 EvaluationRunner를 실행하는 별도 script 추가
2. Low confidence 정책 도입 여부 결정
3. Requirement conflict를 구조화할지 결정
4. CLI runner 추가
5. LangGraph workflow 도입 여부 결정
