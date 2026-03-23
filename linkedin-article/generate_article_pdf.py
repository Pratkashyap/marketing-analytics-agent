"""
LinkedIn Article PDF Generator
Warner Bros. Discovery Singapore — AI Marketing Analytics Agent
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus.flowables import Flowable
import os

# ── Paths ─────────────────────────────────────────────────────
BASE   = os.path.dirname(os.path.abspath(__file__))
SS_DIR = os.path.join(BASE, "screenshots")
OUT    = os.path.join(BASE, "WBD_AI_Marketing_Agent.pdf")

# ── Brand colours ─────────────────────────────────────────────
NAVY   = HexColor("#003087")
GOLD   = HexColor("#C8960C")
LIGHT  = HexColor("#EEF2FF")
MUTED  = HexColor("#64748B")
TEXT   = HexColor("#0F172A")
GREEN  = HexColor("#16A34A")
RED    = HexColor("#DC2626")
BGPAGE = HexColor("#F8F9FC")
BORDER = HexColor("#E2E8F0")
WHITE  = white

W, H = A4   # 210 × 297 mm

# ── Styles ────────────────────────────────────────────────────
def styles():
    return {
        "title": ParagraphStyle("title",
            fontName="Helvetica-Bold", fontSize=26, leading=32,
            textColor=WHITE, alignment=TA_LEFT, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle",
            fontName="Helvetica", fontSize=13, leading=18,
            textColor=HexColor("#C7D2FE"), alignment=TA_LEFT),
        "h1": ParagraphStyle("h1",
            fontName="Helvetica-Bold", fontSize=17, leading=22,
            textColor=NAVY, spaceBefore=18, spaceAfter=6),
        "h2": ParagraphStyle("h2",
            fontName="Helvetica-Bold", fontSize=13, leading=18,
            textColor=NAVY, spaceBefore=12, spaceAfter=4),
        "h3": ParagraphStyle("h3",
            fontName="Helvetica-Bold", fontSize=11, leading=15,
            textColor=TEXT, spaceBefore=8, spaceAfter=3),
        "body": ParagraphStyle("body",
            fontName="Helvetica", fontSize=10, leading=16,
            textColor=TEXT, alignment=TA_JUSTIFY, spaceAfter=6),
        "bullet": ParagraphStyle("bullet",
            fontName="Helvetica", fontSize=10, leading=15,
            textColor=TEXT, leftIndent=14, spaceAfter=3,
            bulletIndent=4),
        "code": ParagraphStyle("code",
            fontName="Courier", fontSize=9, leading=13,
            textColor=HexColor("#1E3A8A"), backColor=LIGHT,
            leftIndent=10, rightIndent=10, spaceAfter=4,
            spaceBefore=4, borderPadding=(6, 8, 6, 8)),
        "caption": ParagraphStyle("caption",
            fontName="Helvetica-Oblique", fontSize=9, leading=13,
            textColor=MUTED, alignment=TA_CENTER, spaceAfter=8),
        "kpi_label": ParagraphStyle("kpi_label",
            fontName="Helvetica-Bold", fontSize=9, leading=12,
            textColor=MUTED, alignment=TA_CENTER),
        "kpi_val": ParagraphStyle("kpi_val",
            fontName="Helvetica-Bold", fontSize=18, leading=22,
            textColor=NAVY, alignment=TA_CENTER),
        "quote": ParagraphStyle("quote",
            fontName="Helvetica-Oblique", fontSize=11, leading=17,
            textColor=NAVY, leftIndent=16, rightIndent=16,
            spaceBefore=8, spaceAfter=8,
            borderColor=GOLD, borderWidth=3, borderPadding=(8,10,8,10)),
        "tag": ParagraphStyle("tag",
            fontName="Helvetica-Bold", fontSize=8, leading=11,
            textColor=NAVY, backColor=LIGHT,
            borderRadius=4, borderPadding=(2, 5, 2, 5)),
    }

S = styles()

# ── Flowable: coloured section banner ─────────────────────────
class SectionBanner(Flowable):
    def __init__(self, text, color=NAVY, text_color=WHITE, h=22):
        super().__init__()
        self.text = text
        self.color = color
        self.text_color = text_color
        self.bh = h
        self.width = W - 40*mm

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.roundRect(0, 0, self.width, self.bh, 4, fill=1, stroke=0)
        self.canv.setFillColor(self.text_color)
        self.canv.setFont("Helvetica-Bold", 11)
        self.canv.drawString(10, 6, self.text)

    def wrap(self, *args):
        return self.width, self.bh + 6

# ── Flowable: architecture diagram ────────────────────────────
class ArchDiagram(Flowable):
    def __init__(self, width, height=260):
        super().__init__()
        self._width = width
        self._height = height

    def wrap(self, *args):
        return self._width, self._height

    def draw(self):
        c = self.canv
        W = self._width
        H = self._height

        # Background
        c.setFillColor(HexColor("#F0F4FF"))
        c.roundRect(0, 0, W, H, 8, fill=1, stroke=0)

        # Title
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(W/2, H - 18, "7-AGENT PIPELINE ARCHITECTURE")

        # Arrow helper
        def arrow(x1, y1, x2, y2):
            import math
            c.setStrokeColor(HexColor("#94A3B8"))
            c.setLineWidth(1.2)
            c.line(x1, y1, x2, y2)
            # arrowhead using path object
            c.setFillColor(HexColor("#94A3B8"))
            angle = math.atan2(y2-y1, x2-x1)
            size = 5
            p = c.beginPath()
            p.moveTo(x2, y2)
            p.lineTo(x2 - size*math.cos(angle-0.4), y2 - size*math.sin(angle-0.4))
            p.lineTo(x2 - size*math.cos(angle+0.4), y2 - size*math.sin(angle+0.4))
            p.close()
            c.drawPath(p, fill=1, stroke=0)

        def box(x, y, w, h, label, sublabel="", color=NAVY, text_color=WHITE, radius=6):
            c.setFillColor(color)
            c.roundRect(x, y, w, h, radius, fill=1, stroke=0)
            # label
            c.setFillColor(text_color)
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(x + w/2, y + h/2 + (5 if sublabel else 2), label)
            if sublabel:
                c.setFont("Helvetica", 7)
                c.setFillColor(HexColor("#C7D2FE") if text_color == WHITE else MUTED)
                c.drawCentredString(x + w/2, y + h/2 - 7, sublabel)

        # ── Row 1: User Query → Orchestrator ──────────────────
        y1 = H - 60
        # User query
        box(8, y1, 70, 28, "User Query", "Natural Language", HexColor("#1D4ED8"), WHITE)
        arrow(78, y1+14, 108, y1+14)
        # Orchestrator
        box(108, y1, 90, 28, "Orchestrator", "Intent + Routing", NAVY, WHITE)

        # ── Row 2: 3 Specialist Agents ────────────────────────
        y2 = y1 - 70
        # Arrows from Orchestrator to agents
        cx = 108 + 45  # orchestrator center x
        arrow(cx, y1, cx, y2+28)  # down to Analysis Hub

        # Agent boxes
        bw = 80; bh = 32; gap = 12
        total = 3*bw + 2*gap
        sx = (W - total) / 2

        box(sx, y2, bw, bh, "Data Agent", "SQL + DuckDB", HexColor("#0891B2"), WHITE)
        box(sx+bw+gap, y2, bw, bh, "Analysis Hub", "Claude Sonnet", NAVY, WHITE)
        box(sx+2*(bw+gap), y2, bw, bh, "Creative Analyst", "Fatigue + CTR", HexColor("#0891B2"), WHITE)

        # Arrows from orchestrator to left/right agents
        arrow(cx, y1, sx+bw/2, y2+bh)
        arrow(cx, y1, sx+2*(bw+gap)+bw/2, y2+bh)

        # ── Row 3: Optimizer + Quality Critic ─────────────────
        y3 = y2 - 70
        bw2 = 90
        sx2 = W/2 - bw2 - 8
        box(sx2, y3, bw2, bh, "Optimizer", "Budget + ROAS", HexColor("#7C3AED"), WHITE)
        box(sx2+bw2+16, y3, bw2, bh, "Quality Critic", "Score + Approve", GREEN, WHITE)

        # Arrows from specialist agents down to optimizer/critic
        for ax in [sx+bw/2, sx+bw+gap+bw/2, sx+2*(bw+gap)+bw/2]:
            arrow(ax, y2, sx2+bw/2, y3+bh)

        for ax in [sx+bw/2, sx+bw+gap+bw/2, sx+2*(bw+gap)+bw/2]:
            arrow(ax, y2, sx2+bw2+16+bw2/2, y3+bh)

        # ── Row 4: Response ───────────────────────────────────
        y4 = y3 - 60
        rw = 120
        rx = W/2 - rw/2
        arrow(sx2+bw2/2, y3, rx+rw/2, y4+28)
        arrow(sx2+bw2+16+bw2/2, y3, rx+rw/2, y4+28)
        box(rx, y4, rw, 28, "Dashboard Response", "Formatted + Scored", GREEN, WHITE)

        # ── Tech stack labels ─────────────────────────────────
        y_tech = y4 - 28
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.5)
        tech_items = [
            ("Python 3.12", 0.05),
            ("Anthropic Claude API", 0.22),
            ("DuckDB 1.5  · 112K rows", 0.48),
            ("Streamlit 1.55", 0.75),
            ("ReportLab", 0.92),
        ]
        for label, xf in tech_items:
            c.drawString(W*xf, y_tech, label)

        c.setStrokeColor(BORDER)
        c.setLineWidth(0.5)
        c.line(10, y_tech+10, W-10, y_tech+10)


# ── Flowable: stat card row ───────────────────────────────────
class StatRow(Flowable):
    def __init__(self, stats, width):
        super().__init__()
        self._width = width
        self.stats = stats  # list of (label, value, color)

    def wrap(self, *args):
        return self._width, 58

    def draw(self):
        c = self.canv
        n = len(self.stats)
        cw = (self._width - (n-1)*8) / n
        for i, (label, val, color) in enumerate(self.stats):
            x = i*(cw+8)
            c.setFillColor(color)
            c.roundRect(x, 0, cw, 52, 5, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 15)
            c.drawCentredString(x+cw/2, 28, val)
            c.setFont("Helvetica", 8)
            c.drawCentredString(x+cw/2, 14, label)


# ── Page template ─────────────────────────────────────────────
class DocTemplate(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._page_num = 0

    def handle_pageBegin(self):
        super().handle_pageBegin()
        self._page_num += 1

def on_first_page(canv, doc):
    """Full navy cover page header"""
    canv.saveState()
    # Navy header band
    canv.setFillColor(NAVY)
    canv.rect(0, H - 80*mm, W, 80*mm, fill=1, stroke=0)
    # Gold accent line
    canv.setFillColor(GOLD)
    canv.rect(0, H - 80*mm, W, 2.5, fill=1, stroke=0)
    # WBD text
    canv.setFillColor(WHITE)
    canv.setFont("Helvetica-Bold", 22)
    canv.drawString(20*mm, H - 28*mm, "WARNER BROS. DISCOVERY")
    canv.setFont("Helvetica", 11)
    canv.setFillColor(HexColor("#C7D2FE"))
    canv.drawString(20*mm, H - 38*mm, "Singapore · Marketing Analytics")
    # Title
    canv.setFillColor(WHITE)
    canv.setFont("Helvetica-Bold", 20)
    canv.drawString(20*mm, H - 54*mm, "Building a 7-Agent AI Marketing Analytics System")
    canv.setFont("Helvetica", 11)
    canv.setFillColor(HexColor("#A5B4FC"))
    canv.drawString(20*mm, H - 64*mm,
        "From natural language question to actionable insight in under a minute")
    # Footer
    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 8)
    canv.drawString(20*mm, 12*mm, "Pratik Kashyap  ·  March 2026  ·  Built with Python, Claude API, DuckDB, Streamlit")
    canv.restoreState()

def on_later_pages(canv, doc):
    canv.saveState()
    # Top bar
    canv.setFillColor(NAVY)
    canv.rect(0, H - 14*mm, W, 14*mm, fill=1, stroke=0)
    canv.setFillColor(WHITE)
    canv.setFont("Helvetica-Bold", 8)
    canv.drawString(20*mm, H - 9*mm, "WBD Singapore · AI Marketing Analytics Agent")
    canv.setFont("Helvetica", 8)
    canv.drawRightString(W - 20*mm, H - 9*mm, f"Page {doc.page}")
    # Bottom
    canv.setFillColor(BORDER)
    canv.rect(0, 0, W, 12*mm, fill=1, stroke=0)
    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 7.5)
    canv.drawString(20*mm, 4*mm, "Built by Pratik Kashyap · github.com/Pratkashyap/marketing-analytics-agent")
    canv.drawRightString(W - 20*mm, 4*mm, "© 2026 · Internal Prototype · Not for Distribution")
    canv.restoreState()

# ── Screenshot helper ──────────────────────────────────────────
def screenshot(name, caption, max_w=None, max_h=None):
    path = os.path.join(SS_DIR, name)
    if not os.path.exists(path):
        return []
    max_w = max_w or (W - 40*mm)
    max_h = max_h or 90*mm
    img = Image(path)
    iw, ih = img.imageWidth, img.imageHeight
    ratio = iw / ih
    if iw > max_w:
        iw = max_w; ih = iw / ratio
    if ih > max_h:
        ih = max_h; iw = ih * ratio
    img.drawWidth  = iw
    img.drawHeight = ih
    img.hAlign = "CENTER"
    return [img, Paragraph(caption, S["caption"]), Spacer(1, 4)]

# ── Build story ────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUT,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=88*mm, bottomMargin=22*mm,   # big top margin for cover header
        title="WBD AI Marketing Analytics Agent",
        author="Pratik Kashyap",
    )

    story = []
    P = lambda txt, style=S["body"]: Paragraph(txt, style)
    SP = lambda h=6: Spacer(1, h)
    HR = lambda: HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=8, spaceBefore=4)

    # ═══════════════════════════════════════════════════════════
    # PAGE 1 — INTRO
    # ═══════════════════════════════════════════════════════════

    # Hook
    story.append(P(
        "<b>What if your entire marketing analytics team — data engineer, analyst, creative "
        "strategist, budget optimizer, and editor — ran automatically, answered any question "
        "in plain English, and cost less than a monthly coffee run?</b>",
        S["quote"]
    ))
    story.append(SP(8))

    story.append(P(
        "That is exactly what I built. Over the past few months, I designed and deployed a "
        "<b>7-agent AI pipeline</b> that connects directly to 112,000 rows of live marketing "
        "performance data for Warner Bros. Discovery's Singapore operation. You type a question. "
        "The system routes it through a chain of specialized AI agents, each doing one job well, "
        "and returns a structured, quality-checked analysis — usually in under a minute.",
        S["body"]
    ))
    story.append(SP(6))

    # Quick stats
    story.append(StatRow([
        ("Live data rows",  "112K",    NAVY),
        ("AI Agents",       "7",       HexColor("#1D4ED8")),
        ("Avg response",    "~28s",    GREEN),
        ("API cost/query",  "~$0.03",  HexColor("#7C3AED")),
        ("Lines of Python", "~2,400",  MUTED),
    ], W - 40*mm))
    story.append(SP(14))

    # ── WHY ──────────────────────────────────────────────────
    story.append(SectionBanner("  THE PROBLEM — Why build this?"))
    story.append(SP(8))
    story.append(P(
        "Traditional marketing analytics workflows have three bottlenecks: <b>(1)</b> a data analyst "
        "has to write SQL, <b>(2)</b> an analyst has to interpret the numbers, and <b>(3)</b> a strategist "
        "has to turn insights into recommendations. Then someone edits the output for quality. "
        "That chain takes hours or days. A single ad-hoc question — 'Which TikTok creatives "
        "are fatiguing?' — requires at minimum three people, three tools, and half a working day.",
        S["body"]
    ))
    story.append(SP(4))
    story.append(P(
        "The alternative: describe each specialist as an AI agent, wire them together, and let "
        "any stakeholder ask questions directly in plain English. The system handles the rest.",
        S["body"]
    ))
    story.append(SP(12))

    # ═══════════════════════════════════════════════════════════
    # PAGE 2 — ARCHITECTURE
    # ═══════════════════════════════════════════════════════════
    story.append(SectionBanner("  THE ARCHITECTURE — How it works"))
    story.append(SP(10))

    story.append(ArchDiagram(W - 40*mm, height=265))
    story.append(SP(6))
    story.append(P(
        "Figure 1: The full agent pipeline. Every user question flows top-to-bottom through "
        "intent classification, specialist agents, and quality review before a response is returned.",
        S["caption"]
    ))
    story.append(SP(10))

    story.append(P("Each agent has a single, well-defined responsibility:", S["body"]))
    story.append(SP(4))

    agents = [
        ("Orchestrator",     NAVY,                    "Classifies the intent (performance / creative / budget / trend), decides which specialist agents to invoke, and assembles the final response."),
        ("Data Agent",       HexColor("#0891B2"),      "Translates natural language into DuckDB SQL, executes against 112K rows of fact_daily_performance, and returns structured results with a plain-English data summary."),
        ("Analysis Hub",     HexColor("#1D4ED8"),      "Receives the raw data and runs deep analysis — trend detection, variance calculations, statistical anomalies — using Claude Sonnet 4.6 as the reasoning engine."),
        ("Creative Analyst", HexColor("#0891B2"),      "Evaluates CTR trend curves for each creative, detects fatigue signals (>20% CTR drop), benchmarks against industry norms by format and platform."),
        ("Optimizer",        HexColor("#7C3AED"),      "Takes the analysis and produces concrete budget reallocation recommendations, ranked by ROAS impact and reallocatable spend."),
        ("Quality Critic",   HexColor("#16A34A"),      "Scores the final response out of 10 on accuracy, actionability, and relevance. Responses below 7/10 are flagged and rewritten before delivery."),
        ("Dashboard Agent",  HexColor("#D97706"),      "Generates the Streamlit dashboard code, manages charts using Plotly, and handles the real-time pipeline display panel."),
    ]

    for name, color, desc in agents:
        row_data = [[
            Paragraph(f"<b>{name}</b>", ParagraphStyle("an",
                fontName="Helvetica-Bold", fontSize=9,
                textColor=WHITE, backColor=color,
                borderPadding=(4,6,4,6), leading=13)),
            Paragraph(desc, ParagraphStyle("ad",
                fontName="Helvetica", fontSize=9, leading=13,
                textColor=TEXT))
        ]]
        t = Table(row_data, colWidths=[36*mm, W - 40*mm - 36*mm - 2*mm])
        t.setStyle(TableStyle([
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING",  (0,0), (0,0),  4),
            ("RIGHTPADDING", (0,0), (0,0),  6),
            ("LEFTPADDING",  (1,0), (1,0),  8),
            ("BOTTOMPADDING",(0,0), (-1,-1), 5),
            ("TOPPADDING",   (0,0), (-1,-1), 5),
            ("LINEBELOW",    (0,0), (-1,-1), 0.5, BORDER),
        ]))
        story.append(t)

    story.append(SP(14))

    # ═══════════════════════════════════════════════════════════
    # PAGE 3 — TECH STACK
    # ═══════════════════════════════════════════════════════════
    story.append(SectionBanner("  THE TECH STACK — What it runs on"))
    story.append(SP(10))

    tech = [
        ["Layer",          "Technology",           "Version",  "Role"],
        ["Language",       "Python",                "3.12",    "Entire backend + agents"],
        ["AI / LLM",       "Anthropic Claude API",  "Sonnet 4.6 / Haiku 4.5",
                                                               "Reasoning, SQL gen, critique"],
        ["Database",       "DuckDB",                "1.5.0",   "In-process SQL, 112K rows, <20ms"],
        ["Dashboard",      "Streamlit",             "1.55",    "Web UI, tabs, charts, chat"],
        ["Charts",         "Plotly",                "6.6",     "Bar, pie, heatmap, scatter"],
        ["Data",           "Pandas",                "2.3",     "DataFrame transforms"],
        ["PDF",            "ReportLab",             "4.4",     "Article and report generation"],
        ["Config",         "python-dotenv",         "1.1",     ".env API key management"],
        ["Version Control","GitHub",                "—",       "Private repo: Pratkashyap"],
    ]
    col_ws = [28*mm, 48*mm, 42*mm, W - 40*mm - 118*mm]
    t = Table(tech, colWidths=col_ws, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT]),
        ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 7),
    ]))
    story.append(t)
    story.append(SP(10))

    # Code snippet
    story.append(P("Core agent invocation — how a question becomes a pipeline run:", S["h3"]))
    story.append(SP(4))

    code_text = (
        "# From dashboard_app.py\n"
        "result = Orchestrator().run(\n"
        '    query,             # "Which TikTok creatives are fatiguing?"\n'
        "    verbose=False,\n"
        "    on_status=on_status  # live pipeline callback\n"
        ")\n"
        'response = result.get("response")  # quality-checked output\n\n'
        "# on_status fires for each agent step:\n"
        "# Orchestrator · classifying  →  Data Agent · sql_generated\n"
        "# Analysis Hub · analysing    →  Quality Critic · done [4.4s]\n"
        "# Total: 27.2s"
    )
    story.append(Paragraph(code_text.replace("\n","<br/>").replace(" ", "&nbsp;"), S["code"]))
    story.append(SP(10))

    # Data schema
    story.append(P("Database schema — 5 tables, 112K rows of simulated SG marketing data:", S["h3"]))
    story.append(SP(4))

    schema_data = [
        ["Table",                    "Key Columns",                              "Rows"],
        ["fact_daily_performance",   "date, campaign_id, platform_id, business_line,\nspend, revenue, roas, impressions, clicks, ctr", "112,362"],
        ["dim_campaign",             "campaign_id, campaign_name, roas_target, status",  "48"],
        ["dim_platform",             "platform_id, platform_name (Meta/Google/TikTok/YouTube)", "4"],
        ["dim_creative",             "creative_id, format, style, is_video",               "96"],
        ["dim_ad_set",               "ad_set_id, audience_type, age_range, daily_budget",  "192"],
    ]
    t = Table(schema_data, colWidths=[46*mm, W-40*mm-70*mm, 24*mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT]),
        ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 7),
        ("FONTNAME",      (0,1), (0,-1),  "Courier-Bold"),
        ("TEXTCOLOR",     (0,1), (0,-1),  HexColor("#1D4ED8")),
    ]))
    story.append(t)

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # PAGE 4 — DASHBOARD SCREENSHOTS
    # ═══════════════════════════════════════════════════════════
    story.append(SectionBanner("  THE DASHBOARD — Live screenshots from localhost:8501"))
    story.append(SP(10))

    story.append(P(
        "The dashboard runs entirely locally via Streamlit. Every chart queries DuckDB directly "
        "on each page load — no cached API calls, no stale data. The Agent Chat tab routes "
        "questions through the full 7-agent pipeline and shows per-agent timings in real time.",
        S["body"]
    ))
    story.append(SP(8))

    # Screenshot: Agent Chat with response
    story.append(P("Agent Chat — Question answered, pipeline timings visible on the right", S["h2"]))
    story += screenshot("agent_chat_response.png",
        "Agent Chat tab: The question 'How are all business lines performing vs ROAS target?' "
        "returned a quality-scored analysis in 27.2s. Pipeline panel shows each agent's "
        "step and individual timing (Data Agent 8.2s, Analysis Hub 12.7s, Quality Critic 4.4s).",
        max_h=110*mm)
    story.append(SP(6))

    # Screenshot: Performance Dashboard
    story.append(P("Performance Dashboard — Live KPIs, spend trend, platform split, ROAS vs targets", S["h2"]))
    story += screenshot("performance_dashboard.png",
        "Performance Dashboard: SGD 18M spend, 65.5M revenue, 3.63x blended ROAS over 30 days. "
        "Bar + line chart shows daily spend vs ROAS. Donut chart shows platform budget split. "
        "Horizontal bar chart compares each business line's actual ROAS vs target — "
        "red = below target, green = above.",
        max_h=110*mm)

    story.append(PageBreak())

    # Screenshot: Creative Health
    story.append(P("Creative Health — Format ROAS, CTR benchmarks, fatigue analysis, heatmap", S["h2"]))
    story += screenshot("creative_health.png",
        "Creative Health tab: Left chart shows ROAS by creative format (Carousel leads at 4.07x). "
        "Right chart shows CTR vs industry benchmark — all formats outperforming benchmarks "
        "by >124%. Below: creative fatigue table and Platform × Format CTR heatmap.",
        max_h=110*mm)
    story.append(SP(10))

    # ═══════════════════════════════════════════════════════════
    # PAGE 5 — HOW A QUERY FLOWS + RESULTS
    # ═══════════════════════════════════════════════════════════
    story.append(SectionBanner("  END-TO-END — Tracing one query through the system"))
    story.append(SP(10))

    story.append(P(
        '<b>Input:</b> "How are all business lines performing vs ROAS target this month?"',
        S["body"]
    ))
    story.append(SP(6))

    steps = [
        ("1",  NAVY,                  "Orchestrator classifies intent",
         "Identifies this as a performance + ROAS comparison query. Routes to Data Agent + Analysis Hub."),
        ("2",  HexColor("#0891B2"),    "Data Agent writes SQL",
         "SELECT business_line, ROUND(SUM(revenue)/NULLIF(SUM(spend),0),2) AS roas "
         "FROM fact_daily_performance WHERE date >= CAST(CURRENT_DATE - INTERVAL 30 DAY AS VARCHAR) "
         "GROUP BY business_line ORDER BY roas DESC  →  Executes in <20ms on DuckDB"),
        ("3",  HexColor("#1D4ED8"),    "Analysis Hub interprets results",
         "Licensing & Merch: 6.68x (+4.18x vs 2.5 target)  |  WB Games: 6.07x (+2.57x)  |  "
         "Home Entertainment: 3.27x (+0.27x)  |  Theatrical: 2.25x (−1.25x)  |  "
         "Max Streaming: 1.62x (−2.38x)  →  3/5 lines on target, 2 need intervention."),
        ("4",  HexColor("#7C3AED"),    "Optimizer generates recommendations",
         "Reallocate SGD 2.1M from Max Streaming campaigns into Licensing & Merch TikTok "
         "and WB Games YouTube — projected blended ROAS improvement: 3.63x → 4.2x."),
        ("5",  HexColor("#16A34A"),    "Quality Critic scores the response",
         "Score: 9/10 — Approved. Deduction: ROAS targets not explicitly stated inline. "
         "Response passes quality gate and is delivered to dashboard."),
        ("✓",  GREEN,                  "Dashboard displays result in under a minute",
         "Full analysis, agent pipeline log with per-step timings, and actionable "
         "budget recommendation — all from a single plain-English question."),
    ]

    for num, color, title, detail in steps:
        row = [[
            Paragraph(f"<b>{num}</b>", ParagraphStyle("sn",
                fontName="Helvetica-Bold", fontSize=12,
                textColor=WHITE, alignment=TA_CENTER, leading=14)),
            [
                Paragraph(f"<b>{title}</b>", ParagraphStyle("st",
                    fontName="Helvetica-Bold", fontSize=10, leading=13,
                    textColor=color)),
                Paragraph(detail, ParagraphStyle("sd",
                    fontName="Helvetica", fontSize=9, leading=13,
                    textColor=TEXT)),
            ]
        ]]
        t = Table(row, colWidths=[14*mm, W-40*mm-16*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (0,0),  color),
            ("BACKGROUND",    (1,0), (1,0),  WHITE),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING",   (0,0), (0,0),  4),
            ("LEFTPADDING",   (1,0), (1,0),  10),
            ("LINEBELOW",     (0,0), (-1,-1), 0.5, BORDER),
            ("ROUNDEDCORNERS",(0,0), (0,0),  4),
        ]))
        story.append(t)
        story.append(SP(4))

    story.append(SP(12))

    # ═══════════════════════════════════════════════════════════
    # PAGE 6 — KEY LEARNINGS + WHAT'S NEXT
    # ═══════════════════════════════════════════════════════════
    story.append(SectionBanner("  WHAT I LEARNED — Key technical insights"))
    story.append(SP(10))

    learnings = [
        ("Agent specialisation beats monolithic prompts",
         "A single 'do everything' Claude prompt produces mediocre results. Breaking the "
         "pipeline into focused agents — each with a narrow task and specific system prompt — "
         "dramatically improves accuracy and auditability. The Quality Critic agent alone "
         "raised response quality scores from ~6.5/10 to ~8.9/10 on average."),
        ("DuckDB is the right tool for this workload",
         "112K rows, in-process, zero latency. The Data Agent generates SQL, runs it "
         "directly in DuckDB (no server, no network), and returns a DataFrame in under 20ms. "
         "For prototyping analytics pipelines on structured data, DuckDB eliminates the "
         "entire data infrastructure layer."),
        ("Streamlit session state requires strict discipline",
         "The most time-consuming bugs were all Streamlit state issues. Using value= "
         "together with key= on a widget resets user input on every rerun. Text inputs "
         "must use key= only, with session state pre-set via a clear flag before the "
         "widget renders. st.form() helps but introduces its own constraints."),
        ("Schema correctness is everything",
         "Every chart was blank for two hours because the SQL said FROM fact_performance "
         "when the actual table is fact_daily_performance. When LLMs generate SQL against "
         "your schema, make sure the schema given to the agent exactly matches the real "
         "table and column names — even a single character off breaks everything silently."),
        ("Cost is negligible at this scale",
         "A full 7-agent pipeline run (Sonnet 4.6 for reasoning, Haiku 4.5 for "
         "classification) costs approximately SGD 0.04 per query. At 50 queries/day that "
         "is SGD 60/month — less than one analyst hour. The ROI case is not even close."),
    ]

    for i, (title, body) in enumerate(learnings):
        story.append(KeepTogether([
            Paragraph(f"<b>{i+1}.  {title}</b>", S["h3"]),
            Paragraph(body, S["body"]),
            SP(6),
        ]))

    story.append(HR())
    story.append(SP(6))

    story.append(SectionBanner("  WHAT'S NEXT — Roadmap", color=HexColor("#7C3AED")))
    story.append(SP(10))

    roadmap = [
        ["Priority", "Feature",                     "Status"],
        ["1",  "Real-time agent status updates via WebSocket",          "Planned"],
        ["2",  "Connect to actual Meta / Google Ads APIs",              "Planned"],
        ["3",  "Automated weekly performance report PDF via email",     "In Design"],
        ["4",  "Natural language budget scenario modelling",            "Research"],
        ["5",  "Multi-market support (SG + AU + MY)",                   "Backlog"],
        ["6",  "Slack integration — push alerts to channel",            "Backlog"],
    ]
    t = Table(roadmap, colWidths=[16*mm, W-40*mm-56*mm, 40*mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  HexColor("#7C3AED")),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT]),
        ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("ALIGN",         (0,0), (0,-1),  "CENTER"),
        ("ALIGN",         (2,0), (2,-1),  "CENTER"),
    ]))
    story.append(t)
    story.append(SP(16))

    # Closing
    story.append(P(
        "This is a working prototype, not a polished product. Every component — agents, "
        "SQL, dashboard, this article — was built iteratively"
        "using only open tools and the Claude API. The goal was to prove that a single person "
        "with modern AI tooling can replace a workflow that used to require a team of five.",
        S["body"]
    ))
    story.append(SP(6))
    story.append(P(
        "<b>Code is on GitHub:</b> github.com/Pratkashyap/marketing-analytics-agent  "
        "(private — DM for access)<br/>"
        "<b>Stack:</b> Python 3.12 · Anthropic Claude API · DuckDB · Streamlit · Plotly · ReportLab",
        ParagraphStyle("closing",
            fontName="Helvetica", fontSize=10, leading=16,
            textColor=NAVY, backColor=LIGHT,
            borderPadding=(10,12,10,12), spaceAfter=8)
    ))

    # Build
    doc.build(story,
              onFirstPage=on_first_page,
              onLaterPages=on_later_pages)
    print(f"PDF generated: {OUT}")

if __name__ == "__main__":
    build()
