# Test Guardian Architecture

## Overview

Test Guardian is organized around agent responsibilities. Production flow uses binary failure responsibility classification:

```text
RequirementExtractor
-> FailureAnalyzer
-> Router
-> if TEST_BUG: TestAuditor
-> PipelineResult
```

Experimental evaluation modules may use extended labels such as `BOTH` and `UNKNOWN`, but those labels are not part of the production routing flow.

## Directory Structure

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
    requirements.py
    failure.py
    routing.py
    test_audit.py
    test_patch.py
    pipeline.py
    evaluation.py
    failure_evaluation.py
    adversarial.py
```

Compatibility wrappers remain at the old import paths, such as `test_guardian.analyzers` and `test_guardian.services`, to avoid breaking existing tests or callers during the transition.

Legacy LangGraph sketch files are preserved under `legacy/`.

## Component Responsibilities

### Requirement Extractor

Normalizes source requirement material into an `ExtractedRequirement`.

It does not classify failures, route agents, or generate patches.

### Failure Analyzer

Classifies CI/test failures as:

- `CODE_BUG`
- `TEST_BUG`

The production analyzer intentionally remains binary.

Experimental analyzers may classify:

- `CODE_BUG`
- `TEST_BUG`
- `BOTH`
- `UNKNOWN`

These experimental classes are used only for evaluation and prompt research.

### Router

Maps production `FailureAnalysisResult` objects to the next target:

- `CODE_BUG -> coding_agent`
- `TEST_BUG -> test_auditor`

The router does not inspect source code, test code, CI logs, or requirements.

### Test Auditor

Runs only for `TEST_BUG` cases and classifies the specific test issue:

- `WRONG_ASSERTION`
- `WRONG_EXCEPTION`
- `WRONG_INPUT`
- `OUTDATED_TEST`

### Test Patch Agent

Generates a structured test patch proposal.

It does not modify files, apply patches, commit changes, or run tests.

### Guardian Pipeline

Orchestrates the production agent sequence.

It owns flow control but delegates classification and reasoning to agents.

### Evaluation

Evaluation modules load fixtures, run analyzers or pipelines, and calculate metrics.

They are separated from production workflow code so experiments do not change routing behavior.

### CLI

CLI modules are thin entry points for running production and evaluation flows.

Root-level scripts remain as compatibility wrappers.

## Improvement Recommendations

1. Move compatibility wrappers out after downstream imports migrate.

The old packages can eventually be removed:

```text
test_guardian/analyzers/
test_guardian/auditors/
test_guardian/routers/
test_guardian/patch_agents/
test_guardian/services/
test_guardian/pipeline.py
```

2. Keep production and experimental labels separate.

Production should continue using `FailureType`, while experiments should use `ExperimentalFailureType`.

3. Add explicit human-review routing only after a product decision.

`BOTH` and `UNKNOWN` should not silently enter production routing until recovery behavior is defined.

4. Move prompts into dedicated prompt files if they continue to grow.

Current prompts are embedded in implementation files. A future structure could be:

```text
test_guardian/prompts/
  failure_analyzer_binary.md
  failure_analyzer_experimental_v1.md
  failure_analyzer_v2.md
  test_auditor.md
  test_patch_agent.md
```

5. Add dependency assembly/factory modules.

CLI modules currently build concrete OpenAI-backed components directly. A future `composition.py` or `container.py` could centralize production dependency wiring.
