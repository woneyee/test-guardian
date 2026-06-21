# Failure Analyzer Agent Specification

## 목적

CI 환경에서 테스트 실패 발생 시 실패 원인을 분석하여 Code Bug 또는 Test Bug로 분류한다.

---

## 입력

### CI Log

테스트 실패 로그

예시

* AssertionError
* Expected X but got Y
* Stack Trace

### Source Code

실패 테스트와 관련된 구현 코드

### Test Code

실패한 테스트 코드

### README.md

프로젝트의 기능 설명 및 요구사항

### Issue.md

현재 작업 중인 기능 요구사항

---

## 출력

JSON 형식

```json
{
  "failure_type": "CODE_BUG",
  "confidence": 0.92,
  "reason": "Implementation does not satisfy requirement."
}
```

---

## Failure Type

### CODE_BUG

요구사항과 테스트는 일치하나 구현 코드가 요구사항을 만족하지 않는 경우

### TEST_BUG

요구사항과 구현 코드는 일치하나 테스트 코드가 잘못 작성된 경우

---

## 판단 기준

### CODE_BUG

Requirement == Test

Requirement != Source

→ CODE_BUG

### TEST_BUG

Requirement == Source

Requirement != Test

→ TEST_BUG

---

## Confidence

0.0 ~ 1.0

분류 결과에 대한 신뢰도

---

## Example

Requirement

세율은 10%이다.

Source

```python
def tax(price):
    return price * 0.1
```

Test

```python
assert tax(1000) == 50
```

Result

```json
{
  "failure_type": "TEST_BUG",
  "confidence": 0.95,
  "reason": "Test expectation conflicts with requirement."
}
```
