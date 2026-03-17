"""
Marketing Analytics Dashboard — Warner Bros. Discovery Singapore
"""
import os, sys, time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import duckdb

_ROOT = os.path.abspath(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

DB_PATH = os.path.join(_ROOT, "data", "marketing_analytics.duckdb")

# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="WBD Marketing Analytics", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp { background:#F8F9FC !important; }
.block-container { padding-top:0.8rem !important; }
#MainMenu,footer,header { visibility:hidden; }
section[data-testid="stSidebar"] { background:#fff; border-right:1px solid #E2E8F0; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background:#fff; border:1px solid #E2E8F0; border-radius:6px; padding:2px; gap:2px;
}
.stTabs [data-baseweb="tab"] {
    color:#64748B; font-weight:600; font-size:13px;
    border-radius:4px; padding:6px 18px; background:transparent;
}
.stTabs [aria-selected="true"] { background:#003087 !important; color:#fff !important; }

/* KPI cards */
.kpi { background:#fff; border:1px solid #E2E8F0; border-radius:8px; padding:16px; }
.kpi-label { color:#64748B; font-size:10px; font-weight:700; letter-spacing:.8px;
             text-transform:uppercase; margin-bottom:4px; }
.kpi-value { color:#003087; font-size:22px; font-weight:800; line-height:1; }
.kpi-up   { color:#16A34A; font-size:11px; margin-top:3px; }
.kpi-down { color:#DC2626; font-size:11px; margin-top:3px; }

/* Section headings */
.sec { font-size:13px; font-weight:700; color:#0F172A;
       border-left:3px solid #003087; padding-left:8px; margin:18px 0 8px; }

/* Chat bubbles */
.chat-user {
    background:#EEF2FF; border:1px solid #C7D2FE;
    border-radius:12px 12px 2px 12px; padding:10px 14px; margin:6px 0;
    color:#1E3A8A; font-size:14px; line-height:1.55;
}
.chat-agent {
    background:#fff; border:1px solid #E2E8F0;
    border-radius:12px 12px 12px 2px; padding:10px 14px; margin:6px 0;
    color:#0F172A; font-size:14px; line-height:1.55;
}

/* Sub-question suggestion cards */
.subq-card {
    background:#fff; border:1px solid #C7D2FE; border-radius:8px;
    padding:10px 14px; margin:4px 0; color:#1E3A8A; font-size:13px;
    cursor:pointer; transition:all 0.15s; line-height:1.4;
}
.subq-card:hover { background:#EEF2FF; border-color:#818CF8; }

/* Pipeline */
.ps { border-left:2px solid #C7D2FE; padding:4px 8px; margin:2px 0;
      font-size:11px; color:#64748B; font-family:monospace; background:#F8F9FC;
      border-radius:0 4px 4px 0; }
.pd { border-left-color:#16A34A !important; color:#16A34A !important; }
.timer-total {
    background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px;
    padding:8px 12px; font-size:12px; font-weight:700; color:#16A34A;
    margin:8px 0 4px; text-align:center;
}
.apill {
    display:inline-block; background:#EEF2FF; border:1px solid #C7D2FE;
    border-radius:12px; padding:2px 10px; font-size:11px;
    color:#003087; font-weight:600; margin:2px 0; line-height:1.8;
}
/* Waiting banner */
.wait-banner {
    background:#FEF9C3; border:1px solid #FDE047; border-radius:8px;
    padding:12px 16px; color:#713F12; font-size:13px; margin:8px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div style="background:#003087;padding:14px 22px;border-radius:6px;
     margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;">
  <div>
    <span style="color:#fff;font-size:20px;font-weight:800;letter-spacing:1px;">
      WARNER BROS. DISCOVERY
    </span>
    <span style="color:rgba(255,255,255,0.55);font-size:12px;margin-left:14px;">
      Singapore · Marketing Analytics
    </span>
  </div>
  <span style="color:rgba(255,255,255,0.45);font-size:11px;">7 Agents · Live Data</span>
</div>""", unsafe_allow_html=True)

# ── DB helper ─────────────────────────────────────────────────
@st.cache_data(ttl=60)
def qry(sql):
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        df  = con.execute(sql).df()
        con.close()
        return df
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})

def fmt_n(n):
    n = float(n or 0)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.0f}K"
    return str(int(n))

NAVY="#003087"; GOLD="#D97706"; GREEN="#16A34A"; RED="#DC2626"
BORDER="#E2E8F0"; TEXT="#0F172A"; MUTED="#64748B"; WHITE="#FFFFFF"

ROAS_TARGETS = {"Theatrical":3.5,"Max Streaming":4.0,
                "Home Entertainment":3.0,"WB Games":3.5,"Licensing & Merch":2.5}

# ── Quick query sets (3 questions per category) ───────────────
QUICK_QUERIES = {
    "ROAS vs Targets": [
        "How are all business lines performing vs ROAS target this month?",
        "Which business lines are below their ROAS target and by how much?",
        "Rank all 5 business lines by ROAS gap and flag which need immediate action",
    ],
    "Creative Fatigue": [
        "Which creatives show fatigue and need urgent refresh?",
        "Show creatives with more than 20% CTR decline in the last 30 days",
        "Which ad formats are fatiguing fastest across platforms?",
    ],
    "Budget Optimisation": [
        "Rebalance my budget to maximise blended ROAS across all platforms",
        "Which campaigns should I pause and reallocate budget from?",
        "What is the optimal budget split across Meta, Google, TikTok and YouTube?",
    ],
    "Top Campaigns": [
        "Show me the top 10 campaigns by ROAS this month",
        "Which campaigns have the best ROI and should get more budget?",
        "Compare top performing campaigns across all business lines",
    ],
    "Underperformers": [
        "Which campaigns are below their ROAS target?",
        "List campaigns spending over SGD 10K but delivering under 2x ROAS",
        "What are the biggest budget drains in our portfolio right now?",
    ],
    "Platform Breakdown": [
        "Compare Meta vs Google vs TikTok vs YouTube performance",
        "Which platform delivers the best ROAS and should get more budget?",
        "Break down CPM, CTR and conversion rates by platform",
    ],
    "Theatrical Performance": [
        "How is the Theatrical business line performing this month?",
        "Analyse all Theatrical campaigns vs their ROAS targets",
        "Which Theatrical creatives perform best and on which platforms?",
    ],
    "WB Games Analysis": [
        "Analyse WB Games campaign performance and creative formats",
        "Which WB Games campaigns have the best ROAS and lowest CPA?",
        "Compare WB Games performance across all platforms this month",
    ],
    "Weekly Trend": [
        "Show week-over-week performance trend for the last 30 days",
        "How has our blended ROAS trended over the past 4 weeks?",
        "Show daily spend and ROAS for last 30 days with trend analysis",
    ],
    "TikTok Deep Dive": [
        "Give me a full TikTok performance analysis with recommendations",
        "Which ad formats perform best on TikTok and what should we prioritise?",
        "Compare TikTok performance across all 5 business lines",
    ],
    "Full Performance Review": [
        "Complete marketing performance review across all business lines",
        "Give me an executive summary of our marketing performance this month",
        "Full analysis: spend efficiency, creative health and budget recommendations",
    ],
}

# ── Session state init ────────────────────────────────────────
_defaults = {
    "messages":      [],
    "pipeline_log":  [],
    "total_time":    None,
    "selected_cat":  "",      # which sidebar category is open
    "prefill_text":  "",      # text to place in the input on next render
    "do_clear_input":False,   # flag: clear input on next render
    "run_now":       "",      # query to auto-run (set by sub-question click)
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:10px 0 6px;">
      <div style="font-size:11px;font-weight:700;color:#003087;letter-spacing:1px;
           text-transform:uppercase;">Quick Queries</div>
      <div style="font-size:10px;color:#94A3B8;margin-top:2px;">
        Click a topic to see suggested questions
      </div>
    </div>
    <hr style="border:none;border-top:1px solid #E2E8F0;margin:6px 0 8px;">
    """, unsafe_allow_html=True)

    for i, cat in enumerate(QUICK_QUERIES.keys()):
        is_open = (st.session_state["selected_cat"] == cat)
        label   = f"▼  {cat}" if is_open else cat
        if st.button(label, key=f"cat{i}"):
            # toggle: if already open, close it; else open it
            st.session_state["selected_cat"] = "" if is_open else cat
            st.rerun()

    st.markdown("""
    <div style="margin-top:16px;padding-top:12px;border-top:1px solid #E2E8F0;">
      <div style="font-size:10px;color:#94A3B8;font-weight:600;letter-spacing:.8px;
           text-transform:uppercase;margin-bottom:6px;">Active Agents</div>
    </div>
    """, unsafe_allow_html=True)
    for a in ["Orchestrator","Data Agent","Analysis Hub",
              "Creative Analyst","Optimizer","Quality Critic"]:
        st.markdown(f'<div class="apill">{a}</div>', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Agent Chat", "Performance Dashboard", "Creative Health", "Data Explorer",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — AGENT CHAT
# ══════════════════════════════════════════════════════════════
with tab1:
    left, right = st.columns([3, 1])

    with left:
        st.markdown('<div class="sec">Ask your marketing analytics team</div>',
                    unsafe_allow_html=True)

        # ── PRE-RENDER: handle clear / prefill flags ──────────
        # These must run BEFORE the text_area widget is instantiated
        if st.session_state["do_clear_input"]:
            st.session_state["chat_val"] = ""
            st.session_state["do_clear_input"] = False
        elif st.session_state["prefill_text"]:
            st.session_state["chat_val"] = st.session_state.pop("prefill_text")

        # ── TEXT INPUT — key only, NO value= param ────────────
        # Using key= means Streamlit stores what the user types in
        # st.session_state["chat_val"] automatically.
        # Never pass value= here — it would override what the user typed on rerun.
        user_q = st.text_area(
            "question",
            placeholder="Type your question here, or pick a topic from the sidebar...",
            label_visibility="collapsed",
            height=90,
            key="chat_val",
        )

        # ── BUTTONS ───────────────────────────────────────────
        b1, b2 = st.columns([5, 1])
        with b1:
            send_btn  = st.button("Send to Agent Team", key="send_btn",
                                  type="primary", use_container_width=True)
        with b2:
            clear_btn = st.button("Clear", key="clear_btn",
                                  use_container_width=True)

        if clear_btn:
            st.session_state["messages"]      = []
            st.session_state["pipeline_log"]  = []
            st.session_state["total_time"]    = None
            st.session_state["do_clear_input"]= True
            st.session_state["selected_cat"]  = ""
            st.rerun()

        # ── SUB-QUESTION PANEL (below buttons) ────────────────
        cat = st.session_state["selected_cat"]
        if cat and cat in QUICK_QUERIES:
            questions = QUICK_QUERIES[cat]
            st.markdown(
                f'<div style="background:#F0F4FF;border:1px solid #C7D2FE;'
                f'border-radius:8px;padding:12px 14px;margin:10px 0 4px;">'
                f'<div style="font-size:12px;font-weight:700;color:#003087;'
                f'margin-bottom:8px;">{cat} — choose a question:</div>',
                unsafe_allow_html=True)

            for qi, q in enumerate(questions):
                short = q[:90] + "..." if len(q) > 90 else q
                if st.button(f"  {short}", key=f"subq_{qi}"):
                    # Populate text area + auto-run
                    st.session_state["prefill_text"] = q
                    st.session_state["run_now"]      = q
                    st.session_state["selected_cat"] = ""
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        # ── DETERMINE QUERY TO RUN ────────────────────────────
        query_to_run = ""
        if send_btn:
            typed = st.session_state.get("chat_val", "").strip()
            if typed:
                query_to_run = typed
        if not query_to_run and st.session_state.get("run_now"):
            query_to_run = st.session_state.pop("run_now")

        # ── RUN AGENT ─────────────────────────────────────────
        if query_to_run:
            # Show wait indicator
            st.markdown(
                '<div class="wait-banner">'
                '⏱  Agent team is analysing your question — '
                'estimated <b>20–35 seconds</b>. '
                'Watch the Pipeline panel on the right to see each agent as it works.'
                '</div>',
                unsafe_allow_html=True)

            steps        = []
            agent_starts = {}

            with st.spinner("Agents working..."):
                t0 = time.time()
                try:
                    from agents.orchestrator import Orchestrator

                    def on_status(agent, event, detail=""):
                        now = time.time()
                        _map = {
                            "orchestrator":    "Orchestrator",
                            "data_agent":      "Data Agent",
                            "analysis_agent":  "Analysis Hub",
                            "creative_analyst":"Creative Analyst",
                            "optimizer":       "Optimizer",
                            "critic":          "Quality Critic",
                        }
                        lbl = _map.get(agent, agent.replace("_"," ").title())
                        if event == "start":
                            agent_starts[agent] = now
                            steps.append(f"{lbl}  ·  starting...")
                        elif event == "done":
                            dur = now - agent_starts.get(agent, now)
                            steps.append(f"{lbl}  ·  done  [{dur:.1f}s]")
                        else:
                            steps.append(f"{lbl}  ·  {event}")

                    result   = Orchestrator().run(
                                   query_to_run, verbose=False, on_status=on_status)
                    response = (result.get("response")
                                or result.get("analysis")
                                or result.get("data_summary")
                                or "No response from agent.")
                except Exception as e:
                    response = f"Agent error: {e}"

                total = time.time() - t0

            # Save results & clear input
            st.session_state["messages"].append(
                {"role": "user", "content": query_to_run})
            st.session_state["messages"].append(
                {"role": "assistant", "content": response})
            st.session_state["pipeline_log"] = steps
            st.session_state["total_time"]   = total
            st.session_state["do_clear_input"] = True  # clear on next render
            st.rerun()

        # ── DIVIDER ───────────────────────────────────────────
        st.markdown(
            '<hr style="border:none;border-top:1px solid #E2E8F0;margin:14px 0 8px;">',
            unsafe_allow_html=True)

        # ── CONVERSATION HISTORY (latest first) ───────────────
        if not st.session_state.messages:
            st.markdown(
                '<div style="color:#94A3B8;font-size:13px;padding:20px 0;text-align:center;">'
                'No messages yet — type a question above, or click a sidebar topic '
                'and choose one of the suggested questions.'
                '</div>',
                unsafe_allow_html=True)
        else:
            # Pair up messages and show latest pair first
            msgs = st.session_state.messages
            pairs = []
            i = 0
            while i < len(msgs) - 1:
                if msgs[i]["role"] == "user" and msgs[i+1]["role"] == "assistant":
                    pairs.append((msgs[i], msgs[i+1]))
                    i += 2
                else:
                    i += 1
            for u_msg, a_msg in reversed(pairs):
                body = a_msg["content"].replace("\n","<br>")
                st.markdown(
                    f'<div class="chat-user"><b>You</b><br>{u_msg["content"]}</div>'
                    f'<div class="chat-agent"><b>Agent Team</b><br>{body}</div>',
                    unsafe_allow_html=True)

    # ── PIPELINE PANEL ────────────────────────────────────────
    with right:
        st.markdown('<div class="sec">Pipeline</div>', unsafe_allow_html=True)

        if st.session_state["total_time"]:
            st.markdown(
                f'<div class="timer-total">Total: '
                f'{st.session_state["total_time"]:.1f}s</div>',
                unsafe_allow_html=True)

        if st.session_state.pipeline_log:
            for step in st.session_state.pipeline_log:
                cls = "pd" if "done" in step.lower() else "ps"
                st.markdown(f'<div class="{cls}">{step}</div>',
                            unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="color:#94A3B8;font-size:12px;padding:10px 0;line-height:1.8;">'
                'Agent steps and timings appear here after you run a query.'
                '</div>',
                unsafe_allow_html=True)
            for a in ["Orchestrator","Data Agent","Analysis Hub",
                      "Creative Analyst","Optimizer","Quality Critic"]:
                st.markdown(f'<div class="apill">{a}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 2 — PERFORMANCE DASHBOARD
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="sec">Key Performance Indicators — Last 30 Days</div>',
                unsafe_allow_html=True)

    kpi   = qry("""
        SELECT ROUND(SUM(spend),0)   AS total_spend,
               ROUND(SUM(revenue),0) AS total_revenue,
               ROUND(SUM(revenue)/NULLIF(SUM(spend),0),2) AS blended_roas,
               SUM(impressions) AS impr, SUM(clicks) AS clicks, SUM(conversions) AS conv
        FROM fact_daily_performance
        WHERE date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
    """)
    kpi_p = qry("""
        SELECT ROUND(SUM(revenue)/NULLIF(SUM(spend),0),2) AS roas
        FROM fact_daily_performance
        WHERE date >= CAST(CURRENT_DATE - INTERVAL 60 DAY AS VARCHAR)
          AND date <  CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
    """)

    if len(kpi) > 0 and "error" not in kpi.columns:
        r = kpi.iloc[0]
        roas_v = float(r.blended_roas or 0)
        delta  = ""
        if len(kpi_p) > 0 and kpi_p.iloc[0].roas:
            d = roas_v - float(kpi_p.iloc[0].roas)
            cls = "kpi-up" if d >= 0 else "kpi-down"
            delta = f'<div class="{cls}">{"+" if d>=0 else ""}{d:.2f}x vs prev 30d</div>'

        for col, lbl, val, dx in zip(
            st.columns(6),
            ["Total Spend","Total Revenue","Blended ROAS","Impressions","Clicks","Conversions"],
            [f"SGD {fmt_n(r.total_spend)}", f"SGD {fmt_n(r.total_revenue)}",
             f"{roas_v:.2f}x", fmt_n(r.impr), fmt_n(r.clicks), fmt_n(r.conv)],
            ["","",delta,"","",""],
        ):
            with col:
                st.markdown(
                    f'<div class="kpi"><div class="kpi-label">{lbl}</div>'
                    f'<div class="kpi-value">{val}</div>{dx}</div>',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ca, cb = st.columns([3, 2])

    with ca:
        st.markdown('<div class="sec">Daily Spend & ROAS</div>', unsafe_allow_html=True)
        trend = qry("""
            SELECT date, ROUND(SUM(spend),0) AS spend,
                   ROUND(SUM(revenue)/NULLIF(SUM(spend),0),2) AS roas
            FROM fact_daily_performance
            WHERE date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
            GROUP BY date ORDER BY date
        """)
        if len(trend) > 0 and "error" not in trend.columns:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=trend.date, y=trend.spend, name="Spend",
                                 marker_color=NAVY, opacity=0.8, yaxis="y"))
            fig.add_trace(go.Scatter(x=trend.date, y=trend.roas, name="ROAS",
                                     line=dict(color=GOLD, width=2.5),
                                     mode="lines+markers", marker_size=3, yaxis="y2"))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=280, margin=dict(l=0,r=0,t=0,b=0), font_color=TEXT,
                legend=dict(orientation="h", y=1.08, bgcolor="rgba(0,0,0,0)"),
                yaxis=dict(title="Spend SGD", gridcolor=BORDER),
                yaxis2=dict(title="ROAS", overlaying="y", side="right",
                            color=GOLD, gridcolor="rgba(0,0,0,0)"),
                xaxis=dict(gridcolor=BORDER),
            )
            st.plotly_chart(fig, use_container_width=True)

    with cb:
        st.markdown('<div class="sec">Spend by Platform</div>', unsafe_allow_html=True)
        plat = qry("""
            SELECT p.platform_name AS platform, ROUND(SUM(f.spend),0) AS spend
            FROM fact_daily_performance f
            JOIN dim_platform p ON f.platform_id = p.platform_id
            WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
            GROUP BY p.platform_name ORDER BY spend DESC
        """)
        if len(plat) > 0 and "error" not in plat.columns:
            fig = go.Figure(go.Pie(
                labels=plat.platform, values=plat.spend, hole=0.52,
                marker=dict(colors=[NAVY,"#3B5BDB","#6B8EE0","#A5B4FC"],
                            line=dict(color=WHITE, width=2)),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", height=280,
                margin=dict(l=0,r=0,t=0,b=0), font_color=TEXT,
                legend=dict(font_size=11, bgcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec">ROAS vs Target by Business Line</div>',
                unsafe_allow_html=True)
    rdf = qry("""
        SELECT business_line,
               ROUND(SUM(revenue)/NULLIF(SUM(spend),0),2) AS actual_roas
        FROM fact_daily_performance
        WHERE date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
        GROUP BY business_line ORDER BY actual_roas DESC
    """)
    if len(rdf) > 0 and "error" not in rdf.columns:
        rdf["target"] = rdf["business_line"].map(ROAS_TARGETS).fillna(3.0)
        rdf["gap"]    = rdf["actual_roas"] - rdf["target"]
        colors = [GREEN if g >= 0 else RED for g in rdf["gap"]]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=rdf["business_line"], x=rdf["actual_roas"], orientation="h",
            name="Actual", marker_color=colors,
            text=[f"{v:.2f}x" for v in rdf["actual_roas"]],
            textposition="outside", textfont_color=TEXT,
        ))
        fig.add_trace(go.Scatter(
            y=rdf["business_line"], x=rdf["target"], mode="markers",
            name="Target", marker=dict(symbol="line-ns", size=18, color=GOLD,
                                       line=dict(width=3, color=GOLD)),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=260, margin=dict(l=0,r=60,t=0,b=0), font_color=TEXT,
            xaxis=dict(title="ROAS", gridcolor=BORDER),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            legend=dict(orientation="h", y=1.08, bgcolor="rgba(0,0,0,0)"),
            bargap=0.4,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec">Top 10 Campaigns by ROAS</div>',
                unsafe_allow_html=True)
    camp = qry("""
        SELECT c.campaign_name, f.business_line, p.platform_name AS platform,
               ROUND(SUM(f.spend),0) AS spend, ROUND(SUM(f.revenue),0) AS revenue,
               ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0),2) AS roas
        FROM fact_daily_performance f
        JOIN dim_campaign c ON f.campaign_id = c.campaign_id
        JOIN dim_platform p ON f.platform_id = p.platform_id
        WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
        GROUP BY c.campaign_name, f.business_line, p.platform_name
        HAVING SUM(f.spend) > 1000 ORDER BY roas DESC LIMIT 10
    """)
    if len(camp) > 0 and "error" not in camp.columns:
        d = camp.copy()
        d["spend"]   = d["spend"].apply(lambda x: f"SGD {int(x):,}")
        d["revenue"] = d["revenue"].apply(lambda x: f"SGD {int(x):,}")
        d["roas"]    = d["roas"].apply(lambda x: f"{x:.2f}x")
        d.columns    = ["Campaign","Business Line","Platform","Spend","Revenue","ROAS"]
        st.dataframe(d, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
# TAB 3 — CREATIVE HEALTH
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec">Creative Format Performance — Last 30 Days</div>',
                unsafe_allow_html=True)
    fmt_df = qry("""
        SELECT cr.format,
               ROUND(AVG(f.ctr)*100,2) AS avg_ctr,
               ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0),2) AS roas,
               ROUND(SUM(f.spend),0) AS spend,
               COUNT(DISTINCT cr.creative_id) AS num_creatives
        FROM fact_daily_performance f
        JOIN dim_creative cr ON f.creative_id = cr.creative_id
        WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
        GROUP BY cr.format ORDER BY roas DESC
    """)
    c1h, c2h = st.columns(2)
    with c1h:
        if len(fmt_df) > 0 and "error" not in fmt_df.columns:
            fig = go.Figure(go.Bar(
                x=fmt_df["format"], y=fmt_df["roas"], marker_color=NAVY, opacity=0.85,
                text=[f"{v:.2f}x" for v in fmt_df["roas"]],
                textposition="outside", textfont_color=TEXT,
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=260, margin=dict(l=0,r=0,t=30,b=0), font_color=TEXT,
                title=dict(text="ROAS by Creative Format", font_size=13),
                xaxis=dict(gridcolor=BORDER, tickangle=-15),
                yaxis=dict(title="ROAS", gridcolor=BORDER),
            )
            st.plotly_chart(fig, use_container_width=True)

    CTR_BENCH = {"Video 15s":3.0,"Video 30s":2.3,"Static Image":1.8,
                 "Carousel":2.2,"Story":2.0,"Reel":2.6,"YouTube Pre-roll":1.9}
    with c2h:
        if len(fmt_df) > 0 and "error" not in fmt_df.columns:
            fmt_df["bench"] = fmt_df["format"].map(CTR_BENCH).fillna(2.0)
            fmt_df["gap"]   = (fmt_df["avg_ctr"] - fmt_df["bench"]).round(2)
            colors = [GREEN if g >= 0 else RED for g in fmt_df["gap"]]
            fig = go.Figure(go.Bar(
                x=fmt_df["format"], y=fmt_df["gap"], marker_color=colors,
                text=[f"{g:+.2f}%" for g in fmt_df["gap"]],
                textposition="outside", textfont_color=TEXT,
            ))
            fig.add_hline(y=0, line_color=GOLD, line_width=1.5)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=260, margin=dict(l=0,r=0,t=30,b=0), font_color=TEXT,
                title=dict(text="CTR vs Industry Benchmark", font_size=13),
                xaxis=dict(gridcolor=BORDER, tickangle=-15),
                yaxis=dict(title="CTR Delta (%)", gridcolor=BORDER),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec">Creative Fatigue — CTR Trend Analysis</div>',
                unsafe_allow_html=True)
    fat = qry("""
        SELECT cr.creative_name, cr.format, p.platform_name AS platform,
               COUNT(DISTINCT f.date) AS days_live,
               ROUND(AVG(CASE WHEN f.date <= CAST(CURRENT_DATE - INTERVAL 45 DAY AS VARCHAR)
                              THEN f.ctr END)*100,2) AS early_ctr,
               ROUND(AVG(CASE WHEN f.date >= CAST(CURRENT_DATE - INTERVAL 14 DAY AS VARCHAR)
                              THEN f.ctr END)*100,2) AS recent_ctr,
               ROUND(SUM(f.spend),0) AS spend
        FROM fact_daily_performance f
        JOIN dim_creative cr ON f.creative_id = cr.creative_id
        JOIN dim_platform  p ON f.platform_id = p.platform_id
        WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 90 DAY AS VARCHAR)
        GROUP BY cr.creative_name, cr.format, p.platform_name
        HAVING early_ctr IS NOT NULL AND recent_ctr IS NOT NULL
           AND COUNT(DISTINCT f.date) >= 30
        ORDER BY (recent_ctr - early_ctr) ASC LIMIT 15
    """)
    if len(fat) > 0 and "error" not in fat.columns:
        fat["drop_pct"] = ((fat["recent_ctr"] - fat["early_ctr"])
                           / fat["early_ctr"].replace(0, 0.001) * 100).round(1)
        fat["status"]   = fat["drop_pct"].apply(
            lambda x: "URGENT" if x < -20 else ("MONITOR" if x < -10 else "OK"))
        d = fat[["creative_name","format","platform","days_live",
                 "early_ctr","recent_ctr","drop_pct","status","spend"]].copy()
        d.columns = ["Creative","Format","Platform","Days Live",
                     "Early CTR%","Recent CTR%","Drop%","Status","Spend"]
        d["Spend"] = d["Spend"].apply(lambda x: f"{int(x):,}")
        st.dataframe(d, use_container_width=True, hide_index=True)
        n = (fat["status"] == "URGENT").sum()
        if n:
            st.warning(f"{n} creative(s) flagged URGENT — CTR dropped >20%. Refresh recommended.")

    st.markdown('<div class="sec">CTR Heatmap: Platform × Format</div>',
                unsafe_allow_html=True)
    heat = qry("""
        SELECT p.platform_name AS platform, cr.format,
               ROUND(AVG(f.ctr)*100,2) AS avg_ctr
        FROM fact_daily_performance f
        JOIN dim_creative cr ON f.creative_id = cr.creative_id
        JOIN dim_platform  p ON f.platform_id = p.platform_id
        WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)
        GROUP BY p.platform_name, cr.format
    """)
    if len(heat) > 0 and "error" not in heat.columns:
        piv = heat.pivot(index="platform", columns="format", values="avg_ctr").fillna(0)
        fig = go.Figure(go.Heatmap(
            z=piv.values, x=piv.columns.tolist(), y=piv.index.tolist(),
            colorscale=[[0,"#EEF2FF"],[0.5,"#3B5BDB"],[1,NAVY]],
            text=[[f"{v:.2f}%" for v in row] for row in piv.values],
            texttemplate="%{text}", textfont_size=11,
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color=TEXT,
            height=210, margin=dict(l=0,r=0,t=0,b=0),
        )
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 4 — DATA EXPLORER
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="sec">SQL Query on Live Data</div>', unsafe_allow_html=True)

    EXAMPLES = {
        "Spend & ROAS by Platform (30d)": (
            "SELECT p.platform_name, ROUND(SUM(f.spend),0) AS spend,\n"
            "       ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0),2) AS roas\n"
            "FROM fact_daily_performance f\n"
            "JOIN dim_platform p ON f.platform_id = p.platform_id\n"
            "WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)\n"
            "GROUP BY p.platform_name ORDER BY roas DESC"
        ),
        "ROAS by Business Line (30d)": (
            "SELECT business_line,\n"
            "       ROUND(SUM(revenue)/NULLIF(SUM(spend),0),2) AS roas,\n"
            "       ROUND(SUM(spend),0) AS spend\n"
            "FROM fact_daily_performance\n"
            "WHERE date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)\n"
            "GROUP BY business_line ORDER BY roas DESC"
        ),
        "Creative Format CTR (30d)": (
            "SELECT cr.format, ROUND(AVG(f.ctr)*100,2) AS avg_ctr,\n"
            "       COUNT(DISTINCT cr.creative_id) AS num_creatives\n"
            "FROM fact_daily_performance f\n"
            "JOIN dim_creative cr ON f.creative_id = cr.creative_id\n"
            "WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)\n"
            "GROUP BY cr.format ORDER BY avg_ctr DESC"
        ),
        "Top 20 Campaigns by Spend (30d)": (
            "SELECT c.campaign_name, f.business_line,\n"
            "       ROUND(SUM(f.spend),0) AS spend,\n"
            "       ROUND(SUM(f.revenue)/NULLIF(SUM(f.spend),0),2) AS roas\n"
            "FROM fact_daily_performance f\n"
            "JOIN dim_campaign c ON f.campaign_id = c.campaign_id\n"
            "WHERE f.date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR)\n"
            "GROUP BY c.campaign_name, f.business_line ORDER BY spend DESC LIMIT 20"
        ),
        "Daily Trend Last 14 Days": (
            "SELECT date, ROUND(SUM(spend),0) AS spend,\n"
            "       ROUND(SUM(revenue)/NULLIF(SUM(spend),0),2) AS roas\n"
            "FROM fact_daily_performance\n"
            "WHERE date >= CAST(CURRENT_DATE - INTERVAL 14 DAY AS VARCHAR)\n"
            "GROUP BY date ORDER BY date DESC"
        ),
    }

    ex = st.selectbox("Load example query", ["Write your own"] + list(EXAMPLES.keys()))
    sql_default = EXAMPLES.get(ex, "") if ex != "Write your own" else ""
    sql_in = st.text_area("SQL", value=sql_default, height=150,
                           placeholder="SELECT ... FROM fact_daily_performance WHERE ...")

    if st.button("Run Query", type="primary"):
        if sql_in.strip():
            with st.spinner("Querying..."):
                res = qry(sql_in.strip())
            if "error" in res.columns:
                st.error(f"Query error: {res['error'].iloc[0]}")
            elif len(res) == 0:
                st.info("No rows returned.")
            else:
                st.success(f"{len(res):,} rows returned")
                st.dataframe(res, use_container_width=True, hide_index=True)
                st.download_button("Download CSV",
                                   res.to_csv(index=False).encode("utf-8"),
                                   "data.csv","text/csv")

    st.markdown('<div class="sec">Schema Reference</div>', unsafe_allow_html=True)
    schema = {
        "fact_daily_performance (112K rows)":
            ["date VARCHAR","campaign_id","platform_id","business_line VARCHAR",
             "spend DOUBLE","revenue DOUBLE","roas DOUBLE",
             "impressions","clicks","conversions","ctr","cpm","cvr"],
        "dim_campaign":
            ["campaign_id PK","campaign_name","business_line",
             "objective","platform_id","roas_target DOUBLE","status"],
        "dim_platform": ["platform_id PK","platform_name","platform_type"],
        "dim_creative":
            ["creative_id PK","creative_name","format","style","business_line","is_video"],
        "dim_ad_set":
            ["ad_set_id PK","campaign_id","ad_set_name","audience_type","age_range","daily_budget"],
    }
    for idx, (tbl, cols) in enumerate(schema.items()):
        rows = "".join(
            f'<div style="color:#64748B;font-size:11px;font-family:monospace;padding:1px 0;">{c}</div>'
            for c in cols)
        with st.columns(3)[idx % 3]:
            st.markdown(
                f'<div style="background:#fff;border:1px solid #E2E8F0;border-radius:6px;'
                f'padding:12px;margin-bottom:10px;">'
                f'<div style="color:#003087;font-size:12px;font-weight:700;'
                f'margin-bottom:6px;">{tbl}</div>{rows}</div>',
                unsafe_allow_html=True)
