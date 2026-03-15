"""
Dashboard Agent — Warner Bros. Singapore Marketing Analytics
4-tab Streamlit UI: Agent Chat | Performance Dashboard | Creative Health | Data Explorer
Sidebar: Quick Queries panel

Open source stack: Streamlit + Plotly + DuckDB (all free)
"""

import os
import sys
import json
import subprocess
import duckdb

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

DB_PATH       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/marketing_analytics.duckdb")
DASHBOARD_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../dashboard_app.py")


# ─────────────────────────────────────────────────────────────
# Questions the agent asks before building
# ─────────────────────────────────────────────────────────────
DASHBOARD_QUESTIONS = [
    {
        "key":     "focus",
        "prompt":  "What should the dashboard focus on?",
        "options": [
            "1. Overall portfolio (all business lines)",
            "2. Single business line deep-dive",
            "3. Platform comparison (Meta vs Google vs TikTok vs YouTube)",
            "4. Creative performance & fatigue",
            "5. Executive summary (CMO view)",
        ],
        "default": "1",
    },
    {
        "key":     "period",
        "prompt":  "What time period?",
        "options": [
            "1. Last 7 days",
            "2. Last 30 days",
            "3. This month (March 2026)",
            "4. Last 90 days (full history)",
        ],
        "default": "2",
    },
    {
        "key":     "business_line",
        "prompt":  "Which business line? (only if you chose option 2 above)",
        "options": [
            "1. Theatrical",
            "2. Max Streaming",
            "3. Home Entertainment",
            "4. WB Games",
            "5. Licensing & Merch",
            "0. Skip (not applicable)",
        ],
        "default": "0",
        "conditional": "focus == '2'",
    },
]

FOCUS_MAP = {
    "1": "portfolio",
    "2": "business_line",
    "3": "platform",
    "4": "creative",
    "5": "executive",
}

PERIOD_MAP = {
    "1": ("Last 7 days",    "f.date >= '2026-03-08'"),
    "2": ("Last 30 days",   "f.date >= '2026-02-13'"),
    "3": ("March 2026",     "f.date LIKE '2026-03-%'"),
    "4": ("Full 90 days",   "f.date >= '2025-12-15'"),
}

BL_MAP = {
    "1": "Theatrical",
    "2": "Max Streaming",
    "3": "Home Entertainment",
    "4": "WB Games",
    "5": "Licensing & Merch",
}


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def safe_rec(df):
    """Serialize DataFrame → JSON-safe list of plain Python dicts (no numpy types)."""
    return json.loads(df.to_json(orient='records'))


# ─────────────────────────────────────────────────────────────
# Data fetchers
# ─────────────────────────────────────────────────────────────

def fetch_kpis(where: str) -> dict:
    con = duckdb.connect(DB_PATH, read_only=True)
    row = con.execute(f"""
        SELECT
            ROUND(SUM(spend), 0)       AS total_spend,
            ROUND(SUM(revenue), 0)     AS total_revenue,
            ROUND(SUM(revenue)/NULLIF(SUM(spend),0), 2) AS roas,
            SUM(impressions)           AS impressions,
            SUM(clicks)                AS clicks,
            SUM(conversions)           AS conversions,
            ROUND(AVG(cpm), 2)         AS avg_cpm,
            ROUND(AVG(ctr), 4)         AS avg_ctr
        FROM fact_daily_performance f
        WHERE {where}
    """).fetchone()
    con.close()
    keys = ["total_spend","total_revenue","roas","impressions","clicks","conversions","avg_cpm","avg_ctr"]
    if row:
        result = dict(zip(keys, row))
        # Convert to plain Python types
        return json.loads(json.dumps(result, default=float))
    return {}


def fetch_daily_trend(where: str):
    con = duckdb.connect(DB_PATH, read_only=True)
    df  = con.execute(f"""
        SELECT date,
               ROUND(SUM(spend), 2)   AS spend,
               ROUND(SUM(revenue)/NULLIF(SUM(spend),0), 2) AS roas,
               SUM(impressions)       AS impressions
        FROM fact_daily_performance f
        WHERE {where}
        GROUP BY date ORDER BY date
    """).df()
    con.close()
    return df


def fetch_by_business_line(where: str):
    con = duckdb.connect(DB_PATH, read_only=True)
    df  = con.execute(f"""
        SELECT f.business_line,
               ROUND(SUM(f.spend), 2) AS spend,
               ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0), 2) AS roas,
               MAX(c.roas_target) AS target,
               SUM(f.conversions) AS conversions,
               ROUND(AVG(f.cpm), 2) AS avg_cpm
        FROM fact_daily_performance f
        JOIN dim_campaign c ON f.campaign_id = c.campaign_id
        WHERE {where}
        GROUP BY f.business_line ORDER BY spend DESC
    """).df()
    con.close()
    return df


