# Failure Analyzer Prompt V1 Results

## Summary

Prompt V1 was evaluated on the 32-case failure classification dataset.

| Metric | Result |
| --- | ---: |
| Total Cases | 32 |
| Overall Accuracy | 59.38% |
| Correct | 19 |
| Incorrect | 13 |

## Accuracy By Class

| Failure Type | Correct / Total | Accuracy |
| --- | ---: | ---: |
| CODE_BUG | 8 / 8 | 100% |
| TEST_BUG | 8 / 8 | 100% |
| BOTH | 1 / 8 | 12.5% |
| UNKNOWN | 2 / 8 | 25% |

## Confusion Matrix

Rows are expected labels. Columns are predicted labels.

| Expected \ Predicted | CODE_BUG | TEST_BUG | BOTH | UNKNOWN |
| --- | ---: | ---: | ---: | ---: |
| CODE_BUG | 8 | 0 | 0 | 0 |
| TEST_BUG | 0 | 8 | 0 | 0 |
| BOTH | 5 | 1 | 1 | 1 |
| UNKNOWN | 3 | 3 | 0 | 2 |

## Observations

Prompt V1 performs strongly on clean binary cases.

It correctly classified all `CODE_BUG` and `TEST_BUG` examples, but it struggled with mixed-responsibility and insufficient-information cases. Most `BOTH` examples were collapsed into `CODE_BUG`, and most `UNKNOWN` examples were over-inferred as either `CODE_BUG` or `TEST_BUG`.
