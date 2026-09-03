import json
import os

from google import genai
from google.genai import types

from state import FraudState


VALID_AGENTS = {"rule_engine", "behaviour", "velocity"}


def ai_router(state: FraudState):
    scenario = state.get("scenario", "")

    prompt = f"""
You are the AI Router and Scenario Parser for FraudGuard.

FraudGuard is a multi-agent financial fraud detection system.
The user provides one fraud or transaction scenario in natural language.

TASK 1 - Extract transaction information:
- transaction_id
- amount
- user_id
- merchant
- transaction_count_5m
- new_device
- failed_logins
- description

If details are missing, use these defaults:
transaction_id = "UNKNOWN"
amount = 0
user_id = "UNKNOWN"
merchant = "UNKNOWN"
transaction_count_5m = 1
new_device = false
failed_logins = 0

TASK 2 - Select relevant specialist agents:
- rule_engine: suspicious/high transaction amounts and deterministic fraud rules
- behaviour: new device, failed logins, unusual account behaviour, possible account takeover
- velocity: repeated or rapid transactions in a short time

Select one or more agents.

TASK 3 - Decide whether the case is high priority.

Return ONLY valid JSON using exactly these keys:
{{
  "transaction_id": "TX-001",
  "amount": 4500,
  "user_id": "USR-001",
  "merchant": "Online Store",
  "transaction_count_5m": 6,
  "new_device": true,
  "failed_logins": 7,
  "description": "Short description",
  "selected_agents": ["rule_engine", "behaviour", "velocity"],
  "is_high_priority": true,
  "reason": "Short routing explanation"
}}

Fraud scenario:
{scenario}
"""

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

        client = genai.Client(api_key=api_key)
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )

        result = json.loads(response.text)

        selected_agents = [
            agent for agent in result.get("selected_agents", [])
            if agent in VALID_AGENTS
        ]
        if not selected_agents:
            selected_agents = ["rule_engine", "behaviour", "velocity"]

        amount = float(result.get("amount", 0) or 0)
        transaction_count_5m = int(result.get("transaction_count_5m", 1) or 1)
        failed_logins = int(result.get("failed_logins", 0) or 0)
        new_device = bool(result.get("new_device", False))
        is_high_priority = bool(result.get("is_high_priority", False))

        if amount > 5000:
            is_high_priority = True

        reason = result.get(
            "reason",
            "Gemini selected the relevant fraud specialists."
        )

        print("\n" + "=" * 60)
        print("GEMINI AI ROUTER")
        print("=" * 60)
        print("Transaction ID:", result.get("transaction_id", "UNKNOWN"))
        print("Amount: RM", amount)
        print("Merchant:", result.get("merchant", "UNKNOWN"))
        print("Transactions in 5 minutes:", transaction_count_5m)
        print("New Device:", new_device)
        print("Failed Logins:", failed_logins)
        print("Selected Agents:", selected_agents)
        print("High Priority:", is_high_priority)
        print("Routing Reason:", reason)

        return {
            "transaction_id": result.get("transaction_id", "UNKNOWN"),
            "amount": amount,
            "user_id": result.get("user_id", "UNKNOWN"),
            "merchant": result.get("merchant", "UNKNOWN"),
            "transaction_count_5m": transaction_count_5m,
            "new_device": new_device,
            "failed_logins": failed_logins,
            "description": result.get("description", scenario),
            "selected_agents": selected_agents,
            "is_high_priority": is_high_priority,
            "router_reason": reason,
        }

    except Exception as exc:
        message = f"Gemini Router Error: {exc}"
        print("\n" + message)

        return {
            "transaction_id": "UNKNOWN",
            "amount": 0.0,
            "user_id": "UNKNOWN",
            "merchant": "UNKNOWN",
            "transaction_count_5m": 1,
            "new_device": False,
            "failed_logins": 0,
            "description": scenario,
            "selected_agents": ["rule_engine", "behaviour", "velocity"],
            "is_high_priority": True,
            "router_reason": "Gemini unavailable. All agents selected for safety.",
            "errors": state.get("errors", []) + [message],
        }