def fetch_by_platform(where: str):
    con = duckdb.connect(DB_PATH, read_only=True)
    df  = con.execute(f"""
        SELECT p.platform_name,
               ROUND(SUM(f.spend), 2) AS spend,
               ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0), 2) AS roas,
               ROUND(AVG(f.cpm), 2) AS avg_cpm,
               ROUND(AVG(f.ctr), 3) AS avg_ctr,
               SUM(f.conversions) AS conversions
        FROM fact_daily_performance f
        JOIN dim_platform p ON f.platform_id = p.platform_id
        WHERE {where}
        GROUP BY p.platform_name ORDER BY spend DESC
    """).df()
    con.close()
    return df


def fetch_top_campaigns(where: str, limit: int = 10):
    con = duckdb.connect(DB_PATH, read_only=True)
    df  = con.execute(f"""
        SELECT c.campaign_name, f.business_line, p.platform_name,
               ROUND(SUM(f.spend), 2) AS spend,
               ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0), 2) AS roas,
               MAX(c.roas_target) AS target,
               SUM(f.conversions) AS conversions
        FROM fact_daily_performance f
        JOIN dim_campaign c  ON f.campaign_id  = c.campaign_id
        JOIN dim_platform p  ON f.platform_id  = p.platform_id
        WHERE {where}
        GROUP BY c.campaign_name, f.business_line, p.platform_name
        ORDER BY spend DESC LIMIT {limit}
    """).df()
    con.close()
    return df


def fetch_creative_fatigue(where: str):
    con = duckdb.connect(DB_PATH, read_only=True)
    df  = con.execute(f"""
        SELECT cr.creative_name, cr.format, f.business_line,
               ROUND(AVG(CASE WHEN f.day_num < 30 THEN f.ctr END), 3) AS early_ctr,
               ROUND(AVG(CASE WHEN f.day_num >= 60 THEN f.ctr END), 3) AS late_ctr,
               ROUND(SUM(f.spend), 2) AS spend
        FROM fact_daily_performance f
        JOIN dim_creative cr ON f.creative_id = cr.creative_id
        WHERE {where}
        GROUP BY cr.creative_name, cr.format, f.business_line
        HAVING early_ctr IS NOT NULL AND late_ctr IS NOT NULL
           AND late_ctr < early_ctr * 0.80
        ORDER BY (late_ctr - early_ctr) ASC LIMIT 10
    """).df()
    con.close()
    return df


def fetch_creative_by_format(where: str):
    con = duckdb.connect(DB_PATH, read_only=True)
    df  = con.execute(f"""
        SELECT cr.format,
               COUNT(DISTINCT cr.creative_id) AS creatives,
               ROUND(SUM(f.spend), 2)  AS spend,
               ROUND(AVG(f.ctr), 3)    AS avg_ctr,
               ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0), 2) AS avg_roas,
               SUM(f.conversions)      AS conversions
        FROM fact_daily_performance f
        JOIN dim_creative cr ON f.creative_id = cr.creative_id
        WHERE {where}
        GROUP BY cr.format ORDER BY spend DESC
    """).df()
    con.close()
    return df


def fetch_top_creatives(where: str, limit: int = 10):
    con = duckdb.connect(DB_PATH, read_only=True)
    df  = con.execute(f"""
        SELECT cr.creative_name, cr.format, f.business_line,
               ROUND(SUM(f.spend), 2)  AS spend,
               ROUND(AVG(f.ctr), 3)    AS avg_ctr,
               ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0), 2) AS roas,
               SUM(f.conversions)      AS conversions
        FROM fact_daily_performance f
        JOIN dim_creative cr ON f.creative_id = cr.creative_id
        WHERE {where}
        GROUP BY cr.creative_name, cr.format, f.business_line
        ORDER BY roas DESC LIMIT {limit}
    """).df()
    con.close()
    return df


# ─────────────────────────────────────────────────────────────
# Dashboard code generator
# ─────────────────────────────────────────────────────────────

