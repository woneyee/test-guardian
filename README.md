# Test Guardian

Test Guardian은 CI 또는 테스트 실패의 책임을 분석하고, 적절한 복구 흐름으로 라우팅하기 위한 Agent 기반 시스템입니다.

일반적인 코딩 에이전트는 테스트 실패를 곧바로 구현 코드 버그로 가정하는 경우가 많습니다. 하지만 실제 TDD/CI 환경에서는 테스트 코드 오류, 잘못된 기대값, 변경된 요구사항, 잘못된 입력, 예외 타입 불일치 등 다양한 이유로 테스트가 실패할 수 있습니다.

Test Guardian은 실패를 먼저 분석한 뒤 책임을 분류합니다.

Production 분류는 의도적으로 binary로 유지합니다.

- `CODE_BUG`
- `TEST_BUG`

실험용 평가 코드에서는 `BOTH`, `UNKNOWN`도 다루지만, 이 값들은 production routing flow에는 포함되지 않습니다.

## 아키텍처

Production 흐름은 다음과 같습니다.

```text
RequirementExtractor
-> FailureAnalyzer
-> Router
-> if TEST_BUG: TestAuditor
-> PipelineResult
```

현재 패키지 구조는 다음과 같습니다.

```text
test_guardian/
  agents/
    requirement_extractor/
    failure_analyzer/
    router/
    test_auditor/
    test_patch_agent/

  workflows/
    guardian_pipeline.py

  evaluation/
    evaluation_runner.py
    failure_classification.py
    adversarial.py

  cli/
    run.py
    evaluate.py
    failure_classification_evaluate.py
    failure_classification_evaluate_v2.py
    adversarial_evaluate.py

  models/
```

기존 import 경로와 루트 실행 스크립트는 호환성을 위해 유지합니다.

예를 들어 아래 명령은 계속 동작합니다.

```bash
py -3.12 run.py ...
```

## Agent 설명

### RequirementExtractor

README, Issue 같은 자연어 요구사항 소스를 정규화하여 `ExtractedRequirement`로 변환합니다.

구현체:

- `SimpleRequirementExtractor`

### FailureAnalyzer

CI 실패의 책임을 분석합니다.

Production에서 지원하는 실패 유형:

- `CODE_BUG`
- `TEST_BUG`

구현체:

- `OpenAIFailureAnalyzer`

실험용 구현체:

- `OpenAIFailureAnalyzerExperimentalV1`
- `OpenAIFailureAnalyzerV2`

실험용 구현체는 `BOTH`, `UNKNOWN` 평가에 사용됩니다. Production routing에는 사용하지 않습니다.

### Router

`FailureAnalysisResult`를 다음 처리 대상으로 라우팅합니다.

라우팅 규칙:

- `CODE_BUG -> coding_agent`
- `TEST_BUG -> test_auditor`

구현체:

- `SimpleFailureRouter`

### TestAuditor

`FailureAnalyzer`가 실패를 `TEST_BUG`로 분류한 경우에만 실행됩니다.

테스트 버그의 구체적인 원인을 분류합니다.

지원하는 reason type:

- `WRONG_ASSERTION`
- `WRONG_EXCEPTION`
- `WRONG_INPUT`
- `OUTDATED_TEST`

구현체:

- `OpenAITestAuditor`

### TestPatchAgent

테스트 수정 제안을 생성합니다.

주의: 실제 파일을 수정하지 않고, git patch도 생성하지 않습니다. 구조화된 제안만 반환합니다.

지원하는 patch type:

- `ASSERTION_FIX`
- `EXCEPTION_FIX`
- `INPUT_FIX`
- `REQUIREMENT_SYNC`

구현체:

- `OpenAITestPatchAgent`

## 환경변수

OpenAI 기반 Agent를 실행하려면 다음 환경변수가 필요합니다.

```text
OPENAI_API_KEY
```

선택 환경변수:

```text
OPENAI_MODEL
```

`OPENAI_MODEL`을 설정하지 않으면 기본 모델은 다음과 같습니다.

```text
gpt-4.1-mini
```

로컬 `.env` 파일은 커밋하면 안 됩니다.

## Pipeline 실행

```bash
py -3.12 run.py \
  --readme README.md \
  --issue ISSUE.md \
  --source src/calculator.py \
  --test tests/test_calculator.py \
  --log ci.log
```

실행 결과는 JSON 형식의 `PipelineResult`로 출력됩니다.

## 평가 실행

기본 fixture dataset 평가:

```bash
py -3.12 evaluate.py
```

실험용 4-class FailureAnalyzer 평가:

```bash
py -3.12 failure_classification_evaluate.py --limit 1
py -3.12 failure_classification_evaluate.py --limit 32
```

실험용 Prompt V1 / V2 비교:

```bash
py -3.12 failure_classification_evaluate_v2.py --limit 32
```

Adversarial evaluation 실행:

```bash
py -3.12 adversarial_evaluate.py --limit 1 --verbose
```

실제 OpenAI API를 사용하는 평가를 실행할 때는 비용 관리를 위해 먼저 `--limit`을 작게 설정하는 것을 권장합니다.

## 테스트 실행

전체 단위 테스트 실행:

```bash
py -3.12 -m unittest discover -s tests
```

단위 테스트는 fake client와 fake pipeline을 사용합니다. 따라서 OpenAI API를 호출하지 않습니다.

## 문서

추가 문서:

- `docs/ARCHITECTURE.md`
- `docs/SYSTEM_OVERVIEW.md`
- `docs/TEST_AUDITOR.md`
- `docs/TEST_PATCH_AGENT.md`
- `docs/EVALUATION_RUNNER.md`
- `docs/experiments/comparison.md`
