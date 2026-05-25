from langgraph.graph import StateGraph, END

from state import GraphState
from router import responsibility_router

from agents.diagnosis_agent import diagnosis_agent
from agents.test_auditor_agent import test_auditor_agent
from agents.coding_agent import coding_agent

# Graph 생성
builder = StateGraph(GraphState)

# Node 등록
builder.add_node("diagnosis", diagnosis_agent)
builder.add_node("test_auditor", test_auditor_agent)
builder.add_node("coding_agent", coding_agent)

# 시작점
builder.set_entry_point("diagnosis")

# Conditional Routing
builder.add_conditional_edges(
    "diagnosis",
    responsibility_router
)

# 종료
builder.add_edge("test_auditor", END)
builder.add_edge("coding_agent", END)

# Compile
graph = builder.compile()

# 실행
result = graph.invoke({
    "error_log": "AssertionError: expected 99999 got 30000",
    "failure_type": "",
    "diagnosis_reason": ""
})

print(result)