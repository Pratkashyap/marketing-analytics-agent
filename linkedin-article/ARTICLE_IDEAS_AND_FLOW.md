# LinkedIn Article — Ideas, Flow & Series Strategy
## Warner Bros. Singapore Marketing Analytics Agent

> **Review this first. Pick direction. Then we write.**
> The full article draft will only be created after you approve the approach below.

---

## YOUR GOALS (Captured from our conversation)

| Goal | How We Address It |
|---|---|
| Show you're learning & progressing in AI | Article narrates the journey honestly — from zero to working system |
| Sprint framing | Sprint narrative: focused execution, phase by phase |
| Not fake click-bait | Real numbers, real tech, real struggle — no "I made $10K overnight" energy |
| Building toward small AI company | Article ends with roadmap — 4–5 use cases, each a future article |
| Publish in batches, not when perfect | Series strategy: V1 now → V2 after dashboard → V3 after 3 use cases |
| People see you becoming an expert | Technical depth, architecture, specific tools — shows fluency |
| Reference the two supplied PDFs | Blueprint + Battle Plan inform the architecture section |
| Screenshots as proof | Terminal output, architecture diagram, agent pipeline visuals |

---

## SERIES STRATEGY — "Building in Public" Batched Publishing

> **This is the most important strategic decision.**
> Don't write ONE article. Write a **series** that grows with the project.
> Each batch shows progress. Readers follow the journey.

```
BATCH 1 ──────────────── NOW (V1 Published)
  "I built a 7-agent AI system for marketing analytics in one sprint.
   Here's exactly how I did it, what I learned, and what comes next."

BATCH 2 ──────────────── +2 weeks (Dashboard complete)
  "The dashboard is live: how I made AI insights visual with Streamlit
   and why that changed how I think about AI products."

BATCH 3 ──────────────── +4–6 weeks (2nd use case added)
  "Use case #2: [new domain]. Reusing the same multi-agent architecture
   to solve a completely different problem."

BATCH 4 ──────────────── +8–10 weeks (3–4 use cases)
  "From side project to AI micro-agency: what 4 use cases taught me
   about building production-grade AI systems."

BATCH 5 ──────────────── +12 weeks (company forming)
  "Why I'm starting an AI analytics firm, and the exact tech stack
   I'm building it on."
```

**Why this works:**
- Each article is honest about the current state — no pretending it's finished
- Readers see real progress over time → you become a trusted voice
- You build an audience BEFORE your product is ready
- Each article links to the next → compound growth

---

## BATCH 1 ARTICLE — Ideas Breakdown

### ▶ TITLE OPTIONS (Ranked by fit)

**Option A — Side Project + Technical (Recommended)**
> "I built a 7-agent AI marketing analytics system from scratch.
> Here's the architecture, the tech, and what I learned."

Why: Honest, specific, shows ambition without hype. Technical audience respects the detail.

---

**Option B — Journey / Learning Angle**
> "I have no CS degree. I built a production-grade AI agent system anyway.
> Here's the blueprint I followed."

Why: Relatable, aspirational. Good if you want broader reach beyond tech.

---

**Option C — Business Context First**
> "What if your marketing team had an AI analyst available 24/7?
> I built one from scratch."

Why: Business audience hook. More click-bait-adjacent but still grounded.

---

**Option D — Building in Public Hook**
> "Batch 1 of building an AI analytics platform in public:
> the architecture, the agents, and the honest failures."

Why: Explicitly frames the series. Attracts followers who want to learn along with you.

---

### ▶ RECOMMENDED TITLE (Best of all angles)
```
"7 AI agents, and 112,000 rows of data:
 How I built a marketing analytics system from scratch — and what's next."
```

---

## ARTICLE FLOW — Section by Section

### SECTION 1: THE HOOK (100–150 words)
**What it covers:**
- The spark: you work in marketing (at a media entertainment company in Singapore)
  and you see a gap — analytics is reactive, slow, expensive
- "What if an AI system could answer any marketing question in under a minute?"
- "I decided to find out. Starting from zero."

**Tone:** Personal. Real. Not "I built the future of marketing."
**No mention of:** company name, real campaign data, real spend numbers

