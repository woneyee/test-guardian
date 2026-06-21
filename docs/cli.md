# Test Guardian CLI

## 목적

Test Guardian를 터미널에서 실행할 수 있도록 한다.

현재 구현된 Pipeline을 감싸는 실행 인터페이스를 제공한다.

---

# 실행 예시

```bash
python run.py \
  --readme README.md \
  --issue ISSUE.md \
  --source calculator.py \
  --test test_calculator.py \
  --log ci.log
```

---

# 입력

## --readme

README 파일 경로

예시

```bash
--readme README.md
```

---

## --issue

Issue 파일 경로

예시

```bash
--issue ISSUE.md
```

---

## --source

분석 대상 소스 코드

예시

```bash
--source src/calculator.py
```

---

## --test

분석 대상 테스트 코드

예시

```bash
--test tests/test_calculator.py
```

---

## --log

CI 실패 로그

예시

```bash
--log ci.log
```

---

# 동작 흐름

```text
README
Issue
Source
Test
CI Log

     ↓

GuardianPipeline

     ↓

PipelineResult
```

---

# 출력

JSON 출력

예시

```json
{
  "failure_type": "TEST_BUG",
  "reason_type": "WRONG_ASSERTION",
  "patch_type": "ASSERTION_FIX"
}
```

---

# 종료 코드

성공

```text
0
```

실패

```text
1
```

---

# 예외 처리

파일이 존재하지 않음

```text
File not found: README.md
```

---

필수 인자 누락

```text
Missing required argument
```

---

# 구현 범위

* argparse 사용
* 파일 읽기
* GuardianPipeline 호출
* JSON 출력

---

# 제외 범위

* GitHub Actions
* LangGraph
* Re-test loop
* Auto patch apply
* Auto commit
* Auto merge
