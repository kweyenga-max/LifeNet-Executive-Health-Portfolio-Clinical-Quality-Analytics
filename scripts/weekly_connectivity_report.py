import calendar
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from pathlib import Path
import tomllib
import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
SECRETS_PATH = BASE_DIR / ".streamlit" / "secrets.toml"
REPORTS_DIR = BASE_DIR / "reports"

STAREDGE_AUTH_URL = "https://auth-api.founders.staredge.net/login"
STAREDGE_CUST_API = "https://customer-api.founders.staredge.net/v1"
UNIFI_API_BASE = "https://api.ui.com"

FACILITY_HOST_MAP = {
    "Kenya001": "LNI-Kenya001-PEFA-Mercy",
    "Kenya002": "LNI-Kenya002-Mulango",
    "Kenya003": "LNI-Kenya003-Buyangu",
    "Kenya004": "LNI-Kenya004-Naikarra",
    "Kenya005": "LNI-Kenya005-Ewaso",
    "Kenya006": "LNI-Kenya006-Ngoswani",
    "Kenya007": "LNI-Kenya007-Mwangaza",
    "Kenya008": "LNI-Kenya008-CMF-Aitong",
    "Kenya009": "LNI-Kenya009-StElizabeth",
    "Kenya0010": "LNI-Kenya010-Ingotse-Health",
}


def load_secrets() -> dict:
    if SECRETS_PATH.exists():
        with open(SECRETS_PATH, "rb") as f:
            return tomllib.load(f)
    return {}