---

### SECTION 2: THE BLUEPRINT — WHERE IT STARTS (150–200 words)
**What it covers:**
- Every good project starts with a plan, not code
- The two documents I built before touching a terminal:
  1. **Architecture Blueprint** — what the system should do, which agents, why
  2. **Sprint Battle Plan** — compressed 6–8 hour execution plan
- Key decision: **Supervisor pattern** (Orchestrator → Specialists)
  not a swarm, not a single LLM — because control and debuggability matter when you're learning

**Visual to include:**
- Photo/screenshot of the blueprint architecture diagram (ASCII art version)

**Tone:** This shows you think before you code. Differentiates you.

---

### SECTION 3: THE TECH STACK (200–250 words)
**What it covers:**
Table format works well here. Real tools, real reasons.

| Layer | Tool | Why |
|---|---|---|
| Language | Python 3.12 | Standard, fast to iterate |
| Database | DuckDB | Zero setup, runs locally, handles 100K+ rows in milliseconds |
| AI (reasoning) | Claude Sonnet 4.6 (Anthropic) | Strong structured analysis, follows complex prompts |
| AI (lightweight) | Claude Haiku 4.5 | SQL generation, fast + cheap |
| Dashboard | Streamlit | Open source, runs locally, no vendor lock-in |
| Charts | Plotly | Interactive, looks professional |
| Terminal UI | Rich library | Makes the agent pipeline visible in real time |
| Data | DuckDB + simulated data | 112,000 rows, 90 days, realistic patterns |

**Key point to make:** No cloud infrastructure. No $500/month SaaS tools.
Runs on a laptop. That's the point.

**Tone:** Technical but accessible. "Here's what each piece does and why I chose it over alternatives."

---

### SECTION 4: THE AGENT ARCHITECTURE (300–350 words)
**What it covers:**
This is the heart of the article. Walk through each of the 7 agents.

```
THE ORCHESTRATOR
├── THE DATA AGENT (SQL generation + DuckDB)
├── THE ANALYSIS AGENT (Claude Sonnet — performance insights)
├── THE CREATIVE ANALYST AGENT (creative fatigue, CTR curves)
├── THE OPTIMIZER AGENT (budget reallocation, SGD amounts)
├── THE DASHBOARD AGENT (generates Streamlit + auto-launches)
└── THE INSIGHT QUALITY CRITIC (scores every output 0–10)
```

**For each agent, cover 3 things:**
1. What it does (one sentence)
2. The interesting engineering challenge
3. What it outputs (concrete example)

**Key insight to share:**
> "The Critic Agent was the most important one I didn't expect.
> It scores every insight 0-10 before it reaches the user.
> An AI reviewing AI output — that's where quality comes from."

**Visual to include:**
- Agent pipeline flow diagram (created fresh, clean)
- Screenshot of terminal showing each agent firing in sequence

---

### SECTION 5: THE SPRINT — FROM ZERO TO WORKING (200–250 words)
**What it covers:**
- Hour-by-hour: how the build actually went
- 6–8 hours total. Phase 1 (data + SQL tool) + Phase 2 (core agents)
- What went wrong (real failures — the Max Streaming SQL bug, the API key issue,
  the DataFrame error in the dashboard)
- Why I published V1 even though the dashboard isn't perfect yet

**Key line to include:**
> "I spent 20 minutes debugging why the dashboard was crashing.
> The fix was two characters: `len()`.
> That's how AI engineering actually works — brilliant 90%, trivial bug 10%."

**Tone:** Honest. Self-aware. Shows you're not faking expertise — you're building it.

---

### SECTION 6: WHAT IT CAN DO NOW (150–200 words)
**What it covers:**
- Real examples of queries the system can answer:
  - "Which creative formats have the highest ROAS this month?"
  - "Show me campaigns below target ROAS and recommend budget reallocation"
  - "What's causing the CTR decline on video creatives?"
  - "Generate a dashboard showing this week's performance"
- What the Critic Agent adds to each output
- Real terminal screenshot

**No real data.** Simulated data only. Be clear about this.

