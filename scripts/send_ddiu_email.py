import smtplib
import tomllib
from email.message import EmailMessage
from pathlib import Path

from scripts.ddiu_report_generator import (
    build_ddiu_dataset,
    default_ddiu_period,
    save_monthly_ddiu_report,
)

BASE_DIR = Path(__file__).resolve().parent.parent


def send_ddiu_report_email(period_label: str | None = None, recipients_override: list[str] | None = None) -> None:
    secrets_path = BASE_DIR / ".streamlit" / "secrets.toml"
    with open(secrets_path, "rb") as f:
        cfg = tomllib.load(f).get("email", {})

    period_label = period_label or default_ddiu_period(BASE_DIR)
    try:
        from scripts.khis_anc_live import get_live_anc_frame
        get_live_anc_frame("IPjuLUsTQHG", force_live=True)
    except Exception:
        pass
    pdf_path = save_monthly_ddiu_report(period_label, base_dir=BASE_DIR)
    data = build_ddiu_dataset(period_label, base_dir=BASE_DIR)

    recipients = recipients_override or cfg["recipients"]
    if isinstance(recipients, str):
        recipients = [recipients]

    sl_df = data.get("starlink_df")
    if sl_df is not None and not sl_df.empty:
        sl_used = float(sl_df["Current Month (GB)"].sum())
        sl_cap = float(sl_df["Share Cap (GB)"].sum())
        sl_pct = (sl_used / sl_cap * 100.0) if sl_cap > 0 else 0.0
        sl_on = int((sl_df["Status"].astype(str).str.upper() == "ONLINE").sum())
        sl_txt_line = f"- Starlink Connectivity Pool: {sl_used:,.1f} GB / {sl_cap/1000.0:.2f} TB ({sl_pct:.1f}% used | {sl_on}/{len(sl_df)} online)\n"
        sl_html_row = (
            f'<tr><td style="padding: 10px; border: 1px solid #E2E8F0;"><b>Starlink Connectivity Pool</b></td>'
            f'<td style="padding: 10px; border: 1px solid #E2E8F0;"><b>{sl_used:,.1f} GB</b> ({sl_pct:.1f}% of {sl_cap/1000.0:.2f} TB) &nbsp;|&nbsp; <b>{sl_on}/{len(sl_df)}</b> Sites Online</td></tr>'
        )
    else:
        sl_txt_line = ""
        sl_html_row = ""

    msg = EmailMessage()
    msg["Subject"] = f"LifeNet Kenya | Monthly DDIU & M&E Executive Brief — {period_label}"
    msg["From"] = f"LifeNet M&E Portal <{cfg['sender_email']}>"
    msg["To"] = ", ".join(recipients)

    msg.set_content(
        f"LifeNet International — Monthly DDIU & M&E Executive Brief ({period_label})\n\n"
        f"- Active Facilities: {data['total_facilities']} (KHIS: {data['khis_reporting']}/{data['total_facilities']}, "
        f"Finance: {data['fin_reporting']}/{data['total_facilities']})\n"
        f"- Total Patient Visits: {int(data['tot_pv']):,} ({data['pv_mom_pct']:+.1f}% MoM | {data['pv_yoy_pct']:+.1f}% YoY)\n"
        f"- Maternity Deliveries: {data['tot_del']:,} ({data['tot_lb']:,} Live Births)\n"
        f"- Network Cost Coverage: {data['cost_coverage']:.1f}% (Net: KES {data['tot_net']:,.0f})\n"
        f"- Facilities Flagged for Follow-Up: {len(data['follow_up_df'])}\n{sl_txt_line}\n"
        f"Full LifeNet-branded Executive PDF Report attached."
    )

    html_body = f"""
    <div style="font-family: Arial, sans-serif; color: #2D3748; max-width: 680px;">
      <div style="background: #0A2540; color: #FFFFFF; padding: 18px 22px; border-radius: 8px 8px 0 0;">
        <h2 style="margin: 0; font-size: 18px;">LifeNet International — Monthly DDIU &amp; M&amp;E Brief</h2>
        <p style="margin: 4px 0 0 0; font-size: 13px; color: #CBD5E1;">
          Reporting Month: <b>{period_label}</b> &nbsp;|&nbsp; Scope: <b>{data['total_facilities']} Active Facilities</b>
        </p>
      </div>
      <div style="border: 1px solid #E2E8F0; border-top: none; padding: 18px 22px; border-radius: 0 0 8px 8px;">
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 14px;">
          <tr style="background: #F7FAFC;">
            <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>Total Patient Visits</b></td>
            <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>{int(data['tot_pv']):,}</b> ({data['pv_mom_pct']:+.1f}% MoM | {data['pv_yoy_pct']:+.1f}% YoY)</td>
          </tr>
          <tr>
            <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>Maternity Deliveries</b></td>
            <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>{data['tot_del']:,}</b> ({data['tot_lb']:,} Live Births | {data['tot_fsb'] + data['tot_msb']} Stillbirths)</td>
          </tr>
          <tr>
            <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>Antenatal Care (ANC) Continuum</b></td>
            <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>{data.get('tot_anc1', 0):,}</b> 1st ANC | Early &le;12w: <b>{data.get('anc_early_pct', 0.0):.1f}%</b> | ANC4+: <b>{data.get('anc4_pct', 0.0):.1f}%</b> | Syphilis: <b>{data.get('anc_syph_pct', 0.0):.1f}%</b></td>
          </tr>
          <tr style="background: #F7FAFC;">
            <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>Reporting Completeness</b></td>
            <td style="padding: 10px; border: 1px solid #E2E8F0;">KHIS: <b>{data['khis_reporting']}/{data['total_facilities']}</b> &nbsp;|&nbsp; MoniTrac Finance: <b>{data['fin_reporting']}/{data['total_facilities']}</b></td>
          </tr>
          <tr>
            <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>Financial Cost Coverage</b></td>
            <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>{data['cost_coverage']:.1f}%</b> (Net Balance: KES {data['tot_net']:,.0f})</td>
          </tr>
          <tr style="background: #F7FAFC;">
            <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>Facilities Flagged for DQA / Follow-Up</b></td>
            <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>{len(data['follow_up_df'])} facilities</b> (see attached PDF for facility queries &amp; team actionables)</td>
          </tr>
        </table>
        <p style="font-size: 13px; color: #475569; margin-bottom: 0;">
          The full <b>LifeNet DDIU Executive PDF Report</b> (with embedded charts and M&amp;E / Mentor action tables) is attached.
        </p>
      </div>
    </div>
    """
    msg.add_alternative(html_body, subtype="html")
    msg.add_attachment(pdf_path.read_bytes(), maintype="application", subtype="pdf", filename=pdf_path.name)

    with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"]), timeout=30) as server:
        server.starttls()
        server.login(cfg["sender_email"], cfg["app_password"])
        server.send_message(msg)

    print(f"Sent {pdf_path.name} to {', '.join(recipients)}")


if __name__ == "__main__":
    send_ddiu_report_email()
