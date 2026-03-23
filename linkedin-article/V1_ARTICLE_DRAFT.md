# LinkedIn Article — V1 Draft
## Series: [PICK NAME] | Batch 1 of 5
## Status: Draft — For Review

---
# TITLE:
# Marketing teams spend 3 days getting answers that should be instant.
# I built the fix — 7 AI agents, 112,000 rows, zero vendor lock-in.
---

---

I'm going to tell you something that nobody in the room ever admits out loud.

Most marketing teams are making **million-dollar decisions on data that's 3 days old**, presented in slides that took 8 hours to prepare, to answer a question someone asked on Monday.

By Thursday, the insight is already obsolete.

I've been in those rooms. And I decided to do something about it.

---

## The Question That Started Everything

A few months ago, I asked a simple question during a campaign review:

**"Why is our ROAS dropping on the video creatives?"**

What followed was a familiar ritual — someone screenshots a dashboard, someone exports a CSV, someone pastes numbers into a deck, someone interprets the numbers in a meeting three days later.

The answer, when it arrived, was: *"Looks like creative fatigue."*

That's it. No drill-down to which creatives. No timeline of when it started. No recommendation on what to do next. No budget impact calculation.

I remember thinking: **an AI could have answered this — and done it better.**

So I built one.

---

## What I Actually Built

Over In a focused sprint, I built a **7-agent AI marketing analytics system** from scratch.

Not a chatbot. Not a dashboard plugin. A fully orchestrated, multi-agent system where each AI agent has a specific job, a defined expertise, and passes work to the next specialist in the chain.

Ask it a question. It figures out what data to pull, writes and runs the SQL query, analyzes the results, checks for creative fatigue, calculates budget reallocation in actual currency, scores the quality of its own output — and returns a structured, CMO-ready answer.

In under a minute.

I'm not pitching a product. I'm documenting a build — in public, in batches, as it gets better. This is Batch 1.

---

## Why This Matters (And Why Most Teams Won't Do It)

Marketing analytics has a dirty secret: **the tools are fast, but the humans in the loop are the bottleneck.**

Your dashboard refreshes in milliseconds. Your analyst still needs to look at it, form a hypothesis, pull supporting data, build context, write it up, present it.

That chain — data → human interpretation → recommendation → action — takes **days**. In a market that moves hourly.

The companies that close this loop with AI aren't going to have a small edge. They're going to have a **structural advantage** that compounds over time.

I wanted to understand how to build that. Not talk about it — build it. Hands on, from scratch, on a laptop.

Here's exactly what I built.

---

## The Architecture: 7 Agents, One Orchestrator

Before I wrote a single line of code, I built two documents:

1. **An architecture blueprint** — what the system should do, what each agent is responsible for, how they communicate
2. **A sprint battle plan** — hour-by-hour execution, compressed into a focused sprint using AI pair programming

The architecture follows a **Supervisor pattern** — one Orchestrator agent receives every question, decides which specialists to involve, coordinates the workflow, and synthesizes the final answer.

```
                    ┌─────────────────────┐
                    │    ORCHESTRATOR      │
                    │  Routes every query  │
                    │  Manages the chain   │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼─────────────────────┐
          │                    │                      │
          ▼                    ▼                      ▼
   ┌─────────────┐    ┌─────────────┐       ┌─────────────┐
   │  DATA AGENT │    │  ANALYSIS   │       │  REPORTING  │
   │  SQL → Data │    │  HUB AGENT  │       │  DASHBOARD  │
   │  112K rows  │    │  Insights   │       │   AGENT     │
   └─────────────┘    └──────┬──────┘       └─────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │   CREATIVE   │ │  OPTIMIZER   │ │   QUALITY    │
     │   ANALYST    │ │    AGENT     │ │   CRITIC     │
     │  CTR + Fatigue│ │ Budget SGD  │ │ Scores 0-10  │
     └──────────────┘ └──────────────┘ └──────────────┘
```

**Here's what each agent does:**

**🧠 Orchestrator** — The routing brain. Classifies every question (data pull? analysis? creative question? budget question?), decides which specialists to invoke, and synthesizes the final output. It never answers directly — it coordinates.

**📊 Data Agent** — The only agent that touches the database. Takes natural language, generates SQL using a lightweight AI model (Claude Haiku), runs it against 112,000 rows of marketing performance data in DuckDB, and returns clean structured results.

**🔍 Analysis Hub Agent** — The senior analyst. Takes the raw data and produces structured insights: performance vs. targets, trend direction, anomalies, week-over-week shifts. Uses Claude Sonnet — the heavier reasoning model.

**🎨 Creative Analyst Agent** — Specialist for creative-level performance. Detects CTR fatigue curves, identifies which formats are overperforming, flags assets running past their effectiveness window. Most marketing teams barely look at this. This agent looks at nothing else.

**💰 Optimizer Agent** — Translates analysis into specific budget recommendations. Not "shift budget to better channels" — it says "reallocate $3,200 from Google Display to Meta Reels, expected ROAS lift 0.4x within 7 days."

**📈 Reporting & Dashboard Agent** — Generates a live Streamlit dashboard on demand. Ask for a dashboard, it builds one, writes the code, and launches it in your browser. Literally generates its own interface.

**⚖️ Insight Quality Critic** — This one surprised me most. It reviews every output before it reaches the user and scores it 0–10 on: specificity, actionability, accuracy, completeness, and tone. An AI reviewing AI output — this is where quality comes from.

---

## The Tech Stack (No Vendor Lock-In, All Open Source)

