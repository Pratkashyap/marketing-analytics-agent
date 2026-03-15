"""
Orchestrator Agent — Warner Bros. Singapore Marketing Analytics

Central routing agent:
  User question
    → classify intent + specialist type
    → Data Agent (always)
    → Specialist Agent (Analysis | Creative Analyst | Optimizer)
    → Quality Critic (always — reviews before delivery)
    → final answer

Intent types:
  data_only    → fetch + return data, no analysis
  analysis     → fetch → Analysis Agent → Critic
  comparison   → fetch → Analysis Agent → Critic
  out_of_scope → politely decline
  error        → handle gracefully

Specialist types:
  analysis   → general Analysis Agent (default)
  creative   → Creative Analyst Agent (format/fatigue/CTR questions)
  optimizer  → Optimizer Agent (budget allocation questions)
"""

import os
import sys
import json
import re
import anthropic
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from agents.data_agent             import DataAgent
from agents.analysis_agent         import AnalysisAgent
from agents.creative_analyst_agent import CreativeAnalystAgent
from agents.optimizer_agent        import OptimizerAgent
from agents.critic_agent           import CriticAgent

_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(_env_path, override=True)

# ─────────────────────────────────────────────
# Orchestrator system prompt
# ─────────────────────────────────────────────
ORCHESTRATOR_SYSTEM = """You are the Orchestrator for Warner Bros. Singapore's Marketing Analytics Agent.
Your job: classify incoming questions and decide how to handle them.

Respond ONLY with a JSON object (no other text):
{
  "intent": "analysis|data_only|comparison|out_of_scope",
  "specialist": "analysis|creative|optimizer",
  "needs_analysis": true|false,
  "scope": "brief description of what data is needed",
  "refined_question": "cleaned up version of the question",
  "out_of_scope_reason": "only if out_of_scope"
}

Intent rules:
- "data_only"    → user wants raw numbers/tables only (e.g. "show me spend by platform", "list campaigns")
- "analysis"     → user wants insights, explanations, recommendations, or performance reviews
- "comparison"   → user wants to compare two things (e.g. "Meta vs Google", "this month vs last month")
- "out_of_scope" → completely unrelated to marketing analytics (weather, jokes, coding help, etc.)

Specialist routing rules:
- "creative"  → question is primarily about: ad formats, creative fatigue, CTR by creative/format, which creatives to refresh, video vs static, Story/Reel performance, creative-specific recommendations
- "optimizer" → question is primarily about: budget allocation, where to spend more/less, budget rebalancing, "I have $X extra", ROI maximisation, shifting budget between platforms or business lines, cutting spend, next month's budget plan
- "analysis"  → ALL other analytical questions: campaign performance, business line ROAS, platform comparison, trend analysis, why something is underperforming, full reviews (default)

Warner Bros. Singapore context:
- Business lines: Theatrical, Max Streaming, Home Entertainment, WB Games, Licensing & Merch
- Platforms: Meta, Google, TikTok, YouTube
- Currency: SGD. Today: 2026-03-15
- Always set needs_analysis=true for: "performing", "how are", "why", "should", "recommend", "review", "what's happening", "where should", "optimise", "allocate", "refresh", "fatigue" questions
- When in doubt, default to intent="analysis", specialist="analysis" """


