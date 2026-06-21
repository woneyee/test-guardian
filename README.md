# Test Guardian

Test Guardian is an agent-based system for routing CI/test failures by responsibility.

Instead of assuming every failing test means an implementation bug, Test Guardian analyzes the failure and routes it to the right recovery path.

Production classification is intentionally binary:

- `CODE_BUG`
- `TEST_BUG`

Experimental evaluation code also explores `BOTH` and `UNKNOWN`, but those labels are not part of the production routing flow.

## Architecture

```text
RequirementExtractor
-> FailureAnalyzer
-> Router
-> if TEST_BUG: TestAuditor
-> PipelineResult
```

Current package structure:

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

Compatibility wrappers remain at the old import paths and root CLI script names, so existing usage such as `py -3.12 run.py ...` still works.

## Agents

### RequirementExtractor

Normalizes natural-language requirement sources into an `ExtractedRequirement`.

Implementation:

- `SimpleRequirementExtractor`

### FailureAnalyzer

Classifies the CI failure responsibility as:

- `CODE_BUG`
- `TEST_BUG`

Implementation:

- `OpenAIFailureAnalyzer`

Experimental implementations:

- `OpenAIFailureAnalyzerExperimentalV1`
- `OpenAIFailureAnalyzerV2`

### Router

Routes the `FailureAnalysisResult` to the next target:

- `CODE_BUG -> coding_agent`
- `TEST_BUG -> test_auditor`

Implementation:

- `SimpleFailureRouter`

### TestAuditor

Runs only when the failure is classified as `TEST_BUG`.

Supported reason types:

- `WRONG_ASSERTION`
- `WRONG_EXCEPTION`
- `WRONG_INPUT`
- `OUTDATED_TEST`

Implementation:

- `OpenAITestAuditor`

### TestPatchAgent

Generates a structured test patch proposal.

It does not modify files or apply patches.

Supported patch types:

- `ASSERTION_FIX`
- `EXCEPTION_FIX`
- `INPUT_FIX`
- `REQUIREMENT_SYNC`

Implementation:

- `OpenAITestPatchAgent`

## Environment Variables

Required for OpenAI-backed agents:

```text
OPENAI_API_KEY
```

Optional:

```text
OPENAI_MODEL
```

If `OPENAI_MODEL` is not set, the default model is:

```text
gpt-4.1-mini
```

Local `.env` files must not be committed.

## Run The Pipeline

```bash
py -3.12 run.py \
  --readme README.md \
  --issue ISSUE.md \
  --source src/calculator.py \
  --test tests/test_calculator.py \
  --log ci.log
```

The command prints a JSON `PipelineResult`.

## Run Evaluation

Evaluate the standard fixture dataset:

```bash
py -3.12 evaluate.py
```

Evaluate experimental 4-class FailureAnalyzer fixtures:

```bash
py -3.12 failure_classification_evaluate.py --limit 1
py -3.12 failure_classification_evaluate.py --limit 32
```

Compare experimental prompt V1 and V2:

```bash
py -3.12 failure_classification_evaluate_v2.py --limit 32
```

Run adversarial evaluation:

```bash
py -3.12 adversarial_evaluate.py --limit 1 --verbose
```

Use `--limit` before live API runs to control cost.

## Tests

Run all unit tests:

```bash
py -3.12 -m unittest discover -s tests
```

Unit tests use fake clients and fake pipelines. They do not call the OpenAI API.

## Documentation

Additional documentation:

- `docs/ARCHITECTURE.md`
- `docs/SYSTEM_OVERVIEW.md`
- `docs/TEST_AUDITOR.md`
- `docs/TEST_PATCH_AGENT.md`
- `docs/EVALUATION_RUNNER.md`
- `docs/experiments/comparison.md`
