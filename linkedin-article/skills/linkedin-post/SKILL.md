---
name: linkedin-post
description: Write LinkedIn posts in Prateek's preferred writing style — punchy, technical, builder tone. Use this skill whenever the user asks to write, rewrite, or improve a LinkedIn post, or uses /linkedin-post. Also trigger when user says "write a post about X", "create a LinkedIn post", "help me post this on LinkedIn", or wants to announce a project/build on LinkedIn. This style is specifically tuned for AI/tech builder content targeting engineers, hiring managers, and technical recruiters.
---

# LinkedIn Post Style Guide — Prateek's Voice

## Who this is for
Technical builders posting about AI projects, tools, and systems. The audience is AI engineers, product builders, technical hiring managers, and recruiters. The goal: show deep expertise without sounding like a marketer.

## Core style rules

**Voice:** Builder's log. Direct. Confident. No hype. No fluff.

**Lines:** Short. One idea per line. Lots of white space. Never write a paragraph where a fragment works.

**Numbers:** Put the most impressive stat as early as possible. Never bury it.

**Emoji:** 0–2 max. Only functional (e.g., → as an arrow). No rocket/fire/bulb emoji.

**Hashtags:** First comment only. Never in the post body.

**Links:** First comment only. Never in the post body (LinkedIn suppresses reach).

**Tone don'ts:**
- No "I'm excited to share..."
- No "In today's world..."
- No explaining why you're posting
- No "weekend" or time-pressure language
- No repetition — say each thing once
- Never undersell the build — make it sound complex and significant

---

## Hook formulas (pick one, never mix)

**Stat-first** — no sentence needed, just the number:
> 7 agents. $0.03 per query.

**Equation hook** — two things combined = result:
> Python + Claude API = a 7-agent marketing analytics team.

**Replacement hook** — replaced something expensive:
> We replaced a 5-person analytics workflow with 7 AI agents.

**Identity shift hook** — your next X isn't human:
> Your next marketing analytics team isn't human. It's AI.

**Reframe hook** — this isn't what you think:
> This isn't a dashboard. It's a 7-agent AI analytics team.

---

## Power lines (one per post max)

Single lines that do heavy lifting — credibility, objection kill, or FOMO:

- "This isn't theory. It's a working system."
- "This isn't a [simple thing]. It's a [bigger thing]."
- "X used to be the bottleneck. Not anymore."
- "The builders that win in [year] won't be the ones with [old]. They'll be the ones with [new]."
- "If you understand [domain], this becomes unfair."

---

## Post structure

Flexible — not every post needs every section. Pick what serves the content.

```
[HOOK]
One line. Use a hook formula above.

[CREDIBILITY BLOCK — optional]
"Built on:" or "Based on:"
– Specific data point (volume, spend, tests run)
– Another stat that proves you know this deeply

[REFRAME — optional]
"This isn't a [X]. It's a [Y]."

[HOW IT WORKS]
"Here's how it works:" or "This is how:"
– Fragment bullet 1
– Fragment bullet 2
– Fragment bullet 3
(Use em dash –, not bullet •)

[WHAT IT REPLACES — optional]
What this replaces:
– Specific named role or tool
– Another specific role

[ECONOMICS]
Cost: $X
Time: Y
Scale: Z
(One stat per line. No sentences.)

[CONTRAST — optional]
"Instead of [old way], you can now [new way]."
Or: "We're moving from [old]… to [new]."

[OUTCOME]
"The result:" or "X used to be the bottleneck. Not anymore."

[BIG PICTURE — optional]
1–2 lines. The paradigm shift.

[CTA]
Comment "KEYWORD" — I'll reply with [what they get].
```

---

## Agent boundary reference (use when writing posts about the system)

Each agent has a hard boundary — what it OWNS and what it is BLOCKED from doing.
Use this to write posts that feel technically precise, not vague.

| Agent | Owns | Blocked from |
|---|---|---|
| Orchestrator | Routing, intent classification, final synthesis | Querying data, analysis, recommendations |
| Data Agent | SQL generation, live database queries | Interpreting results, making recommendations |
| Analysis Hub | Interpreting data, building insight layer | Writing SQL, touching budget or creative |
| Creative Analyst | Ad fatigue detection, CTR trend analysis | Data queries, budget decisions |
| Budget Optimizer | Reallocation recommendations, spend efficiency | Creative decisions, data queries |
| Dashboard Agent | Generating live visual reports | Analysis, recommendations |
| Quality Critic | Scoring all outputs 1–10, rewriting below 6 | Everything else |

When writing posts about the architecture or how agents work — reference these boundaries specifically. Concrete constraints sound more impressive than vague descriptions. "The Orchestrator is explicitly blocked from querying data" lands harder than "agents have clear roles."

---

## Compression technique

When listing what agents/systems do, compress into one powerful line:

Instead of:
> – Handles hook testing
> – Handles script variation
> – Handles performance analysis

Write:
> Agents handle hook testing, script variation, and performance analysis — all running in parallel.

---

## For Prateek's AI agent project

Key facts:
- 7 agents: Orchestrator, Data Agent, Analysis Hub, Creative Analyst, Budget Optimizer, Dashboard Agent, Quality Critic
- Python + Claude Sonnet API, SQLite + Streamlit
- No cloud, no SaaS, runs on a laptop
- 112,000 rows of live marketing data
- $0.03 per query, under 1 minute
- Supervisor pattern — one Orchestrator, six specialists, no direct agent-to-agent communication
- Quality Critic scores every answer — below 6/10 gets rewritten
- Each agent = one Claude API call with one dedicated system prompt

Links (first comment only):
- Hub: notion.so/3270f002382e8112a2cecf50f8b164a5
- Architecture: notion.so/3270f002382e8157a274ee7b0cfdc1cf
- Agent breakdown: notion.so/3270f002382e81d8b75ccca5c8149e3a

Hashtags (first comment only):
#AIAgents #BuildingInPublic #ClaudeAPI #Python #MultiAgentAI #AIEngineering #ProductAI

---

## Output format

Always return:

1. **POST BODY** — plain text, ready to paste into LinkedIn
2. **IMAGE** — which screenshot to attach (image 1 = feed preview)
3. **FIRST COMMENT** — hashtags + links, ready to paste

Never mix links or hashtags into the post body.
