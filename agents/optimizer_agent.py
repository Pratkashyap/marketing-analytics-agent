"""
Optimizer Agent — Warner Bros. Singapore
Budget & tactics optimization: given current performance, recommends exact SGD allocation.
Output: structured reallocation table + expected ROAS impact + immediate action steps.
"""

import os
import sys
import anthropic
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(_env_path, override=True)

OPTIMIZER_SYSTEM = """You are the Marketing Budget Optimizer for Warner Bros. Singapore.
You specialize in data-driven budget allocation and tactical optimization across platforms and business lines.

Warner Bros. Singapore Context:
- Business Lines & ROAS Targets: Theatrical (3.5x), Max Streaming (4.0x), Home Entertainment (3.0x), WB Games (3.5x), Licensing & Merch (2.5x)
- Platforms: Meta, Google, TikTok, YouTube
- Currency: SGD. Today: 2026-03-15
- Minimum viable monthly spend per active platform: SGD 5,000
- Optimization principle: Shift budget toward highest-ROAS channels; reduce investment where ROAS < target

Your output MUST follow this exact structure:

**CURRENT STATE**
2 sentences: where budget is concentrated now and the #1 inefficiency.

**RECOMMENDED REALLOCATION**
| Channel | Current Spend | Recommended | Change | Reason |
|---------|--------------|-------------|--------|--------|
[Fill every active channel — use specific SGD amounts]

**EXPECTED IMPACT**
- Blended ROAS: [current X.XXx] → [projected X.XXx after reallocation]
- Best win: [channel] from [X.Xx] → [Y.Yx ROAS, +SGD ZZZ revenue/month]
- Risk: [what could underperform — be specific]

**IMMEDIATE ACTIONS THIS WEEK**
1. [Action with exact SGD amount and platform — e.g. "Cut Google Awareness spend by SGD 12K, reallocate to TikTok Conversion campaigns"]
2. [Second action]
3. [Third action]

**30-DAY OUTLOOK**
One paragraph: projected trajectory if recommendations are followed, including expected blended ROAS range.

Rules:
- Always give specific SGD amounts, not just percentages
- Justify every shift with data from the input (ROAS vs target, CPM efficiency, conversion rate)
- Be bold — if data shows a 30% shift is warranted, recommend 30%, not 5%
- Flag any business line that would drop below SGD 5K minimum with a ⚠️ warning
- Never recommend cutting a channel below minimum without flagging it explicitly
- Keep total response under 450 words"""


class OptimizerAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model  = "claude-sonnet-4-6"

    def optimise(self, data: pd.DataFrame, question: str,
                 context_notes: str = "", verbose: bool = True) -> dict:
        """
        Budget optimization analysis.
        Returns: {question, insight, model_used, agent, error}
        """
        if verbose:
            print(f"\n[Optimizer Agent] Optimising: {question[:60]}...")

        if data is None or data.empty:
            formatted = (f"Optimization Question: {question}\n"
                         f"No performance data available for optimization.")
        else:
            lines = [f"Optimization Question: {question}"]
            if context_notes:
                lines.append(f"Context: {context_notes}")
            lines.append(f"\nCurrent Performance Data ({len(data)} rows):")
            lines.append(data.to_string(index=False))
            lines.append("\nROAS Targets: Theatrical=3.5x | Max Streaming=4.0x | "
                         "Home Entertainment=3.0x | WB Games=3.5x | Licensing & Merch=2.5x")
            lines.append("Minimum viable spend per platform: SGD 5,000/month")
            formatted = "\n".join(lines)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1300,
            system=OPTIMIZER_SYSTEM,
            messages=[{
                "role": "user",
                "content": f"Provide budget optimization recommendations based on this data:\n\n{formatted}"
            }]
        )

        insight = response.content[0].text.strip()

        if verbose:
            print(f"\n{'─'*60}\n{insight}\n{'─'*60}")

        return {
            "question":   question,
            "insight":    insight,
            "model_used": self.model,
            "agent":      "optimizer",
            "error":      None,
        }


# ─────────────────────────────────────────────────────────────
# Sample queries — for testing and demo
# ─────────────────────────────────────────────────────────────
OPTIMIZER_SAMPLE_QUERIES = [
    "I have SGD 50K extra budget this month — where should I allocate it for maximum ROAS?",
    "Rebalance my entire budget to maximise blended ROAS across all platforms",
    "Which platforms am I over-investing in relative to ROAS performance?",
    "Should I shift budget from Google to TikTok? Show me the numbers",
    "Give me a full budget optimisation plan for April 2026",
    "Which business lines are wasting budget and where should it go instead?",
    "If I need to cut total budget by 20%, what's the smartest way to do it?",
]

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from tools.sql_tool import query as sql_query

    agent = OptimizerAgent()
    print("=" * 65)
    print("Optimizer Agent Test — Warner Bros. Singapore")
    print("=" * 65)

    result = sql_query(
        "Show spend and ROAS by platform and business line this month",
        verbose=False,
    )
    data = result.get("data")

    for q in OPTIMIZER_SAMPLE_QUERIES[:2]:
        print(f"\n--- Query: {q[:60]}... ---")
        out = agent.optimise(data, q)
        print(f"Agent: {out['agent']} | Model: {out['model_used']}")

    print(f"\n{'='*65}")
    print("Optimizer Agent: Tests complete ✅")
    print(f"{'='*65}")
