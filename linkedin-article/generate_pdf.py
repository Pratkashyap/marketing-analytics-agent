"""
Generate LinkedIn Article V3 as a styled PDF
Warner Bros. Singapore · Marketing Analytics Agent · Build Series
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas as pdfcanvas

# ── Brand colours ─────────────────────────────────────────────
NAVY   = colors.HexColor("#1428A0")
GOLD   = colors.HexColor("#FFD700")
WHITE  = colors.white
DARK   = colors.HexColor("#0A0F1E")
CARD   = colors.HexColor("#111827")
GREY   = colors.HexColor("#6B7280")
LIGHT  = colors.HexColor("#E5E7EB")
GREEN  = colors.HexColor("#22C55E")
RED    = colors.HexColor("#EF4444")

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "V3_LINKEDIN_ARTICLE.pdf")

W, H = A4
MARGIN = 18 * mm


# ── Custom canvas for header/footer ───────────────────────────
class WBDCanvas(pdfcanvas.Canvas):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def _draw_header_footer(self, page_count):
        self.saveState()
        page_num = self._pageNumber

        # ── Header bar ─────────────────────────────
        self.setFillColor(NAVY)
        self.rect(0, H - 14*mm, W, 14*mm, fill=1, stroke=0)

        # WB shield hex
        self.setFillColor(GOLD)
        self.setFont("Helvetica-Bold", 9)
        self.drawString(MARGIN, H - 9*mm, "WB")

        # Series title
        self.setFillColor(WHITE)
        self.setFont("Helvetica-Bold", 8)
        self.drawString(MARGIN + 14*mm, H - 9*mm, "AGENT MODE  ·  BUILD SERIES")

        # Batch tag
        self.setFillColor(GOLD)
        self.setFont("Helvetica-Bold", 7)
        self.drawRightString(W - MARGIN, H - 9*mm, "BATCH 1 OF 5")

        # ── Footer ─────────────────────────────────
        self.setFillColor(CARD)
        self.rect(0, 0, W, 10*mm, fill=1, stroke=0)
        self.setStrokeColor(NAVY)
        self.setLineWidth(0.5)
        self.line(MARGIN, 10*mm, W - MARGIN, 10*mm)

        self.setFillColor(GREY)
        self.setFont("Helvetica", 7)
        self.drawString(MARGIN, 3.5*mm,
                        "Building in Public · AI Marketing Agent Series · Not for distribution")
        self.drawRightString(W - MARGIN, 3.5*mm,
                             f"Page {page_num} of {page_count}")

        self.restoreState()


def build_styles():
    """Return a dict of named ParagraphStyles."""
    base = dict(fontName="Helvetica", fontSize=10, leading=15,
                textColor=DARK, spaceAfter=6)

    return {
        "title": ParagraphStyle("title",
            fontName="Helvetica-Bold", fontSize=26, leading=32,
            textColor=NAVY, spaceAfter=6, alignment=TA_LEFT),

        "subtitle": ParagraphStyle("subtitle",
            fontName="Helvetica", fontSize=13, leading=18,
            textColor=GREY, spaceAfter=14, alignment=TA_LEFT),

        "hook": ParagraphStyle("hook",
            fontName="Helvetica-BoldOblique", fontSize=13, leading=20,
            textColor=NAVY, spaceAfter=12, leftIndent=8,
            borderPad=8, backColor=colors.HexColor("#EEF2FF"),
            borderWidth=0, borderColor=NAVY),

        "h2": ParagraphStyle("h2",
            fontName="Helvetica-Bold", fontSize=15, leading=20,
            textColor=NAVY, spaceBefore=18, spaceAfter=6),

        "h3": ParagraphStyle("h3",
            fontName="Helvetica-Bold", fontSize=11, leading=16,
            textColor=NAVY, spaceBefore=10, spaceAfter=4),

        "body": ParagraphStyle("body",
            **{**base, "alignment": TA_JUSTIFY, "leading": 17}),

        "body_bold": ParagraphStyle("body_bold",
            fontName="Helvetica-Bold", fontSize=10, leading=15,
            textColor=DARK, spaceAfter=4),

        "bullet": ParagraphStyle("bullet",
            fontName="Helvetica", fontSize=10, leading=15,
            textColor=DARK, leftIndent=14, bulletIndent=4,
            spaceAfter=4),

        "code": ParagraphStyle("code",
            fontName="Courier", fontSize=8.5, leading=13,
            textColor=colors.HexColor("#1E3A5F"),
            backColor=colors.HexColor("#F0F4FF"),
            leftIndent=10, rightIndent=10,
            spaceAfter=6, spaceBefore=4),

        "agent_name": ParagraphStyle("agent_name",
            fontName="Helvetica-Bold", fontSize=10, leading=14,
            textColor=GOLD),

        "agent_role": ParagraphStyle("agent_role",
            fontName="Helvetica-BoldOblique", fontSize=9, leading=13,
            textColor=NAVY, spaceAfter=3),

        "agent_body": ParagraphStyle("agent_body",
            fontName="Helvetica", fontSize=9, leading=14,
            textColor=DARK, spaceAfter=2),

        "caption": ParagraphStyle("caption",
            fontName="Helvetica-Oblique", fontSize=8, leading=12,
            textColor=GREY, alignment=TA_CENTER, spaceAfter=10),

        "tag": ParagraphStyle("tag",
            fontName="Helvetica-Bold", fontSize=8, leading=12,
            textColor=GREY, spaceAfter=16, alignment=TA_LEFT),

        "cta": ParagraphStyle("cta",
            fontName="Helvetica-Bold", fontSize=11, leading=17,
            textColor=NAVY, spaceAfter=6, alignment=TA_CENTER),

        "quote": ParagraphStyle("quote",
            fontName="Helvetica-Oblique", fontSize=11, leading=18,
            textColor=NAVY, leftIndent=16, rightIndent=16,
            spaceAfter=10, spaceBefore=6),
    }


def gold_rule():
    return HRFlowable(width="100%", thickness=1.5, color=GOLD,
                      spaceAfter=10, spaceBefore=4)

def thin_rule():
    return HRFlowable(width="100%", thickness=0.5, color=LIGHT,
                      spaceAfter=8, spaceBefore=4)


def screenshot_placeholder(s, label, note=""):
    """A styled box representing where a screenshot goes."""
    inner = []
    inner.append(Paragraph(f"[ SCREENSHOT: {label} ]", ParagraphStyle(
        "ph_label", fontName="Helvetica-Bold", fontSize=9,
        textColor=NAVY, alignment=TA_CENTER)))
    if note:
        inner.append(Paragraph(note, ParagraphStyle(
            "ph_note", fontName="Helvetica-Oblique", fontSize=7.5,
            textColor=GREY, alignment=TA_CENTER, spaceBefore=3)))

    t = Table([[inner]], colWidths=[W - 2*MARGIN - 20])
    t.setStyle(TableStyle([
        ("BOX",         (0,0), (-1,-1), 1, NAVY),
        ("BACKGROUND",  (0,0), (-1,-1), colors.HexColor("#EEF2FF")),
        ("TOPPADDING",  (0,0), (-1,-1), 18),
        ("BOTTOMPADDING",(0,0),(-1,-1), 18),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING",(0,0), (-1,-1), 10),
    ]))
    return t


def agent_card(s, icon, name, role, description):
    """A styled card for each agent."""
    header = Table([[
        Paragraph(icon, ParagraphStyle("icon", fontName="Helvetica-Bold",
                                       fontSize=18, leading=22, textColor=GOLD)),
        [Paragraph(name, s["agent_name"]),
         Paragraph(role, s["agent_role"])],
    ]], colWidths=[14*mm, W - 2*MARGIN - 14*mm - 24])
    header.setStyle(TableStyle([
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING",(0,0), (-1,-1), 0),
        ("TOPPADDING",  (0,0), (-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
    ]))

    body_para = Paragraph(description, s["agent_body"])
    content   = Table([
        [header],
        [body_para],
    ], colWidths=[W - 2*MARGIN - 24])
    content.setStyle(TableStyle([
        ("BOX",         (0,0), (-1,-1), 1,   colors.HexColor("#DBEAFE")),
        ("LINEABOVE",   (0,0), (-1, 0), 3,   NAVY),
        ("BACKGROUND",  (0,0), (-1,-1),      colors.HexColor("#F8FAFF")),
        ("TOPPADDING",  (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING",(0,0), (-1,-1), 12),
    ]))
    return content


def roadmap_table(s):
    data = [
        ["Status", "Batch", "Focus"],
        ["✅ DONE",   "Batch 1 · Now",       "7 agents built · Terminal UI · Dashboard V1"],
        ["🔨 NEXT",   "Batch 2 · +2 weeks",  "Dashboard upgrade · Tabs · Live queries · Creative Health"],
        ["🔨 SOON",   "Batch 3 · +5 weeks",  "Use Case #2 — same architecture, new industry domain"],
        ["🔨 LATER",  "Batch 4 · +8 weeks",  "3–4 polished use cases running in parallel"],
        ["🔨 FUTURE", "Batch 5 · +12 weeks", "Company formation · AI micro-agency · Production"],
    ]
    col_w = [(W - 2*MARGIN - 20) * r for r in [0.12, 0.25, 0.63]]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1, 0),  NAVY),
        ("TEXTCOLOR",    (0,0), (-1, 0),  GOLD),
        ("FONTNAME",     (0,0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1, 0),  8),
        ("FONTNAME",     (0,1), (-1,-1),  "Helvetica"),
        ("FONTSIZE",     (0,1), (-1,-1),  8),
        ("BACKGROUND",   (0,1), (-1, 1),  colors.HexColor("#DCFCE7")),
        ("BACKGROUND",   (0,2), (-1, 2),  colors.HexColor("#F0F4FF")),
        ("BACKGROUND",   (0,3), (-1, 3),  colors.HexColor("#F0F4FF")),
        ("BACKGROUND",   (0,4), (-1, 4),  colors.HexColor("#F0F4FF")),
        ("BACKGROUND",   (0,5), (-1, 5),  colors.HexColor("#F0F4FF")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [colors.HexColor("#F8FAFF"), colors.HexColor("#EEF2FF")]),
        ("GRID",         (0,0), (-1,-1),  0.4, colors.HexColor("#DBEAFE")),
        ("TOPPADDING",   (0,0), (-1,-1),  5),
        ("BOTTOMPADDING",(0,0), (-1,-1),  5),
        ("LEFTPADDING",  (0,0), (-1,-1),  6),
        ("RIGHTPADDING", (0,0), (-1,-1),  6),
        ("ALIGN",        (0,0), (0,-1),   "CENTER"),
        ("VALIGN",       (0,0), (-1,-1),  "MIDDLE"),
    ]))
    return t


def build_pdf():
    doc = SimpleDocTemplate(
        OUT_PATH,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=20*mm,
        bottomMargin=16*mm,
        title="Agent Mode · Batch 1 — I Built a Marketing Analytics Team Out of AI",
        author="Pratkash Yap",
        subject="LinkedIn Article · Build in Public Series",
    )

    s     = build_styles()
    story = []

    # ── Cover block ───────────────────────────────────────────
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        "AGENT MODE  ·  BATCH 1 OF 5", s["tag"]))
    story.append(Paragraph(
        "I built a marketing analytics team that works 24/7, "
        "costs $15/month, and answers in 12 seconds.",
        s["title"]))
    story.append(Paragraph(
        "Here's who's on it — and how I built them in a weekend.", s["subtitle"]))
    story.append(gold_rule())
    story.append(Spacer(1, 3*mm))

    # ── Screenshot 1 — Hero ───────────────────────────────────
    story.append(screenshot_placeholder(s,
        "Terminal Pipeline — All 7 Agents Firing",
        "Run: python3 main.py → type 'demo' → screenshot the full terminal output"))
    story.append(Spacer(1, 4*mm))

    # ── Hook ──────────────────────────────────────────────────
    story.append(Paragraph(
        "Most marketing leaders I know are understaffed on the analytics side. "
        "Not because the budget isn't there. Because the right combination of people "
        "— someone who lives in the data, someone who interprets it, someone who knows "
        "the creatives inside out, someone who manages budget like a chess game — "
        "rarely exists in one team, at one time, at the speed the business actually needs.",
        s["body"]))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "So I stopped looking for that team. I built it.", s["hook"]))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Over one weekend sprint — 6 to 8 hours of focused building — I assembled a "
        "<b>7-person marketing analytics team</b>. Except every person is an AI agent "
        "with a specific role, a defined expertise, and a clear reporting line. "
        "They're always available. They don't have calendar conflicts. "
        "They don't need a brief by Wednesday to have slides ready by Friday.",
        s["body"]))

    # ── The Team ──────────────────────────────────────────────
    story.append(Paragraph("Meet the Team", s["h2"]))
    story.append(thin_rule())

    agents = [
        ("🧠", "Orchestrator Agent", "The Director",
         "Receives every question, classifies intent, routes to the right specialist, "
         "coordinates the team, synthesises the final answer. The only agent the user "
         "ever talks to. It does nothing but orchestration — and it does it perfectly."),

        ("📊", "Data Agent", "The Data Engineer",
         "Converts plain-English questions into SQL, runs them against 112,000 rows of "
         "marketing performance data in real time, and returns clean structured results. "
         "Handles ambiguous time windows. Retries on error. Nobody else touches the database."),

        ("🔍", "Analysis Hub Agent", "The Senior Performance Analyst",
         "Takes raw data and produces structured performance insights: ROAS vs target, "
         "trend direction (improving / declining / stable), anomaly detection, "
         "week-over-week shifts, and objective-aligned evaluation. Uses the more powerful "
         "reasoning model because this is where thinking depth matters."),

        ("🎨", "Creative Analyst Agent", "The Creative Strategist",
         "Plots CTR curves over the lifetime of each format. Detects the fatigue "
         "inflection point — the moment performance starts decaying faster than expected. "
         "Identifies format winners by platform. Flags creatives that need refresh "
         "before ROAS drops. Most teams find out after the fact. This agent finds it while "
         "there is still budget to act."),

        ("💰", "Optimizer Agent", "The Budget Manager",
         "Gives specific budget reallocation recommendations: platform, campaign, "
         "SGD amount, reason, projected ROAS impact. Not vague advice — exact numbers, "
         "before-and-after comparison, respects minimum spend floors, flags risks."),

        ("📈", "Dashboard Agent", "The Reporting Analyst",
         "Generates a live Streamlit dashboard on demand. 4 tabs: Agent Chat, "
         "Performance Dashboard, Creative Health, Data Explorer. WBD-branded design. "
         "Always built from live data. Launches in your browser in seconds."),

        ("⚖️", "Quality Critic Agent", "The Editor",
         "Every insight — before it reaches you — is scored 0–10 across five dimensions: "
         "Specificity, Actionability, Accuracy, Completeness, Tone. "
         "Score 8+: approved. 6–7: enhanced. Below 6: weakest section rewritten. "
         "An AI reviewing AI output. That is where quality control comes from."),
    ]

    for icon, name, role, desc in agents:
        story.append(agent_card(s, icon, name, role, desc))
        story.append(Spacer(1, 4*mm))

    # ── Screenshot 2 ─────────────────────────────────────────
    story.append(screenshot_placeholder(s,
        "Dashboard — Performance Tab with WBD Logo + KPI Cards",
        "Run: venv/bin/streamlit run dashboard_app.py → screenshot the Performance tab"))
    story.append(Spacer(1, 4*mm))

    # ── Architecture ──────────────────────────────────────────
    story.append(Paragraph("The Architecture", s["h2"]))
    story.append(thin_rule())
    story.append(Paragraph(
        "The pattern is called <b>Supervisor / Orchestrator</b>. One central agent "
        "manages the workflow. Specialists do one job each. No agent talks directly "
        "to another — everything routes through the Orchestrator. "
        "It's explicit, debuggable, and production-friendly.",
        s["body"]))
    story.append(Spacer(1, 3*mm))

    arch_lines = [
        "              ┌──────────────────────────────┐",
        "              │        ORCHESTRATOR           │",
        "              │  Routes · Coordinates        │",
        "              │  Synthesises · Delivers      │",
        "              └──────────┬───────────────────┘",
        "                         │",
        "       ┌─────────────────┼──────────────────┐",
        "       ▼                 ▼                  ▼",
        " ┌───────────┐  ┌──────────────┐  ┌───────────────┐",
        " │ DATA      │  │ ANALYSIS HUB │  │  DASHBOARD    │",
        " │ AGENT     │  │    AGENT     │  │    AGENT      │",
        " └───────────┘  └──────┬───────┘  └───────────────┘",
        "                       │",
        "         ┌─────────────┼────────────┐",
        "         ▼             ▼            ▼",
        "  ┌──────────┐ ┌─────────────┐ ┌──────────┐",
        "  │ CREATIVE │ │  OPTIMIZER  │ │ QUALITY  │",
        "  │ ANALYST  │ │   AGENT     │ │  CRITIC  │",
        "  └──────────┘ └─────────────┘ └──────────┘",
    ]
    for line in arch_lines:
        story.append(Paragraph(line, s["code"]))
    story.append(Spacer(1, 2*mm))

    # ── Real example ──────────────────────────────────────────
    story.append(Paragraph("How the Team Works Together — A Real Example", s["h2"]))
    story.append(thin_rule())
    story.append(Paragraph(
        'Here is what happens when you ask: <i>"Why is ROAS declining on video creatives?"</i>',
        s["body"]))
    story.append(Spacer(1, 2*mm))

    pipeline = [
        "You → Orchestrator   (classifies: creative + performance question)",
        "   → Data Agent      (pulls 30-day video creative data — 2.1 seconds)",
        "   → Analysis Hub    (\"ROAS down 0.6x WoW, CTR declining on 3 assets\")",
        "   → Creative Analyst (\"3 assets past fatigue threshold — 21+ days on-air\")",
        "   → Optimizer        (\"Reallocate to Carousel formats — projected +0.4x ROAS\")",
        "   → Quality Critic   (\"✅ Quality Score: 9/10 — Approved\")",
        "   → You              (full structured answer)",
        "",
        "Total time: 11 seconds.",
    ]
    for line in pipeline:
        story.append(Paragraph(line, s["code"]))

    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "The answer your team would have had by Thursday. In 11 seconds.",
        s["quote"]))

    # ── Screenshot 3 ─────────────────────────────────────────
    story.append(screenshot_placeholder(s,
        "Agent Chat Tab — Pipeline Steps Visible on Right",
        "Run a query in dashboard Agent Chat tab → screenshot showing pipeline steps panel"))
    story.append(Spacer(1, 4*mm))

    # ── Why it matters ────────────────────────────────────────
    story.append(Paragraph("Why This Matters Beyond the Technology", s["h2"]))
    story.append(thin_rule())
    story.append(Paragraph(
        "This is not really about AI agents. It is about what happens when you "
        "<b>model a team as a system</b>.",
        s["body"]))
    story.append(Spacer(1, 2*mm))

    points = [
        "Every role has a clear, singular responsibility.",
        "Every handoff is explicit — no Slack threads, no 'did you see my message?'",
        "Every output has a quality gate before it reaches the decision-maker.",
        "The architecture is reusable. Swap the domain knowledge. Keep the pattern.",
    ]
    for p in points:
        story.append(Paragraph(f"→  {p}", s["bullet"]))

    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Building this in AI forced me to think clearly about what each function "
        "<i>actually does</i>, what inputs it needs, and what good output looks like. "
        "That clarity made the AI team better. And it made me think differently about "
        "how <i>any</i> team should be structured.",
        s["body"]))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "Retail. SaaS. E-commerce. Media. FMCG. Swap the agents' domain knowledge. "
        "Keep the orchestration pattern. The framework holds.",
        s["body"]))

    # ── Screenshot 4 ─────────────────────────────────────────
    story.append(screenshot_placeholder(s,
        "Creative Health Tab — Fatigue Heatmap + CTR vs Benchmark",
        "Navigate to Creative Health tab in dashboard → screenshot both charts"))
    story.append(Spacer(1, 4*mm))

    # ── Tech stack ────────────────────────────────────────────
    story.append(Paragraph("What It's Built With", s["h2"]))
    story.append(thin_rule())

    stack_data = [
        ["Layer", "Technology", "Why"],
        ["Language",      "Python 3.12",          "Stability, ecosystem, tooling"],
        ["Database",      "DuckDB 1.5",            "112K rows, millisecond queries, zero infra"],
        ["AI (Reasoning)","Claude Sonnet 4.6",     "Deep analysis, insights, complex reasoning"],
        ["AI (Fast)",     "Claude Haiku 4.5",      "SQL generation, classification, critic scoring"],
        ["Dashboard",     "Streamlit + Plotly",    "Open source, no cloud required, instant deploy"],
        ["Terminal UI",   "Rich",                  "Live agent pipeline display with colour + icons"],
        ["Data",          "Simulated (112K rows)", "4 platforms, 5 business lines, 90 days, SGD"],
    ]
    col_w = [(W - 2*MARGIN - 20) * r for r in [0.22, 0.28, 0.50]]
    t = Table(stack_data, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1, 0), NAVY),
        ("TEXTCOLOR",    (0,0), (-1, 0), GOLD),
        ("FONTNAME",     (0,0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1, 0), 8),
        ("FONTNAME",     (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",     (0,1), (-1,-1), 8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, colors.HexColor("#F0F4FF")]),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#DBEAFE")),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(t)
    story.append(Spacer(1, 4*mm))

    # ── Honest limitations ────────────────────────────────────
    story.append(Paragraph("What V1 Doesn't Do Yet (And That's OK)", s["h2"]))
    story.append(thin_rule())
    story.append(Paragraph(
        "This is a working V1, not a finished product. The honest limitations:",
        s["body"]))

    limits = [
        "Memory doesn't persist across sessions — ask the same thing twice, it starts fresh.",
        "Complex multi-part questions sometimes need better routing logic.",
        "The dashboard is regenerated each time, not truly real-time streaming.",
        "No authentication, user management, or multi-tenant support yet.",
    ]
    for l in limits:
        story.append(Paragraph(f"·  {l}", s["bullet"]))

    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "But improving a working team is very different from building one from scratch. "
        "The foundation is solid. Everything else is iteration.",
        s["body"]))

    # ── Roadmap ───────────────────────────────────────────────
    story.append(Paragraph("The Roadmap", s["h2"]))
    story.append(thin_rule())
    story.append(roadmap_table(s))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "I am documenting the full build — architecture, decisions, failures, "
        "breakthroughs — in batches as the project grows. <b>Not when it is finished. "
        "Because the journey is the content.</b>",
        s["body"]))

    # ── CTA ───────────────────────────────────────────────────
    story.append(Spacer(1, 4*mm))
    story.append(gold_rule())
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "If you run a marketing team and have a question you have been waiting "
        "three days to get answered — drop it in the comments. "
        "I will run it through the system and share what comes back.",
        s["cta"]))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Follow for Batch 2 — dashboard upgrade, second use case, and what breaks next.",
        s["cta"]))
    story.append(Spacer(1, 3*mm))

    # Tags
    story.append(Paragraph(
        "#AIMarketing  #MarketingAnalytics  #MultiAgentAI  #BuildingInPublic  "
        "#MarketingTech  #AIAgents  #AgentMode  #WeekendProject  #LLM  #Anthropic",
        s["tag"]))

    # ── Screenshot notes page ─────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Screenshot Guide — Before You Publish", s["h2"]))
    story.append(gold_rule())
    story.append(Paragraph(
        "Take these 4 screenshots and replace the placeholder boxes above "
        "before publishing the article.", s["body"]))
    story.append(Spacer(1, 3*mm))

    shots = [
        ("Screenshot 1 — Terminal Pipeline",
         "cd ~/Desktop/marketing-analytics-agent",
         "source venv/bin/activate",
         "python3 main.py",
         "→ Type: demo",
         "→ Let all 5 queries run. Scroll up. Screenshot the full terminal showing agent steps."),
        ("Screenshot 2 — Dashboard Performance Tab",
         "venv/bin/streamlit run dashboard_app.py",
         "→ Navigate to: 📊 Performance Dashboard tab",
         "→ Screenshot: WBD logo header + all 6 KPI cards + daily trend chart"),
        ("Screenshot 3 — Agent Chat with Pipeline",
         "→ In dashboard, click: 💬 Agent Chat tab",
         "→ Ask: 'Which platforms are underperforming vs ROAS target?'",
         "→ Screenshot: chat response + pipeline steps showing on the right"),
        ("Screenshot 4 — Creative Health Tab",
         "→ In dashboard, click: 🎨 Creative Health tab",
         "→ Screenshot: ROAS by format + CTR vs benchmark + fatigue table"),
    ]

    for shot in shots:
        title = shot[0]
        steps = shot[1:]
        story.append(Paragraph(title, s["h3"]))
        for step in steps:
            story.append(Paragraph(f"   {step}", s["code"]))
        story.append(Spacer(1, 4*mm))

    story.append(thin_rule())
    story.append(Paragraph(
        "Tip: Use CMD+SHIFT+4 on Mac to take a precise screenshot. "
        "Crop tightly. Dark background screenshots look great on LinkedIn.",
        s["body"]))

    # ── Build ──────────────────────────────────────────────────
    doc.build(story, canvasmaker=WBDCanvas)
    print(f"PDF generated: {OUT_PATH}")
    return OUT_PATH


if __name__ == "__main__":
    build_pdf()
