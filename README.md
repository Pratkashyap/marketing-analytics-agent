# 🎬 Marketing Analytics Agent

> A 7-agent AI system that answers marketing analytics questions in under 15 seconds.
> Built as a weekend sprint. Documented publicly as it grows.

---

## What This Is

A fully orchestrated, multi-agent AI marketing analytics platform built from scratch using Python, DuckDB, and the Anthropic Claude API.

Ask it any marketing question in plain English. It pulls the data, analyses performance, checks creative fatigue, recommends budget reallocation, scores the quality of its own output — and returns a structured, CMO-ready answer.

**No cloud infrastructure. No SaaS subscriptions. Runs entirely on a laptop.**

---

## The Agent Team

| Agent | Role | Model |
|-------|------|-------|
| 🧠 **Orchestrator** | Routes every query, coordinates the team, synthesises the final answer | Claude Sonnet 4.6 |
| 📊 **Data Agent** | Natural language → SQL → DuckDB → structured results | Claude Haiku 4.5 |
| 🔍 **Analysis Hub** | KPI analysis, trend detection, anomaly flagging, ROAS vs target | Claude Sonnet 4.6 |
| 🎨 **Creative Analyst** | CTR fatigue curves, format performance, creative refresh priorities | Claude Sonnet 4.6 |
| 💰 **Optimizer** | Specific budget reallocation recommendations with projected ROAS impact | Claude Sonnet 4.6 |
| 📈 **Dashboard Agent** | Generates and launches a live Streamlit dashboard on demand | Claude Haiku 4.5 |
| ⚖️ **Quality Critic** | Scores every insight 0–10 before it reaches the user | Claude Haiku 4.5 |

---

## Architecture

```
                    ┌─────────────────────────┐
                    │      ORCHESTRATOR        │
                    │  Routes · Coordinates    │
                    │  Synthesises · Delivers  │
                    └──────────┬──────────────┘
                               │
          ┌────────────────────┼─────────────────────┐
          │                    │                      │
          ▼                    ▼                      ▼
   ┌─────────────┐    ┌──────────────┐      ┌─────────────┐
   │ DATA AGENT  │    │ ANALYSIS HUB │      │  DASHBOARD  │
   │ SQL + DuckDB│    │   AGENT      │      │   AGENT     │
   └─────────────┘    └──────┬───────┘      └─────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │   CREATIVE   │ │  OPTIMIZER   │ │   QUALITY    │
     │   ANALYST    │ │    AGENT     │ │    CRITIC    │
     │ CTR · Fatigue│ │ Budget · SGD │ │ Score · 0-10 │
     └──────────────┘ └──────────────┘ └──────────────┘
```

**Pattern:** Supervisor / Orchestrator — one central agent routes to specialists. No swarm. Explicit, debuggable, production-friendly.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Database | DuckDB 1.5.0 — 112K rows, millisecond queries |
| AI (Reasoning) | Claude Sonnet 4.6 — deep analysis and insights |
| AI (Lightweight) | Claude Haiku 4.5 — SQL generation, classification |
| Dashboard | Streamlit — open source, no cloud required |
| Charts | Plotly — interactive visualisations |
| Terminal UI | Rich — live agent pipeline display |
| Data | Simulated — 112K rows, 4 platforms, 90 days |

---

## Project Structure

```
marketing-analytics-agent/
│
├── agents/
│   ├── orchestrator.py          # Central routing + coordination
│   ├── data_agent.py            # SQL generation + DuckDB queries
│   ├── analysis_agent.py        # Performance insights + KPIs
│   ├── creative_analyst_agent.py # Creative fatigue + CTR analysis
│   ├── optimizer_agent.py       # Budget reallocation recommendations
│   ├── dashboard_agent.py       # Streamlit dashboard generation
│   └── critic_agent.py          # Insight quality scoring (0–10)
│
├── tools/
│   └── sql_tool.py              # NL → SQL → DuckDB interface
│
├── data/
│   └── generate_data.py         # Simulated marketing data generator
│
├── config/                      # Business context, prompts (future)
│
├── linkedin-article/            # Build-in-public article series
│   ├── ARTICLE_IDEAS_AND_FLOW.md
│   ├── V1_ARTICLE_DRAFT.md
│   └── V2_ARTICLE_DRAFT.md
│
├── ref image/                   # Reference images and screenshots
│
├── main.py                      # Entry point — Rich terminal UI
├── requirements.txt             # All dependencies with pinned versions
├── .env.example                 # Copy to .env and add your API key
└── .gitignore                   # Protects .env, venv, data files
```

