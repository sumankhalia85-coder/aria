import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

# Color palette
DEEP = colors.HexColor("#050D1A")
NAVY = colors.HexColor("#0A1628")
ELECTRIC = colors.HexColor("#00D4FF")
ELECTRIC_DIM = colors.HexColor("#003D4D")
AMBER = colors.HexColor("#FF8C00")
RED = colors.HexColor("#FF3B3B")
GREEN = colors.HexColor("#00C896")
PURPLE = colors.HexColor("#7C3AED")
LIGHT = colors.HexColor("#E8F4F8")
MID = colors.HexColor("#94A3B8")
WHITE = colors.white

SEVERITY_COLORS = {
    "critical": colors.HexColor("#FF3B3B"),
    "high": colors.HexColor("#FF8C00"),
    "medium": colors.HexColor("#F59E0B"),
    "low": colors.HexColor("#00C896"),
}

PRIORITY_COLORS = {
    "must-have": colors.HexColor("#FF3B3B"),
    "should-have": colors.HexColor("#FF8C00"),
    "nice-to-have": colors.HexColor("#00C896"),
}

def build_ux_report(report) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()

    def style(name, **kwargs):
        return ParagraphStyle(name, parent=styles["Normal"], **kwargs)

    title_s = style("T", fontSize=28, textColor=WHITE, fontName="Helvetica-Bold",
        spaceAfter=4, alignment=TA_LEFT)
    sub_s = style("S", fontSize=11, textColor=ELECTRIC, spaceAfter=20, alignment=TA_LEFT)
    h1_s = style("H1", fontSize=16, textColor=ELECTRIC, fontName="Helvetica-Bold",
        spaceAfter=10, spaceBefore=20)
    h2_s = style("H2", fontSize=12, textColor=WHITE, fontName="Helvetica-Bold",
        spaceAfter=6, spaceBefore=12)
    body_s = style("B", fontSize=10, textColor=LIGHT, leading=16)
    small_s = style("SM", fontSize=9, textColor=MID, leading=14)
    label_s = style("LB", fontSize=8, textColor=ELECTRIC, fontName="Helvetica-Bold",
        letterSpacing=1.5, spaceAfter=4)
    white_s = style("W", fontSize=10, textColor=WHITE, leading=15)
    bold_white = style("BW", fontSize=10, textColor=WHITE, fontName="Helvetica-Bold")

    story = []

    # ── COVER ──────────────────────────────────────────────────
    cover_data = [[
        Paragraph("UX RESEARCH BRIEF", style("CL", fontSize=10, textColor=ELECTRIC,
            fontName="Helvetica-Bold", letterSpacing=3)),
    ]]
    cover_table = Table(cover_data, colWidths=[17*cm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("PADDING", (0,0), (-1,-1), 20),
        ("BOX", (0,0), (-1,-1), 2, ELECTRIC),
        ("LINEBELOW", (0,0), (-1,0), 1, ELECTRIC),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Pain Point Analysis Report", title_s))
    story.append(Paragraph(f"Customer: {report.customer_name}  ·  {report.customer_role}  ·  {report.customer_company}", sub_s))

    meta_data = [
        [Paragraph("GENERATED", label_s), Paragraph(datetime.now().strftime("%B %d, %Y"), white_s)],
        [Paragraph("STATUS", label_s), Paragraph("Ready for UX + Architecture Review", white_s)],
    ]
    meta_table = Table(meta_data, colWidths=[4*cm, 13*cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("PADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("BOX", (0,0), (-1,-1), 1, ELECTRIC_DIM),
        ("INNERGRID", (0,0), (-1,-1), 0.5, ELECTRIC_DIM),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=ELECTRIC))
    story.append(Spacer(1, 0.3*cm))

    # ── EXECUTIVE SUMMARY ──────────────────────────────────────
    story.append(Paragraph("01 — Executive Summary", h1_s))
    summary_table = Table([[Paragraph(report.executive_summary or "", body_s)]],
        colWidths=[17*cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("BOX", (0,0), (-1,-1), 1, ELECTRIC_DIM),
        ("PADDING", (0,0), (-1,-1), 14),
        ("TOPPADDING", (0,0), (-1,-1), 14),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5*cm))

    # ── PAIN POINTS ────────────────────────────────────────────
    story.append(Paragraph("02 — Pain Points", h1_s))

    for i, pp in enumerate(report.pain_points or []):
        sev = pp.get("severity", "medium")
        sev_color = SEVERITY_COLORS.get(sev, AMBER)

        header_data = [[
            Paragraph(f"#{i+1}  {pp.get('title','')}", bold_white),
            Paragraph(sev.upper(), style(f"SEV{i}", fontSize=9, textColor=sev_color,
                fontName="Helvetica-Bold", alignment=TA_RIGHT)),
        ]]
        header_t = Table(header_data, colWidths=[13*cm, 4*cm])
        header_t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#0D1E35")),
            ("LEFTPADDING", (0,0), (0,-1), 12),
            ("RIGHTPADDING", (-1,0), (-1,-1), 12),
            ("TOPPADDING", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
            ("LINEABOVE", (0,0), (-1,0), 2, sev_color),
        ]))

        detail_rows = [
            [Paragraph("Description", label_s), Paragraph(pp.get("description",""), small_s)],
            [Paragraph("Root Cause", label_s), Paragraph(pp.get("root_cause",""), small_s)],
            [Paragraph("Business Impact", label_s), Paragraph(pp.get("business_impact",""), small_s)],
            [Paragraph("Frequency", label_s), Paragraph(pp.get("frequency","").title(), small_s)],
        ]
        detail_t = Table(detail_rows, colWidths=[3.5*cm, 13.5*cm])
        detail_t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NAVY),
            ("PADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("INNERGRID", (0,0), (-1,-1), 0.5, ELECTRIC_DIM),
            ("BOX", (0,0), (-1,-1), 1, ELECTRIC_DIM),
        ]))

        story.append(KeepTogether([header_t, detail_t, Spacer(1, 0.3*cm)]))

    # ── UX REQUIREMENTS ────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("03 — UX Requirements", h1_s))
    story.append(Paragraph("Actionable requirements for the UX/Design team:", body_s))
    story.append(Spacer(1, 0.2*cm))

    req_header = [
        Paragraph("REQUIREMENT", label_s),
        Paragraph("CATEGORY", label_s),
        Paragraph("PRIORITY", label_s),
        Paragraph("RATIONALE", label_s),
    ]
    req_rows = [req_header]
    for req in (report.ux_requirements or []):
        pri = req.get("priority", "should-have")
        pri_color = PRIORITY_COLORS.get(pri, AMBER)
        req_rows.append([
            Paragraph(req.get("requirement",""), small_s),
            Paragraph(req.get("category","").title(), small_s),
            Paragraph(pri.upper(), style(f"PRI", fontSize=8, textColor=pri_color, fontName="Helvetica-Bold")),
            Paragraph(req.get("rationale",""), small_s),
        ])
    req_table = Table(req_rows, colWidths=[5.5*cm, 2.5*cm, 2.5*cm, 6.5*cm])
    req_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0D1E35")),
        ("BACKGROUND", (0,1), (-1,-1), NAVY),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [NAVY, colors.HexColor("#0D1A2A")]),
        ("PADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("INNERGRID", (0,0), (-1,-1), 0.5, ELECTRIC_DIM),
        ("BOX", (0,0), (-1,-1), 1, ELECTRIC),
        ("LINEBELOW", (0,0), (-1,0), 1, ELECTRIC),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(req_table)
    story.append(Spacer(1, 0.5*cm))

    # ── ARCHITECTURE NOTES ─────────────────────────────────────
    story.append(Paragraph("04 — Architecture Notes", h1_s))
    story.append(Paragraph("Technical findings for the Solution Architecture team:", body_s))
    story.append(Spacer(1, 0.2*cm))

    for note in (report.architecture_notes or []):
        pri = note.get("priority", "medium")
        pri_c = SEVERITY_COLORS.get(pri, AMBER)
        arch_data = [
            [Paragraph(note.get("area",""), style("AR", fontSize=10, textColor=ELECTRIC,
                fontName="Helvetica-Bold")),
             Paragraph(pri.upper(), style("ARP", fontSize=8, textColor=pri_c,
                fontName="Helvetica-Bold", alignment=TA_RIGHT))],
            [Paragraph(f"Finding: {note.get('finding','')}", small_s), ""],
            [Paragraph(f"Recommendation: {note.get('recommendation','')}", style("REC",
                fontSize=9, textColor=GREEN, leading=14)), ""],
        ]
        arch_t = Table(arch_data, colWidths=[13.5*cm, 3.5*cm])
        arch_t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NAVY),
            ("BOX", (0,0), (-1,-1), 1, ELECTRIC_DIM),
            ("LINEABOVE", (0,0), (-1,0), 2, ELECTRIC),
            ("PADDING", (0,0), (-1,-1), 10),
            ("SPAN", (0,1), (1,1)),
            ("SPAN", (0,2), (1,2)),
        ]))
        story.append(arch_t)
        story.append(Spacer(1, 0.25*cm))

    # ── RECOMMENDED SOLUTIONS ──────────────────────────────────
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("05 — Recommended Solutions", h1_s))
    for j, sol in enumerate(report.recommended_solutions or []):
        sol_data = [[
            Paragraph(f"{j+1:02d}", style("NUM", fontSize=20, textColor=ELECTRIC,
                fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph(sol, body_s)
        ]]
        sol_t = Table(sol_data, colWidths=[1.5*cm, 15.5*cm])
        sol_t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NAVY),
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#0D1E35")),
            ("BOX", (0,0), (-1,-1), 1, ELECTRIC_DIM),
            ("PADDING", (0,0), (-1,-1), 10),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ]))
        story.append(sol_t)
        story.append(Spacer(1, 0.2*cm))

    # ── USER JOURNEY ───────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("06 — Observed User Journey", h1_s))
    for k, step in enumerate(report.user_journey or []):
        step_data = [[
            Paragraph(f"→", style("ARR", fontSize=14, textColor=ELECTRIC,
                fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph(step, body_s)
        ]]
        step_t = Table(step_data, colWidths=[1*cm, 16*cm])
        step_t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NAVY),
            ("LINEBELOW", (0,0), (-1,-1), 0.5, ELECTRIC_DIM),
            ("PADDING", (0,0), (-1,-1), 8),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ]))
        story.append(step_t)

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=ELECTRIC))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"Confidential UX Research Brief  ·  Generated {datetime.now().strftime('%B %d, %Y')}  ·  Pain Point Mapper AI",
        style("FT", fontSize=8, textColor=MID, alignment=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
