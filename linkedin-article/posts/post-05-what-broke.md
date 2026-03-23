POST 05 — WHAT BROKE
Publish: Wednesday, Week 2
Screenshot to attach: tech_stack.png
Hashtags: first comment only — not in post body
NOTE: This post has the engagement hook — highest comment potential
-----------------------------------------------------

4 things broke while building this.
Nobody publishes these. I will.

Failure 1 — The schema that cost 2 hours
One table name was wrong in the agent's context.
Every chart returned blank. No error. No warning. Just silence.
Fix: copy your schema verbatim. Never type it from memory.

Failure 2 — Agents doing each other's jobs
The Orchestrator started analysing data.
The Analyst started generating budget recommendations.
Outputs overlapped. Responses contradicted each other.
Fix: system prompts need explicit prohibitions, not just a job description.

Failure 3 — The Streamlit session state bug
User types a question. Clicks Send. Watches their text disappear.
The pipeline fires on an empty string. Returns a confused response.
Fix: three lines of code. Never use value= and key= together on a text input.

Failure 4 — Vague queries routing to everything
"How are things going?" activated all 7 agents simultaneously.
Pipeline ran 3x longer. Output tried to cover everything at once.
Fix: classify intent before routing. Every query gets categorised first.

The meta-lesson: every single one of these happened because of moving too fast through design.

A working system is built slowly, then runs fast. Not the other way around.

Which one of these have you hit in your own builds?

-----------------------------------------------------
FIRST COMMENT (post within 60 seconds of publishing):

Full breakdown of every failure and fix — with the actual code:
Phase 6 — What Broke: https://www.notion.so/3270f002382e81f3b88eefa41a975ef1
Full project hub: https://www.notion.so/3270f002382e8112a2cecf50f8b164a5

#AIAgents #BuildingInPublic #AIEngineering #Python #MultiAgentAI #ClaudeAPI #ProductAI
