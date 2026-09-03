from state import FraudState


def evaluator_node(state: FraudState):
    try:
        results = state.get("agent_results", {})
        selected_agents = state.get("selected_agents", [])

        scores = []
        for agent in selected_agents:
            result = results.get(agent)
            if result is not None:
                scores.append(float(result["score"]))

        if not scores:
            return {
                "risk_score": 1.0,
                "evaluator_decision": "MANUAL_REVIEW",
                "final_action": "FALLBACK_MANUAL_REVIEW",
                "errors": state.get("errors", []) + [
                    "No fraud-agent scores available"
                ],
            }

        average_score = sum(scores) / len(scores)

        if average_score > 0.70:
            decision = "REJECT"
            final_action = "DECLINED"
        elif average_score > 0.40:
            decision = "MANUAL_REVIEW"
            final_action = "PENDING_REVIEW"
        else:
            decision = "APPROVE"
            final_action = "APPROVED"

        if state.get("is_high_priority") and decision == "APPROVE":
            decision = "MANUAL_REVIEW"
            final_action = "ESCALATED_HIGH_PRIORITY"

        print("\n=== EVALUATOR ===")
        print("Average Risk Score:", round(average_score, 3))
        print("Decision:", decision)
        print("Final Action:", final_action)

        return {
            "risk_score": round(average_score, 3),
            "evaluator_decision": decision,
            "final_action": final_action,
        }

    except Exception as exc:
        return {
            "risk_score": 1.0,
            "evaluator_decision": "MANUAL_REVIEW",
            "final_action": "FALLBACK_MANUAL_REVIEW",
            "errors": state.get("errors", []) + [f"Evaluator error: {exc}"],
        }
