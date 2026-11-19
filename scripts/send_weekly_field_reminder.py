import tomllib
from pathlib import Path
import os
import sys
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
def _load_local_env(env_path: str = ".env") -> None:
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_local_env()

DASHBOARD_URL = os.getenv(
    "LIFENET_DASHBOARD_URL",
    "https://lifenet-executive-health-portfolio-clinical-quality-analytics.streamlit.app",
)

DEFAULT_WEEKLY_RECIPIENTS = [
    "nbyegon@lninternational.org",
    "esemeadrian@gmail.com",
    "mwanyama@lninternational.org",
    "lmuriuki@lninternational.org",
    "jkirori@lninternational.org",
    "enyakan@lninternational.org",
    "kweyenga@lninternational.org",
    "tmukabi@lninternational.org",
    "kenya@lninternational.org",
]


def _discover_recipients() -> list[str]:
    env_recips = os.getenv("WEEKLY_REMINDER_RECIPIENTS")
    if env_recips:
        return [e.strip() for e in env_recips.split(",") if "@" in e]
    return list(DEFAULT_WEEKLY_RECIPIENTS)


def build_weekly_reminder_html(run_date: datetime) -> tuple[str, str, str]:
    week_str = run_date.strftime("%A, %d %B %Y")
    subject = f"ACTION REQUIRED: Weekly Health Facility Visit Readiness, DQA & Performance Alignment ({run_date.strftime('%d %b %Y')})"

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0; padding:0; background-color:#F1F5F9; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; color:#0F172A;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F1F5F9; padding:24px 12px;">
        <tr>
          <td align="center">
            <table width="680" cellpadding="0" cellspacing="0" style="max-width:680px; width:100%; background:#FFFFFF; border-radius:14px; overflow:hidden; border:1px solid #CBD5E1; box-shadow:0 6px 20px rgba(15,44,89,0.08);">
              
              <!-- EXECUTIVE HEADER BANNER -->
              <tr>
                <td style="background:linear-gradient(90deg, #C8102E 0%, #881337 45%, #0F2C59 100%); padding:24px 28px; color:#FFFFFF;">
                  <div style="font-size:11px; font-weight:800; letter-spacing:1.4px; text-transform:uppercase; opacity:0.92;">
                    LIFENET INTERNATIONAL • PROGRAM OPERATIONS &amp; CLINICAL QUALITY
                  </div>
                  <h1 style="margin:6px 0 4px 0; font-size:21px; font-weight:800; line-height:1.25; color:#FFFFFF;">
                    Weekly Facility Visit Readiness, DQA &amp; Performance Alignment
                  </h1>
                  <div style="font-size:13px; color:#E2E8F0; font-weight:500;">
                    Monday Executive Dispatch • {week_str} • 07:00 AM EAT
                  </div>
                </td>
              </tr>

              <!-- INTRO CALLOUT -->
              <tr>
                <td style="padding:20px 28px 8px 28px;">
                  <div style="background:#EFF6FF; border-left:4px solid #0F2C59; padding:13px 16px; border-radius:0 8px 8px 0; font-size:13.5px; line-height:1.55; color:#1E293B;">
                    <strong>Dear Program Officers,</strong><br/>
                    Every facility visit is a strategic opportunity to drive measurable clinical and operational impact. To ensure our mentorship translates into sustained quality improvement rather than routine check-ins, please complete the following five pre-visit and on-site actions for every facility on your itinerary this week:
                  </div>
                </td>
              </tr>

              <!-- CHECKLIST ITEMS -->
              <tr>
                <td style="padding:12px 28px 20px 28px;">
                  <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:separate; border-spacing:0 12px;">
                    
                    <!-- 1 -->
                    <tr>
                      <td style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:4px solid #0F2C59; border-radius:8px; padding:14px 16px;">
                        <div style="font-size:14px; font-weight:800; color:#0F2C59; margin-bottom:4px;">
                          1. Pre-Visit Performance Analysis, Trend Sharing &amp; Action Planning
                        </div>
                        <ul style="margin:6px 0 0 18px; padding:0; font-size:13px; line-height:1.55; color:#334155;">
                          <li><strong>Diagnose before arrival:</strong> Review each scheduled facility in <strong>Facility 360°</strong> prior to your visit to interpret longitudinal service trends and identify root causes behind performance shifts.</li>
                          <li><strong>Sustain strengths &amp; close gaps:</strong> Partner with facility leadership to reinforce and sustain high-performing indicators while executing targeted interventions on lagging metrics.</li>
                          <li><strong>Co-create accountability:</strong> Present visual trends directly to facility teams and anchor commitments using the <strong>Recommended Action Plans</strong> built into the Dashboard.</li>
                        </ul>
                      </td>
                    </tr>

                    <!-- 2 -->
                    <tr>
                      <td style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:4px solid #C8102E; border-radius:8px; padding:14px 16px;">
                        <div style="font-size:14px; font-weight:800; color:#991B1B; margin-bottom:4px;">
                          2. Data Quality Assessment (DQA) Verification &amp; M&amp;E Escalation
                        </div>
                        <ul style="margin:6px 0 0 18px; padding:0; font-size:13px; line-height:1.55; color:#334155;">
                          <li><strong>Audit facility records:</strong> Review the <strong>DQA Tab</strong> alongside individual facility profiles ahead of your visit to flag reporting anomalies early.</li>
                          <li><strong>Reconcile at the source:</strong> Work directly with facility records officers on-site to verify, correct, and amend discrepancies across source registers and KHIS.</li>
                          <li><strong>Close the feedback loop:</strong> Report all DQA amendments and unresolved data risks to the <strong>M&amp;E Team</strong> during weekly check-ins — or escalate immediately when urgent follow-up is required.</li>
                        </ul>
                      </td>
                    </tr>

                    <!-- 3 -->
                    <tr>
                      <td style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:4px solid #0284C7; border-radius:8px; padding:14px 16px;">
                        <div style="font-size:14px; font-weight:800; color:#075985; margin-bottom:4px;">
                          3. Health Facility Dashboard Wall-Chart vs. Inbuilt Dashboard Reconciliation
                        </div>
                        <ul style="margin:6px 0 0 18px; padding:0; font-size:13px; line-height:1.55; color:#334155;">
                          <li><strong>Verify active utilization:</strong> Confirm that each visited facility is consistently updating its physical <strong>Health Facility Dashboard</strong> wall-chart as a live management tool.</li>
                          <li><strong>Ensure single-source accuracy:</strong> Cross-check wall-chart entries against the <strong>inbuilt Health Facility Dashboard</strong> in Facility 360° (covering OPD &lt;5/&gt;5 workload, ANC, deliveries, and zero-mortality tracking) to confirm exact alignment.</li>
                          <li><strong>Flag variances:</strong> Share immediate reconciliation feedback with <strong>M&amp;E</strong> wherever discrepancies arise.</li>
                        </ul>
                      </td>
                    </tr>

                    <!-- 4 -->
                    <tr>
                      <td style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:4px solid #0D9488; border-radius:8px; padding:14px 16px;">
                        <div style="font-size:14px; font-weight:800; color:#115E59; margin-bottom:4px;">
                          4. Facility Financial Reporting Compliance &amp; Same-Day Collection
                        </div>
                        <ul style="margin:6px 0 0 18px; padding:0; font-size:13px; line-height:1.55; color:#334155;">
                          <li><strong>Pre-check submission status:</strong> Review the <strong>Facility Financial Reporting Rate</strong> on the Dashboard prior to travel.</li>
                          <li><strong>Eliminate reporting backlogs:</strong> For any visited facility with an outstanding financial submission, collect and submit the pending financial data <strong>on the exact day of your visit</strong>.</li>
                        </ul>
                      </td>
                    </tr>

                    <!-- 5 -->
                    <tr>
                      <td style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:4px solid #D97706; border-radius:8px; padding:14px 16px;">
                        <div style="font-size:14px; font-weight:800; color:#92400E; margin-bottom:4px;">
                          5. Starlink Sites: Strategic Bandwidth &amp; Data Governance Check-In
                        </div>
                        <ul style="margin:6px 0 0 18px; padding:0; font-size:13px; line-height:1.55; color:#334155;">
                          <li><strong>Protect mission-critical connectivity:</strong> At all <strong>Starlink-equipped facilities</strong>, hold a structured review with facility leadership on bandwidth allocation and data consumption.</li>
                          <li><strong>Enforce purposeful usage:</strong> Confirm the connection reliably powers KHIS reporting, LifeNet eLearning, and clinical workflows while reinforcing governance standards to prevent non-operational bandwidth drain.</li>
                        </ul>
                      </td>
                    </tr>

                  </table>

                  <!-- CTA BUTTON -->
                  <div style="text-align:center; margin-top:18px;">
                    <a href="{DASHBOARD_URL}" style="display:inline-block; background:#0F2C59; color:#FFFFFF; text-decoration:none; font-weight:700; font-size:13.5px; padding:12px 26px; border-radius:8px; border-bottom:3px solid #C8102E;">
                      Open LifeNet Executive Health Portfolio &amp; Facility 360° Dashboard →
                    </a>
                  </div>
                </td>
              </tr>

              <!-- FOOTER -->
              <tr>
                <td style="background:#F8FAFC; border-top:1px solid #E2E8F0; padding:14px 28px; font-size:11.5px; color:#64748B; text-align:center;">
                  Automated Monday Program Readiness Dispatch • Sent every Monday at 7:00 AM EAT • LifeNet Kenya M&amp;E &amp; Program Operations
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    plain_text = (
        f"WEEKLY FACILITY VISIT READINESS, DQA & PERFORMANCE ALIGNMENT ({week_str})\n"
        "================================================================================\n\n"
        "Dear Program Officers,\n\n"
        "Every facility visit is a strategic opportunity to drive measurable clinical and operational impact. "
        "Please complete the following five pre-visit and on-site actions for every facility on your itinerary this week:\n\n"
        "1. PRE-VISIT PERFORMANCE ANALYSIS, TREND SHARING & ACTION PLANNING\n"
        "   - Diagnose before arrival: Review each scheduled facility in Facility 360° prior to your visit.\n"
        "   - Sustain strengths & close gaps: Reinforce high-performing indicators and target lagging metrics.\n"
        "   - Co-create accountability: Share visual trends and anchor commitments using the Dashboard's Recommended Action Plans.\n\n"
        "2. DATA QUALITY ASSESSMENT (DQA) VERIFICATION & M&E ESCALATION\n"
        "   - Audit facility records: Review the DQA Tab and individual facility profiles ahead of your visit.\n"
        "   - Reconcile at the source: Verify, correct, and amend discrepancies across source registers and KHIS on-site.\n"
        "   - Close the feedback loop: Report DQA amendments to M&E during weekly check-ins or earlier for urgent follow-ups.\n\n"
        "3. HEALTH FACILITY DASHBOARD WALL-CHART VS. INBUILT DASHBOARD RECONCILIATION\n"
        "   - Verify active utilization: Confirm the physical Health Facility Dashboard wall-chart is being filled.\n"
        "   - Ensure single-source accuracy: Cross-check entries against the inbuilt Health Facility Dashboard in Facility 360°.\n"
        "   - Flag variances: Share immediate reconciliation feedback with M&E wherever discrepancies arise.\n\n"
        "4. FACILITY FINANCIAL REPORTING COMPLIANCE & SAME-DAY COLLECTION\n"
        "   - Pre-check submission status: Review the Facility Financial Reporting Rate on the Dashboard prior to travel.\n"
        "   - Eliminate reporting backlogs: Collect and submit pending financial data on the exact day of your visit.\n\n"
        "5. STARLINK SITES: STRATEGIC BANDWIDTH & DATA GOVERNANCE CHECK-IN\n"
        "   - Protect mission-critical connectivity: Review bandwidth allocation and data consumption with facility leadership.\n"
        "   - Enforce purposeful usage: Confirm active support for KHIS, eLearning, and clinical workflows while preventing non-operational drain.\n\n"
        f"Dashboard Link: {DASHBOARD_URL}\n"
    )
    return subject, html, plain_text