| Layer | Tool | Why |
|---|---|---|
| Language | Python 3.12 | Fast iteration, massive ecosystem |
| Database | DuckDB | Zero setup, 100K+ rows in milliseconds, runs locally |
| AI Reasoning | Claude Sonnet 4.6 | Structured analysis, follows complex prompts reliably |
| AI Lightweight | Claude Haiku 4.5 | SQL generation — fast and cheap |
| Dashboard | Streamlit | Open source, no cloud required, production-ready UI |
| Charts | Plotly | Interactive charts, professional quality |
| Terminal UI | Rich library | Makes the agent pipeline visible and readable in real time |
| Data | Simulated (DuckDB) | 112,000 rows, 90 days, 4 platforms, realistic patterns |

**Total infrastructure cost: $0.** Runs on a laptop. No subscriptions, no SaaS bills, no cloud costs during development.

The only recurring cost is the Anthropic API — roughly $5–15/month at development usage levels.

---

## The Breakthrough Moment

Let me tell you about Hour 4.

I'd spent three hours building the data layer and the first two agents. The Orchestrator was wired up. I typed the first end-to-end test:

> *"Why is ROAS declining on video creatives this month?"*

And watched the terminal.

The Orchestrator classified the question, routed it to the Data Agent, SQL generated and ran. Analysis Agent picked it up. Creative Analyst ran in parallel. Optimizer calculated reallocation. Critic scored the output 9/10.

The full response came back in under a minute.

It said: *"Video creative CTR has declined 28% over the last 21 days on Meta Reels and TikTok — consistent with a fatigue curve. Three specific creative variants are past their effective window. Recommend pausing these and reallocating that spend to the two Carousel formats currently running at 2.8x the average CTR."*

With the exact budget amounts. With a confidence score. With a quality badge from the Critic Agent.

I sat there for a moment.

That answer — with that specificity, that structure, that speed — would have taken my team until Thursday.

It took the system under a minute.

That was the moment I knew this was worth building properly.

---

## What the System Can Do Right Now (V1 — Honest Assessment)

✅ Answer any natural language marketing question against 112K rows of performance data
✅ Detect creative fatigue by format, platform, and time window
✅ Recommend specific budget reallocation with projected ROAS impact
✅ Generate and launch a live Streamlit dashboard on demand
✅ Score every insight 0–10 before it reaches the user
✅ Handle edge cases: out-of-scope questions, ambiguous queries, empty inputs

❌ Not connected to real platform APIs yet (Meta, Google, TikTok) — simulated data only
❌ Dashboard V1 still has a UI bug being fixed (a DataFrame check — two characters away from done)
❌ No persistent memory across sessions yet
❌ Not production-hardened or enterprise-ready

**This is V1. It works. It's real. And it's not finished.**

I'm publishing now anyway — because waiting for perfect is how good projects die in a folder.

---

## Why This Applies to Almost Every Marketing Team

This isn't just a technical side project. It's a proof of concept for a shift in how marketing teams can operate.

The pattern — **Orchestrator → Data → Specialist Analysis → Quality Check → Response** — applies to any domain where:
- You have structured performance data
- You ask the same types of questions repeatedly
- The value is in the interpretation, not just the numbers
- Speed and consistency matter

Retail. SaaS. E-commerce. Media. FMCG. The architecture is the same. The agents are swapped out. The data schema changes.

I built this for marketing analytics because that's where I live. But the framework is reusable.

---

## What's Coming Next

This is **Batch 1 of 5** in a building-in-public series.

```
✅ Batch 1 (NOW)       → 7 agents built, architecture documented, V1 live
🔨 Batch 2 (+2 weeks)  → Dashboard perfected: tabs, live queries, visual KPIs
🔨 Batch 3 (+5 weeks)  → Use Case #2: same architecture, different domain
🔨 Batch 4 (+8 weeks)  → 3–4 polished use cases, architecture evolution
🔨 Batch 5 (+12 weeks) → Turning this into something more than a side project
```

The bigger goal: **4–5 polished, production-tested AI agent use cases** — each solving a real business problem, each built on the same modular architecture, each refined publicly.

Not a startup pitch. Not a product launch. A documented learning journey that's turning into something with real value.

---

## The Honest Take

I'm not an AI researcher. I don't have a CS degree. I'm a marketing professional who got curious, made a plan, and executed a sprint.

The tools available right now — Claude API, DuckDB, Streamlit, Python — are good enough that the gap between "curious" and "working AI system" is measured in focused sprints, not years.

What it takes isn't genius. It's a blueprint, a battle plan, and a willingness to debug a DataFrame error at midnight because you know what the output *should* feel like.

If you've been thinking about building something with AI but haven't started — I'd genuinely encourage you to just build a V1. Break it publicly. Fix it publicly. That's the only way this goes anywhere interesting.

---

**What would you want an AI analytics system to answer for your team?** Drop it in the comments — I'll tell you if the current architecture handles it, and if not, it might become Batch 3.

Follow for Batch 2 — coming in ~2 weeks when the dashboard gets its full makeover.

---

*#AIMarketing #MarketingAnalytics #MultiAgentAI #BuildingInPublic #PythonAI #MarketingTech #ArtificialIntelligence #AIEngineering #MarketingStrategy #TechForMarketers*

---

**[SCREENSHOT NOTES — Add before publishing:]**
- [ ] Screenshot 1: Terminal pipeline showing all 7 agents firing (after `demo` command in main.py)
- [ ] Screenshot 2: Architecture diagram (clean version — can use the ASCII above or create in Canva)
- [ ] Screenshot 3: Sample agent output showing the structured format with quality badge
- [ ] Screenshot 4: Dashboard preview (after bug fix)
- [ ] Header image: Navy blue background (#1428A0), gold accent text (#FFD700), agent pipeline visual

---
*V1 Draft | [SERIES NAME] | Batch 1*
*Word count: ~1,850 | Read time: ~7 min*
