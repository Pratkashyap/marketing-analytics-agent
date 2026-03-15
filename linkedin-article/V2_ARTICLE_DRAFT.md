# LinkedIn Article — V2 Draft (STRONGER ANGLE)
## Series: [SERIES NAME] | Batch 1 of 5
## Core Message: AI agents as a marketing team
## Status: Ready for screenshots + publish

---

# TITLE:
# I built a marketing analytics team that works 24/7, costs $15/month,
# and answers in 12 seconds. Here's who's on it.

---

Most marketing leaders I know are understaffed on the analytics side.

Not because the budget isn't there. Because **the right combination of people** — someone who lives in the data, someone who interprets it, someone who knows the creatives inside out, someone who manages budget like a chess game — rarely exists in one team, at one time, at the speed the business actually needs.

So I stopped looking for that team.

I built it.

---

## Meet the Team

Over one weekend sprint — 6 to 8 hours of focused execution — I assembled a **7-person marketing analytics team** — except every person is an AI agent with a specific role, a defined expertise, and a clear reporting line.

They're always available. They don't have calendar conflicts. They don't need a brief by Wednesday to have slides ready by Friday.

Let me introduce them.

---

**🧠 The Director — Orchestrator Agent**

Every team needs someone who receives the question, knows who to send it to, and brings the answer back coherent and complete.

That's the Orchestrator. It's the only agent the user talks to. It classifies every incoming question — is this a data pull? a performance analysis? a creative question? a budget call? — and routes it to the right specialist. It coordinates parallel workstreams, waits for outputs, and synthesises the final answer.

No analyst does all of this well. The Orchestrator does nothing but this.

---

**📊 The Data Engineer — Data Agent**

The person on every team who actually knows where the data lives, how to get it, and why the dashboard is lying to you.

The Data Agent converts natural language questions into SQL, runs them against 112,000 rows of marketing performance data in real time, and returns clean, structured results. It knows the schema. It handles ambiguous time windows. It retries on error with a simpler approach rather than failing.

When the rest of the team needs data, they get it from here. Nobody else touches the database.

---

**🔍 The Senior Performance Analyst — Analysis Hub Agent**

The person who looks at the numbers and tells you what they actually mean.

The Analysis Hub Agent takes raw data and produces structured performance insights: ROAS vs. target, trend direction (improving / declining / stable), anomaly detection, week-over-week shifts, and objective-aligned evaluation. A branding campaign is judged on reach and CPM. A conversion campaign is judged on ROAS and CPA.

It uses the more powerful reasoning model (Claude Sonnet) because this is where thinking depth matters.

---

**🎨 The Creative Strategist — Creative Analyst Agent**

Most marketing teams under-invest in creative analytics. They look at CTR and call it a day.

The Creative Analyst Agent goes deeper. It plots CTR curves over the lifetime of each creative format. It detects the fatigue inflection point — the moment when a creative's performance starts to decay faster than expected. It identifies which formats (Video 15s, Carousel, Reels, Static) are overperforming on which platforms, and it flags creative assets that need to be refreshed before performance falls off a cliff.

Most teams find out a creative has fatigued after it already has. This agent finds it while there's still budget to act.

---

**💰 The Budget Manager — Optimizer Agent**

The person whose entire job is making sure every dollar is working as hard as possible.

The Optimizer Agent doesn't give vague advice like "shift spend to better-performing channels." It gives specific recommendations: platform, campaign, amount, reason, and projected ROAS impact. In actual currency. With a before-and-after comparison.

---

**📈 The Reporting Analyst — Dashboard Agent**

The person who makes sure the right people can see the right information at the right time — without a weekly email chain.

The Dashboard Agent generates a live Streamlit dashboard on demand. Ask for a dashboard. It writes the code, builds the visualisations, and launches it in your browser. Charts, KPI cards, trend lines, creative fatigue heatmaps — all generated from live data, not a screenshot from last Tuesday.

---

**⚖️ The Editor — Insight Quality Critic Agent**

This is the one I didn't plan for. And it might be the most important one.

Every insight this team produces — before it reaches you — goes through the Critic. It scores the output 0–10 across five dimensions:

- **Specificity** — Are real numbers present, or is it vague?
- **Actionability** — Can you act on this today?
- **Accuracy** — Are targets referenced correctly?
- **Completeness** — Does it actually answer what was asked?
- **Tone** — Is it executive-ready, or full of hedging?

If the score is 8+, the insight passes. If it's 6–7, it gets enhanced. Below 6, the weakest section is rewritten.

**An AI reviewing AI output. That's where quality control comes from in this team.**

---

## How the Team Works Together — A Real Example

Here's what happens when you ask: *"Why is ROAS declining on video creatives this month?"*

```
You → Orchestrator   (classifies: creative + performance question)
   → Data Agent      (pulls 30-day video creative data — 2.1 seconds)
   → Analysis Hub    ("ROAS down 0.6x WoW, CTR declining on 3 assets")
   → Creative Analyst ("3 assets past fatigue threshold — 21+ days on-air")
   → Optimizer        ("Pause those 3, reallocate to Carousel — +0.4x ROAS")
   → Quality Critic   ("✅ Quality Score: 9/10 — Approved")
   → You              (full structured answer)

Total time: 11 seconds.
```

The answer your team would have had by Thursday. In 11 seconds.

---

## What This Team Has Achieved

They've answered every question I've thrown at them. Across 112,000 rows of data. Across 4 platforms, multiple campaign types, 5 business lines, 90 days of performance history.

Not once have they said *"I'll need to check and come back to you."*

Not perfectly — V1 has rough edges. The dashboard has a bug being fixed. Some complex questions need better routing logic. Memory doesn't persist across sessions yet.

But the core team works. And improving a working team is very different from building one from scratch.

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

**[SCREENSHOTS TO ADD BEFORE PUBLISHING:]**
- [ ] Terminal pipeline — all 7 agents firing (run: `python3 main.py` → type `demo`)
- [ ] Architecture diagram — clean visual (navy #1428A0 + gold #FFD700)
- [ ] Sample agent output — structured response with quality badge
- [ ] Dashboard preview — after the bug fix is complete
- [ ] Header image — dark background, agent names as "team cards"

---

*#AIMarketing #MarketingTeam #MultiAgentAI #MarketingAnalytics #BuildingInPublic #MarketingTech #AIAgents*

---
*V2 Draft | [SERIES NAME] | Batch 1*
*Word count: ~1,450 | Read time: ~6 min*
*This is the stronger version — use this for publishing.*