**Tone:** Show don't tell. Let the output speak.

---

### SECTION 7: THE BIGGER PICTURE — WHAT'S NEXT (200–250 words)
**What it covers:**
- This is V1. It works. It's not perfect.
- The roadmap for where this goes:

```
V1 (NOW):        7 agents, marketing analytics, 1 domain
V2 (+2 weeks):   Dashboard perfected, tabs UI, quick query panel
V3 (+4 weeks):   2nd use case (different industry or function)
V4 (+8 weeks):   3rd and 4th use cases, refining the architecture
V5 (+12 weeks):  Forming a micro AI consulting firm around this
```

- Why publish now and not when it's finished?
  > "Because waiting for perfect is how good ideas die.
  > I'd rather show imperfect progress than perfect silence."

- The bigger vision: 4–5 polished AI agent use cases, each solving a real
  business problem, built with the same architecture, refined over time.

**Tone:** Ambitious but humble. Learning openly, building deliberately.

---

### SECTION 8: CLOSING + CTA (100–150 words)
**What it covers:**
- What you took away from this sprint (technical + mindset)
- Invitation to follow the series
- One practical tip for readers who want to start their own agent project

**CTA options:**
- "Follow me for Batch 2 — the dashboard evolution (coming in ~2 weeks)"
- "Drop a comment: what would YOU want an AI analytics agent to do for you?"
- "Building something similar? Let's connect — I want to hear about it."

---

## SCREENSHOTS TO PREPARE

Before writing the final article, capture these:

| Screenshot | What to Capture | File Name |
|---|---|---|
| Terminal pipeline | Run a demo query, screenshot the full agent pipeline with colored steps | `terminal-pipeline.png` |
| Architecture diagram | Clean diagram showing 7 agents with flow arrows | `agent-architecture.png` |
| Dashboard (when fixed) | Full dashboard with tabs and KPI cards | `dashboard-overview.png` |
| Agent output example | A sample response showing structure: Summary / Findings / Alerts / Recommendations | `agent-output-example.png` |
| Code snippet | The Critic Agent scoring loop — elegant and impressive | `critic-agent-code.png` |

---

## WHAT TO NOT INCLUDE

| Don't Include | Why |
|---|---|
| Real company name or division | Privacy + professional reasons |
| Real campaign names or spend data | Confidential |
| Exact API key or env files | Security |
| Overpromises ("This will replace analysts") | Damages credibility |
| Fake metrics ("This saved X hours") | You don't have real data yet |
| "This is perfect / production ready" | It's V1 — be honest |

---

## STYLE GUIDE FOR THE ARTICLE

**Voice:** First person. Conversational but technical. Like a senior dev writing a build log.

**Colors (for any visuals):**
- Primary: `#1428A0` (deep navy blue)
- Accent: `#FFD700` (gold)
- Background: `#0A0A0A` (near black for code blocks)
- Text: `#FFFFFF` white on dark, `#1A1A1A` dark on light

**Formatting rules:**
- Short paragraphs (2–3 sentences max)
- Use tables for comparisons (readers skim)
- Code snippets for technical sections (shows real work)
- Architecture diagram as a visual break
- Section headers as anchor points
- No corporate buzzwords ("synergize", "leverage", "disruptive")

**Estimated read time:** 6–8 minutes (LinkedIn sweet spot for technical content)
**Word count target:** ~1,800–2,200 words

---

## DECISION NEEDED FROM YOU

Before I write the full article, tell me:

1. **Which title do you prefer?** (A, B, C, D, or the recommended combined option)

2. **How personal do you want it?**
   - Option P1: First name, general "media entertainment company in Singapore"
   - Option P2: First name only, no company context

3. **Series name?** Suggestions:
   - "Building AI in Public" series
   - "The AI Sprint Logs" series
   - "From Code to Company" series

4. **Anything you want to add that isn't covered above?**
   - Any specific experience from the build you want highlighted?
   - Any tools or decisions you want to talk about more?

---

*Once you confirm direction → I write the full V1 article as a separate file in this folder.*
*Screenshots → save to `linkedin-article/assets/` folder*