class Orchestrator:
    def __init__(self):
        self.client          = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model           = "claude-haiku-4-5-20251001"
        self.data_agent      = DataAgent()
        self.analysis_agent  = AnalysisAgent()
        self.creative_agent  = CreativeAnalystAgent()
        self.optimizer_agent = OptimizerAgent()
        self.critic_agent    = CriticAgent()

    def _classify(self, question: str) -> dict:
        """Classify intent + specialist type of the question."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=350,
            system=ORCHESTRATOR_SYSTEM,
            messages=[{"role": "user", "content": question}]
        )
        text  = response.content[0].text.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {
            "intent":           "analysis",
            "specialist":       "analysis",
            "needs_analysis":   True,
            "scope":            question,
            "refined_question": question,
        }

    def _handle_out_of_scope(self, classification: dict) -> dict:
        reason = classification.get("out_of_scope_reason", "unrelated to marketing analytics")
        return {
            "question": classification.get("refined_question", ""),
            "intent":   "out_of_scope",
            "response": (f"I'm focused on Warner Bros. Singapore marketing analytics. "
                         f"That question ({reason}) is outside my scope. "
                         f"Try asking about campaigns, ROAS, budget allocation, "
                         f"creative performance, or platform analysis."),
            "data":     None,
            "error":    None,
        }

    def _handle_empty(self) -> dict:
        return {
            "question": "",
            "intent":   "error",
            "response": ("Please ask a marketing analytics question.\n\n"
                         "Examples:\n"
                         "• \"How are all business lines performing vs ROAS target?\"\n"
                         "• \"Which creative format has the best ROAS?\"\n"
                         "• \"Which creatives need urgent refresh?\"\n"
                         "• \"I have SGD 50K extra — where should I allocate it?\"\n"
                         "• \"Full audit: performance, creatives, and budget optimisation\"\n\n"
                         "Type 'queries' to see all sample queries by agent type.\n"
                         "Type 'demo' to run a showcase of all agents.\n"
                         "Type 'dashboard' to build a live visual dashboard."),
            "data":     None,
            "error":    None,
        }

    def run(self, question: str, verbose: bool = True, on_status=None) -> dict:
        """
        Main entry point.
        Input : plain English question
        on_status: optional callback(agent, event, detail) for live display
        Output: dict with response, data, intent, specialist, error
        """
        def emit(agent, event, detail=""):
            if on_status:
                on_status(agent, event, detail)

        question = question.strip()
        if not question:
            return self._handle_empty()

        # ── Step 1: Orchestrator classifies ──────────────────
        emit("orchestrator", "start")
        emit("orchestrator", "classifying", "Determining intent and routing...")
        classification = self._classify(question)
        intent         = classification.get("intent", "analysis")
        specialist     = classification.get("specialist", "analysis")
        refined_q      = classification.get("refined_question", question)
        scope          = classification.get("scope", "")
        needs_analysis = classification.get("needs_analysis", True)

        emit("orchestrator", "classified", json.dumps({
            "intent":           intent,
            "specialist":       specialist,
            "scope":            scope,
            "needs_analysis":   needs_analysis,
            "refined_question": refined_q,
        }))

        if intent == "out_of_scope":
            emit("orchestrator", "out_of_scope",
                 classification.get("out_of_scope_reason", ""))
            return self._handle_out_of_scope(classification)

        specialist_label = {
            "creative":  "Data Agent → Creative Analyst → Quality Critic",
            "optimizer": "Data Agent → Optimizer Agent → Quality Critic",
        }.get(specialist, "Data Agent → Analysis Agent → Quality Critic")

        if not needs_analysis:
            specialist_label = "Data Agent only"

        emit("orchestrator", "routing", specialist_label)

        # ── Step 2: Data Agent ────────────────────────────────
        emit("data_agent", "start")
        original_fetch = self.data_agent.fetch

        def patched_fetch(q, verbose=False):
            emit("data_agent", "classifying_query", "Refining question for SQL...")
            result = original_fetch(q, verbose=False)
            emit("data_agent", "query_classified", json.dumps({
                "query_type":  result.get("query_type", ""),
                "time_window": result.get("time_window", ""),
            }))
            emit("data_agent", "sql_generated", result.get("sql", "")[:120])
            emit("data_agent", "query_executed", str(result.get("row_count", 0)))
            return result

        data_result = patched_fetch(refined_q)

        if data_result.get("error"):
            emit("data_agent", "error", data_result["error"])
            return {
                "question": question, "intent": intent, "specialist": specialist,
                "response": f"I couldn't retrieve that data: {data_result['error']}",
                "data": None, "error": data_result["error"],
            }

        data = data_result.get("data")
        emit("data_agent", "done", str(data_result.get("row_count", 0)))

        # ── Step 3: Specialist Agent ──────────────────────────
        if not needs_analysis:
            emit("orchestrator", "done")
            response_text = (data.to_string(index=False)
                             if (data is not None and not data.empty)
                             else "No data found.")
            return {
                "question": question, "intent": intent, "specialist": specialist,
                "response": response_text,
                "data":     data,
                "sql":      data_result.get("sql"),
                "error":    None,
            }

        context_notes = data_result.get("context_notes", "")

        if specialist == "creative":
            emit("creative_analyst", "start")
            emit("creative_analyst", "preparing",
                 f"Received {data_result.get('row_count', 0)} rows — running format & fatigue analysis...")
            emit("creative_analyst", "analysing",
                 "Comparing formats, detecting fatigue, building refresh priority list...")
            spec_result = self.creative_agent.analyse(
                data=data, question=question,
                context_notes=context_notes, verbose=False,
            )
            emit("creative_analyst", "done", "Creative insights generated")

        elif specialist == "optimizer":
            emit("optimizer", "start")
            emit("optimizer", "preparing",
                 f"Received {data_result.get('row_count', 0)} rows — calculating allocation efficiency...")
            emit("optimizer", "optimising",
                 "Building reallocation table across platforms and business lines...")
            spec_result = self.optimizer_agent.optimise(
                data=data, question=question,
                context_notes=context_notes, verbose=False,
            )
            emit("optimizer", "done", "Optimisation plan generated")

        else:
            emit("analysis_agent", "start")
            emit("analysis_agent", "preparing",
                 f"Preparing {data_result.get('row_count', 0)} rows...")
            emit("analysis_agent", "analysing",
                 "Generating CMO-ready insights via Claude Sonnet...")
            spec_result = self.analysis_agent.analyse(
                data=data, question=question,
                context_notes=context_notes, verbose=False,
            )
            emit("analysis_agent", "done", "Insights generated")

        raw_insight = spec_result.get("insight", "No insight generated.")

        # ── Step 4: Quality Critic ────────────────────────────
        emit("critic", "start")
        emit("critic", "reviewing", "Scoring specificity, actionability, accuracy, tone...")
        critic_result = self.critic_agent.review(
            insight=raw_insight, question=question, verbose=False,
        )
        emit("critic", "done", f"Score: {critic_result.get('score', '?')}/10")

        final_response = critic_result.get("reviewed_insight", raw_insight)

        emit("orchestrator", "done")
        return {
            "question":   question,
            "intent":     intent,
            "specialist": specialist,
            "response":   final_response,
            "data":       data,
            "sql":        data_result.get("sql"),
            "error":      None,
        }


# ─────────────────────────────────────────────
# End-to-end test
# ─────────────────────────────────────────────
if __name__ == "__main__":
    orch = Orchestrator()

    print("\n" + "🎬 " * 20)
    print("WARNER BROS. SINGAPORE — FULL 6-AGENT PIPELINE TEST")
    print("🎬 " * 20)

    test_questions = [
        ("Analysis",  "How are all business lines performing vs ROAS target this month?"),
        ("Creative",  "Which creative format has the best ROAS and what needs to be refreshed?"),
        ("Optimizer", "I have SGD 30K extra — where should I allocate it for maximum ROAS?"),
    ]

    for label, q in test_questions:
        print(f"\n{'='*65}")
        print(f"[{label}] {q}")
        print('='*65)

        def show(agent, event, detail=""):
            icons = {"orchestrator": "🧠", "data_agent": "📊", "analysis_agent": "🔍",
                     "creative_analyst": "🎨", "optimizer": "💰", "critic": "⚖️"}
            if event not in ("start", "done"):
                print(f"  {icons.get(agent,'•')} {agent}: {event}"
                      + (f" — {detail[:50]}" if detail else ""))

        result = orch.run(q, verbose=False, on_status=show)
        print(f"\nSPECIALIST: {result.get('specialist', 'unknown')}")
        print(f"RESPONSE (first 250 chars):\n{result['response'][:250]}...")
