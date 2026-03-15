"""
main.py — Warner Bros. Singapore Marketing Analytics Agent
Rich terminal UI showing every agent step in real time.

Usage:
  cd ~/Desktop/marketing-analytics-agent
  source venv/bin/activate
  python3 main.py
"""

import os, sys, time, json, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel   import Panel
from rich.text    import Text
from rich.rule    import Rule
from rich.table   import Table
from rich import   box

from agents.orchestrator    import Orchestrator
from agents.dashboard_agent import (
    DASHBOARD_QUESTIONS, FOCUS_MAP, PERIOD_MAP, BL_MAP,
    generate_dashboard, launch_dashboard,
)

DASHBOARD_KEYWORDS = {"dashboard", "chart", "charts", "visuali", "graph",
                       "plot", "visual", "show me a", "build a dashboard",
                       "create a dashboard", "open dashboard"}

console = Console()

# ── colour palette ──────────────────────────────────────
C_ORCH    = "bold cyan"
C_DATA    = "bold yellow"
C_ANAL    = "bold magenta"
C_OK      = "bold green"
C_ERR     = "bold red"
C_DIM     = "dim white"
C_LABEL   = "bold white"
C_RESP    = "bright_white"
C_HEADER  = "bold bright_cyan"

AGENT_ICONS = {
    "orchestrator":    "🧠",
    "data_agent":      "📊",
    "analysis_agent":  "🔍",
    "creative_analyst":"🎨",
    "optimizer":       "💰",
    "critic":          "⚖️",
}

C_CREATIVE = "bold green"
C_OPT      = "bold yellow"
C_CRITIC   = "bold magenta"

AGENT_COLORS = {
    "orchestrator":    C_ORCH,
    "data_agent":      C_DATA,
    "analysis_agent":  C_ANAL,
    "creative_analyst":C_CREATIVE,
    "optimizer":       C_OPT,
    "critic":          C_CRITIC,
}

AGENT_LABELS = {
    "orchestrator":    "ORCHESTRATOR",
    "data_agent":      "DATA AGENT",
    "analysis_agent":  "ANALYSIS AGENT",
    "creative_analyst":"CREATIVE ANALYST",
    "optimizer":       "OPTIMIZER AGENT",
    "critic":          "QUALITY CRITIC",
}

# track open agent headers so we don't reprint them
_printed_agents: set = set()


def _agent_header(agent: str):
    """Print agent section header once."""
    if agent in _printed_agents:
        return
    _printed_agents.add(agent)
    icon  = AGENT_ICONS.get(agent, "•")
    label = AGENT_LABELS.get(agent, agent.upper())
    color = AGENT_COLORS.get(agent, "white")
    console.print(f"\n  {icon}  [{color}]{label}[/{color}]")


def _step(agent: str, text: str, value: str = "", ok: bool = False, indent: int = 6):
    """Print a single pipeline step line."""
    prefix = " " * indent + "├─ "
    if ok:
        suffix = f"  [bold green]✓[/bold green]"
    else:
        suffix = ""
    if value:
        console.print(f"{prefix}[{C_LABEL}]{text}[/{C_LABEL}] [dim]{value}[/dim]{suffix}")
    else:
        console.print(f"{prefix}[{C_LABEL}]{text}[/{C_LABEL}]{suffix}")


def _step_last(agent: str, text: str, value: str = "", ok: bool = True, indent: int = 6):
    """Print the last step in a section (uses └─)."""
    prefix = " " * indent + "└─ "
    suffix = f"  [bold green]✓[/bold green]" if ok else ""
    if value:
        console.print(f"{prefix}[{C_LABEL}]{text}[/{C_LABEL}] [dim]{value}[/dim]{suffix}")
    else:
        console.print(f"{prefix}[{C_LABEL}]{text}[/{C_LABEL}]{suffix}")


