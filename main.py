from langgraph.graph import StateGraph, START, END

from state import FraudState
from router import ai_router
from agents.rule_engine_agent import rule_engine_agent
from agents.behaviour_agent import behaviour_agent
from agents.velocity_agent import velocity_agent
from agents.strategic_agent import strategic_agent
from evaluator import evaluator_node


def build_graph():
    workflow = StateGraph(FraudState)

    workflow.add_node("router", ai_router)
    workflow.add_node("rule_engine", rule_engine_agent)
    workflow.add_node("behaviour", behaviour_agent)
    workflow.add_node("velocity", velocity_agent)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("strategic", strategic_agent)

    workflow.add_edge(START, "router")
    workflow.add_edge("router", "rule_engine")
    workflow.add_edge("rule_engine", "behaviour")
    workflow.add_edge("behaviour", "velocity")
    workflow.add_edge("velocity", "evaluator")
    workflow.add_edge("evaluator", "strategic")
    workflow.add_edge("strategic", END)

    return workflow.compile()


def main():
    app = build_graph()

    print("=" * 60)
    print("FRAUDGUARD")
    print("AI-DRIVEN MULTI-AGENT FRAUD DETECTION SYSTEM")
    print("=" * 60)

    scenario = input("\nDescribe the fraud scenario:\n> ")

    initial_state = {
        "scenario": scenario,
        "agent_results": {},
        "errors": [],
    }

    result = app.invoke(initial_state)

    print("\n" + "=" * 60)
    print("FINAL FRAUDGUARD ASSESSMENT")
    print("=" * 60)

    print("\nScenario:")
    print(scenario)

    print("\nSelected Agents:")
    for agent in result.get("selected_agents", []):
        print("-", agent)

    print("\nAI Router Reason:")
    print(result.get("router_reason", "No reason available"))

    print("\nRisk Score:", result.get("risk_score", 0))
    print("Decision:", result.get("evaluator_decision", "UNKNOWN"))
    print("Final Action:", result.get("final_action", "UNKNOWN"))

    print("\nRecommendation:")
    print(
        result.get(
            "strategic_recommendation",
            "No recommendation available",
        )
    )

    if result.get("errors"):
        print("\nSystem Notes:")
        for error in result["errors"]:
            print("-", error)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
