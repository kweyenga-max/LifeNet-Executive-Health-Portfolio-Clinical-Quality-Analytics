import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Base Directory Setup
BASE_DIR = Path(__file__).resolve().parent.parent
data_dir = BASE_DIR / "data"
output_pdf = BASE_DIR / "bDQA_Cohort3_Baseline_Executive_Report.pdf"

print(f"📄 Building Executive Baseline PDF Report: {output_pdf}")

doc = SimpleDocTemplate(
    str(output_pdf),
    pagesize=A4,
    rightMargin=36,
    leftMargin=36,
    topMargin=36,
    bottomMargin=36,
)

styles = getSampleStyleSheet()

# LifeNet Palette Colors
c_navy = colors.HexColor("#0A2540")
c_teal = colors.HexColor("#00A8CC")
c_dark = colors.HexColor("#2D3748")
c_light_bg = colors.HexColor("#F7FAFC")
c_border = colors.HexColor("#E2E8F0")

title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    textColor=c_navy,
    spaceAfter=4,
)
subtitle_style = ParagraphStyle(
    "DocSubTitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10.5,
    leading=14,
    textColor=c_teal,
    spaceAfter=12,
)
h1_style = ParagraphStyle(
    "H1",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=17,
    textColor=c_navy,
    spaceBefore=12,
    spaceAfter=6,
)
h2_style = ParagraphStyle(
    "H2",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=14,
    textColor=c_teal,
    spaceBefore=8,
    spaceAfter=4,
)
body_style = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=13,
    textColor=c_dark,
    spaceAfter=6,
)
bullet_style = ParagraphStyle(
    "Bullet", parent=body_style, leftIndent=12, firstLineIndent=-8, spaceAfter=4
)

story = []

# Title Block
story.append(
    Paragraph("Baseline Data Quality Assessment (bDQA) Executive Report", title_style)
)
story.append(
    Paragraph(
        "<b>Cohort 3 Health Facilities (13 Facilities) | Baseline Period: Q4 2025</b>",
        subtitle_style,
    )
)
story.append(
    HRFlowable(width="100%", thickness=2, color=c_navy, spaceBefore=0, spaceAfter=10)
)

# 1. Background & Objectives
story.append(Paragraph("1. Background, Rationale & Core Objectives", h1_style))
story.append(
    Paragraph(
        "Data Quality Assessments (DQAs) serve as the foundation for clinical governance, health system accountability, and strategic planning. Data integrity degrades as information flows from primary registers to monthly summary sheets and electronic national databases (KHIS/DHIS2). This baseline report establishes performance benchmarks across 13 Cohort 3 facilities prior to targeted M&E technical assistance.",
        body_style,
    )
)

for obj in [
    "<b>Tri-Platform Verification:</b> Reconcile clinical counts across Primary Registers, MOH Summary Sheets, and KHIS.",
    "<b>Clinical Logic Auditing:</b> Interrogate essential service cascades (Deliveries vs. Live Births/Stillbirths, Live Births vs. Immediate Breastfeeding).",
    "<b>Operational Vulnerability Mapping:</b> Identify root causes driving documentation gaps and transcription errors.",
    "<b>Actionable M&E Roadmap:</b> Establish baseline performance tiers to guide targeted technical assistance.",
]:
    story.append(Paragraph(f"• {obj}", bullet_style))

story.append(Spacer(1, 8))

# 2. Methodology Table
story.append(Paragraph("2. Assessment Methodology Framework", h1_style))
methodology_data = [
    [
        Paragraph("<b>Reporting Level</b>", body_style),
        Paragraph("<b>Data Source Evaluated</b>", body_style),
        Paragraph("<b>Core Focus & Metric Evaluated</b>", body_style),
    ],
    [
        Paragraph("<b>Tier 1: Primary Source</b>", body_style),
        Paragraph("MOH Primary Registers (OPD, ANC, Delivery, PNC)", body_style),
        Paragraph(
            "Direct patient encounter documentation at point of care.", body_style
        ),
    ],
    [
        Paragraph("<b>Tier 2: Facility Tally</b>", body_style),
        Paragraph("Monthly MOH Summary Sheets (MOH 705, 711, 717)", body_style),
        Paragraph(
            "Manual aggregation of primary register counts at month-end.", body_style
        ),
    ],
    [
        Paragraph("<b>Tier 3: National DHIS2</b>", body_style),
        Paragraph("Kenya Health Information System (KHIS)", body_style),
        Paragraph("Electronic data uploaded to national DHIS2 repository.", body_style),
    ],
]
t_method = Table(methodology_data, colWidths=[1.4 * inch, 2.5 * inch, 3.3 * inch])
t_method.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), c_navy),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, c_border),
            ("BACKGROUND", (0, 1), (-1, -1), c_light_bg),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]
    )
)
for c in range(3):
    t_method._cellvalues[0][c].style.textColor = colors.white
story.append(t_method)