def on_status(agent: str, event: str, detail: str):
    """Callback — called by Orchestrator for every pipeline step."""

    # ── ORCHESTRATOR events ──────────────────────────────
    if agent == "orchestrator":
        if event == "start":
            _agent_header(agent)

        elif event == "classifying":
            _step(agent, "Classifying intent...", "")

        elif event == "classified":
            try:
                d = json.loads(detail)
            except Exception:
                d = {}
            intent     = d.get("intent", "")
            specialist = d.get("specialist", "analysis")
            scope      = d.get("scope", "")
            refined    = d.get("refined_question", "")
            needs      = d.get("needs_analysis", True)

            intent_color = {
                "analysis":    "green",
                "comparison":  "cyan",
                "data_only":   "yellow",
                "out_of_scope":"red",
            }.get(intent, "white")

            specialist_color = {
                "creative":  "green",
                "optimizer": "yellow",
                "analysis":  "magenta",
            }.get(specialist, "white")

            _step(agent, "Intent detected",
                  f"[{intent_color}]{intent}[/{intent_color}]", ok=True)
            _step(agent, "Specialist agent",
                  f"[{specialist_color}]{specialist}[/{specialist_color}]", ok=True)

            if scope:
                _step(agent, "Scope",
                      textwrap.shorten(scope, width=60, placeholder="..."))

            if refined:
                _step(agent, "Refined question",
                      f"[italic]{textwrap.shorten(refined, width=60, placeholder='...')}[/italic]")

            _step(agent, "Analysis needed",
                  f"{'[green]Yes[/green]' if needs else '[yellow]No[/yellow]'}")

        elif event == "routing":
            _step_last(agent, "Routing pipeline", detail, ok=True)

        elif event == "out_of_scope":
            _step_last(agent, "Out of scope", detail, ok=False)

        elif event == "done":
            pass   # final done — handled by response block

    # ── DATA AGENT events ────────────────────────────────
    elif agent == "data_agent":
        if event == "start":
            _agent_header(agent)

        elif event == "classifying_query":
            _step(agent, detail)

        elif event == "query_classified":
            try:
                d = json.loads(detail)
            except Exception:
                d = {}
            qtype  = d.get("query_type", "")
            window = d.get("time_window", "")
            if qtype:
                _step(agent, "Query type",   qtype, ok=True)
            if window:
                _step(agent, "Time window",  window)

        elif event == "sql_generated":
            sql_preview = detail.replace("\n", " ").strip()
            _step(agent, "SQL generated",
                  f"[dim italic]{textwrap.shorten(sql_preview, width=65, placeholder='...')}[/dim italic]",
                  ok=True)

        elif event == "query_executed":
            rows = detail
            _step(agent, "Query executed on DuckDB", ok=True)
            _step_last(agent, "Rows returned",
                       f"[bold green]{rows} rows[/bold green]", ok=True)

        elif event == "error":
            _step_last(agent, "Error", f"[red]{detail}[/red]", ok=False)

    # ── ANALYSIS AGENT events ────────────────────────────
    elif agent == "analysis_agent":
        if event == "start":
            _agent_header(agent)

        elif event == "preparing":
            _step(agent, "Data received", detail)
            _step(agent, "Model",
                  "[bold]claude-sonnet-4-6[/bold]  (high-quality analysis)")

        elif event == "analysing":
            _step(agent, "Generating insights...", "")

        elif event == "done":
            _step_last(agent, "CMO-ready insights generated", ok=True)

    # ── CREATIVE ANALYST AGENT events ────────────────────
    elif agent == "creative_analyst":
        if event == "start":
            _agent_header(agent)

        elif event == "preparing":
            _step(agent, "Creative data received", detail)
            _step(agent, "Model",
                  "[bold]claude-sonnet-4-6[/bold]  (creative specialist)")

        elif event == "analysing":
            _step(agent, "Running format comparison & fatigue detection...", "")

        elif event == "done":
            _step_last(agent, "Creative analysis complete", ok=True)

    # ── OPTIMIZER AGENT events ────────────────────────────
    elif agent == "optimizer":
        if event == "start":
            _agent_header(agent)

        elif event == "preparing":
            _step(agent, "Performance data received", detail)
            _step(agent, "Model",
                  "[bold]claude-sonnet-4-6[/bold]  (budget optimisation)")

        elif event == "optimising":
            _step(agent, "Building reallocation table...", "")

        elif event == "done":
            _step_last(agent, "Budget optimisation plan ready", ok=True)

    # ── QUALITY CRITIC events ─────────────────────────────
    elif agent == "critic":
        if event == "start":
            _agent_header(agent)

        elif event == "reviewing":
            _step(agent, "Scoring: specificity · actionability · accuracy · tone...", "")

        elif event == "done":
            score_txt = detail  # e.g. "Score: 9/10"
            _step_last(agent, "Quality check complete",
                       f"[bold green]{score_txt}[/bold green]", ok=True)


