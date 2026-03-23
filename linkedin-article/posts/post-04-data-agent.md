POST 04 — THE DATA AGENT
Publish: Monday, Week 2
Screenshot to attach: data_explorer_sql.png
Hashtags: first comment only — not in post body
-----------------------------------------------------

Plain English in. Live SQL out. 112,000 rows queried in under 20ms.

The Data Agent's job: convert a plain English question into SQL, run it against the database, and return structured results.

No BI tool. No dashboard to navigate. No analyst to brief.

Type: "Which campaigns are below their ROAS target this month?"
The agent writes the SQL, executes it, and returns the answer with a plain English summary.

But here's what cost me 2 hours:

The agent's system prompt had the table named fact_performance.
The actual table was fact_daily_performance.

Every query was syntactically valid.
Every chart returned blank.
No error. No warning. Just silence.

The fix: copy your actual schema directly into the agent's system prompt. Never type it from memory. Never abbreviate. One character off breaks everything silently.

That's the most important technical lesson in this entire build.

The agents are only as good as the context you give them.
Garbage in, silence out.

Next — 4 more things broke. Nobody publishes these. I will.

Comment DATA — I'll reply with the full data layer breakdown.

-----------------------------------------------------
FIRST COMMENT (post within 60 seconds of publishing):

Full data layer breakdown — schema, DuckDB setup, real SQL the agent generates:
Phase 3 — Data Layer: https://www.notion.so/3270f002382e81e5803cf6389bc68402
Full project hub: https://www.notion.so/3270f002382e8112a2cecf50f8b164a5

#AIAgents #BuildingInPublic #Python #DuckDB #ClaudeAPI #DataEngineering #ProductAI