def pull_merged_telemetry() -> pd.DataFrame:
    sec = load_secrets()
    se_cfg = sec.get("staredge", {})
    ui_cfg = sec.get("unifi", {})

    auth = requests.post(
        STAREDGE_AUTH_URL,
        data={"username": se_cfg["username"], "password": se_cfg["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        timeout=15,
    )
    auth.raise_for_status()
    sh = {"Authorization": f"Bearer {auth.json()['jwt_token']}", "Accept": "application/json"}
    sites = requests.get(
        f"{STAREDGE_CUST_API}/accounts/{se_cfg.get('account_id', 1363)}/sites",
        params={"paging": "size==50"},
        headers=sh,
        timeout=15,
    ).json().get("rows", [])

    records = []
    for s in sites:
        raw_name = s.get("site_name", "")
        code = raw_name.split("|")[0].strip() if "|" in raw_name else raw_name
        clean_name = raw_name.split("|")[1].strip() if "|" in raw_name else raw_name
        cap_gb = float((s.get("site_capacity") or "307.20 GB").replace("GB", "").strip())
        today_gb = float(s.get("today_usage_mb") or 0) / 1000.0
        curr_gb = float(s.get("current_month_usage_mb") or 0) / 1000.0
        prev_gb = float(s.get("previous_month_usage_mb") or 0) / 1000.0
        records.append(
            {
                "Site Code": code,
                "Facility": clean_name,
                "UniFi Host": FACILITY_HOST_MAP.get(code, ""),
                "Status": s.get("status", "UNKNOWN"),
                "Share Cap (GB)": round(cap_gb, 2),
                "Today (GB)": round(today_gb, 2),
                "Current Month (GB)": round(curr_gb, 2),
                "Previous Month (GB)": round(prev_gb, 2),
                "% Share": round((curr_gb / cap_gb * 100.0) if cap_gb else 0.0, 1),
            }
        )
    df = pd.DataFrame(records)

    if ui_cfg.get("api_key"):
        uh = {"X-API-KEY": ui_cfg["api_key"], "Accept": "application/json"}
        hosts = requests.get(f"{UNIFI_API_BASE}/ea/hosts", headers=uh, timeout=15).json().get("data", [])
        sites_data = requests.get(f"{UNIFI_API_BASE}/ea/sites", headers=uh, timeout=15).json().get("data", [])
        clients_map = {}
        for item in sites_data:
            c = item.get("statistics", {}).get("counts", {})
            clients_map[item.get("hostId")] = int(c.get("wifiClient", 0) or 0) + int(c.get("wiredClient", 0) or 0)
        ui_rows = [
            {
                "UniFi Host": h.get("reportedState", {}).get("hostname", ""),
                "Active Clients": clients_map.get(h.get("id"), 0),
            }
            for h in hosts
        ]
        df = pd.merge(df, pd.DataFrame(ui_rows), on="UniFi Host", how="left")

    return df.sort_values("Current Month (GB)", ascending=False).reset_index(drop=True)


def generate_and_send_weekly_brief(send_email: bool = True) -> tuple[bool, str]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    df = pull_merged_telemetry()
    now = datetime.now()
    stamp = now.strftime("%Y-%m-%d")

    csv_path = REPORTS_DIR / f"Starlink_Weekly_Telemetry_{stamp}.csv"
    df.to_csv(csv_path, index=False)

    days_in_month = calendar.monthrange(now.year, now.month)[1]
    elapsed_days = max(now.day, 1)
    remaining_days = max(days_in_month - elapsed_days, 1)

    pool_cap_gb = df["Share Cap (GB)"].sum()
    pool_cap_tb = pool_cap_gb / 1000.0
    used_gb = df["Current Month (GB)"].sum()
    used_tb = used_gb / 1000.0
    today_gb = df["Today (GB)"].sum()
    rem_gb = max(pool_cap_gb - used_gb, 0.0)
    rem_tb = rem_gb / 1000.0
    pct_pool = (used_gb / pool_cap_gb * 100.0) if pool_cap_gb else 0.0
    avg_daily = used_gb / elapsed_days
    req_daily = rem_gb / remaining_days
    proj_eom_gb = used_gb + avg_daily * remaining_days
    proj_eom_tb = proj_eom_gb / 1000.0
    proj_unused_gb = pool_cap_gb - proj_eom_gb
    online_cnt = int((df["Status"].str.upper() == "ONLINE").sum())
    top_site = df.iloc[0]

    cols = ["Site Code", "Facility", "Status", "Today (GB)", "Current Month (GB)", "Previous Month (GB)", "% Share", "Active Clients"]
    header_cells = "".join(
        f'<th style="padding: 9px 10px; text-align: {"left" if i < 2 else ("center" if i == 2 else "right")}; border-bottom: 2px solid #CBD5E1; color: #0F172A; font-size: 11.5px; white-space: nowrap;">{c}</th>'
        for i, c in enumerate(cols)
    )
    body_rows = []
    for idx, r in df[cols].iterrows():
        bg = "#F8FAFC" if idx % 2 else "#FFFFFF"
        status_color = "#15803D" if str(r["Status"]).upper() == "ONLINE" else "#B91C1C"
        body_rows.append(
            f'<tr style="background:{bg}; border-bottom:1px solid #E2E8F0;">'
            f'<td style="padding:8px 10px; font-weight:600; color:#334155;">{r["Site Code"]}</td>'
            f'<td style="padding:8px 10px; color:#0F172A;">{r["Facility"]}</td>'
            f'<td style="padding:8px 10px; text-align:center; font-weight:700; color:{status_color};">{r["Status"]}</td>'
            f'<td style="padding:8px 10px; text-align:right;">{r["Today (GB)"]:.2f}</td>'
            f'<td style="padding:8px 10px; text-align:right; font-weight:700; color:#0F4C81;">{r["Current Month (GB)"]:.2f}</td>'
            f'<td style="padding:8px 10px; text-align:right; color:#475569;">{r["Previous Month (GB)"]:.2f}</td>'
            f'<td style="padding:8px 10px; text-align:right;">{r["% Share"]:.1f}%</td>'
            f'<td style="padding:8px 10px; text-align:right;">{int(r["Active Clients"])}</td>'
            f'</tr>'
        )
    table_html = f'<table style="width:100%; border-collapse:collapse; font-size:12.5px;"><thead><tr style="background:#EFF6FF;">{header_cells}</tr></thead><tbody>{"".join(body_rows)}</tbody></table>'

    html_body = f"""
    <html><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #0F172A; line-height: 1.6; max-width: 780px; margin: auto;">
      <div style="background: #0F172A; color: #FFFFFF; padding: 18px 24px; border-radius: 8px 8px 0 0; border-bottom: 4px solid #38BDF8;">
        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: #93C5FD;">LifeNet Kenya • Weekly Connectivity Brief</div>
        <div style="font-size: 20px; font-weight: 700; margin-top: 4px;">Starlink &amp; Facility Network Utilization ({now.strftime('%d %B %Y')})</div>
      </div>
      <div style="border: 1px solid #CBD5E1; border-top: none; padding: 20px 24px; border-radius: 0 0 8px 8px; background: #FFFFFF;">
        <p>As of <strong>{now.strftime('%d %B %Y')}</strong>, the Starlink &amp; UniFi dashboard indicates the following:</p>
        <ul>
          <li><strong>Monthly data usage:</strong> {used_gb:,.2f} GB ({used_tb:.2f} TB)</li>
          <li><strong>Today's data usage:</strong> {today_gb:,.2f} GB</li>
          <li><strong>Sites online:</strong> {online_cnt} of {len(df)}</li>
        </ul>
        <p>Current usage represents <strong>{pct_pool:.1f}%</strong> of the <strong>{pool_cap_tb:.2f} TB ({pool_cap_gb:,.0f} GB)</strong> pooled monthly allocation, leaving <strong>{rem_tb:.2f} TB ({rem_gb:,.2f} GB)</strong> available for the remainder of {now.strftime('%B')}.</p>
        <p>To consume the remaining <strong>{rem_tb:.2f} TB</strong> over the remaining <strong>{remaining_days} days</strong>, the portfolio would need to average <strong>{req_daily:,.1f} GB/day</strong>, compared to our current run rate of <strong>{avg_daily:,.1f} GB/day</strong>. At this pace, we are projected to close {now.strftime('%B')} at <strong>{proj_eom_tb:.2f} TB ({proj_eom_gb:,.0f} GB)</strong>, leaving roughly <strong>{proj_unused_gb:,.0f} GB</strong> buffer. Top consumer: <strong>{top_site['Facility']}</strong> ({top_site['Current Month (GB)']:.1f} GB / {top_site['% Share']:.1f}% reference share).</p>
        <h3 style="color: #0F4C81; margin-top: 20px;">Facility Breakdown</h3>
        <div style="font-size: 12.5px;">{table_html}</div>
      </div>
    </body></html>
    """

    html_path = REPORTS_DIR / f"Starlink_Weekly_Brief_{stamp}.html"
    html_path.write_text(html_body, encoding="utf-8")

    if not send_email:
        return True, f"Saved snapshot to {csv_path.name}"

    sec = load_secrets()
    email_cfg = sec.get("email", {})
    sender = email_cfg.get("sender_email") or email_cfg.get("sender", "kweyenga@lninternational.org")
    smtp_host = email_cfg.get("smtp_host", "smtp.gmail.com")
    smtp_port = int(email_cfg.get("smtp_port", 587))
    app_password = email_cfg.get("app_password", "")
    recipients = email_cfg.get("starlink_recipients") or ["kweyenga@lninternational.org", "enyakan@lninternational.org"]

    if not app_password:
        return True, f"Snapshot saved ({csv_path.name}). Missing app_password in [email]."

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"LifeNet Kenya Weekly Starlink & Connectivity Brief — {now.strftime('%d %b %Y')} ({pct_pool:.1f}% Pool Used)"
    msg["From"] = f"LifeNet M&E Portal <{sender}>"
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.starttls()
        server.login(sender, app_password)
        server.sendmail(sender, recipients, msg.as_string())

    return True, f"Weekly brief emailed to {', '.join(recipients)} and saved to {csv_path.name}."


if __name__ == "__main__":
    ok, message = generate_and_send_weekly_brief(send_email=True)
    print(message)