def print_banner():
    console.print()
    console.print(Panel(
        Text.assemble(
            ("  WARNER BROS. SINGAPORE\n", "bold bright_white"),
            ("  Marketing Analytics Agent\n", "bold cyan"),
            ("  ─────────────────────────────────────────────────\n", "dim"),
            ("  Business Lines:  ", "dim"), ("Theatrical  │  Max Streaming  │  WB Games\n", "white"),
            ("                   ", "dim"), ("Home Entertainment  │  Licensing & Merch\n", "white"),
            ("  Platforms:       ", "dim"), ("Meta  │  Google  │  TikTok  │  YouTube\n", "white"),
            ("  Currency:        ", "dim"), ("SGD                 ", "white"),
            ("Today: ", "dim"), ("2026-03-15\n", "white"),
            ("  ─────────────────────────────────────────────────\n", "dim"),
            ("  Agents: ", "dim"), ("Orchestrator · Data · Analysis · Creative · Optimizer · Critic\n", "white"),
            ("  ─────────────────────────────────────────────────\n", "dim"),
            ("  Type a question  │  'demo' for showcase  │  'dashboard' for charts  │  'quit' to exit", "dim italic"),
        ),
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        padding=(0, 2),
    ))
    console.print()


DEMO_QUERIES = [
    # Analysis Agent
    "Give me a full performance review across all business lines this month",
    "Why is Max Streaming underperforming and what should we do?",
    # Creative Analyst Agent
    "Which creative format has the best ROAS and which creatives need urgent refresh?",
    "How are Video 15s vs Static Image creatives performing across platforms?",
    # Optimizer Agent
    "I have SGD 50K extra budget — where should I allocate it for maximum ROAS?",
    "Which platforms are we over-investing in relative to their ROAS performance?",
    # Combo (multi-agent orchestration)
    "Complete audit: full performance review, creative health, and budget optimisation",
]


def run_query(orch: Orchestrator, question: str):
    """Run one question through the pipeline with full live display."""
    global _printed_agents
    _printed_agents = set()   # reset per question

    console.print()
    console.rule(f"[bold white]{question}[/bold white]", style="dim cyan")

    console.print()
    console.print(f"  [dim]Pipeline starting...[/dim]")

    result = orch.run(question, verbose=False, on_status=on_status)

    # ── Response ─────────────────────────────────────────
    console.print()
    console.rule("[bold bright_cyan]  AGENT RESPONSE[/bold bright_cyan]", style="cyan")
    console.print()

    if result.get("error"):
        console.print(f"  [bold red]Error:[/bold red] {result['error']}")
    elif result.get("intent") == "out_of_scope":
        console.print(Panel(result["response"], border_style="yellow", padding=(1, 2)))
    else:
        # Pretty-print the markdown-style response
        for line in result["response"].split("\n"):
            if line.startswith("**") and line.endswith("**"):
                console.print(f"  [bold bright_cyan]{line.strip('*')}[/bold bright_cyan]")
            elif line.startswith("- "):
                console.print(f"  [white]  •{line[1:]}[/white]")
            elif line.startswith("1. ") or line.startswith("2. ") or line.startswith("3. "):
                console.print(f"  [bright_white]  {line}[/bright_white]")
            elif line.startswith("---"):
                console.print(f"  [dim]{'─'*60}[/dim]")
            elif line.strip():
                console.print(f"  {line}")

    console.print()


def is_dashboard_request(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in DASHBOARD_KEYWORDS)


