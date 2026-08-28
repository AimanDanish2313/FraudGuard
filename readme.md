# FraudGuard - Multi-Agent Fraud Detection Engine

FraudGuard is a stateful LangGraph pipeline designed to process real-time transactions through dynamically routed verification nodes.

## Core Architecture
* **Router Node**: Directs standard transactions to parallel evaluation agents and high-value or flagged requests directly to express handling.
* **Parallel Workers**:
  * `rule_engine`: Evaluates static business rules (Assigned to Batrisya).
  * `ml_scoring`: Runs ML model inference (Assigned to Damia).
* **Evaluator Node**: Aggregates worker signals, calculates overall risk scores, and includes fallback mechanisms for unexpected errors.

## Quick Start

1. **Activate Virtual Environment**:
   ```bash
   .\venv\Scripts\activate