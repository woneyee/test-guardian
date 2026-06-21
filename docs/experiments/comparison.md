# Failure Analyzer Prompt V1 vs V2 Comparison

## Accuracy Comparison

| Failure Type | V1 Accuracy | V2 Accuracy | Change |
| --- | ---: | ---: | ---: |
| CODE_BUG | 100% | 75% | -25 pts |
| TEST_BUG | 100% | 37.5% | -62.5 pts |
| BOTH | 12.5% | 75% | +62.5 pts |
| UNKNOWN | 25% | 37.5% | +12.5 pts |
| Overall | 59.38% | 56.25% | -3.13 pts |

## Key Findings

1. V1 performs strongly on binary classification.

V1 correctly classified all clean `CODE_BUG` and `TEST_BUG` cases. This makes it a better fit for the current MVP production routing flow.

2. V2 significantly improves BOTH detection.

V2 improved `BOTH` accuracy from 1/8 to 6/8 by forcing explicit source-code and test-code responsibility checks.

3. V2 introduces over-classification of BOTH.

V2 often classified cases as `BOTH` when only the test violated the requirement. This was especially harmful for clean `TEST_BUG` cases.

4. V2 reduces TEST_BUG accuracy.

`TEST_BUG` accuracy dropped from 8/8 to 3/8. The added source/test reasoning made the model more sensitive to disagreement between source and test, but it sometimes treated disagreement itself as evidence that both sides were wrong.

5. BOTH and UNKNOWN remain future work.

`BOTH` improved under V2 but is not stable enough for production routing. `UNKNOWN` remains weak in both prompts because the model often infers missing business rules from vague requirements or sparse CI logs.

## Confusion Matrix Summary

### V1

| Expected \ Predicted | CODE_BUG | TEST_BUG | BOTH | UNKNOWN |
| --- | ---: | ---: | ---: | ---: |
| CODE_BUG | 8 | 0 | 0 | 0 |
| TEST_BUG | 0 | 8 | 0 | 0 |
| BOTH | 5 | 1 | 1 | 1 |
| UNKNOWN | 3 | 3 | 0 | 2 |

### V2

| Expected \ Predicted | CODE_BUG | TEST_BUG | BOTH | UNKNOWN |
| --- | ---: | ---: | ---: | ---: |
| CODE_BUG | 6 | 0 | 2 | 0 |
| TEST_BUG | 1 | 3 | 4 | 0 |
| BOTH | 2 | 0 | 6 | 0 |
| UNKNOWN | 2 | 3 | 0 | 3 |

## Conclusion

The MVP will continue using binary classification:

- `CODE_BUG`
- `TEST_BUG`

`BOTH` and `UNKNOWN` remain experimental and are not part of the production routing flow.

Future prompt work should preserve V1's binary accuracy while selectively improving mixed-responsibility and insufficient-information handling. In particular, any future V3 prompt should enforce consistency between intermediate source/test judgments and the final label.