---

## Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/marketing-analytics-agent.git
cd marketing-analytics-agent
```

### 2. Create virtual environment
```bash
python3.12 -m venv venv
source venv/bin/activate          # Mac/Linux
# venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
```bash
cp .env.example .env
# Open .env and add your Anthropic API key
# Get one at: https://console.anthropic.com/
```

### 5. Generate the data
```bash
python3 data/generate_data.py
```

### 6. Run the agent
```bash
python3 main.py
```

---

## Sample Queries

Once running, try these:

```
> What is our total ROAS across all platforms this month?
> Which creative formats have the highest CTR on TikTok?
> Why is ROAS declining on video creatives?
> Show me campaigns below their ROAS target
> Which ad sets show signs of creative fatigue?
> Recommend budget reallocation to improve overall ROAS
> Give me a full performance review across all platforms
> dashboard
```

Type `demo` to run 5 showcase queries automatically.
Type `quit` to exit.

---

## What the Output Looks Like

```
🧠 ORCHESTRATOR  Classified: analysis → Creative Analyst + Optimizer
📊 DATA AGENT    SQL generated → 847 rows returned (2.1s)
🎨 CREATIVE      Fatigue detected on 3 video assets (21+ days on-air)
💰 OPTIMIZER     Reallocation: $3,200 Meta → Carousel formats
⚖️  CRITIC        ✅ Quality Score: 9/10 — Approved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERFORMANCE SUMMARY
Video creative CTR has declined 28% over 21 days on Meta and TikTok.
Three specific variants are past their effective window.

KEY FINDINGS
• Carousel formats running at 2.8x average CTR — strong performers
• Meta Reels: CTR stable, ROAS 3.9x — above target
• TikTok Video 15s: frequency > 6 on 2 ad sets — saturation risk

RECOMMENDATIONS
1. Pause 3 fatigued video variants immediately
2. Reallocate $3,200 to Carousel — projected +0.4x ROAS within 7 days
3. Reduce TikTok frequency cap from 8 to 4 on saturated ad sets
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Data Notes

This project uses **fully simulated data**. No real campaign data, spend figures, or company information is included.

The simulated dataset includes:
- 4 platforms: Meta, Google, TikTok, YouTube
- 112,000+ daily performance rows
- 90-day date range
- Realistic patterns: seasonality, creative fatigue curves, diminishing returns, anomalies
- All figures in SGD

---

## Roadmap

```
✅ V1 — 7 agents live, terminal UI, basic dashboard
🔨 V2 — Dashboard upgrade: tabs, live queries, creative health view
🔨 V3 — Use Case #2: same architecture, new domain
🔨 V4 — 3–4 polished use cases, production hardening
🔨 V5 — Public product / AI micro-agency formation
```

This project is documented publicly in batches. Follow the journey on LinkedIn → [link coming].

---

## The Build Series

This project is part of **[SERIES NAME]** — a building-in-public series documenting the journey from weekend sprint to production-grade AI platform.

- **Batch 1:** 7 agents built, architecture documented ← *you are here*
- **Batch 2:** Dashboard evolution
- **Batch 3:** Second use case
- **Batch 4:** Multi-use-case architecture
- **Batch 5:** Company formation

---

## Acknowledgements

Built with:
- [Anthropic Claude API](https://anthropic.com)
- [DuckDB](https://duckdb.org)
- [Streamlit](https://streamlit.io)
- [Rich](https://rich.readthedocs.io)
- [Plotly](https://plotly.com)

---

## Licence

MIT — use it, build on it, share what you make.

---

*V1 · Built in one weekend sprint · Documented publicly*
