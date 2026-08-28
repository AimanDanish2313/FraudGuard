import pytest
from graph import router_node, evaluator_node, FraudState

def test_router_express_flag():
    state: FraudState = {
        "transaction_id": "T1",
        "amount": 100.0,
        "user_id": "U1",
        "merchant": "M1",
        "is_high_priority": True,
        "risk_score": 0.0,
        "parallel_results": {},
        "evaluator_decision": None,
        "final_action": "",
        "errors": []
    }
    result = router_node(state)
    assert result["is_high_priority"] is True

def test_router_high_amount_express():
    state: FraudState = {
        "transaction_id": "T2",
        "amount": 6000.0,
        "user_id": "U2",
        "merchant": "M2",
        "is_high_priority": False,
        "risk_score": 0.0,
        "parallel_results": {},
        "evaluator_decision": None,
        "final_action": "",
        "errors": []
    }
    result = router_node(state)
    assert result["is_high_priority"] is True

def test_evaluator_fallback_on_error():
    # Pass None to force an AttributeError and trigger the exception handler
    state = None
    result = evaluator_node(state)
    assert result["evaluator_decision"] == "MANUAL_REVIEW"
    assert result["final_action"] == "FALLBACK_MANUAL_REVIEW"
    assert len(result["errors"]) > 0