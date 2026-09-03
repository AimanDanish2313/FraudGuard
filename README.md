# FraudGuard - Gemini Scenario-Based Multi-Agent Fraud Detection

## What this version does

The user enters one natural-language fraud scenario. Gemini:
1. extracts transaction information from the scenario,
2. selects relevant specialist agents,
3. marks high-priority cases.

The local FraudGuard agents then calculate risk and the evaluator returns:
- APPROVE
- MANUAL_REVIEW
- REJECT

## Project structure

```text
FraudGuard_Gemini_Scenario/
├── main.py
├── state.py
├── router.py
├── evaluator.py
├── requirements.txt
├── .env.example
├── agents/
│   ├── __init__.py
│   ├── rule_engine_agent.py
│   ├── behaviour_agent.py
│   ├── velocity_agent.py
│   └── strategic_agent.py
└── tools/
    └── __init__.py
```

## Windows PowerShell setup

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
$env:GEMINI_API_KEY="your_gemini_api_key"
python main.py
```

Optional model override:

```powershell
$env:GEMINI_MODEL="gemini-2.5-flash"
```

## Example scenario

```text
A customer made six RM4,500 purchases within five minutes from a new device after seven failed login attempts.
```

The Gemini router should extract the relevant values and select rule_engine, behaviour, and velocity when appropriate.
