# Failure Analyzer Prompt V2 Results

## Summary

Prompt V2 was evaluated on the same 32-case failure classification dataset.

V2 introduced an explicit source/test responsibility check before selecting the final label:

```text
Does the source code violate the requirement?
Does the test code violate the requirement?
```

| Metric | Result |
| --- | ---: |
| Total Cases | 32 |
| Overall Accuracy | 56.25% |
| Correct | 18 |
| Incorrect | 14 |

## Accuracy By Class

| Failure Type | Correct / Total | Accuracy |
| --- | ---: | ---: |
| CODE_BUG | 6 / 8 | 75% |
| TEST_BUG | 3 / 8 | 37.5% |
| BOTH | 6 / 8 | 75% |
| UNKNOWN | 3 / 8 | 37.5% |

## Confusion Matrix

Rows are expected labels. Columns are predicted labels.

| Expected \ Predicted | CODE_BUG | TEST_BUG | BOTH | UNKNOWN |
| --- | ---: | ---: | ---: | ---: |
| CODE_BUG | 6 | 0 | 2 | 0 |
| TEST_BUG | 1 | 3 | 4 | 0 |
| BOTH | 2 | 0 | 6 | 0 |
| UNKNOWN | 2 | 3 | 0 | 3 |

## Observations

Prompt V2 significantly improved `BOTH` detection, increasing accuracy from 12.5% to 75%.

However, it introduced over-classification of `BOTH`. Several clean `TEST_BUG` cases were incorrectly classified as `BOTH`, even when the source code matched the requirement and only the test violated it.

V2 also reduced `CODE_BUG` and `TEST_BUG` accuracy compared with V1. The intermediate source/test reasoning helped mixed cases, but the final label was sometimes inconsistent with the stated routing rules.
