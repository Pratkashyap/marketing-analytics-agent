"""
Insight Quality Critic Agent — Warner Bros. Singapore
Reviews every insight before it reaches the CMO.
Checks: specificity of numbers, actionability, correct ROAS target usage, tone.
Fast model (Haiku) — adds quality score and optionally improves the insight.
"""

import os
import sys
import anthropic
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(_env_path, override=True)

CRITIC_SYSTEM = """You are the Insight Quality Critic for Warner Bros. Singapore's marketing analytics system.
You review insights before they reach the CMO. Your job is fast, precise quality control.

Score each insight on 5 criteria (0–2 points each, max 10):
1. Specificity   — Are real numbers and SGD amounts present? (not vague like "ROAS improved")
2. Actionability — Can the CMO act on this TODAY? Are recommendations concrete?
3. Accuracy      — Are ROAS targets referenced correctly? (Theatrical=3.5x, Max=4.0x, HomeEnt=3.0x, WBGames=3.5x, L&M=2.5x)
4. Completeness  — Does the insight answer the full question asked?
5. Tone          — Is it confident, executive-ready, data-driven? (no hedging like "might", "could possibly")

Output rules:
- If score >= 8: Return EXACTLY this line, then the ORIGINAL insight unchanged:
  ✅ Quality Score: [X]/10 — Approved

- If score 6–7: Return this line, then the ORIGINAL insight with a short ⚡ improvement appended:
  ⚡ Quality Score: [X]/10 — Enhanced

- If score < 6: Return this line, then a rewritten version of the weakest section only:
  🔧 Quality Score: [X]/10 — Revised

Never add lengthy critique. Just score badge + (optionally) improved content.
Your addition/revision must be under 60 words.
Do not repeat the score at the end."""


class CriticAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model  = "claude-haiku-4-5-20251001"   # Fast — just reviewing

    def review(self, insight: str, question: str, verbose: bool = True) -> dict:
        """
        Review and optionally improve an insight.
        Returns: {reviewed_insight, score, model_used, agent, error}
        """
        if verbose:
            print(f"\n[Quality Critic] Reviewing insight for: {question[:50]}...")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1300,
            system=CRITIC_SYSTEM,
            messages=[{
                "role": "user",
                "content": (f"Question asked: {question}\n\n"
                            f"Insight to review:\n\n{insight}")
            }]
        )

        reviewed = response.content[0].text.strip()

        # Extract score from first line
        score = None
        first_line = reviewed.split("\n")[0]
        import re
        m = re.search(r"(\d+)/10", first_line)
        if m:
            score = int(m.group(1))

        if verbose:
            print(f"  → {first_line}")

        return {
            "reviewed_insight": reviewed,
            "score":            score,
            "model_used":       self.model,
            "agent":            "critic",
            "error":            None,
        }


if __name__ == "__main__":
    agent = CriticAgent()
    print("=" * 65)
    print("Quality Critic Agent Test — Warner Bros. Singapore")
    print("=" * 65)

    test_insight = """**PERFORMANCE SUMMARY**
Overall performance is mixed. Some business lines are doing well while others could improve.

**KEY FINDINGS**
- Revenue looks okay
- ROAS is around 3x for most lines
- TikTok seems to be doing better than Google

**RECOMMENDATIONS**
1. Consider shifting budget
2. Review creative performance
3. Monitor results"""

    test_q = "How are all business lines performing vs ROAS target this month?"

    result = agent.review(test_insight, test_q)
    print(f"\nReviewed insight:\n{result['reviewed_insight']}")
    print(f"\nScore: {result['score']}/10")
    print(f"\n{'='*65}")
    print("Quality Critic Agent: Test complete ✅")
    print(f"{'='*65}")
