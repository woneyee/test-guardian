# Evaluation Runner

## 목적

Test Guardian의 Failure Analyzer 및 Test Auditor 성능을 정량적으로 측정한다.

평가 데이터셋(fixtures)을 순회하며 예측 결과와 정답을 비교한다.

---

# 입력

Fixture Dataset

경로:

```text
tests/fixtures/test_guardian_eval.json
```

형식:

```json
{
  "requirement": "...",
  "source_code": "...",
  "test_code": "...",
  "ci_log": "...",
  "expected_failure_type": "CODE_BUG",
  "expected_reason_type": null
}
```

또는

```json
{
  "requirement": "...",
  "source_code": "...",
  "test_code": "...",
  "ci_log": "...",
  "expected_failure_type": "TEST_BUG",
  "expected_reason_type": "WRONG_ASSERTION"
}
```

---

# 평가 대상

## Failure Analyzer

예측

```json
{
  "failure_type": "CODE_BUG"
}
```

정답

```json
{
  "expected_failure_type": "CODE_BUG"
}
```

비교

---

## Test Auditor

Failure Type이 TEST_BUG인 경우만 평가

예측

```json
{
  "reason_type": "WRONG_ASSERTION"
}
```

정답

```json
{
  "expected_reason_type": "WRONG_ASSERTION"
}
```

비교

---

# 출력

EvaluationReport

```json
{
  "total_cases": 25,

  "failure_accuracy": 0.96,

  "reason_accuracy": 0.95,

  "failure_correct": 24,
  "failure_incorrect": 1,

  "reason_correct": 19,
  "reason_incorrect": 1
}
```

---

# 계산 방식

Failure Accuracy

```text
failure_correct / total_cases
```

Reason Accuracy

```text
reason_correct / total_test_bug_cases
```

---

# 콘솔 출력

예시

```text
====================================

Test Guardian Evaluation

Total Cases: 25

Failure Accuracy: 96.00%
Failure Correct: 24
Failure Incorrect: 1

Reason Accuracy: 95.00%
Reason Correct: 19
Reason Incorrect: 1

====================================
```

---

# 구현 범위

## Models

EvaluationReport

---

## Services

EvaluationRunner

---

## Functions

load_dataset()

evaluate_failure_types()

evaluate_reason_types()

generate_report()

---

# 테스트

Unit Test 추가

검증 항목

* dataset 로딩
* accuracy 계산
* empty dataset 처리
* report 생성

---

# 제외 범위

* LangGraph
* CodingAgent
* TestPatchAgent
* Re-test loop
* CI 연동
* Github Action

```
```
