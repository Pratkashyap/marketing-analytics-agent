POST 03 — ARCHITECTURE
Publish: Friday, Week 1
Screenshot to attach: agent_pipeline_diagram.png
Hashtags: first comment only — not in post body
-----------------------------------------------------

7 agents. None of them talk to each other directly.

That was the core architectural decision: Supervisor / Orchestrator pattern.

One central agent receives every question.
It classifies intent, decides who handles what, and synthesises the final answer.
The specialists never communicate directly with each other.

Three patterns exist for multi-agent systems:

Swarm — agents talk peer-to-peer. Flexible, but impossible to debug.
Pipeline — fixed sequence. Predictable, but rigid.
Supervisor — one coordinator, clear specialists. Explicit, debuggable, production-ready.

I chose Supervisor for one reason: when something breaks, you know exactly where.

But the bigger lesson wasn't what each agent should do.
It was what each agent must never do.

The Orchestrator's system prompt contains this line:
"You must not query data. You must not perform analysis. You must not generate recommendations."

Without that constraint, it does everything. The specialists become redundant.
The outputs overlap. The system becomes inconsistent.

Narrow roles. Explicit prohibitions. That's what makes 7 agents feel like one system.

Next — I gave this system access to 112,000 rows of marketing data. Here's what the Data Agent does with a plain English question.

Comment ARCHITECT — I'll reply with the full architecture breakdown.

-----------------------------------------------------
FIRST COMMENT (post within 60 seconds of publishing):

Full architecture deep dive — why Supervisor pattern, how each agent was designed:
Phase 2 — Architecture: https://www.notion.so/3270f002382e8157a274ee7b0cfdc1cf
Full project hub: https://www.notion.so/3270f002382e8112a2cecf50f8b164a5

#AIAgents #MultiAgentAI #AIArchitecture #BuildingInPublic #ClaudeAPI #Python #ProductAI
