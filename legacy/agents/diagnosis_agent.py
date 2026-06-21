def diagnosis_agent(state):

    print("Diagnosis Agent 실행")

    error_log = state["error_log"]

    if "AssertionError" in error_log:
        return {
            "failure_type": "test_bug",
            "diagnosis_reason": "Assertion mismatch"
        }

    return {
        "failure_type": "code_bug",
        "diagnosis_reason": "Default classification"
    }