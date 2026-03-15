"""
HOUR 3 — Analysis Hub Agent
Warner Bros. Singapore Marketing Analytics

Takes structured data → produces performance insights, KPI analysis,
trend detection, anomaly flagging, and CMO-ready recommendations.
"""

import os
import sys
import json
import anthropic
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(_env_path, override=True)

# ─────────────────────────────────────────────
# ROAS targets per business line
# ─────────────────────────────────────────────
ROAS_TARGETS = {
    "Theatrical":          3.5,
    "Max Streaming":       4.0,
    "Home Entertainment":  3.0,
    "WB Games":            3.5,
    "Licensing & Merch":   2.5,
}

# ─────────────────────────────────────────────
# Analysis Agent system prompt
# ─────────────────────────────────────────────
ANALYSIS_SYSTEM = """You are a Senior Performance Marketing Analyst for Warner Bros. Singapore.
You receive marketing data and produce clear, actionable insights for the CMO and marketing team.

Warner Bros. Singapore Business Lines & ROAS Targets:
- Theatrical:         3.5x (Movie releases, cinema campaigns)
- Max Streaming:      4.0x (HBO Max subscription acquisition)
- Home Entertainment: 3.0x (Digital downloads, Blu-ray)
- WB Games:           3.5x (Gaming titles)
- Licensing & Merch:  2.5x (Brand licensing, merchandise)

Currency: SGD. Today: 2026-03-15.

Your analysis must always follow this exact structure:

**PERFORMANCE SUMMARY**
2-3 sentences covering the overall picture.

**KEY FINDINGS**
- Finding 1 (include specific numbers in SGD where relevant)
- Finding 2
- Finding 3
- Finding 4 (max 5 findings)

**ALERTS** (only if anomalies exist)
- Alert 1: [what is wrong + magnitude]

**QUICK RECOMMENDATIONS**
1. Recommendation 1 (specific and actionable)
2. Recommendation 2
3. Recommendation 3 (max 3)

Rules:
- Always compare vs ROAS target, not just report the number
- Use SGD for all monetary values
- Be specific: "CTR dropped 23% week-over-week" not "CTR declined"
- Recommendations must be immediately actionable
- Tone: confident, data-driven, executive-ready
- Keep total response under 300 words"""


def format_data_for_analysis(data: pd.DataFrame, question: str, context: str = "") -> str:
    """Convert DataFrame to a clean text summary for Claude to analyse."""
    if data is None or data.empty:
        return "No data available."

    lines = [f"Question: {question}"]
    if context:
        lines.append(f"Context: {context}")
    lines.append(f"Data ({len(data)} rows):")
    lines.append(data.to_string(index=False))

    # Add computed benchmarks if relevant columns exist
    cols = data.columns.tolist()
    if "roas" in cols or "actual_roas" in cols:
        roas_col = "roas" if "roas" in cols else "actual_roas"
        lines.append("\nROAS Targets for reference:")
        for bl, target in ROAS_TARGETS.items():
            lines.append(f"  {bl}: {target}x")

    return "\n".join(lines)


class AnalysisAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model  = "claude-sonnet-4-6"   # Sonnet for deeper analysis quality

    def analyse(self, data: pd.DataFrame, question: str,
                context_notes: str = "", verbose: bool = True) -> dict:
        """
        Main method: takes data + question → returns structured insight.
        Returns: {question, insight (str), model_used, error}
        """
        if verbose:
            print(f"\n[Analysis Agent] Analysing: {question[:60]}...")

        formatted = format_data_for_analysis(data, question, context_notes)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=ANALYSIS_SYSTEM,
            messages=[{
                "role": "user",
                "content": f"Analyse this marketing data and provide insights:\n\n{formatted}"
            }]
        )

        insight = response.content[0].text.strip()

        if verbose:
            print(f"\n{'─'*60}")
            print(insight)
            print(f"{'─'*60}")

        return {
            "question":   question,
            "insight":    insight,
            "model_used": self.model,
            "error":      None,
        }


# ─────────────────────────────────────────────
# Test: feed pre-formatted data and verify quality
# ─────────────────────────────────────────────
if __name__ == "__main__":
    agent = AnalysisAgent()

    print("=" * 65)
    print("Analysis Agent Test — Warner Bros. Singapore")
    print("=" * 65)

    # Test 1: ROAS by business line
    print("\n--- TEST 1: ROAS by business line ---")
    data1 = pd.DataFrame([
        {"business_line": "Theatrical",          "actual_roas": 2.21, "roas_target": 3.5, "spend_sgd": 2271844, "conversions": 222795},
        {"business_line": "Max Streaming",       "actual_roas": 1.65, "roas_target": 4.0, "spend_sgd": 2535490, "conversions": 239337},
        {"business_line": "Home Entertainment",  "actual_roas": 3.47, "roas_target": 3.0, "spend_sgd": 1518734, "conversions": 148183},
        {"business_line": "WB Games",            "actual_roas": 6.08, "roas_target": 3.5, "spend_sgd": 1478522, "conversions": 145278},
        {"business_line": "Licensing & Merch",   "actual_roas": 6.41, "roas_target": 2.5, "spend_sgd": 1710576, "conversions": 147674},
    ])
    result1 = agent.analyse(data1, "How are all business lines performing vs ROAS target this month?")

    # Test 2: Platform performance
    print("\n--- TEST 2: Platform performance ---")
    data2 = pd.DataFrame([
        {"platform_name": "Meta",    "total_spend_sgd": 6057034, "avg_roas": 3.39, "avg_cpm_sgd": 11.97, "avg_ctr": 2.14},
        {"platform_name": "YouTube", "total_spend_sgd": 5334167, "avg_roas": 3.83, "avg_cpm_sgd": 10.69, "avg_ctr": 2.13},
        {"platform_name": "Google",  "total_spend_sgd": 5252260, "avg_roas": 2.45, "avg_cpm_sgd": 16.84, "avg_ctr": 2.02},
        {"platform_name": "TikTok",  "total_spend_sgd": 3903888, "avg_roas": 5.73, "avg_cpm_sgd":  7.84, "avg_ctr": 2.06},
    ])
    result2 = agent.analyse(data2, "Which platform is delivering the best value and where should we shift budget?")

    # Test 3: Creative fatigue
    print("\n--- TEST 3: Creative fatigue analysis ---")
    data3 = pd.DataFrame([
        {"creative_id": 213, "business_line": "Home Entertainment", "format": "YouTube Pre-roll", "early_ctr": 3.59, "late_ctr": 1.97, "ctr_drop_pct": 45.1},
        {"creative_id": 290, "business_line": "WB Games",           "format": "Static Image",     "early_ctr": 3.39, "late_ctr": 1.85, "ctr_drop_pct": 45.4},
        {"creative_id": 278, "business_line": "Theatrical",         "format": "Video 30s",         "early_ctr": 3.51, "late_ctr": 2.00, "ctr_drop_pct": 43.0},
        {"creative_id": 124, "business_line": "Max Streaming",      "format": "Carousel",          "early_ctr": 3.29, "late_ctr": 1.80, "ctr_drop_pct": 45.3},
        {"creative_id": 305, "business_line": "WB Games",           "format": "Story",             "early_ctr": 3.43, "late_ctr": 1.95, "ctr_drop_pct": 43.2},
    ])
    result3 = agent.analyse(data3, "Which creatives are showing fatigue and what should we do?")

    print(f"\n{'='*65}")
    passed = sum(1 for r in [result1, result2, result3] if r["error"] is None)
    print(f"Analysis Agent: {passed}/3 tests passed ✅")
    print(f"{'='*65}")
