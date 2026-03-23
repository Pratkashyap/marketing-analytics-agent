# LinkedIn Article — V2 Draft (UPDATED)
## Series: Build AI Raw | Batch 1 of 5
## Core Message: AI agents as a marketing team
## Status: Updated with Phase detail — ready for final review

---

# TITLE:
# I built a marketing analytics team that works 24/7, costs $15/month.
# Here's who's on it — and what broke while building them.

---

Most marketing leaders I know are understaffed on the analytics side.

Not because the budget isn't there. Because **the right combination of people** — someone who lives in the data, someone who interprets it, someone who knows the creatives inside out, someone who manages budget like a chess game — rarely exists in one team, at one time, at the speed the business actually needs.

So I stopped looking for that team.

I built it.

---

## Meet the Team

In a focused sprint, I assembled a **7-person marketing analytics team** — except every person is an AI agent with a specific role, a defined expertise, and a clear reporting line.

They're always available. They don't have calendar conflicts. They don't need a brief by Wednesday to have slides ready by Friday.

Two models power the whole team — used deliberately. Claude Sonnet 4.6 handles the agents that require deep reasoning: interpretation, creative analysis, budget decisions. Claude Haiku 4.5 handles the deterministic tasks: SQL generation, dashboard code, quality scoring. Speed and cost where it matters. Reasoning depth where it counts.

Let me introduce them.

---

**🧠 The Director — Orchestrator Agent**

Every team needs someone who receives the question, knows who to send it to, and brings the answer back coherent and complete.

That's the Orchestrator. It's the only agent the user talks to. It classifies every incoming question — is this a data pull? a performance analysis? a creative question? a budget call? — and routes it to the right specialist. It coordinates workstreams, waits for outputs, and synthesises the final answer.

The Orchestrator's system prompt is explicit not just about what it does — but about what it must never do. It must not query data. It must not analyse. It must not recommend. Route and synthesise only. Without this constraint, it drifts into doing everything and the specialists become redundant.

---

**📊 The Data Engineer — Data Agent**

The person on every team who actually knows where the data lives, how to get it, and why the dashboard is lying to you.

The Data Agent converts natural language questions into SQL, runs them against 112,000 rows of marketing performance data in real time, and returns clean, structured results. It knows the schema. It handles ambiguous time windows. It retries on error rather than failing.

When the rest of the team needs data, they get it from here. Nobody else touches the database.

---

**🔍 The Senior Performance Analyst — Analysis Hub Agent**

The person who looks at the numbers and tells you what they actually mean.

The Analysis Hub takes raw data and produces structured performance insights: ROAS vs. target, trend direction (improving / declining / stable), anomaly detection, week-over-week shifts. Every claim must reference the data. The agent is explicitly instructed not to use language like "seems to be" or "appears to be." If it can't point to the numbers, it doesn't say it.

This is where Claude Sonnet earns its cost. Contextual interpretation requires reasoning depth.

---

**🎨 The Creative Strategist — Creative Analyst Agent**

Most marketing teams under-invest in creative analytics. They look at CTR and call it a day.

The Creative Analyst goes deeper. It plots CTR curves over the lifetime of each creative asset and identifies the fatigue inflection point — the exact day when performance starts decaying faster than the baseline rate. Assets that have crossed this threshold are flagged by name, with the date they crossed it. Not "some video assets may be fatiguing." "Video_03 has been on-air for 24 days and crossed the fatigue threshold on Day 18."

Most teams find out a creative has fatigued after it already has. This agent finds it while there's still budget to act.

---

**💰 The Budget Manager — Optimizer Agent**

The person whose entire job is making sure every dollar is working as hard as possible.

The Optimizer doesn't give vague advice like "shift spend to better-performing channels." It gives specific recommendations: platform, campaign, SGD amount, reason, projected ROAS impact. Before-and-after comparison included. Minimum spend floors respected. Risks flagged.

---

**📈 The Reporting Analyst — Dashboard Agent**

The person who makes sure the right people can see the right information at the right time — without a weekly email chain.

The Dashboard Agent generates a live Streamlit dashboard on demand. Ask for a dashboard. It writes complete, runnable code, builds the visualisations, and launches it in your browser. Charts, KPI cards, trend lines, creative fatigue heatmaps — all generated from live DuckDB queries, not a screenshot from last Tuesday.

---

**⚖️ The Editor — Insight Quality Critic Agent**

This is the one I didn't plan for. And it might be the most important one.

Every insight this team produces — before it reaches you — goes through the Critic. It scores the output 0–10 across five dimensions:

- **Specificity** — Are real numbers present, or is it vague?
- **Actionability** — Can a CMO act on this today?
- **Accuracy** — Are targets referenced correctly?
- **Completeness** — Does it actually answer what was asked?
- **Tone** — Is it direct and executive-ready, or full of hedging?

Score 8+: approved. Score 6–7: enhanced. Below 6: the weakest section is fully rewritten.

**Adding this single agent raised average response quality from 6.5/10 to 8.9/10.**

An AI reviewing AI output. That's where quality control comes from in this team.

