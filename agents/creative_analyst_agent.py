"""
Creative Analyst Agent — Warner Bros. Singapore
Specialist agent for deep creative performance analysis.
Focuses on: format ROAS, CTR trends, fatigue curves, refresh priorities, new format tests.
"""

import os
import sys
import anthropic
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(_env_path, override=True)

CREATIVE_SYSTEM = """You are the Creative Performance Analyst for Warner Bros. Singapore.
You are a specialist in marketing creative analysis — ad formats, CTR curves, and creative fatigue.

Warner Bros. Singapore Creative Context:
- Formats: Video 15s, Video 30s, Static Image, Carousel, Story, Reel, YouTube Pre-roll
- Business Lines: Theatrical, Max Streaming, Home Entertainment, WB Games, Licensing & Merch
- Platforms: Meta (Story/Reel/Carousel/Video), Google (Static/Display), TikTok (Video 15s/Reel), YouTube (Pre-roll/Video 30s)
- Currency: SGD. Today: 2026-03-15
- Creative fatigue: CTR drop >20% from early period (days 0–30) to late period (days 60+)
- CTR benchmarks: Video 15s ~2.5%, Video 30s ~2.3%, Static Image ~1.8%, Carousel ~2.2%, Story ~2.0%, Reel ~2.6%, YouTube Pre-roll ~1.9%

Your analysis MUST follow this exact structure:

**CREATIVE PERFORMANCE SUMMARY**
2 sentences covering the creative landscape.

**TOP PERFORMERS**
- Format / Creative: [CTR, ROAS, why it works — specific numbers required]
- Format / Creative: [same]
- Format / Creative: [same]

**FATIGUE ALERTS** (include only if CTR drop >20% detected)
- [Creative/Format] on [Platform]: Early CTR [X]% → Late CTR [Y]%, drop [Z]% — Urgency: HIGH/MEDIUM
- [repeat for each fatigued creative]

**FORMAT RECOMMENDATIONS**
1. [Specific action — e.g. "Increase Video 15s budget on TikTok by SGD 8K — it's outperforming CTR benchmark by 22%"]
2. [Creative refresh recommendation with timeline]
3. [New format or platform to test with rationale]

**REFRESH PRIORITY LIST**
- URGENT (refresh within 7 days): [list creatives/formats]
- CAN WAIT (refresh within 30 days): [list creatives/formats]
- RETIRE: [formats/creatives to discontinue]

Rules:
- Always compare formats against each other AND against CTR benchmarks
- Recommendations must name the specific format AND platform
- Use SGD for all budget mentions
- Never recommend vague actions — e.g. not "improve creatives" but "replace the Video 30s Carousel on Meta with a 15s hook video"
- Keep total response under 400 words"""


class CreativeAnalystAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model  = "claude-sonnet-4-6"

    def analyse(self, data: pd.DataFrame, question: str,
                context_notes: str = "", verbose: bool = True) -> dict:
        """
        Deep creative analysis.
        Returns: {question, insight, model_used, agent, error}
        """
        if verbose:
            print(f"\n[Creative Analyst] Analysing: {question[:60]}...")

        if data is None or data.empty:
            formatted = f"Question: {question}\nNo creative data available."
        else:
            lines = [f"Question: {question}"]
            if context_notes:
                lines.append(f"Context: {context_notes}")
            lines.append(f"\nCreative Data ({len(data)} rows):")
            lines.append(data.to_string(index=False))
            lines.append("\nCTR Benchmarks: Video 15s=2.5%, Video 30s=2.3%, Static=1.8%, "
                         "Carousel=2.2%, Story=2.0%, Reel=2.6%, Pre-roll=1.9%")
            formatted = "\n".join(lines)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1100,
            system=CREATIVE_SYSTEM,
            messages=[{
                "role": "user",
                "content": f"Analyse this creative performance data and provide specialist insights:\n\n{formatted}"
            }]
        )

        insight = response.content[0].text.strip()

        if verbose:
            print(f"\n{'─'*60}\n{insight}\n{'─'*60}")

        return {
            "question":   question,
            "insight":    insight,
            "model_used": self.model,
            "agent":      "creative_analyst",
            "error":      None,
        }


# ─────────────────────────────────────────────────────────────
# Sample queries — for testing and demo
# ─────────────────────────────────────────────────────────────
CREATIVE_SAMPLE_QUERIES = [
    "Which creative format has the best ROAS across all platforms this month?",
    "Show me detailed creative fatigue analysis — which creatives need urgent refresh?",
    "How are video creatives (15s vs 30s) performing compared to static images?",
    "Which Reel and Story formats are working best on Meta?",
    "Give me a creative refresh priority list ranked by urgency",
    "What creative formats should we be testing that we're not running yet?",
    "Compare TikTok video performance vs YouTube Pre-roll — which deserves more budget?",
]

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from tools.sql_tool import query as sql_query

    agent = CreativeAnalystAgent()
    print("=" * 65)
    print("Creative Analyst Agent Test — Warner Bros. Singapore")
    print("=" * 65)

    result = sql_query(
        "Show creative performance by format with CTR, ROAS, spend this month",
        verbose=False,
    )
    data = result.get("data")

    for q in CREATIVE_SAMPLE_QUERIES[:2]:
        print(f"\n--- Query: {q[:60]}... ---")
        out = agent.analyse(data, q)
        print(f"Agent: {out['agent']} | Model: {out['model_used']}")

    print(f"\n{'='*65}")
    print("Creative Analyst Agent: Tests complete ✅")
    print(f"{'='*65}")
