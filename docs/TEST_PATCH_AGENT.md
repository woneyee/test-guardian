# TestPatchAgent MVP

## 목적

TestAuditor가 TEST_BUG로 판정한 경우 테스트 코드 수정 제안을 생성한다.

TestPatchAgent는 실제 파일을 수정하지 않는다.

수정 제안(Patch Proposal)만 생성한다.

---

# 입력

## ExtractedRequirement

```json
{
  "feature": "...",
  "requirement": "...",
  "sources": [...]
}
```

---

## TestAuditResult

```json
{
  "reason_type": "WRONG_ASSERTION",
  "confidence": 0.92,
  "reason": "...",
  "evidence": [...]
}
```

---

## Test Code

```python
assert discount() == 20
```

---

# 출력

## TestPatchProposal

```json
{
  "patch_type": "ASSERTION_FIX",
  "confidence": 0.91,
  "before": "assert discount() == 20",
  "after": "assert discount() == 10",
  "justification": "Requirement and source both specify 10"
}
```

---

# PatchType

## ASSERTION_FIX

잘못된 예상값 수정

예시

```diff
- assert discount() == 20
+ assert discount() == 10
```

---

## EXCEPTION_FIX

잘못된 예외 타입 수정

예시

```diff
- pytest.raises(TypeError)
+ pytest.raises(ValueError)
```

---

## INPUT_FIX

잘못된 테스트 입력 수정

예시

```diff
- calculate(1000)
+ calculate(100)
```

---

## REQUIREMENT_SYNC

요구사항 변경에 맞게 테스트 동기화

예시

```diff
- assert tax() == 10
+ assert tax() == 8
```

---

# Mapping Rules

## WRONG_ASSERTION

↓

```text
ASSERTION_FIX
```

---

## WRONG_EXCEPTION

↓

```text
EXCEPTION_FIX
```

---

## WRONG_INPUT

↓

```text
INPUT_FIX
```

---

## OUTDATED_TEST

↓

```text
REQUIREMENT_SYNC
```

---

# 인터페이스

```python
class TestPatchAgent:

    def generate(
        self,
        requirement,
        test_audit,
        test_code
    ) -> TestPatchProposal:
        pass
```

---

# 구현

## OpenAITestPatchAgent

OpenAI Structured Output 사용

출력 모델:

```python
TestPatchProposal
```

---

# 모델

## PatchType

```python
ASSERTION_FIX
EXCEPTION_FIX
INPUT_FIX
REQUIREMENT_SYNC
```

---

## TestPatchProposal

```python
patch_type
confidence
before
after
justification
```

---

# Unit Test

지원 유형별 테스트

## WRONG_ASSERTION

PatchType

```python
ASSERTION_FIX
```

---

## WRONG_EXCEPTION

PatchType

```python
EXCEPTION_FIX
```

---

## WRONG_INPUT

PatchType

```python
INPUT_FIX
```

---

## OUTDATED_TEST

PatchType

```python
REQUIREMENT_SYNC
```

---

## OpenAI Structured Output 계약 테스트

* 정상 응답
* 파싱 실패
* 필수 필드 누락

---

# 제외 범위

* 실제 파일 수정
* Git patch 생성
* Re-test loop
* CodingAgent
* LangGraph
* GitHub Actions
* Auto commit
* Auto merge

```
```