---

## How the Team Works Together — A Real Example

Here's what happens when you ask: *"Why is ROAS declining on video creatives this month?"*

```
You → Orchestrator   (classifies: creative + performance question)
   → Data Agent      (pulls 30-day video creative data)
   → Analysis Hub    ("ROAS down 0.6x WoW, CTR declining on 3 assets")
   → Creative Analyst ("3 assets past fatigue threshold — 21+ days on-air")
   → Optimizer        ("Pause those 3, reallocate to Carousel — +0.4x ROAS")
   → Quality Critic   ("Quality Score: 9/10 — Approved")
   → You              (full structured answer)

Total time: under a minute.
```

The answer your team would have had by Thursday.

---

## What Broke — The Failures Nobody Publishes

Nobody publishes these. Everyone polishes their project story and skips the part where everything broke.

Here's the part where everything broke.

**Blank charts for two hours.**
Every chart in the dashboard returned empty results. No error. No warning. Just silence. The Data Agent's system prompt had the table named `fact_performance`. The actual DuckDB table is `fact_daily_performance`. One word. The SQL was syntactically valid — it just queried a table that didn't exist. The fix: copy table and column names directly from your actual schema into the agent's prompt. Never type them from memory. One character off breaks everything silently.

**Agents doing each other's jobs.**
The Orchestrator was writing analysis. The Analysis Hub was generating budget recommendations. The outputs overlapped and contradicted each other. The cause: system prompts that were too vague. "You are a helpful marketing analytics agent" is not a system prompt — it's an invitation to do everything. The fix: rewrite every prompt to be explicit about what the agent must never do, not just what it does.

**The text input that deleted itself.**
The Agent Chat tab had a question input and a Send button. Users would type a question, click Send, and watch their text disappear. Streamlit reruns the entire script on every interaction. Using `value=` and `key=` together on the same input resets it to the default on every rerun. Three lines of code fixed it. Finding those three lines took several hours.

**The meta-lesson across all of it:**
Every failure came from moving too fast through the design phase. A working system is built slowly, then runs fast. Not the other way around.

---

## What This Team Has Achieved

They've answered every question I've thrown at them. Across 112,000 rows of data. Across 4 platforms, multiple campaign types, 5 business lines, 90 days of performance history.

Not once have they said *"I'll need to check and come back to you."*

**By the numbers:**
- API cost per query: ~$0.03
- Quality Critic impact: average response quality 6.5 → 8.9 out of 10
- Total codebase: ~2,400 lines of Python
- Dataset: 112K rows · 4 platforms · 5 business lines · 90 days

V1 has honest limitations. Memory doesn't persist across sessions. Complex multi-part questions sometimes overwhelm the routing logic. No multi-user support yet. But the core team works. And improving a working team is very different from building one from scratch.

---

## Why This Matters Beyond the Technology

This isn't really about AI agents. It's about what happens when you **model a team as a system**.

Every role has a clear responsibility. Every handoff is explicit. Every output has a quality gate. Nobody's work reaches the decision-maker without being reviewed.

Most real teams don't operate that cleanly. People wear multiple hats. Handoffs happen over Slack threads. Quality control is whoever remembers to check before the deck goes out.

Building this in AI forced me to think clearly about what each function *actually does*, what inputs it needs, and what good output looks like. That clarity made the AI team better — and it made me think differently about how any team should be structured.

**The architecture is reusable.** Retail. SaaS. E-commerce. Media. FMCG. Swap the agents' domain knowledge. Keep the orchestration pattern. The framework holds.

---

## What's Next for the Team

```
✅ Batch 1 (NOW)       → Team assembled. All 7 agents live.
🔨 Batch 2 (+2 weeks)  → Dashboard upgraded: tabs, live queries, visual KPIs
🔨 Batch 3 (+5 weeks)  → Use Case #2: same team structure, different industry
🔨 Batch 4 (+8 weeks)  → 3–4 polished use cases running in parallel
🔨 Batch 5 (+12 weeks) → Building something more permanent around this
```

I'm documenting the full build — architecture, decisions, failures, breakthroughs — in batches as the project grows. Not when it's finished. **Because the journey is the content.**

---

If you run a marketing team and have a question you've been waiting three days to get answered — drop it in the comments. I'll run it through the system and share what comes back.

Follow for Batch 2 — the dashboard gets its full upgrade in ~2 weeks.

---

**[SCREENSHOTS TO ATTACH BEFORE PUBLISHING:]**
- [ ] agent_pipeline_diagram.png — architecture overview
- [ ] agent_chat_roas_analysis.png — real agent output with pipeline steps
- [ ] performance_dashboard.png — KPI cards + ROAS chart
- [ ] creative_health_dashboard.png — fatigue table + CTR benchmarks
- [ ] thumbnail.png — use as header image

---

*#AIMarketing #MarketingTeam #MultiAgentAI #MarketingAnalytics #BuildingInPublic #MarketingTech #AIAgents*

---
*V2 Updated | Build AI Raw | Batch 1*
*Word count: ~1,650 | Read time: ~7 min*