def _load_streamlit_email_cfg() -> dict:
    sec_path = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"
    if sec_path.exists():
        with open(sec_path, "rb") as f:
            return tomllib.load(f).get("email", {})
    return {}


def send_weekly_reminder(dry_run: bool = False) -> None:
    now = datetime.now()
    subject, html_body, text_body = build_weekly_reminder_html(now)
    recipients = _discover_recipients()

    if dry_run:
        os.makedirs("logs", exist_ok=True)
        preview_path = "logs/weekly_field_reminder_preview.html"
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(html_body)
        print(f"✅ Dry-run preview written to: {preview_path}")
        print(f"Subject: {subject}")
        print(f"Configured Recipients ({len(recipients)}): {recipients}")
        return

    sec_email = _load_streamlit_email_cfg()
    smtp_host = os.getenv("SMTP_HOST") or sec_email.get("smtp_host", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT") or sec_email.get("smtp_port", 587))
    smtp_user = os.getenv("SMTP_USER") or sec_email.get("sender_email") or sec_email.get("sender")
    smtp_pass = os.getenv("SMTP_PASS") or os.getenv("SMTP_PASSWORD") or sec_email.get("app_password")

    if not smtp_user or not smtp_pass:
        raise RuntimeError("Missing SMTP_USER / SMTP_PASS in .env — cannot dispatch Monday reminder email.")
    if not recipients:
        raise RuntimeError("No recipients found. Set WEEKLY_REMINDER_RECIPIENTS in .env.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"LifeNet M&E & Program Ops <{smtp_user}>"
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, recipients, msg.as_string())

    print(f"✅ [{now.isoformat()}] Weekly Monday 7 AM Program Officer reminder sent to {len(recipients)} recipient(s).")


if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    send_weekly_reminder(dry_run=is_dry)
