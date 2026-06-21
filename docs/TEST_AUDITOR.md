# Test Auditor

## 목적

Failure Analyzer가 TEST_BUG로 분류한 경우 테스트 코드의 구체적인 실패 원인을 분석한다.

---

## 입력

* Requirement
* Source Code
* Test Code
* CI Log

---

## 출력

```json
{
  "reason_type": "WRONG_ASSERTION",
  "confidence": 0.92,
  "reason": "Expected value is inconsistent with requirement"
}
```

---

## TestBugReason

### WRONG_ASSERTION

테스트가 잘못된 결과를 기대하는 경우

예시

Requirement: discount = 10%

Source:

```python
return 10
```

Test:

```python
assert discount() == 20
```

---

### WRONG_EXCEPTION

예외 타입 검증이 잘못된 경우

예시

Requirement:

negative value -> ValueError

Test:

```python
with pytest.raises(TypeError)
```

---

### WRONG_INPUT

요구사항 범위를 벗어난 입력을 사용하는 경우

예시

Requirement:

1~100 허용

Test:

```python
calculate(1000)
```

---

### OUTDATED_TEST

요구사항 변경 후 테스트가 갱신되지 않은 경우

예시

README: tax = 10%

Issue: tax = 8%

Source: 8%

Test: 10%

```

---

## 구현 범위

### Models

TestBugReason
TestAuditResult

### Interface

TestAuditor

### Implementation

OpenAITestAuditor

### Unit Tests

- WRONG_ASSERTION
- WRONG_EXCEPTION
- WRONG_INPUT
- OUTDATED_TEST

---

## 제외 범위

- Patch 생성
- Test 수정
- LangGraph
- Re-test Loop
```