story.append(Spacer(1, 10))

# 3. Findings & Figures
story.append(Paragraph("3. Quantitative Findings & Clinical Consistency", h1_style))

# Chart 1
img1_path = data_dir / "01_bDQA_Cohort3_Baseline_Platform_Reconciliation.png"
if img1_path.exists():
    story.append(
        Paragraph("A. Platform Data Reconciliation Across Key Indicators", h2_style)
    )
    story.append(Image(str(img1_path), width=7.0 * inch, height=3.5 * inch))
    story.append(Spacer(1, 6))

# Chart 2
img2_path = data_dir / "02_bDQA_Cohort3_Baseline_Facility_Accuracy.png"
if img2_path.exists():
    story.append(Paragraph("B. Facility Data Accuracy Performance Rankings", h2_style))
    story.append(Image(str(img2_path), width=7.0 * inch, height=3.7 * inch))
    story.append(Spacer(1, 6))

# Chart 4
img4_path = data_dir / "04_bDQA_Cohort3_Baseline_Clinical_Cascade.png"
if img4_path.exists():
    story.append(
        Paragraph("C. Delivery & Essential Newborn Care Clinical Cascade", h2_style)
    )
    story.append(Image(str(img4_path), width=6.8 * inch, height=3.5 * inch))
    story.append(Spacer(1, 6))

# 4. Operational Bottlenecks
story.append(Paragraph("4. Operational & Structural Root Causes", h1_style))
for rc in [
    "<b>Improvised & Non-Standard Registers:</b> Shortages of official MOH primary registers forced facilities to use improvised notebooks lacking standard clinical columns.",
    "<b>Absence of Data Reviews:</b> No monthly data verification meetings (DRMs) occur at facility or sub-county levels prior to KHIS submission.",
    "<b>Minimal Supportive Supervision:</b> Irregular supervision from partners and SCHMT limits routine coaching opportunities.",
    "<b>Lack of Data Management SOPs:</b> Facilities lack formal SOPs for data tallies, archiving, and error validation.",
    "<b>Delegated Data Entry to Interns:</b> Sub-county HRIOs delegate KHIS uploads to casual clerks/interns without proper training or quality checks.",
    "<b>Completely Missing Datasets in KHIS:</b> Certain facility monthly reporting sheets were entirely missing from KHIS.",
]:
    story.append(Paragraph(f"• {rc}", bullet_style))

story.append(Spacer(1, 10))

# 5. Action Plan Table
story.append(Paragraph("5. Strategic Recommendations & Action Plan", h1_style))
action_matrix_data = [
    [
        Paragraph("<b>Identified Vulnerability</b>", body_style),
        Paragraph("<b>Targeted M&E Intervention</b>", body_style),
        Paragraph("<b>Responsible Entity</b>", body_style),
        Paragraph("<b>Success Target</b>", body_style),
    ],
    [
        Paragraph("Improvised Registers", body_style),
        Paragraph(
            "Procure and distribute standard MOH primary registers across all service areas.",
            body_style,
        ),
        Paragraph("LifeNet / SCHMT", body_style),
        Paragraph("100% register standardization", body_style),
    ],
    [
        Paragraph("No Data Reviews", body_style),
        Paragraph(
            "Establish mandatory monthly pre-submission Data Review Meetings (DRMs).",
            body_style,
        ),
        Paragraph("Facility In-Charges / LifeNet", body_style),
        Paragraph("Monthly DRM sign-off sheets", body_style),
    ],
    [
        Paragraph("Erroneous Data Entry", body_style),
        Paragraph(
            "Conduct targeted data entry & DHIS2 orientation for SCHMT interns and clerks.",
            body_style,
        ),
        Paragraph("Sub-County HRIO / LifeNet", body_style),
        Paragraph("Zero entry error rate", body_style),
    ],
    [
        Paragraph("Lack of Governance", body_style),
        Paragraph(
            "Develop, print, and distribute standardized Data Management SOPs.",
            body_style,
        ),
        Paragraph("LifeNet M&E Team", body_style),
        Paragraph("SOPs posted in all records units", body_style),
    ],
    [
        Paragraph("Minimal Supervision", body_style),
        Paragraph(
            "Institute bi-monthly joint supportive supervision visits (SCHMT + LifeNet).",
            body_style,
        ),
        Paragraph("SCHMT / LifeNet", body_style),
        Paragraph("100% supervision coverage", body_style),
    ],
]
t_action = Table(
    action_matrix_data, colWidths=[1.4 * inch, 2.8 * inch, 1.5 * inch, 1.5 * inch]
)
t_action.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), c_navy),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, c_border),
            ("BACKGROUND", (0, 1), (-1, -1), c_light_bg),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]
    )
)
for c in range(4):
    t_action._cellvalues[0][c].style.textColor = colors.white
story.append(t_action)

# Build Document
doc.build(story)
print(f"✅ PDF Report generated successfully at:\n   {output_pdf}")
