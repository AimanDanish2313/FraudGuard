from typing import TypedDict, List, Dict, Any


class FraudState(TypedDict, total=False):
    scenario: str

    transaction_id: str
    amount: float
    user_id: str
    merchant: str
    transaction_count_5m: int
    new_device: bool
    failed_logins: int
    description: str

    selected_agents: List[str]
    is_high_priority: bool
    router_reason: str

    agent_results: Dict[str, Any]

    risk_score: float
    evaluator_decision: str
    final_action: str
    strategic_recommendation: str

    errors: List[str]
