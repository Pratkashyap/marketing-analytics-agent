# Bug Fix Log — Marketing Analytics Agent
All timestamps in SGT (UTC+8).

---

## 2026-03-17

### [17:00] Send button not working — text area wiped on rerun
**Root cause:** `st.text_area(value=..., key=...)` — using both `value=` and `key=` resets widget to `value=` on every rerun, wiping typed text.
**Fix:** Remove `value=` entirely. Use `key="chat_val"` only. Pre-set `st.session_state["chat_val"]` before widget renders via `do_clear_input` flag.

### [17:10] Quick queries not populating text box
**Root cause:** Sub-question click set `pending_q` but never wrote it to the text area widget state before render.
**Fix:** `prefill_text` flag — set before widget renders, applied as `st.session_state["chat_val"] = prefill_text` pre-render.

### [17:15] Sidebar button keys silently dropped
**Root cause:** Streamlit 1.55 drops buttons with spaces/special chars in `key=` (e.g. `key="qq_ROAS vs Targets"`).
**Fix:** Numeric keys only — `key="cat0"`, `key="cat1"`, etc.

### [17:20] Send button CSS hidden
**Root cause:** Global `.stButton > button { background: #F8F9FC }` overrode Streamlit's primary button blue.
**Fix:** Separate CSS rules for primary vs secondary buttons using `[data-testid="baseButton-primary"]`.

### [17:30] Wrong SQL table name
**Root cause:** Queries used `fact_performance` — table doesn't exist. Actual table is `fact_daily_performance`.
**Fix:** Updated all SQL across dashboard to `fact_daily_performance`. Also removed references to non-existent `dim_business_line` (it's a VARCHAR column on the fact table, not a dimension table).

### [17:45] Performance dashboard charts blank / axis numbers invisible
**Root cause:** No `.streamlit/config.toml` → Streamlit defaulted to dark mode for internal components. Charts used `paper_bgcolor="rgba(0,0,0,0)"` (transparent) → dark container showed through, making dark axis labels invisible.
**Fix:** Created `.streamlit/config.toml` with `base="light"`. Set explicit `paper_bgcolor="#FFFFFF"` and `tickfont_color` on every axis in every chart.

### [18:00] Top 10 Campaigns / Creative Fatigue table black background
**Root cause:** Same dark mode issue — `st.dataframe()` respects Streamlit theme. No config.toml → dark theme.
**Fix:** `config.toml` light theme forces all dataframes to white background.

---

## 2026-03-18

### [10:00] Sidebar quick query buttons — text invisible on hover
**Root cause:** No CSS override for sidebar buttons. Streamlit's default dark hover state took over.
**Fix:** Global `.stButton > button:hover` rule with light blue bg `#E0E7FF` and dark text `#003087`.

### [10:05] Sub-question buttons and Clear button — same black hover issue
**Root cause:** Previous fix only scoped to `section[data-testid="stSidebar"]`. Main area buttons not covered.
**Fix:** Moved to global `.stButton > button` rule covering all buttons. Primary button re-asserted separately.

### [10:20] Text area black background
**Root cause:** Streamlit dark mode bleeding into textarea. No explicit override.
**Fix:** `.stTextArea textarea { background:#ffffff !important; color:#0F172A !important; }` with focus and placeholder rules.

### [10:40] Agent response rendered as raw text dump
**Root cause 1:** `data_only` intent returned `data.to_string(index=False)` — raw pandas string, no formatting.
**Root cause 2:** Response embedded in HTML div with `\n→<br>` conversion, stripping all markdown.
**Fix 1:** `data_only` path now builds a markdown table manually and returns `**N results found.**\n\n| col | col |`.
**Fix 2:** Switched to `st.chat_message("assistant")` + `st.markdown(content)` — renders tables, bullets, bold, headers correctly.

### [10:50] Pipeline panel — no live updates, couldn't tell which agent running
**Root cause:** Pipeline panel rendered statically after run completed. No `st.empty()` placeholders for live updates.
**Fix:** Define `pipe_status_ph`, `pipe_agent_ph`, `pipe_steps_ph` as `st.empty()` in right column *before* left column runs. `on_status` callback updates them live. Shows: pulsing amber timer, active agent + elapsed, step log updating in real time. On complete: green "✅ Complete — Xs" banner.

### [11:10] Quality score badge leaking into response body
**Root cause:** Critic agent prepends `"✅ Quality Score: 9/10 — Approved"` to response. Dashboard rendered entire string including badge as body text.
**Fix:** Strip badge line in orchestrator before returning response. Also strip defensively in dashboard render. Badge shown as `st.caption()` inside chat bubble.

### [11:15] First question showing no content (only badge)
**Root cause:** Mixing HTML div tags with `st.container()` + `st.markdown()` — HTML divs don't wrap Streamlit widget output. Response content rendered outside the visual box, appearing to belong to the next message.
**Fix:** `st.chat_message()` which correctly contains all child `st.markdown()` output inside one visual component.

---
