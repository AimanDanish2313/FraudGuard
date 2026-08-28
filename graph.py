import asyncio
from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END, START


# --- 1. STATE DEFINITION ---
class FraudState(TypedDict):
    transaction_id: str
    amount: float
    user_id: str
    merchant: str
    is_high_priority: bool
    risk_score: float
    parallel_results: Dict[str, Any]
    evaluator_decision: Optional[str]
    final_action: str
    errors: List[str]


# --- 2. ROUTER & EVALUATOR SCHEMAS ---
class RouterOutput(BaseModel):
    is_high_priority: bool = Field(description="True if transaction requires priority/express path")
    reasoning: str


class EvaluatorOutput(BaseModel):
    decision: str = Field(description="APPROVE, REJECT, or MANUAL_REVIEW")
    confidence: float
    reasoning: str


# --- 3. NODE IMPLEMENTATIONS ---

def router_node(state: FraudState) -> Dict[str, Any]:
    """Router logic determining express vs. parallel flow."""
    # Express condition: High amount (> $5,000) or explicit flag
    amount = state.get("amount", 0.0)
    is_express = amount > 5000.0 or state.get("is_high_priority", False)
    
    return {
        "is_high_priority": is_express
    }


def express_node(state: FraudState) -> Dict[str, Any]:
    """Bypasses parallel agents for immediate escalation."""
    return {
        "final_action": "ESCALATED_HIGH_PRIORITY",
        "evaluator_decision": "MANUAL_REVIEW"
    }


# Parallel Sub-Agents (Batrisya & Damia implementation targets)
def rule_engine_agent(state: FraudState) -> Dict[str, Any]:
    # TODO (Batrisya): Implement deterministic rule checking
    return {"rule_engine": {"status": "PASSED", "score": 0.1}}


def ml_scoring_agent(state: FraudState) -> Dict[str, Any]:
    # TODO (Damia): Implement ML model inference / anomaly detection
    return {"ml_scoring": {"status": "PASSED", "score": 0.15}}


def combine_parallel_results(state: FraudState) -> Dict[str, Any]:
    """Aggregates parallel worker node outputs into state."""
    # Combines results populated by parallel steps
    results = state.get("parallel_results", {})
    return {"parallel_results": results}


def evaluator_node(state: FraudState) -> Dict[str, Any]:
    """Evaluates combined results with robust fallback logic."""
    try:
        results = state.get("parallel_results", {})
        rule_score = results.get("rule_engine", {}).get("score", 0.0)
        ml_score = results.get("ml_scoring", {}).get("score", 0.0)
        
        avg_score = (rule_score + ml_score) / 2.0
        
        if avg_score > 0.7:
            decision = "REJECT"
            action = "DECLINED"
        elif avg_score > 0.4:
            decision = "MANUAL_REVIEW"
            action = "PENDING_REVIEW"
        else:
            decision = "APPROVE"
            action = "APPROVED"
            
        return {
            "risk_score": avg_score,
            "evaluator_decision": decision,
            "final_action": action
        }
    except Exception as e:
        # Fallback mechanism in case evaluation fails
        return {
            "risk_score": 1.0,
            "evaluator_decision": "MANUAL_REVIEW",
            "final_action": "FALLBACK_MANUAL_REVIEW",
            "errors": [str(e)]
        }


# --- 4. CONDITIONAL ROUTING FUNCTION ---
def route_transaction(state: FraudState) -> str:
    if state.get("is_high_priority"):
        return "express_node"
    return "run_parallel"


# --- 5. BUILD GRAPH ---
builder = StateGraph(FraudState)

# Add Nodes
builder.add_node("router", router_node)
builder.add_node("express_node", express_node)
builder.add_node("rule_engine", rule_engine_agent)
builder.add_node("ml_scoring", ml_scoring_agent)
builder.add_node("evaluator", evaluator_node)

# Flow Connections
builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    route_transaction,
    {
        "express_node": "express_node",
        "run_parallel": "rule_engine"  # Parallel branch 1
    }
)

# Connect worker branches to evaluator
builder.add_edge("rule_engine", "evaluator")
builder.add_edge("ml_scoring", "evaluator")

# End connections
builder.add_edge("express_node", END)
builder.add_edge("evaluator", END)

# Compile Graph
graph = builder.compile()


# --- 6. DEMO EXECUTION ---
if __name__ == "__main__":
    print("\n--- Running Demo 1: Standard Transaction ---")
    normal_tx = {
        "transaction_id": "TX-1001",
        "amount": 150.0,
        "user_id": "USR-88",
        "merchant": "Store A",
        "is_high_priority": False,
        "parallel_results": {},
        "errors": []
    }
    out1 = graph.invoke(normal_tx)
    print(f"Result: {out1['final_action']} | Decision: {out1['evaluator_decision']}")

    print("\n--- Running Demo 2: High Priority Express Path ---")
    express_tx = {
        "transaction_id": "TX-9999",
        "amount": 12000.0,
        "user_id": "USR-01",
        "merchant": "Luxury Retail",
        "is_high_priority": True,
        "parallel_results": {},
        "errors": []
    }
    out2 = graph.invoke(express_tx)
    print(f"Result: {out2['final_action']} | Decision: {out2['evaluator_decision']}\n")