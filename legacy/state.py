from typing_extensions import TypedDict

class GraphState(TypedDict):
    error_log: str
    failure_type: str
    diagnosis_reason: str