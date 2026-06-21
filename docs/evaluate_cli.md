# Evaluation CLI

## 목적

평가 데이터셋을 이용하여 Test Guardian 성능 측정

---

# 실행

```bash
python evaluate.py
```

---

# 입력

```text
tests/fixtures/test_guardian_eval.json
```

---

# 출력

```text
================================

Test Guardian Evaluation

Total Cases: 25

Failure Accuracy: 96.00%

Reason Accuracy: 95.00%

================================
```

---

# 구현 범위

* EvaluationRunner 호출
* 결과 출력

---

# 제외 범위

* HTML Report
* CSV Export
* CI Upload
