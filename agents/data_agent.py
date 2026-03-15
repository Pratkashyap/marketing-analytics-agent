"""
HOUR 2 — Data Ingestion Agent
Warner Bros. Singapore Marketing Analytics

Receives a natural language question → fetches structured data from DuckDB.
Acts as the data layer for the Orchestrator and Analysis agents.
"""

import os
import sys
import anthropic
from dotenv import load_dotenv

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from tools.sql_tool import query as sql_query

_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(_env_path, override=True)

# ─────────────────────────────────────────────
# Agent system prompt
# ─────────────────────────────────────────────
DATA_AGENT_SYSTEM = """You are the Data Ingestion Agent for Warner Bros. Singapore's marketing analytics system.

Your job:
1. Receive a marketing question
2. Decide what data is needed
3. Formulate the right query (you work with a SQL tool that handles execution)
4. Return clean, structured data with context

Warner Bros. Singapore Business Lines:
- Theatrical        (ROAS target: 3.5x) — Movie releases
- Max Streaming     (ROAS target: 4.0x) — HBO Max subscriptions
- Home Entertainment(ROAS target: 3.0x) — Digital downloads, Blu-ray
- WB Games          (ROAS target: 3.5x) — Gaming titles
- Licensing & Merch (ROAS target: 2.5x) — Brand licensing

Currency: SGD. Today: 2026-03-15.
Time windows: "this month"=March 2026, "last 7 days"=2026-03-08 to 2026-03-14, "last 30 days"=2026-02-13 to 2026-03-14

When you receive a question, respond with a JSON object:
{
  "query_type": "simple|multi|comparison|trend",
  "time_window": "description of time period",
  "refined_question": "optimized question for SQL generation",
  "context_notes": "any important business context"
}

Be precise. Marketing questions often need careful time-window handling."""


class DataAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model  = "claude-haiku-4-5-20251001"

    def _classify_query(self, question: str) -> dict:
        """Ask Claude to classify and refine the query before SQL generation."""
        import json, re
        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=DATA_AGENT_SYSTEM,
            messages=[{"role": "user", "content": f"Classify this query: {question}"}]
        )
        text = response.content[0].text.strip()
        # Extract JSON from response
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return {
            "query_type": "simple",
            "time_window": "last 30 days",
            "refined_question": question,
            "context_notes": ""
        }

    def fetch(self, question: str, verbose: bool = True) -> dict:
        """
        Main method: takes a question, returns structured data.
        Returns: {question, query_type, sql, data (DataFrame), error, row_count}
        """
        if verbose:
            print(f"\n[Data Agent] Received: {question}")

        # Step 1: Classify & refine
        classification = self._classify_query(question)
        refined_q = classification.get("refined_question", question)

        if verbose:
            print(f"[Data Agent] Type: {classification.get('query_type')} | "
                  f"Window: {classification.get('time_window')}")

        # Step 2: Run SQL tool
        result = sql_query(refined_q, verbose=verbose)

        return {
            "question":      question,
            "refined":       refined_q,
            "query_type":    classification.get("query_type"),
            "time_window":   classification.get("time_window"),
            "context_notes": classification.get("context_notes", ""),
            "sql":           result.get("sql"),
            "data":          result.get("data"),
            "error":         result.get("error"),
            "row_count":     len(result["data"]) if result.get("data") is not None else 0,
        }


# ─────────────────────────────────────────────
# Test with 8 queries from the sprint plan
# ─────────────────────────────────────────────
if __name__ == "__main__":
    agent = DataAgent()

    test_queries = [
        "Total spend across all platforms this month",
        "Meta campaign performance last 7 days by campaign",
        "Top 5 creatives by CTR on TikTok",
        "Compare Google vs Meta ROAS for the Theatrical business line",
        "Which ad sets have frequency above 5?",
        "Daily spend trend for the last 7 days",
        "Campaigns with ROAS below target",
        "Creative performance breakdown for video vs static",
    ]

    print("=" * 65)
    print("Data Agent Test — 8 queries")
    print("=" * 65)

    passed = 0
    for q in test_queries:
        result = agent.fetch(q, verbose=True)
        if result["error"] is None and result["row_count"] >= 0:
            passed += 1
            status = "✅"
        else:
            status = f"❌ {result['error']}"
        print(f"\n  {status} | Rows: {result['row_count']} | Q: {q[:55]}")

    print(f"\n{'='*65}")
    print(f"Data Agent: {passed}/{len(test_queries)} queries passed")
    print(f"{'='*65}")
