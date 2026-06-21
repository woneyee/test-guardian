# Failure Responsibility Routing Agent System

## 프로젝트 개요

기존 AI Coding Agent는 테스트 실패를 코드 버그로 가정하고 구현 코드를 수정하는 방식으로 동작한다.

그러나 실제 TDD/CI 환경에서는 테스트 코드 자체의 오류, 요구사항 변경, 환경 문제 등 다양한 원인으로 테스트가 실패할 수 있다.

본 시스템은 테스트 실패를 단순 코드 버그로 간주하지 않고, 실패의 책임(Failure Responsibility)을 분석한 후 적절한 복구 전략으로 라우팅하는 LangGraph 기반 멀티 에이전트 시스템을 목표로 한다.

---

## 문제 정의

기존 방식

```text
CI Failure
↓
Coding Agent
↓
Code Fix
↓
Re-Test
```

문제점

* 테스트를 절대적인 정답으로 가정
* 테스트 코드 오류를 고려하지 않음
* 요구사항 변경을 반영하지 못함
* 잘못된 테스트에 맞추어 코드를 수정할 수 있음

---

## 제안 방식

```text
CI Failure
↓
Requirement Extractor
↓
Failure Analyzer
↓
Router
↓
┌───────────────────┐
│ CODE_BUG          │
│ TEST_BUG          │
└───────────────────┘
↓
Specialized Agent
↓
Patch
↓
Re-Test
↓
Pass ? End : Loop
```

---

## 전체 Workflow

### Step 1. CI Failure

CI 환경에서 테스트 실패 발생

입력

* CI Log
* Source Code
* Test Code

---

### Step 2. Requirement Extractor

프로젝트 요구사항 수집

입력

* README.md
* Issue.md

출력

```json
{
  "feature": "...",
  "requirement": "..."
}
```

목적

* 자연어 요구사항 정규화
* Failure Analyzer에 전달할 요구사항 생성

---

### Step 3. Failure Analyzer

실패 원인 분석

입력

* Requirement
* Source Code
* Test Code
* CI Log

출력

```json
{
  "failure_type": "CODE_BUG",
  "confidence": 0.92,
  "reason": "..."
}
```

---

### Step 4. Router

Failure Analyzer 결과를 기반으로 다음 Agent 결정

입력

```json
{
  "failure_type": "CODE_BUG"
}
```

출력

```text
coding_agent
```

Routing Rules

* CODE_BUG → Coding Agent
* TEST_BUG → Test Auditor

---

### Step 5-A. Coding Agent

목적

* 구현 코드 수정

입력

* Source Code
* Test Code
* CI Log
* Requirement

출력

* Code Patch

제약

* 테스트 수정 금지

---

### Step 5-B. Test Auditor

목적

* 테스트 코드 검증

입력

* Requirement
* Test Code
* Source Code

출력

* Test Patch

제약

* 구현 코드 수정 금지

---

### Step 6. Re-Test

수정 결과 검증

입력

* Patch 적용 결과

출력

```json
{
  "status": "PASS"
}
```

또는

```json
{
  "status": "FAIL"
}
```

FAIL인 경우 Failure Analyzer 단계로 재진입

---

## MVP 범위

현재 구현 범위

* Requirement Extractor
* Failure Analyzer
* Router

Failure Type

* CODE_BUG
* TEST_BUG

---

## 향후 확장 계획

Failure Type 추가

* ENV_BUG
* REQUIREMENT_DRIFT
* FLAKY_TEST

Requirement Source 확장

* README.md
* Issue.md
* Pull Request
* Docs
* Jira
* Confluence

Repository RAG 도입

* Chroma
* Qdrant
* FAISS

을 활용한 Semantic Requirement Retrieval 지원
## Future Work

Current MVP supports:

* CODE_BUG
* TEST_BUG

Validation experiments revealed additional failure responsibility categories that may be introduced in future versions.

### BOTH

Both implementation code and test code violate the requirement.

Example:

Requirement: 10% discount

Implementation: 5%

Test expectation: 20%

### UNKNOWN

Available evidence is insufficient or requirement sources conflict.

Example:

README and Issue specify contradictory requirements.

These categories are intentionally excluded from the MVP to keep routing behavior simple and measurable.