def generate_dashboard(config: dict) -> str:
    """Generate dashboard_app.py — 4-tab UI with Agent Chat, Performance, Creative Health, Data Explorer."""

    focus       = FOCUS_MAP.get(config.get("focus", "1"), "portfolio")
    period_key  = config.get("period", "2")
    period_label, where = PERIOD_MAP.get(period_key, PERIOD_MAP["2"])
    bl          = BL_MAP.get(config.get("business_line", "0"), None)

    if focus == "business_line" and bl:
        where_bl = f"{where} AND f.business_line = '{bl}'"
        title    = f"Warner Bros. Singapore — {bl} Dashboard"
    else:
        where_bl = where
        title    = "Warner Bros. Singapore — Marketing Analytics Dashboard"

    # Pre-fetch all data
    kpis          = fetch_kpis(where_bl)
    daily         = fetch_daily_trend(where_bl)
    by_bl         = fetch_by_business_line(where_bl)
    by_plat       = fetch_by_platform(where_bl)
    campaigns     = fetch_top_campaigns(where_bl)
    fatigue       = fetch_creative_fatigue(where_bl)
    by_format     = fetch_creative_by_format(where_bl)
    top_creatives = fetch_top_creatives(where_bl)

    # Serialize to JSON-safe records
    daily_rec         = safe_rec(daily)
    by_bl_rec         = safe_rec(by_bl)
    by_plat_rec       = safe_rec(by_plat)
    campaigns_rec     = safe_rec(campaigns)
    fatigue_rec       = safe_rec(fatigue)
    by_format_rec     = safe_rec(by_format)
    top_creatives_rec = safe_rec(top_creatives)

    db_abs       = os.path.abspath(DB_PATH)
    project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    env_path     = os.path.join(project_root, ".env")

    code = f'''"""
Warner Bros. Singapore — Marketing Analytics Dashboard
4 Tabs: Agent Chat | Performance Dashboard | Creative Health | Data Explorer
Period: {period_label} | Generated by Dashboard Agent
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import duckdb
import os
import sys
from dotenv import load_dotenv

# ── Setup ─────────────────────────────────────────────
load_dotenv("{env_path}", override=True)
sys.path.insert(0, "{project_root}")

st.set_page_config(
    page_title="WB Singapore Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand colours ─────────────────────────────────────
WB_BLUE   = "#1428A0"
WB_YELLOW = "#FFD700"
WB_DARK   = "#0D0D0D"
GOOD      = "#00C48C"
WARN      = "#FFB800"
BAD       = "#FF4444"
DB_PATH   = "{db_abs}"

# ── Inline pre-fetched data ────────────────────────────
kpis          = {kpis}
daily         = pd.DataFrame({daily_rec})
by_bl         = pd.DataFrame({by_bl_rec})
by_plat       = pd.DataFrame({by_plat_rec})
campaigns     = pd.DataFrame({campaigns_rec})
fatigue       = pd.DataFrame({fatigue_rec})
by_format     = pd.DataFrame({by_format_rec})
top_creatives = pd.DataFrame({top_creatives_rec})

if len(daily) > 0:
    daily["date"] = pd.to_datetime(daily["date"])

# ── Session state ─────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quick_query" not in st.session_state:
    st.session_state.quick_query = None

# ── Orchestrator (cached across reruns) ───────────────
@st.cache_resource
def get_orchestrator():
    try:
        from agents.orchestrator import Orchestrator
        return Orchestrator()
    except Exception as e:
        return None

# ── Page Header ───────────────────────────────────────
st.markdown("""
<div style="background: linear-gradient(90deg, #1428A0 0%, #0D0D0D 100%);
            padding: 16px 28px; border-radius: 10px; margin-bottom: 12px;">
  <h1 style="color:#FFD700; margin:0; font-size:22px; font-weight:700;">
    🎬 {title}
  </h1>
  <p style="color:#aaa; margin:4px 0 0; font-size:13px;">
    Period: {period_label} &nbsp;|&nbsp; Claude AI &nbsp;|&nbsp; SGD &nbsp;|&nbsp; Today: 2026-03-15
  </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar: Quick Queries ────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ Quick Queries")
    st.markdown("<p style='color:#888; font-size:12px;'>Click to send to Agent Chat</p>", unsafe_allow_html=True)
    st.divider()

    QUICK_QUERIES = [
        ("📊 Analysis",  "How are all business lines performing vs ROAS target this month?"),
        ("📊 Analysis",  "Why is Max Streaming underperforming and what should we do?"),
        ("📊 Analysis",  "Compare Meta vs TikTok performance this month"),
        ("🎨 Creative",  "Which creative format has the best ROAS?"),
        ("🎨 Creative",  "Which creatives need to be refreshed urgently?"),
        ("🎨 Creative",  "How are Video 15s vs Static Image creatives performing?"),
        ("💰 Optimizer", "I have SGD 50K extra — where should I allocate it?"),
        ("💰 Optimizer", "Which platforms are we over-investing in?"),
        ("💰 Optimizer", "Rebalance my budget to maximise blended ROAS"),
        ("⚡ Combo",     "Full audit: performance, creatives, and budget optimisation"),
        ("⚡ Combo",     "Which business lines need creative refresh AND budget change?"),
    ]

    for i, (tag, q) in enumerate(QUICK_QUERIES):
        label = f"{{tag}}  {{q[:36]}}..." if len(q) > 38 else f"{{tag}}  {{q}}"
        if st.button(label, use_container_width=True, key=f"qq_{{i}}"):
            st.session_state.quick_query = q

    st.divider()
    st.markdown("### 🤖 Agent Pipeline")
    st.markdown("**6 agents active:**")
    st.markdown("🧠 Orchestrator — routes intent")
    st.markdown("📊 Data Agent — SQL → DuckDB")
    st.markdown("🔍 Analysis Agent — performance")
    st.markdown("🎨 Creative Analyst — formats")
    st.markdown("💰 Optimizer — budget allocation")
    st.markdown("⚖️ Quality Critic — review")
    st.divider()
    st.markdown("### 📅 Dashboard Info")
    st.markdown(f"**Period:** {period_label}")
    st.markdown(f"**Focus:** {focus.replace('_', ' ').title()}")
    st.markdown("**Data:** 112K rows (DuckDB)")

# ── Tabs ──────────────────────────────────────────────
tab_chat, tab_perf, tab_creative, tab_data = st.tabs([
    "💬  Agent Chat",
    "📊  Performance Dashboard",
    "🎨  Creative Health",
    "🔍  Data Explorer",
])


# ══════════════════════════════════════════════════════
# TAB 1 — AGENT CHAT
# ══════════════════════════════════════════════════════
with tab_chat:
    st.markdown("### 💬 Ask Your Marketing Analytics Agent")
    st.markdown(
        "<p style='color:#888; font-size:13px;'>Powered by Claude AI — ask anything about WB Singapore campaigns. "
        "Use the ⚡ Quick Queries panel on the left to run pre-built questions.</p>",
        unsafe_allow_html=True,
    )

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Consume quick query from sidebar
    pending = st.session_state.get("quick_query")

    # Chat input
    user_input = st.chat_input("Ask about campaigns, ROAS, budget allocation, platforms, creatives…")

    if pending and not user_input:
        user_input = pending
        st.session_state.quick_query = None

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({{"role": "user", "content": user_input}})

        # ── Agent pipeline icons and labels ────────────────
        PIPELINE_ICONS = {{
            "orchestrator":    "🧠", "data_agent":      "📊",
            "analysis_agent":  "🔍", "creative_analyst": "🎨",
            "optimizer":       "💰", "critic":           "⚖️",
        }}
        PIPELINE_NAMES = {{
            "orchestrator":    "Orchestrator",    "data_agent":      "Data Agent",
            "analysis_agent":  "Analysis Agent",  "creative_analyst": "Creative Analyst",
            "optimizer":       "Optimizer Agent", "critic":           "Quality Critic",
        }}
        SKIP_EVENTS = {{"start", "done", "classifying", "refining"}}

        with st.chat_message("assistant"):
            try:
                orch = get_orchestrator()
                if orch is None:
                    raise RuntimeError("Orchestrator unavailable — check your ANTHROPIC_API_KEY in .env")

                # ── Live pipeline display using st.status ──
                with st.status("🧠 Running agent pipeline…", expanded=True) as pipeline_status:

                    def on_pipeline_status(agent, event, detail=""):
                        icon = PIPELINE_ICONS.get(agent, "•")
                        name = PIPELINE_NAMES.get(agent, agent)
                        if event == "start":
                            st.write(f"{{icon}} **{{name}}** starting…")
                        elif event == "classified":
                            import json as _json
                            try:
                                d = _json.loads(detail)
                                intent     = d.get("intent", "")
                                specialist = d.get("specialist", "analysis")
                                st.write(f"  ↳ Intent: `{{intent}}` · Specialist: `{{specialist}}`")
                            except Exception:
                                pass
                        elif event == "routing":
                            st.write(f"  ↳ Pipeline: **{{detail}}**")
                        elif event == "query_executed":
                            st.write(f"  ↳ ✅ {{detail}} rows fetched from DuckDB")
                        elif event == "sql_generated":
                            short_sql = detail.replace("\\n", " ")[:80]
                            st.write(f"  ↳ SQL: `{{short_sql}}…`")
                        elif event == "preparing":
                            st.write(f"  ↳ {{detail}}")
                        elif event in ("analysing", "optimising"):
                            st.write(f"  ↳ {{icon}} Generating insights…")
                        elif event == "reviewing":
                            st.write(f"  ↳ ⚖️ Scoring: specificity · actionability · accuracy")
                        elif event == "done":
                            if agent == "critic":
                                st.write(f"  ↳ ✅ {{detail}}")
                            elif agent != "orchestrator":
                                st.write(f"  ↳ ✅ {{name}} complete")

                    result = orch.run(user_input, verbose=False, on_status=on_pipeline_status)
                    specialist = result.get("specialist", "analysis")
                    spec_label = {{"creative": "Creative Analyst", "optimizer": "Optimizer",
                                   "analysis": "Analysis Agent"}}.get(specialist, specialist)
                    pipeline_status.update(
                        label=f"✅ Pipeline complete — routed to **{{spec_label}}**",
                        state="complete", expanded=False,
                    )

                raw_resp = result.get("response", "No response generated.")

                # Pretty-format the WB-style markdown response
                lines, formatted = raw_resp.split("\\n"), []
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("**") and stripped.endswith("**"):
                        formatted.append(f"### {{stripped.strip('*')}}")
                    elif stripped.startswith("- "):
                        formatted.append(f"• {{stripped[2:]}}")
                    elif stripped.startswith("---"):
                        formatted.append("---")
                    else:
                        formatted.append(line)
                final = "\\n".join(formatted)
                st.markdown(final)
                st.session_state.messages.append({{"role": "assistant", "content": final}})

            except Exception as exc:
                err = f"⚠️ Error: {{exc}}"
                st.error(err)
                st.session_state.messages.append({{"role": "assistant", "content": err}})

        st.rerun()

    if st.session_state.messages:
        if st.button("🗑️  Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()


# ══════════════════════════════════════════════════════
# TAB 2 — PERFORMANCE DASHBOARD
# ══════════════════════════════════════════════════════
with tab_perf:

    # — KPI Row —
    st.subheader(f"Key Metrics — {period_label}")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    roas_val = kpis.get("roas", 0) or 0
    with c1: st.metric("Total Spend",   f"SGD {{kpis.get('total_spend', 0):,.0f}}")
    with c2: st.metric("Total Revenue", f"SGD {{kpis.get('total_revenue', 0):,.0f}}")
    with c3: st.metric("Blended ROAS",  f"{{roas_val:.2f}}x",
                        delta=f"{{roas_val - 3.5:.2f}}x vs 3.5x target")
    with c4: st.metric("Impressions",   f"{{kpis.get('impressions', 0) / 1e6:.1f}}M")
    with c5: st.metric("Clicks",        f"{{kpis.get('clicks', 0) / 1e3:.0f}}K")
    with c6: st.metric("Conversions",   f"{{kpis.get('conversions', 0) / 1e3:.0f}}K")

    st.divider()

    # — Row 1: Daily Trend + Platform Pie —
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.subheader("📈 Daily Spend & ROAS Trend")
        if len(daily) > 0:
            fig = make_subplots(specs=[[{{"secondary_y": True}}]])
            fig.add_trace(go.Bar(
                x=daily["date"], y=daily["spend"],
                name="Daily Spend (SGD)", marker_color=WB_BLUE, opacity=0.8,
            ), secondary_y=False)
            fig.add_trace(go.Scatter(
                x=daily["date"], y=daily["roas"],
                name="ROAS", line=dict(color=WB_YELLOW, width=2.5),
                mode="lines+markers", marker=dict(size=4),
            ), secondary_y=True)
            fig.add_hline(y=3.5, line_dash="dot", line_color="red",
                          annotation_text="Target 3.5x", secondary_y=True)
            fig.update_layout(
                plot_bgcolor="#0D0D0D", paper_bgcolor="#111",
                font=dict(color="white"), legend=dict(bgcolor="#1a1a1a"),
                height=320, margin=dict(t=10, b=10),
            )
            fig.update_yaxes(title_text="Spend (SGD)", secondary_y=False, gridcolor="#222")
            fig.update_yaxes(title_text="ROAS",        secondary_y=True,  gridcolor="#222")
            st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("🎯 Spend by Platform")
        if len(by_plat) > 0:
            fig2 = px.pie(
                by_plat, values="spend", names="platform_name",
                color_discrete_sequence=[WB_BLUE, WB_YELLOW, "#00C48C", "#FF6B6B"],
                hole=0.45,
            )
            fig2.update_layout(
                plot_bgcolor="#0D0D0D", paper_bgcolor="#111",
                font=dict(color="white"), height=320,
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(bgcolor="#1a1a1a"),
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # — Row 2: ROAS vs Target + Platform Table —
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.subheader("📊 ROAS by Business Line vs Target")
        if len(by_bl) > 0:
            colors = [
                GOOD if r >= t else BAD
                for r, t in zip(by_bl["roas"], by_bl["target"])
            ]
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                x=by_bl["business_line"], y=by_bl["roas"],
                name="Actual ROAS", marker_color=colors,
                text=by_bl["roas"].apply(lambda x: f"{{x:.2f}}x"),
                textposition="outside",
            ))
            fig3.add_trace(go.Scatter(
                x=by_bl["business_line"], y=by_bl["target"],
                name="Target ROAS", mode="markers",
                marker=dict(symbol="line-ew", size=22, color=WB_YELLOW,
                            line=dict(width=3, color=WB_YELLOW)),
            ))
            fig3.update_layout(
                plot_bgcolor="#0D0D0D", paper_bgcolor="#111",
                font=dict(color="white"), height=340,
                margin=dict(t=10, b=10), legend=dict(bgcolor="#1a1a1a"),
                yaxis=dict(gridcolor="#222"),
            )
            st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.subheader("📡 Platform Performance")
        if len(by_plat) > 0:
            df_p2 = by_plat[["platform_name", "spend", "roas", "avg_cpm", "avg_ctr"]].copy()
            df_p2.columns = ["Platform", "Spend (SGD)", "ROAS", "CPM (SGD)", "CTR %"]
            df_p2["Spend (SGD)"] = df_p2["Spend (SGD)"].apply(lambda x: f"{{x:,.0f}}")
            df_p2["ROAS"]        = df_p2["ROAS"].apply(lambda x: f"{{x:.2f}}x")
            df_p2["CPM (SGD)"]   = df_p2["CPM (SGD)"].apply(lambda x: f"{{x:.2f}}")
            df_p2["CTR %"]       = df_p2["CTR %"].apply(lambda x: f"{{x:.2f}}%")
            st.dataframe(df_p2, use_container_width=True, hide_index=True, height=340)

    st.divider()

    # — Top Campaigns Table —
    st.subheader("🏆 Top 10 Campaigns by Spend")
    if len(campaigns) > 0:
        df_c = campaigns.copy()
        df_c["vs_target"] = df_c["roas"] - df_c["target"]
        df_c["Status"]    = df_c["vs_target"].apply(
            lambda x: "✅ Above" if x >= 0 else f"🔴 {{x:.2f}}x below"
        )
        df_c["spend_fmt"] = df_c["spend"].apply(lambda x: f"SGD {{x:,.0f}}")
        df_c["roas_fmt"]  = df_c["roas"].apply(lambda x: f"{{x:.2f}}x")
        disp = df_c[["campaign_name", "business_line", "platform_name",
                     "spend_fmt", "roas_fmt", "conversions", "Status"]]
        disp.columns = ["Campaign", "Business Line", "Platform",
                        "Spend", "ROAS", "Conversions", "vs Target"]
        st.dataframe(disp, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════
# TAB 3 — CREATIVE HEALTH
# ══════════════════════════════════════════════════════
with tab_creative:
    st.subheader("🎨 Creative Health Dashboard")

    # — Format Performance —
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 ROAS by Creative Format")
        if len(by_format) > 0:
            fig_fmt = px.bar(
                by_format.sort_values("avg_roas", ascending=True),
                x="avg_roas", y="format", orientation="h",
                color="avg_roas",
                color_continuous_scale=["#FF4444", "#FFB800", "#00C48C"],
                text=by_format.sort_values("avg_roas", ascending=True)["avg_roas"].apply(
                    lambda x: f"{{x:.2f}}x"
                ),
            )
            fig_fmt.update_traces(textposition="outside")
            fig_fmt.update_layout(
                plot_bgcolor="#0D0D0D", paper_bgcolor="#111",
                font=dict(color="white"), height=320,
                margin=dict(t=10, b=10, l=10, r=40),
                coloraxis_showscale=False,
                xaxis=dict(gridcolor="#222"),
            )
            st.plotly_chart(fig_fmt, use_container_width=True)

    with col2:
        st.markdown("#### 💰 Spend Distribution by Format")
        if len(by_format) > 0:
            fig_spend = px.pie(
                by_format, values="spend", names="format",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_spend.update_layout(
                plot_bgcolor="#0D0D0D", paper_bgcolor="#111",
                font=dict(color="white"), height=320,
                margin=dict(t=10, b=10),
                legend=dict(bgcolor="#1a1a1a"),
            )
            st.plotly_chart(fig_spend, use_container_width=True)

    if len(by_format) > 0:
        df_fmt_disp = by_format.copy()
        df_fmt_disp["spend_fmt"]  = df_fmt_disp["spend"].apply(lambda x: f"SGD {{x:,.0f}}")
        df_fmt_disp["roas_fmt"]   = df_fmt_disp["avg_roas"].apply(lambda x: f"{{x:.2f}}x")
        df_fmt_disp["ctr_fmt"]    = df_fmt_disp["avg_ctr"].apply(lambda x: f"{{x:.2f}}%")
        disp_fmt = df_fmt_disp[["format", "creatives", "spend_fmt", "roas_fmt", "ctr_fmt", "conversions"]]
        disp_fmt.columns = ["Format", "# Creatives", "Total Spend", "Avg ROAS", "Avg CTR", "Conversions"]
        st.dataframe(disp_fmt, use_container_width=True, hide_index=True)

    st.divider()

    # — Creative Fatigue —
    st.markdown("#### ⚠️ Creative Fatigue Alerts")
    st.markdown(
        "<p style='color:#888; font-size:12px;'>Creatives where CTR dropped >20% "
        "from early period (days 0–30) to late period (days 60+)</p>",
        unsafe_allow_html=True,
    )

    if len(fatigue) > 0:
        df_f = fatigue.copy()
        df_f["ctr_drop_pct"] = (
            (df_f["early_ctr"] - df_f["late_ctr"]) / df_f["early_ctr"] * 100
        ).round(1)

        fig_fat = go.Figure()
        x_labels = df_f["format"] + " | " + df_f["business_line"]
        fig_fat.add_trace(go.Bar(
            name="Early CTR (days 0–30)", x=x_labels, y=df_f["early_ctr"],
            marker_color=GOOD,
        ))
        fig_fat.add_trace(go.Bar(
            name="Late CTR (days 60+)", x=x_labels, y=df_f["late_ctr"],
            marker_color=BAD,
            text=df_f["ctr_drop_pct"].apply(lambda x: f"-{{x:.0f}}%"),
            textposition="outside",
        ))
        fig_fat.update_layout(
            barmode="group", plot_bgcolor="#0D0D0D", paper_bgcolor="#111",
            font=dict(color="white"), height=320,
            margin=dict(t=10, b=10), legend=dict(bgcolor="#1a1a1a"),
            yaxis=dict(title="CTR %", gridcolor="#222"),
            xaxis=dict(tickangle=-20),
        )
        st.plotly_chart(fig_fat, use_container_width=True)

        df_f_disp = df_f[["creative_name","format","business_line",
                           "early_ctr","late_ctr","ctr_drop_pct","spend"]].copy()
        df_f_disp.columns = ["Creative","Format","Business Line",
                              "Early CTR","Late CTR","Drop %","Spend (SGD)"]
        df_f_disp["Spend (SGD)"] = df_f_disp["Spend (SGD)"].apply(lambda x: f"{{x:,.0f}}")
        st.dataframe(df_f_disp, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No significant creative fatigue detected in this period.")

    st.divider()

    # — Top Performing Creatives —
    st.markdown("#### 🏆 Top Creatives by ROAS")
    if len(top_creatives) > 0:
        df_tc = top_creatives.copy()
        df_tc["spend_fmt"] = df_tc["spend"].apply(lambda x: f"SGD {{x:,.0f}}")
        df_tc["roas_fmt"]  = df_tc["roas"].apply(lambda x: f"{{x:.2f}}x")
        df_tc["ctr_fmt"]   = df_tc["avg_ctr"].apply(lambda x: f"{{x:.2f}}%")
        disp_tc = df_tc[["creative_name","format","business_line",
                          "spend_fmt","roas_fmt","ctr_fmt","conversions"]]
        disp_tc.columns = ["Creative","Format","Business Line","Spend","ROAS","CTR","Conversions"]
        st.dataframe(disp_tc, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════
# TAB 4 — DATA EXPLORER
# ══════════════════════════════════════════════════════
with tab_data:
    st.subheader("🔍 Data Explorer")
    st.markdown(
        "<p style='color:#888; font-size:13px;'>Query the DuckDB marketing analytics database directly. "
        "Select a preset or write your own SQL.</p>",
        unsafe_allow_html=True,
    )

    SAMPLE_QUERIES = {{
        "Business Line KPIs (this month)": """SELECT
    business_line,
    ROUND(SUM(spend), 0)  AS total_spend_sgd,
    ROUND(SUM(revenue), 0) AS total_revenue_sgd,
    ROUND(SUM(revenue)/SUM(spend), 2) AS roas,
    SUM(conversions) AS conversions
FROM fact_daily_performance
WHERE date LIKE '2026-03-%'
GROUP BY business_line
ORDER BY total_spend_sgd DESC;""",

        "Platform Daily Trend (last 7 days)": """SELECT
    f.date,
    p.platform_name,
    ROUND(SUM(f.spend), 0) AS spend_sgd,
    ROUND(SUM(f.revenue)/SUM(f.spend), 2) AS roas
FROM fact_daily_performance f
JOIN dim_platform p ON f.platform_id = p.platform_id
WHERE f.date >= '2026-03-08'
GROUP BY f.date, p.platform_name
ORDER BY f.date, spend_sgd DESC;""",

        "Top Campaigns by ROAS": """SELECT
    c.campaign_name,
    f.business_line,
    ROUND(SUM(f.spend), 0)  AS spend,
    ROUND(SUM(f.revenue)/SUM(f.spend), 2) AS roas,
    MAX(c.roas_target) AS target
FROM fact_daily_performance f
JOIN dim_campaign c ON f.campaign_id = c.campaign_id
WHERE f.date >= '2026-02-13'
GROUP BY c.campaign_name, f.business_line
ORDER BY roas DESC LIMIT 10;""",

        "Creative Format Analysis": """SELECT
    cr.format,
    COUNT(DISTINCT cr.creative_id) AS creatives,
    ROUND(AVG(f.ctr), 3)  AS avg_ctr,
    ROUND(AVG(f.roas), 2) AS avg_roas,
    SUM(f.conversions)    AS total_conversions
FROM fact_daily_performance f
JOIN dim_creative cr ON f.creative_id = cr.creative_id
WHERE f.date >= '2026-02-13'
GROUP BY cr.format
ORDER BY avg_roas DESC;""",

        "Creative Fatigue Detection": """SELECT
    cr.creative_name, cr.format, f.business_line,
    ROUND(AVG(CASE WHEN f.day_num < 30 THEN f.ctr END), 3) AS early_ctr,
    ROUND(AVG(CASE WHEN f.day_num >= 60 THEN f.ctr END), 3) AS late_ctr,
    ROUND(SUM(f.spend), 0) AS spend
FROM fact_daily_performance f
JOIN dim_creative cr ON f.creative_id = cr.creative_id
GROUP BY cr.creative_name, cr.format, f.business_line
HAVING early_ctr IS NOT NULL AND late_ctr IS NOT NULL
   AND late_ctr < early_ctr * 0.80
ORDER BY (late_ctr - early_ctr) ASC LIMIT 15;""",

        "Platform CPM & Efficiency": """SELECT
    p.platform_name,
    ROUND(AVG(f.cpm), 2)  AS avg_cpm_sgd,
    ROUND(AVG(f.ctr), 3)  AS avg_ctr_pct,
    ROUND(AVG(f.roas), 2) AS avg_roas,
    SUM(f.conversions)    AS total_conversions
FROM fact_daily_performance f
JOIN dim_platform p ON f.platform_id = p.platform_id
WHERE f.date >= '2026-02-13'
GROUP BY p.platform_name
ORDER BY avg_roas DESC;""",
    }}

    preset = st.selectbox(
        "📋 Load a preset query:",
        ["(write your own…)"] + list(SAMPLE_QUERIES.keys()),
    )
    default_sql = SAMPLE_QUERIES.get(preset, "SELECT * FROM fact_daily_performance LIMIT 20;")

    sql_input = st.text_area("SQL Query:", value=default_sql, height=160,
                             placeholder="SELECT … FROM fact_daily_performance …")

    run_col, _ = st.columns([1, 5])
    with run_col:
        run_btn = st.button("▶️  Run Query", type="primary", use_container_width=True)

    if run_btn:
        try:
            con       = duckdb.connect(DB_PATH, read_only=True)
            result_df = con.execute(sql_input).df()
            con.close()
            st.success(f"✅ {{len(result_df)}} rows returned")
            st.dataframe(result_df, use_container_width=True, height=420)
            csv = result_df.to_csv(index=False)
            st.download_button(
                "⬇️  Download CSV",
                data=csv,
                file_name="wb_analytics_export.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"❌ SQL Error: {{e}}")

    st.divider()
    st.markdown("#### 📚 Schema Reference")

    SCHEMA = {{
        "fact_daily_performance (112K rows)":
            "Main fact table — date, campaign_id, ad_set_id, creative_id, platform_id, "
            "business_line, objective, impressions, clicks, conversions, spend (SGD), "
            "revenue (SGD), roas, cpm, ctr, cvr, frequency, day_num",
        "dim_campaign":
            "campaign_name, business_line, objective, platform_id, roas_target, daily_budget, status",
        "dim_platform":
            "platform_id (1=Meta, 2=Google, 3=TikTok, 4=YouTube), platform_name, platform_type, avg_cpm_baseline",
        "dim_creative":
            "creative_name, format (Video 15s/30s, Static Image, Carousel, Story, Reel, YouTube Pre-roll), "
            "style, business_line, is_video",
        "dim_ad_set":
            "ad_set_name, audience_type, age_range, gender, daily_budget",
    }}

    for tbl, desc in SCHEMA.items():
        with st.expander(f"📋  {{tbl}}"):
            st.markdown(f"**{{desc}}**")
            try:
                con    = duckdb.connect(DB_PATH, read_only=True)
                sample = con.execute(f"SELECT * FROM {{tbl.split()[0]}} LIMIT 3").df()
                con.close()
                st.dataframe(sample, use_container_width=True, hide_index=True)
            except Exception:
                pass


# ── Footer ────────────────────────────────────────────
st.divider()
st.markdown("""
<p style="text-align:center; color:#555; font-size:11px;">
🎬 Warner Bros. Singapore &nbsp;|&nbsp; Marketing Analytics Agent &nbsp;|&nbsp;
Streamlit + Plotly + DuckDB &nbsp;|&nbsp; Powered by Claude AI
</p>
""", unsafe_allow_html=True)
'''

    with open(DASHBOARD_OUT, "w") as f:
        f.write(code)

    return DASHBOARD_OUT


def launch_dashboard(path: str) -> subprocess.Popen:
    """Launch Streamlit in background, return process."""
    streamlit_bin = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../venv/bin/streamlit"
    )
    proc = subprocess.Popen(
        [streamlit_bin, "run", path,
         "--server.port", "8501",
         "--server.headless", "false",
         "--browser.gatherUsageStats", "false"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc
