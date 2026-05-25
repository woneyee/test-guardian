def responsibility_router(state):

    failure_type = state["failure_type"]

    if failure_type == "test_bug":
        return "test_auditor"

    return "coding_agent"