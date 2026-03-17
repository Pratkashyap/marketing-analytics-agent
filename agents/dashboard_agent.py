"""
Dashboard Agent — Warner Bros. Singapore Marketing Analytics
Clean, professional Streamlit dashboard. Light theme. WBD branding.

Tabs:
  1. Agent Chat        — live 7-agent pipeline
  2. Performance       — KPIs, trends, platform, ROAS vs target
  3. Creative Health   — format performance, fatigue, heatmap
  4. Data Explorer     — direct SQL on live DuckDB

Sidebar: Quick Queries panel (auto-sends on click)
"""

import os
import sys
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

DB_PATH       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/marketing_analytics.duckdb")
DASHBOARD_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../dashboard_app.py")

DASHBOARD_QUESTIONS = [
    {
        "key":     "focus",
        "prompt":  "What should the dashboard focus on?",
        "options": [
            "1. Overall portfolio (all business lines)",
            "2. Single business line deep-dive",
            "3. Platform comparison",
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
        "prompt":  "Which business line? (only if option 2 above)",
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
    "1": "portfolio", "2": "business_line",
    "3": "platform",  "4": "creative", "5": "executive",
}
PERIOD_MAP = {
    "1": "last_7",  "2": "last_30",
    "3": "march",   "4": "last_90",
}
BL_MAP = {
    "1": "Theatrical",        "2": "Max Streaming",
    "3": "Home Entertainment","4": "WB Games",
    "5": "Licensing & Merch", "0": None,
}


def generate_dashboard(config: dict) -> str:
    """Write dashboard_app.py and return its path."""

    # Load base64 logos at generation time so they're baked into dashboard_app.py
    try:
        from assets.logo_b64 import WBD_SHIELD_B64, WBD_HORIZ_B64
    except ImportError:
        WBD_SHIELD_B64 = ""
        WBD_HORIZ_B64  = ""

    code = '''"""
Marketing Analytics Dashboard — Warner Bros. Discovery Singapore
Clean professional dashboard | 7-Agent AI Pipeline
"""
import os, sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import duckdb

_ROOT = os.path.abspath(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

DB_PATH = os.path.join(_ROOT, "data", "marketing_analytics.duckdb")

# ── WBD Logo (baked in at generation time) ────────────────────
WBD_HORIZ_B64  = "''' + WBD_HORIZ_B64 + '''"
WBD_SHIELD_B64 = "''' + WBD_SHIELD_B64 + '''"

# ── Colours ──────────────────────────────────────────────────
NAVY   = "#003087"
GOLD   = "#B8860B"
BLUE   = "#3B5BDB"
WHITE  = "#FFFFFF"
BG     = "#F8F9FC"
BORDER = "#E2E8F0"
TEXT   = "#0F172A"
MUTED  = "#64748B"
GREEN  = "#16A34A"
RED    = "#DC2626"
AMBER  = "#D97706"

st.set_page_config(
    page_title="Marketing Analytics | WBD Singapore",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .stApp { background-color: #F8F9FC; }
  .block-container { padding-top: 1rem; }
  #MainMenu, footer, header { visibility: hidden; }

  section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E2E8F0;
  }
  section[data-testid="stSidebar"] .block-container { padding-top: 0; }

  .stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-radius: 6px;
    border: 1px solid #E2E8F0;
    padding: 3px;
    gap: 2px;
  }
  .stTabs [data-baseweb="tab"] {
    color: #64748B;
    font-weight: 600;
    font-size: 13px;
    border-radius: 4px;
    padding: 7px 18px;
    background: transparent;
  }
  .stTabs [aria-selected="true"] {
    background: #003087 !important;
    color: #FFFFFF !important;
  }

  .kpi { background: #FFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px 16px; }
  .kpi-label { color: #64748B; font-size: 11px; font-weight: 600; letter-spacing: .8px; text-transform: uppercase; margin-bottom: 5px; }
  .kpi-value { color: #003087; font-size: 24px; font-weight: 800; line-height: 1; }
  .kpi-delta { font-size: 11px; margin-top: 4px; }
  .kpi-up   { color: #16A34A; }
  .kpi-down { color: #DC2626; }

  .sec { font-size: 14px; font-weight: 700; color: #0F172A;
         border-left: 3px solid #003087; padding-left: 9px;
         margin: 20px 0 10px; }

  .stButton > button {
    background: #F8F9FC;
    border: 1px solid #E2E8F0;
    color: #0F172A;
    border-radius: 5px;
    font-size: 12px;
    text-align: left;
    padding: 6px 10px;
    width: 100%;
    font-weight: 500;
    transition: all 0.15s;
  }
  .stButton > button:hover {
    border-color: #003087;
    color: #003087;
    background: #EEF2FF;
  }

  .chat-user {
    background: #EEF2FF; border: 1px solid #C7D2FE;
    border-radius: 10px 10px 2px 10px;
    padding: 10px 14px; margin: 6px 0;
    color: #1E3A8A; font-size: 14px;
  }
  .chat-agent {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-radius: 10px 10px 10px 2px;
    padding: 10px 14px; margin: 6px 0;
    color: #0F172A; font-size: 14px;
  }
  .pipeline-step {
    border-left: 2px solid #C7D2FE;
    padding: 4px 8px; margin: 2px 0;
    border-radius: 0 4px 4px 0;
    font-size: 11px; color: #64748B;
    font-family: monospace; background: #F8F9FC;
  }
  .pipeline-done { border-left-color: #16A34A !important; color: #16A34A !important; }

  .stTextInput input, .stTextArea textarea {
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
    background: #FFFFFF !important;
    color: #0F172A !important;
  }
  .stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #003087 !important;
    box-shadow: 0 0 0 2px rgba(0,48,135,0.1) !important;
  }

  .agent-pill {
    display: inline-block;
    background: #EEF2FF; border: 1px solid #C7D2FE;
    border-radius: 12px; padding: 2px 10px;
    font-size: 11px; color: #003087; font-weight: 600;
    margin: 2px 0; line-height: 1.8;
  }

  .stDataFrame { border-radius: 8px; overflow: hidden; }

  /* Form submit button — primary style */
  div[data-testid="stForm"] .stFormSubmitButton > button[kind="primaryFormSubmit"] {
    background: #003087 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px !important;
    border-radius: 6px !important;
  }
  div[data-testid="stForm"] .stFormSubmitButton > button[kind="primaryFormSubmit"]:hover {
    background: #00247a !important;
  }
</style>
""", unsafe_allow_html=True)

# ── WBD Header ────────────────────────────────────────────────
if WBD_HORIZ_B64:
    st.markdown(
        f\'\'\'<div style="margin-bottom:20px;">
  <img src="data:image/svg+xml;base64,{WBD_HORIZ_B64}"
       style="height:60px; display:block; border-radius:4px;" />
</div>\'\'\',
        unsafe_allow_html=True)
else:
    st.markdown("""
<div style="background:#003087; padding:16px 24px; border-radius:4px; margin-bottom:20px;">
  <span style="color:#FFFFFF; font-size:20px; font-weight:800; letter-spacing:1px;">
    WARNER BROS. DISCOVERY
  </span>
  <span style="color:rgba(255,255,255,0.6); font-size:12px; margin-left:16px;">
    Singapore · Marketing Analytics
  </span>
</div>""", unsafe_allow_html=True)


# ── DB helper ─────────────────────────────────────────────────
@st.cache_data(ttl=60)
def run_query(sql: str) -> pd.DataFrame:
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        df  = con.execute(sql).df()
        con.close()
        return df
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})


# ── Quick Queries ─────────────────────────────────────────────
QUICK_QUERIES = [
    ("ROAS vs Targets",        "How are all business lines performing vs ROAS target this month?"),
    ("Creative Fatigue",       "Which creatives show fatigue and need urgent refresh?"),
    ("Budget Optimisation",    "Rebalance my budget to maximise blended ROAS across all platforms"),
    ("Top Campaigns",          "Show me the top 10 campaigns by ROAS this month"),
    ("Underperformers",        "Which campaigns are below their ROAS target?"),
    ("Platform Breakdown",     "Compare Meta vs Google vs TikTok vs YouTube performance"),
    ("Theatrical Performance", "How is the Theatrical business line performing this month?"),
    ("WB Games Analysis",      "Analyse WB Games campaign performance and creative formats"),
    ("Weekly Trend",           "Show me week-over-week performance trend for the last 30 days"),
    ("TikTok Deep Dive",       "Give me a full TikTok performance analysis with recommendations"),
    ("Full Performance Review","Give me a complete marketing performance review across everything"),
]

# ── Session state ─────────────────────────────────────────────
defaults = {
    "messages":     [],
    "pipeline_log": [],
    "pending_query": "",
    "auto_send":    False,
    "running":      False,
    "stop":         False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    # WBD Shield logo
    if WBD_SHIELD_B64:
        st.markdown(
            f\'\'\'<div style="text-align:center; padding:16px 0 12px;">
  <img src="data:image/svg+xml;base64,{WBD_SHIELD_B64}"
       style="height:56px; display:inline-block;" />
</div>\'\'\',
            unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:4px 0 8px; border-bottom:1px solid #E2E8F0; margin-bottom:10px;">
      <div style="font-size:11px; font-weight:700; color:#003087; letter-spacing:1px;
           text-transform:uppercase;">Quick Queries</div>
      <div style="font-size:10px; color:#94A3B8; margin-top:2px;">Click to run instantly</div>
    </div>
    """, unsafe_allow_html=True)

    for label, query in QUICK_QUERIES:
        if st.button(label, key=f"qq_{label}"):
            st.session_state["pending_query"] = query
            st.session_state["auto_send"]     = True
            st.rerun()

    st.markdown("""
    <div style="margin-top:20px; padding-top:14px; border-top:1px solid #E2E8F0;">
      <div style="font-size:10px; color:#94A3B8; font-weight:600; letter-spacing:.8px;
           text-transform:uppercase; margin-bottom:8px;">Active Agents</div>
    </div>
    """, unsafe_allow_html=True)

    for label in ["Orchestrator", "Data Agent", "Analysis Hub",
                  "Creative Analyst", "Optimizer", "Dashboard", "Quality Critic"]:
        st.markdown(f\'<div class="agent-pill">{label}</div>\', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Agent Chat",
    "Performance Dashboard",
    "Creative Health",
    "Data Explorer",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — AGENT CHAT
# ══════════════════════════════════════════════════════════════
with tab1:
    col_chat, col_pipe = st.columns([3, 1])

    with col_chat:
        st.markdown(\'<div class="sec">Ask your marketing analytics team</div>\',
                    unsafe_allow_html=True)

        # ── Render conversation history ──────────────────────
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f\'<div class="chat-user"><strong>You</strong><br>{msg["content"]}</div>\',
                    unsafe_allow_html=True)
            else:
                content = msg["content"].replace("\\n", "<br>")
                st.markdown(
                    f\'<div class="chat-agent"><strong>Agent Team</strong><br>{content}</div>\',
                    unsafe_allow_html=True)

        # ── Auto-send from quick queries (bypass form) ───────
        if st.session_state.get("auto_send") and st.session_state.get("pending_query"):
            query_to_send = st.session_state["pending_query"]
            st.session_state["auto_send"]     = False
            st.session_state["pending_query"] = ""
            st.session_state["stop"]          = False
            st.session_state.messages.append({"role": "user", "content": query_to_send})
            st.session_state.pipeline_log = []

            with st.spinner("Agent team processing..."):
                try:
                    from agents.orchestrator import Orchestrator
                    steps = []

                    def on_status(agent, event, detail=""):
                        if st.session_state.get("stop"):
                            raise InterruptedError("Stopped by user.")
                        labels = {
                            "orchestrator":    "Orchestrator",
                            "data_agent":      "Data Agent",
                            "analysis_agent":  "Analysis Hub",
                            "creative_analyst":"Creative Analyst",
                            "optimizer":       "Optimizer",
                            "critic":          "Quality Critic",
                        }
                        label = labels.get(agent, agent.replace("_", " ").title())
                        step  = f"{label}  ·  {event}"
                        if detail:
                            step += f"  —  {detail[:80]}"
                        steps.append(step)

                    result   = Orchestrator().run(query_to_send, verbose=False, on_status=on_status)
                    response = (result.get("response")
                                or result.get("analysis")
                                or result.get("data_summary", "No response."))
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.pipeline_log = steps
                except InterruptedError:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": "Pipeline stopped by user."})
                    st.session_state["stop"] = False
                except Exception as e:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"Agent error: {e}"})
            st.rerun()

        # ── Chat form ────────────────────────────────────────
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "question",
                placeholder="e.g. Which platforms are underperforming vs ROAS target this month?",
                label_visibility="collapsed",
            )
            col_send, col_stop, col_clear = st.columns([4, 1, 1])
            with col_send:
                submitted = st.form_submit_button(
                    "Send to Agent Team",
                    use_container_width=True,
                    type="primary",
                )
            with col_stop:
                stopped = st.form_submit_button(
                    "Stop",
                    use_container_width=True,
                )
            with col_clear:
                cleared = st.form_submit_button(
                    "Clear",
                    use_container_width=True,
                )

        if stopped:
            st.session_state["stop"] = True
            st.info("Stop signal sent. Pipeline will halt at next checkpoint.")

        if cleared:
            st.session_state.messages    = []
            st.session_state.pipeline_log = []
            st.rerun()

        if submitted and user_input.strip():
            query_to_send = user_input.strip()
            st.session_state["stop"] = False
            st.session_state.messages.append({"role": "user", "content": query_to_send})
            st.session_state.pipeline_log = []

            with st.spinner("Agent team processing..."):
                try:
                    from agents.orchestrator import Orchestrator
                    steps = []

                    def on_status_form(agent, event, detail=""):
                        if st.session_state.get("stop"):
                            raise InterruptedError("Stopped by user.")
                        labels = {
                            "orchestrator":    "Orchestrator",
                            "data_agent":      "Data Agent",
                            "analysis_agent":  "Analysis Hub",
                            "creative_analyst":"Creative Analyst",
                            "optimizer":       "Optimizer",
                            "critic":          "Quality Critic",
                        }
                        label = labels.get(agent, agent.replace("_", " ").title())
                        step  = f"{label}  ·  {event}"
                        if detail:
                            step += f"  —  {detail[:80]}"
                        steps.append(step)

                    result   = Orchestrator().run(query_to_send, verbose=False, on_status=on_status_form)
                    response = (result.get("response")
                                or result.get("analysis")
                                or result.get("data_summary", "No response."))
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.pipeline_log = steps
                except InterruptedError:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": "Pipeline stopped by user."})
                    st.session_state["stop"] = False
                except Exception as e:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"Agent error: {e}"})
            st.rerun()

    with col_pipe:
        st.markdown(\'<div class="sec">Pipeline</div>\', unsafe_allow_html=True)
        if len(st.session_state.pipeline_log) > 0:
            for step in st.session_state.pipeline_log:
                cls = "pipeline-done" if any(
                    x in step.lower() for x in ["done", "approved", "complete"]) else "pipeline-step"
                st.markdown(f\'<div class="{cls}">{step}</div>\', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="color:#94A3B8; font-size:12px; padding:12px 0; line-height:1.8;">
              Pipeline steps will appear here once you send a question.
            </div>
            """, unsafe_allow_html=True)
            for a in ["Orchestrator", "Data Agent", "Analysis Hub",
                      "Creative Analyst", "Optimizer", "Quality Critic"]:
                st.markdown(f\'<div class="agent-pill">{a}</div>\', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — PERFORMANCE DASHBOARD
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown(\'<div class="sec">Key Performance Indicators — Last 30 Days</div>\',
                unsafe_allow_html=True)

    kpi_df = run_query("""
        SELECT ROUND(SUM(spend),0) AS total_spend,
               ROUND(SUM(revenue),0) AS total_revenue,
               ROUND(SUM(revenue)/NULLIF(SUM(spend),0),2) AS blended_roas,
               SUM(impressions) AS impressions,
               SUM(clicks) AS clicks,
               SUM(conversions) AS conversions
        FROM fact_performance
        WHERE date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
    """)
    kpi_prev = run_query("""
        SELECT ROUND(SUM(revenue)/NULLIF(SUM(spend),0),2) AS blended_roas
        FROM fact_performance
        WHERE date >= CAST(CURRENT_DATE - INTERVAL 60 DAY AS VARCHAR)
          AND date <  CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
    """)

    if len(kpi_df) > 0 and "error" not in kpi_df.columns:
        row  = kpi_df.iloc[0]
        prev = kpi_prev.iloc[0] if len(kpi_prev) > 0 else None

        def fmt(n):
            n = float(n or 0)
            if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
            if n >= 1_000:     return f"{n/1_000:.0f}K"
            return str(int(n))

        roas_val   = float(row.blended_roas or 0)
        roas_delta = ""
        if prev is not None and prev.blended_roas:
            diff = roas_val - float(prev.blended_roas or 0)
            cls  = "kpi-up" if diff >= 0 else "kpi-down"
            sign = "+" if diff >= 0 else ""
            roas_delta = f\'<div class="kpi-delta {cls}">{sign}{diff:.2f}x vs prev 30d</div>\'

        cols = st.columns(6)
        for col, label, val, delta in zip(cols, [
            "Total Spend", "Total Revenue", "Blended ROAS", "Impressions", "Clicks", "Conversions"
        ], [
            f"SGD {fmt(row.total_spend)}",
            f"SGD {fmt(row.total_revenue)}",
            f"{roas_val:.2f}x",
            fmt(row.impressions),
            fmt(row.clicks),
            fmt(row.conversions),
        ], [
            "", "", roas_delta, "", "", ""
        ]):
            with col:
                st.markdown(
                    f\'<div class="kpi"><div class="kpi-label">{label}</div>\'
                    f\'<div class="kpi-value">{val}</div>{delta}</div>\',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(\'<div class="sec">Daily Spend & ROAS Trend</div>\', unsafe_allow_html=True)
        trend_df = run_query("""
            SELECT date,
                   ROUND(SUM(spend),0) AS spend,
                   ROUND(SUM(revenue)/NULLIF(SUM(spend),0),2) AS roas
            FROM fact_performance
            WHERE date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
            GROUP BY date ORDER BY date
        """)
        if len(trend_df) > 0 and "error" not in trend_df.columns:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=trend_df.date, y=trend_df.spend,
                name="Spend (SGD)", marker_color=NAVY, opacity=0.75, yaxis="y"))
            fig.add_trace(go.Scatter(
                x=trend_df.date, y=trend_df.roas,
                name="ROAS", line=dict(color=AMBER, width=2),
                mode="lines+markers", marker=dict(size=3), yaxis="y2"))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color=TEXT, height=290, margin=dict(l=0, r=0, t=0, b=0),
                legend=dict(orientation="h", y=1.08, bgcolor="rgba(0,0,0,0)", font_size=11),
                yaxis=dict(title="Spend SGD", gridcolor=BORDER, color=MUTED),
                yaxis2=dict(title="ROAS", overlaying="y", side="right",
                            color=AMBER, gridcolor="rgba(0,0,0,0)"),
                xaxis=dict(gridcolor=BORDER),
            )
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(\'<div class="sec">Spend by Platform</div>\', unsafe_allow_html=True)
        plat_df = run_query("""
            SELECT platform, ROUND(SUM(spend),0) AS spend
            FROM fact_performance
            WHERE date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
            GROUP BY platform ORDER BY spend DESC
        """)
        if len(plat_df) > 0 and "error" not in plat_df.columns:
            fig = go.Figure(go.Pie(
                labels=plat_df.platform, values=plat_df.spend, hole=0.5,
                marker=dict(colors=[NAVY, "#3B5BDB", "#6B8EE0", "#A5B4FC"],
                            line=dict(color=WHITE, width=2)),
                textfont_color=TEXT,
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font_color=TEXT,
                height=290, margin=dict(l=0, r=0, t=0, b=0),
                legend=dict(font_size=11, bgcolor="rgba(0,0,0,0)"),
                annotations=[dict(text="Spend", x=0.5, y=0.5,
                                  font_size=13, font_color=MUTED, showarrow=False)],
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown(\'<div class="sec">ROAS vs Target by Business Line</div>\', unsafe_allow_html=True)
    roas_df = run_query("""
        SELECT bl.business_line_name AS business_line,
               ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0),2) AS actual_roas
        FROM fact_performance f
        JOIN dim_business_line bl ON f.business_line_id = bl.business_line_id
        WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
        GROUP BY bl.business_line_name ORDER BY actual_roas DESC
    """)
    ROAS_TARGETS = {"Theatrical": 3.5, "Max Streaming": 4.0, "Home Entertainment": 3.0,
                    "WB Games": 3.5, "Licensing & Merch": 2.5}
    if len(roas_df) > 0 and "error" not in roas_df.columns:
        roas_df["target"] = roas_df["business_line"].map(ROAS_TARGETS).fillna(3.0)
        roas_df["gap"]    = roas_df["actual_roas"] - roas_df["target"]
        colors = [GREEN if g >= 0 else RED for g in roas_df["gap"]]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=roas_df["business_line"], x=roas_df["actual_roas"], orientation="h",
            name="Actual ROAS", marker_color=colors,
            text=[f"{v:.2f}x" for v in roas_df["actual_roas"]],
            textposition="outside", textfont_color=TEXT,
        ))
        fig.add_trace(go.Scatter(
            y=roas_df["business_line"], x=roas_df["target"], mode="markers",
            name="Target", marker=dict(symbol="line-ns", size=14,
                                       color=AMBER, line=dict(width=2, color=AMBER)),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color=TEXT, height=270, margin=dict(l=0, r=50, t=0, b=0),
            xaxis=dict(title="ROAS", gridcolor=BORDER),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            legend=dict(orientation="h", y=1.08, bgcolor="rgba(0,0,0,0)"),
            bargap=0.35,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(\'<div class="sec">Top 10 Campaigns by ROAS</div>\', unsafe_allow_html=True)
    camp_df = run_query("""
        SELECT c.campaign_name,
               bl.business_line_name AS business_line,
               p.platform_name       AS platform,
               ROUND(SUM(f.spend),0)   AS spend,
               ROUND(SUM(f.revenue),0) AS revenue,
               ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0),2) AS roas
        FROM fact_performance f
        JOIN dim_campaign      c  ON f.campaign_id      = c.campaign_id
        JOIN dim_business_line bl ON f.business_line_id = bl.business_line_id
        JOIN dim_platform      p  ON f.platform_id      = p.platform_id
        WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
        GROUP BY c.campaign_name, bl.business_line_name, p.platform_name
        HAVING SUM(f.spend) > 1000
        ORDER BY roas DESC LIMIT 10
    """)
    if len(camp_df) > 0 and "error" not in camp_df.columns:
        d = camp_df.copy()
        d["spend"]   = d["spend"].apply(lambda x: f"SGD {int(x):,}")
        d["revenue"] = d["revenue"].apply(lambda x: f"SGD {int(x):,}")
        d["roas"]    = d["roas"].apply(lambda x: f"{x:.2f}x")
        d.columns    = ["Campaign", "Business Line", "Platform", "Spend", "Revenue", "ROAS"]
        st.dataframe(d, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — CREATIVE HEALTH
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown(\'<div class="sec">Creative Format Performance — Last 30 Days</div>\',
                unsafe_allow_html=True)

    fmt_df = run_query("""
        SELECT cr.format,
               ROUND(AVG(f.ctr)*100,2) AS avg_ctr,
               ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0),2) AS roas,
               ROUND(SUM(f.spend),0)   AS spend,
               COUNT(DISTINCT cr.creative_id) AS num_creatives
        FROM fact_performance f
        JOIN dim_creative cr ON f.creative_id = cr.creative_id
        WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
        GROUP BY cr.format ORDER BY roas DESC
    """)
    CTR_BENCH = {"Video 15s": 3.0, "Video 30s": 2.3, "Static Image": 1.8,
                 "Carousel": 2.2, "Story": 2.0, "Reel": 2.6, "YouTube Pre-roll": 1.9}

    ca, cb = st.columns(2)
    with ca:
        if len(fmt_df) > 0 and "error" not in fmt_df.columns:
            fig = go.Figure(go.Bar(
                x=fmt_df["format"], y=fmt_df["roas"],
                marker_color=NAVY, opacity=0.85,
                text=[f"{v:.2f}x" for v in fmt_df["roas"]],
                textposition="outside", textfont_color=TEXT,
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color=TEXT, height=270, margin=dict(l=0, r=0, t=30, b=0),
                title=dict(text="ROAS by Format", font_color=TEXT, font_size=13),
                xaxis=dict(gridcolor=BORDER, tickangle=-20),
                yaxis=dict(title="ROAS", gridcolor=BORDER),
            )
            st.plotly_chart(fig, use_container_width=True)

    with cb:
        if len(fmt_df) > 0 and "error" not in fmt_df.columns:
            fmt_df["benchmark"]    = fmt_df["format"].map(CTR_BENCH).fillna(2.0)
            fmt_df["ctr_vs_bench"] = (fmt_df["avg_ctr"] - fmt_df["benchmark"]).round(2)
            c_list = [GREEN if v >= 0 else RED for v in fmt_df["ctr_vs_bench"]]
            fig = go.Figure(go.Bar(
                x=fmt_df["format"], y=fmt_df["ctr_vs_bench"],
                marker_color=c_list,
                text=[f"{v:+.2f}%" for v in fmt_df["ctr_vs_bench"]],
                textposition="outside", textfont_color=TEXT,
            ))
            fig.add_hline(y=0, line_color=AMBER, line_width=1.2)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color=TEXT, height=270, margin=dict(l=0, r=0, t=30, b=0),
                title=dict(text="CTR vs Industry Benchmark", font_color=TEXT, font_size=13),
                xaxis=dict(gridcolor=BORDER, tickangle=-20),
                yaxis=dict(title="CTR Delta (%)", gridcolor=BORDER),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown(\'<div class="sec">Creative Fatigue Analysis</div>\', unsafe_allow_html=True)
    fatigue_df = run_query("""
        SELECT cr.creative_name,
               cr.format,
               p.platform_name AS platform,
               COUNT(DISTINCT f.date) AS days_running,
               ROUND(AVG(CASE WHEN f.date <= CAST(CURRENT_DATE - INTERVAL 45 DAY AS VARCHAR)
                              THEN f.ctr END)*100,2) AS early_ctr,
               ROUND(AVG(CASE WHEN f.date >= CAST(CURRENT_DATE - INTERVAL 14 DAY AS VARCHAR)
                              THEN f.ctr END)*100,2) AS recent_ctr,
               ROUND(SUM(f.spend),0) AS total_spend
        FROM fact_performance f
        JOIN dim_creative cr ON f.creative_id = cr.creative_id
        JOIN dim_platform  p ON f.platform_id = p.platform_id
        WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 90 DAY AS VARCHAR)
        GROUP BY cr.creative_name, cr.format, p.platform_name
        HAVING early_ctr IS NOT NULL AND recent_ctr IS NOT NULL
           AND COUNT(DISTINCT f.date) >= 30
        ORDER BY (recent_ctr - early_ctr) ASC
        LIMIT 15
    """)
    if len(fatigue_df) > 0 and "error" not in fatigue_df.columns:
        fatigue_df["ctr_drop_pct"] = (
            (fatigue_df["recent_ctr"] - fatigue_df["early_ctr"])
            / fatigue_df["early_ctr"].replace(0, 0.001) * 100
        ).round(1)
        fatigue_df["status"] = fatigue_df["ctr_drop_pct"].apply(
            lambda x: "URGENT" if x < -20 else ("MONITOR" if x < -10 else "HEALTHY"))
        disp = fatigue_df[["creative_name", "format", "platform", "days_running",
                            "early_ctr", "recent_ctr", "ctr_drop_pct", "status", "total_spend"]].copy()
        disp.columns = ["Creative", "Format", "Platform", "Days Live",
                        "Early CTR%", "Recent CTR%", "CTR Drop%", "Status", "Spend SGD"]
        disp["Spend SGD"] = disp["Spend SGD"].apply(lambda x: f"{int(x):,}")
        st.dataframe(disp, use_container_width=True, hide_index=True)

        urgent = fatigue_df[fatigue_df["ctr_drop_pct"] < -20]
        if len(urgent) > 0:
            st.warning(f"{len(urgent)} creative(s) need urgent refresh — CTR has dropped >20% from early performance. Recommend replacing within 7 days.")

    st.markdown(\'<div class="sec">CTR by Platform x Format</div>\', unsafe_allow_html=True)
    heat_df = run_query("""
        SELECT p.platform_name AS platform, cr.format,
               ROUND(AVG(f.ctr)*100,2) AS avg_ctr
        FROM fact_performance f
        JOIN dim_creative cr ON f.creative_id = cr.creative_id
        JOIN dim_platform  p ON f.platform_id = p.platform_id
        WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
        GROUP BY p.platform_name, cr.format
    """)
    if len(heat_df) > 0 and "error" not in heat_df.columns:
        pivot = heat_df.pivot(index="platform", columns="format", values="avg_ctr").fillna(0)
        fig = go.Figure(go.Heatmap(
            z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
            colorscale=[[0, "#EEF2FF"], [0.5, "#3B5BDB"], [1, "#003087"]],
            text=[[f"{v:.2f}%" for v in row] for row in pivot.values],
            texttemplate="%{text}", textfont_size=11, showscale=True,
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color=TEXT,
            height=220, margin=dict(l=0, r=0, t=0, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 4 — DATA EXPLORER
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown(\'<div class="sec">SQL Query on Live Data</div>\', unsafe_allow_html=True)

    EXAMPLES = {
        "Spend & ROAS by Platform":
            "SELECT p.platform_name, ROUND(SUM(f.spend),0) AS spend,\\n"
            "       ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0),2) AS roas\\n"
            "FROM fact_performance f\\n"
            "JOIN dim_platform p ON f.platform_id = p.platform_id\\n"
            "WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)\\n"
            "GROUP BY p.platform_name ORDER BY roas DESC",

        "Creative Format CTR":
            "SELECT cr.format, ROUND(AVG(f.ctr)*100,2) AS avg_ctr,\\n"
            "       COUNT(DISTINCT cr.creative_id) AS num_creatives\\n"
            "FROM fact_performance f\\n"
            "JOIN dim_creative cr ON f.creative_id = cr.creative_id\\n"
            "WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)\\n"
            "GROUP BY cr.format ORDER BY avg_ctr DESC",

        "Business Line ROAS":
            "SELECT bl.business_line_name,\\n"
            "       ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0),2) AS actual_roas\\n"
            "FROM fact_performance f\\n"
            "JOIN dim_business_line bl ON f.business_line_id = bl.business_line_id\\n"
            "WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)\\n"
            "GROUP BY bl.business_line_name ORDER BY actual_roas DESC",

        "Top Campaigns by Spend":
            "SELECT c.campaign_name, ROUND(SUM(f.spend),0) AS spend,\\n"
            "       ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0),2) AS roas\\n"
            "FROM fact_performance f\\n"
            "JOIN dim_campaign c ON f.campaign_id = c.campaign_id\\n"
            "WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)\\n"
            "GROUP BY c.campaign_name ORDER BY spend DESC LIMIT 20",

        "Daily Trend Last 14 Days":
            "SELECT date, ROUND(SUM(spend),0) AS spend,\\n"
            "       ROUND(SUM(revenue)/NULLIF(SUM(spend),0),2) AS roas\\n"
            "FROM fact_performance\\n"
            "WHERE date >= CAST(CURRENT_DATE - INTERVAL 14 DAY AS VARCHAR)\\n"
            "GROUP BY date ORDER BY date DESC",
    }

    ex_choice = st.selectbox("Load example", ["Write your own"] + list(EXAMPLES.keys()))
    default   = EXAMPLES.get(ex_choice, "") if ex_choice != "Write your own" else ""
    sql_in    = st.text_area("SQL", value=default, height=150,
                              placeholder="SELECT ... FROM fact_performance WHERE ...")

    if st.button("Run Query"):
        if sql_in.strip():
            with st.spinner("Running..."):
                res = run_query(sql_in.strip())
            if "error" in res.columns:
                st.error(f"Error: {res[\'error\'].iloc[0]}")
            elif len(res) > 0:
                st.success(f"{len(res)} rows returned")
                st.dataframe(res, use_container_width=True, hide_index=True)
                st.download_button("Download CSV",
                                   res.to_csv(index=False).encode("utf-8"),
                                   "result.csv", "text/csv")
            else:
                st.info("No rows returned.")

    st.markdown(\'<div class="sec">Schema Reference</div>\', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    schema = {
        "fact_performance": ["date", "campaign_id", "platform_id", "business_line_id",
                             "creative_id", "spend", "revenue", "impressions",
                             "clicks", "conversions", "ctr", "cpm", "cpc"],
        "dim_campaign":     ["campaign_id (PK)", "campaign_name", "campaign_type",
                             "objective", "business_line_id"],
        "dim_platform":     ["platform_id (PK)", "platform_name"],
        "dim_business_line":["business_line_id (PK)", "business_line_name"],
        "dim_creative":     ["creative_id (PK)", "creative_name", "format",
                             "platform_id", "business_line_id"],
    }
    for i, (tbl, cols) in enumerate(schema.items()):
        with [s1, s2, s3][i % 3]:
            rows = "".join(
                f\'<div style="color:#64748B;font-size:11px;font-family:monospace;\'
                f\'padding:1px 0;">{c}</div>\' for c in cols)
            st.markdown(
                f\'<div style="background:#FFFFFF;border:1px solid #E2E8F0;\'
                f\'border-radius:6px;padding:12px;margin-bottom:10px;">\'
                f\'<div style="color:#003087;font-size:12px;font-weight:700;\'
                f\'margin-bottom:6px;">{tbl}</div>{rows}</div>\',
                unsafe_allow_html=True)
'''

    with open(DASHBOARD_OUT, "w") as f:
        f.write(code)

    return DASHBOARD_OUT


def launch_dashboard(path: str) -> None:
    """Launch the Streamlit dashboard."""
    streamlit_bin = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../venv/bin/streamlit"
    )
    if not os.path.exists(streamlit_bin):
        streamlit_bin = "streamlit"

    subprocess.Popen(
        [streamlit_bin, "run", path,
         "--server.port=8501",
         "--server.headless=false",
         "--browser.gatherUsageStats=false"],
        cwd=os.path.dirname(path),
    )