def run_dashboard_flow():
    """Ask 2-3 questions, build and launch a Streamlit dashboard."""
    console.print()
    console.rule("[bold yellow]🎛️  DASHBOARD BUILDER[/bold yellow]", style="yellow")
    console.print()
    console.print("  [bold yellow]📊 Dashboard Agent[/bold yellow] — Let me ask a few quick questions.\n")

    config = {}

    # Q1: Focus
    q1 = DASHBOARD_QUESTIONS[0]
    console.print(f"  [bold white]{q1['prompt']}[/bold white]")
    for opt in q1["options"]:
        console.print(f"    [dim]{opt}[/dim]")
    try:
        ans1 = console.input("  [cyan]Your choice (1-5, default 1):[/cyan] ").strip() or "1"
    except (KeyboardInterrupt, EOFError):
        return
    config["focus"] = ans1 if ans1 in FOCUS_MAP else "1"
    console.print(f"  [green]✓[/green] Focus: [white]{FOCUS_MAP.get(config['focus'])}[/white]\n")

    # Q2: Period
    q2 = DASHBOARD_QUESTIONS[1]
    console.print(f"  [bold white]{q2['prompt']}[/bold white]")
    for opt in q2["options"]:
        console.print(f"    [dim]{opt}[/dim]")
    try:
        ans2 = console.input("  [cyan]Your choice (1-4, default 2):[/cyan] ").strip() or "2"
    except (KeyboardInterrupt, EOFError):
        return
    config["period"] = ans2 if ans2 in PERIOD_MAP else "2"
    period_label = PERIOD_MAP[config["period"]][0]
    console.print(f"  [green]✓[/green] Period: [white]{period_label}[/white]\n")

    # Q3: Business line (only if focus == '2')
    config["business_line"] = "0"
    if config["focus"] == "2":
        q3 = DASHBOARD_QUESTIONS[2]
        console.print(f"  [bold white]{q3['prompt']}[/bold white]")
        for opt in q3["options"]:
            console.print(f"    [dim]{opt}[/dim]")
        try:
            ans3 = console.input("  [cyan]Your choice (1-5):[/cyan] ").strip() or "0"
        except (KeyboardInterrupt, EOFError):
            return
        config["business_line"] = ans3 if ans3 in BL_MAP else "0"
        bl_label = BL_MAP.get(config["business_line"], "All")
        console.print(f"  [green]✓[/green] Business Line: [white]{bl_label}[/white]\n")

    # Build dashboard
    console.print()
    console.print("  [bold yellow]🔧  Dashboard Agent[/bold yellow] generating dashboard...")

    with console.status("[yellow]  Fetching data from DuckDB...[/yellow]", spinner="dots"):
        try:
            path = generate_dashboard(config)
        except Exception as e:
            console.print(f"  [red]Error building dashboard: {e}[/red]")
            return

    console.print("  [green]✓[/green] Data fetched and charts configured")
    console.print("  [green]✓[/green] Streamlit app generated")
    console.print()

    with console.status("[yellow]  Launching Streamlit dashboard...[/yellow]", spinner="dots"):
        proc = launch_dashboard(path)
        time.sleep(3)

    console.print(Panel(
        Text.assemble(
            ("  ✅ Dashboard is live!\n\n", "bold green"),
            ("  URL:  ", "dim"), ("http://localhost:8501\n", "bold bright_cyan"),
            ("  File: ", "dim"), (f"{path}\n\n", "dim"),
            ("  Opening in your browser automatically...\n", "dim"),
            ("  Press Ctrl+C in this window to stop the dashboard.", "dim italic"),
        ),
        border_style="green",
        padding=(0, 2),
    ))
    console.print()


def run_demo(orch: Orchestrator):
    console.print()
    console.rule("[bold cyan]DEMO MODE — 5 Showcase Queries[/bold cyan]")
    for i, q in enumerate(DEMO_QUERIES, 1):
        console.print(f"\n  [dim]Demo {i}/{len(DEMO_QUERIES)}[/dim]")
        run_query(orch, q)
        if i < len(DEMO_QUERIES):
            try:
                input("  [dim]Press Enter for next query...[/dim]")
            except (KeyboardInterrupt, EOFError):
                break


def main():
    print_banner()
    orch = Orchestrator()
    console.print("  [bold green]✓[/bold green] Agent ready — ask me anything.\n")

    while True:
        try:
            user_input = console.input("  [bold cyan]You:[/bold cyan] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n  Goodbye! 🎬\n")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "bye", "q"):
            console.print("\n  Goodbye! 🎬\n")
            break
        if user_input.lower() == "demo":
            run_demo(orch)
            continue

        if user_input.lower() == "dashboard" or is_dashboard_request(user_input):
            run_dashboard_flow()
            continue

        run_query(orch, user_input)


if __name__ == "__main__":
    main()
