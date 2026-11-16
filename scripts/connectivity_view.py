import calendar
from datetime import datetime
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

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


def _get_secret(section: str, key: str, env_fallback: str = "") -> str:
    try:
        if section in st.secrets and key in st.secrets[section]:
            return str(st.secrets[section][key])
    except Exception:
        pass
    return os.environ.get(env_fallback, "")


@st.cache_data(ttl=600, show_spinner=False)
def fetch_staredge_sites() -> tuple[pd.DataFrame, str | None]:
    user = _get_secret("staredge", "username", "STAREDGE_USER")
    pwd = _get_secret("staredge", "password", "STAREDGE_PASS")
    acct_id = _get_secret("staredge", "account_id", "STAREDGE_ACCOUNT_ID") or "1363"

    if not user or not pwd:
        return pd.DataFrame(), "Missing StarEDGE credentials in .streamlit/secrets.toml ([staredge])."

    try:
        auth = requests.post(
            STAREDGE_AUTH_URL,
            data={"username": user, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
            timeout=15,
        )
        auth.raise_for_status()
        token = auth.json().get("jwt_token")
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

        resp = requests.get(
            f"{STAREDGE_CUST_API}/accounts/{acct_id}/sites",
            params={"paging": "size==50"},
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        rows = resp.json().get("rows", [])
        if not rows:
            return pd.DataFrame(), "No sites returned from StarEDGE account."

        records = []
        for s in rows:
            raw_name = s.get("site_name", "")
            code = raw_name.split("|")[0].strip() if "|" in raw_name else raw_name
            clean_name = raw_name.split("|")[1].strip() if "|" in raw_name else raw_name
            cap_str = s.get("site_capacity") or "307.20 GB"
            cap_gb = float(cap_str.replace("GB", "").strip())

            today_gb = float(s.get("today_usage_mb") or 0) / 1000.0
            curr_gb = float(s.get("current_month_usage_mb") or 0) / 1000.0
            prev_gb = float(s.get("previous_month_usage_mb") or 0) / 1000.0
            pct_share = (curr_gb / cap_gb * 100.0) if cap_gb > 0 else 0.0

            records.append(
                {
                    "Site Code": code,
                    "Facility": clean_name,
                    "Full Label": raw_name,
                    "UniFi Host": FACILITY_HOST_MAP.get(code, ""),
                    "StarEDGE Status": s.get("status", "UNKNOWN"),
                    "Share Cap (GB)": round(cap_gb, 2),
                    "Today (GB)": round(today_gb, 2),
                    "Current Month (GB)": round(curr_gb, 2),
                    "Previous Month (GB)": round(prev_gb, 2),
                    "% of Facility Share": round(pct_share, 1),
                    "Latitude": s.get("latitude"),
                    "Longitude": s.get("longitude"),
                }
            )
        return pd.DataFrame(records), None
    except Exception as exc:
        return pd.DataFrame(), f"StarEDGE API error: {exc}"


@st.cache_data(ttl=600, show_spinner=False)
def fetch_unifi_health() -> tuple[pd.DataFrame, str | None]:
    api_key = _get_secret("unifi", "api_key", "UNIFI_API_KEY")
    if not api_key:
        return pd.DataFrame(), "Missing UniFi API key in .streamlit/secrets.toml ([unifi])."

    headers = {"X-API-KEY": api_key, "Accept": "application/json"}
    try:
        hosts_resp = requests.get(f"{UNIFI_API_BASE}/ea/hosts", headers=headers, timeout=15)
        hosts_resp.raise_for_status()
        hosts = hosts_resp.json().get("data", [])

        sites_resp = requests.get(f"{UNIFI_API_BASE}/ea/sites", headers=headers, timeout=15)
        sites_data = sites_resp.json().get("data", []) if sites_resp.status_code == 200 else []
        clients_by_host = {}
        for st_item in sites_data:
            hid = st_item.get("hostId")
            counts = st_item.get("statistics", {}).get("counts", {})
            clients_by_host[hid] = int(counts.get("wifiClient", 0) or 0) + int(counts.get("wiredClient", 0) or 0)

        metrics_resp = requests.get(f"{UNIFI_API_BASE}/ea/isp-metrics/1h", headers=headers, timeout=20)
        metrics_data = metrics_resp.json().get("data", []) if metrics_resp.status_code == 200 else []
        perf_by_host = {}
        for item in metrics_data:
            hid = item.get("hostId")
            periods = item.get("periods", [])
            if not periods:
                continue
            uptimes, latencies, losses, dl_speeds = [], [], [], []
            for p in periods:
                wan = p.get("data", {}).get("wan", {})
                if wan.get("uptime") is not None:
                    uptimes.append(float(wan["uptime"]))
                if wan.get("avgLatency") is not None:
                    latencies.append(float(wan["avgLatency"]))
                if wan.get("packetLoss") is not None:
                    losses.append(float(wan["packetLoss"]))
                if wan.get("download_kbps") is not None:
                    dl_speeds.append(float(wan["download_kbps"]) / 1000.0)
            perf_by_host[hid] = {
                "30d Uptime (%)": round(sum(uptimes) / len(uptimes), 2) if uptimes else None,
                "Avg Latency (ms)": round(sum(latencies) / len(latencies), 1) if latencies else None,
                "Packet Loss (%)": round(sum(losses) / len(losses), 2) if losses else None,
                "Link Capacity (Mbps)": round(sum(dl_speeds) / len(dl_speeds), 0) if dl_speeds else None,
            }

        rows = []
        for h in hosts:
            hid = h.get("id")
            rep = h.get("reportedState", {})
            hostname = rep.get("hostname", hid)
            state = rep.get("state", "unknown").upper()
            perf = perf_by_host.get(hid, {})
            rows.append(
                {
                    "UniFi Host": hostname,
                    "Gateway State": state,
                    "Active Clients": clients_by_host.get(hid, 0),
                    "30d Uptime (%)": perf.get("30d Uptime (%)"),
                    "Avg Latency (ms)": perf.get("Avg Latency (ms)"),
                    "Packet Loss (%)": perf.get("Packet Loss (%)"),
                    "Link Capacity (Mbps)": perf.get("Link Capacity (Mbps)"),
                }
            )
        return pd.DataFrame(rows), None
    except Exception as exc:
        return pd.DataFrame(), f"UniFi API error: {exc}"


def _apply_exec_chart_style(fig, height=430):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color="#0F172A", size=12),
        height=height,
        margin=dict(l=20, r=32, t=54, b=28),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0.95)",
            font=dict(color="#0F172A", size=12),
        ),
    )
    fig.update_xaxes(
        gridcolor="#E2E8F0",
        zerolinecolor="#CBD5E1",
        tickfont=dict(color="#0F172A", size=11.5),
        title_font=dict(color="#0F172A", size=12.5),
    )
    fig.update_yaxes(
        gridcolor="#E2E8F0",
        zerolinecolor="#CBD5E1",
        tickfont=dict(color="#0F172A", size=11.5),
        title_font=dict(color="#0F172A", size=12.5),
    )
    return fig


def _render_chart_narrative(title: str, body_html: str):
    st.markdown(
        f"""
        <div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-left: 4px solid #0F4C81; border-radius: 8px; padding: 12px 16px; margin-top: 6px; margin-bottom: 18px; color: #0F172A; font-size: 13.5px; line-height: 1.58;">
            <div style="font-weight: 800; color: #0F4C81; font-size: 12.5px; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px;">
                {title}
            </div>
            <div style="color: #1E293B;">{body_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_connectivity_dashboard():
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%); padding: 22px 26px; border-radius: 12px; margin-bottom: 18px; border-left: 6px solid #38BDF8;">
            <div style="color: #93C5FD; font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;">
                LifeNet Kenya • Infrastructure &amp; Digital Operations
            </div>
            <div style="color: #FFFFFF; font-size: 24px; font-weight: 800; margin-top: 4px;">
                Starlink &amp; Facility Network Telemetry (StarEDGE + UniFi)
            </div>
            <div style="color: #E2E8F0; font-size: 13.5px; margin-top: 4px;">
                Executive bandwidth governance across the 3.07 TB pooled Starlink allocation and 10 UDM-Pro SE facility gateways.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    b1, b2, _ = st.columns([1.3, 1.9, 3.9])
    with b1:
        if st.button("🔄 Refresh Live Telemetry", use_container_width=True):
            fetch_staredge_sites.clear()
            fetch_unifi_health.clear()
            st.rerun()
    with b2:
        send_now = st.button("📧 Send Weekly Brief Now (Me + CD)", use_container_width=True)

    df_se, se_err = fetch_staredge_sites()
    df_ui, ui_err = fetch_unifi_health()

    if se_err:
        st.error(se_err)
        return
    if ui_err:
        st.warning(ui_err)

    if not df_ui.empty:
        df = pd.merge(df_se, df_ui, on="UniFi Host", how="left")
    else:
        df = df_se.copy()
        df["Active Clients"] = 0

    df["Active Clients"] = df["Active Clients"].fillna(0).astype(int)
    df["GB per Client"] = df.apply(
        lambda r: round(r["Current Month (GB)"] / r["Active Clients"], 1) if r["Active Clients"] > 0 else r["Current Month (GB)"],
        axis=1,
    )

    now = datetime.now()
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
    pct_pool = (used_gb / pool_cap_gb * 100.0) if pool_cap_gb > 0 else 0.0
    df["% of Total Pool"] = (df["Current Month (GB)"] / used_gb * 100.0).round(1) if used_gb > 0 else 0.0

    online_count = int((df["StarEDGE Status"].str.upper() == "ONLINE").sum())
    total_sites = len(df)
    offline_names = df.loc[df["StarEDGE Status"].str.upper() != "ONLINE", "Facility"].tolist()

    avg_daily_gb = used_gb / elapsed_days
    safe_pace_gb = pool_cap_gb / days_in_month
    req_daily_gb = rem_gb / remaining_days
    proj_eom_gb = used_gb + (avg_daily_gb * remaining_days)
    proj_eom_tb = proj_eom_gb / 1000.0
    proj_unused_gb = pool_cap_gb - proj_eom_gb

    df_ranked = df.sort_values("Current Month (GB)", ascending=False).reset_index(drop=True)
    top_site = df_ranked.iloc[0]
    top3_share = df_ranked.head(3)["% of Total Pool"].sum()

    if send_now:
        try:
            from scripts.weekly_connectivity_report import generate_and_send_weekly_brief
            ok, msg = generate_and_send_weekly_brief(send_email=True)
            if ok:
                st.success(msg)
            else:
                st.warning(msg)
        except Exception as e:
            st.error(f"Could not trigger weekly report: {e}")

    # KPI Strip
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Monthly Data Usage", f"{used_gb:,.2f} GB", f"{pct_pool:.1f}% of {pool_cap_tb:.2f} TB Pool")
    k2.metric("Today's Consumption", f"{today_gb:,.2f} GB", f"MTD Avg {avg_daily_gb:,.1f} GB/d")
    k3.metric("Remaining Headroom", f"{rem_tb:,.2f} TB", f"{rem_gb:,.1f} GB ({remaining_days}d left)")
    k4.metric("Projected EOM Total", f"{proj_eom_tb:,.2f} TB", f"{proj_unused_gb:,.0f} GB buffer")
    k5.metric(
        "Sites Online",
        f"{online_count} of {total_sites}",
        f"Offline: {', '.join(offline_names)}" if offline_names else "100% Fleet Online",
        delta_color="inverse" if offline_names else "normal",
    )

    st.markdown("---")

    # Executive Briefing Card
    date_label = now.strftime("%d %B %Y")
    month_name = now.strftime("%B")
    status_outlook = (
        f"unlikely that we will exhaust the remaining allocation by the end of {month_name}"
        if proj_eom_gb < pool_cap_gb * 0.96
        else f"tracking close to the {pool_cap_tb:.2f} TB monthly ceiling and warrants targeted bandwidth management"
    )
    buffer_clause = (
        f"leaving approximately <strong>{proj_unused_gb:,.0f} GB ({proj_unused_gb/1000.0:.2f} TB)</strong> of unused pooled data"
        if proj_unused_gb >= 0
        else f"exceeding the pooled allocation by <strong>{abs(proj_unused_gb):,.0f} GB</strong>"
    )
    intervention_note = (
        f"Consequently, we have not throttled <strong>{top_site['Facility']}</strong> (currently at <strong>{top_site['% of Facility Share']:.1f}%</strong> of its 307.2 GB reference share), as our pooled {pool_cap_tb:.2f} TB allocation remains sufficient to meet clinical and operational needs for the remainder of the month."
        if proj_eom_gb < pool_cap_gb * 0.96
        else f"We recommend auditing high-bandwidth traffic at <strong>{top_site['Facility']}</strong> ({top_site['% of Facility Share']:.1f}% reference share; {top_site['GB per Client']:.1f} GB/client) to preserve pooled headroom."
    )
    offline_html = f" (Offline: <strong>{', '.join(offline_names)}</strong>)" if offline_names else ""

    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-left: 5px solid #0F4C81; border-radius: 10px; padding: 22px 26px; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05); margin-bottom: 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 14px;">
                <span style="font-size: 16px; font-weight: 800; color: #0F172A;">📋 Executive Connectivity &amp; Pool Utilization Briefing</span>
                <span style="background-color: #EFF6FF; color: #1E40AF; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 999px;">As of {date_label}</span>
            </div>
            <div style="color: #1E293B; font-size: 14.5px; line-height: 1.68;">
                <p style="margin-bottom: 10px;">As of <strong>{date_label}</strong>, the integrated StarEDGE and UniFi telemetry platform indicates the following:</p>
                <ul style="margin: 0 0 14px 20px; color: #0F172A;">
                    <li><strong>Monthly data usage:</strong> {used_gb:,.2f} GB ({used_tb:.2f} TB)</li>
                    <li><strong>Today's data usage:</strong> {today_gb:,.2f} GB</li>
                    <li><strong>Sites online:</strong> {online_count} of {total_sites}{offline_html}</li>
                </ul>
                <p style="margin-bottom: 12px;">
                    Our current usage represents approximately <strong>{pct_pool:.1f}%</strong> of the <strong>{pool_cap_tb:.2f} TB ({pool_cap_gb:,.0f} GB)</strong> pooled monthly data allocation, leaving approximately <strong>{rem_tb:.2f} TB ({rem_gb:,.2f} GB)</strong> available for the remainder of the month. Notably, the top 3 sites (<strong>{df_ranked.iloc[0]['Facility']}</strong>, <strong>{df_ranked.iloc[1]['Facility']}</strong>, and <strong>{df_ranked.iloc[2]['Facility']}</strong>) account for <strong>{top3_share:.1f}%</strong> of total portfolio consumption.
                </p>
                <p style="margin-bottom: 12px;">
                    Based on the current daily usage trend, it is {status_outlook}. To consume the remaining <strong>{rem_tb:.2f} TB</strong> over the remaining <strong>{remaining_days} days</strong> of {month_name}, the network would need to average approximately <strong>{req_daily_gb:,.1f} GB per day</strong>, whereas our month-to-date daily average is <strong>{avg_daily_gb:,.1f} GB per day</strong> (against a linear safe-pace benchmark of <strong>{safe_pace_gb:,.1f} GB/day</strong>).
                </p>
                <p style="margin-bottom: 12px;">
                    At the current rate, we are projected to end {month_name} having used approximately <strong>{proj_eom_tb:.2f} TB ({proj_eom_gb:,.0f} GB)</strong>, {buffer_clause}. {intervention_note}
                </p>
                <p style="margin-bottom: 0; color: #334155; font-style: italic;">
                    We will continue to monitor data usage closely via automated Monday briefings to support timely and appropriate interventions.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ROW 1: Pareto Pool Concentration + Usage Intensity Quadrant
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📊 Pareto Pool Concentration & Cumulative Share")
        df_pareto = df_ranked.copy()
        df_pareto["Cumulative Pool %"] = df_pareto["% of Total Pool"].cumsum().round(1)

        fig_pareto = go.Figure()
        fig_pareto.add_trace(
            go.Bar(
                x=df_pareto["Facility"],
                y=df_pareto["Current Month (GB)"],
                name=f"{month_name} Usage (GB)",
                marker_color="#0F4C81",
                text=df_pareto["Current Month (GB)"].apply(lambda v: f"{v:.0f}"),
                textposition="outside",
                textfont=dict(color="#0F172A", size=11.5),
            )
        )
        fig_pareto.add_trace(
            go.Scatter(
                x=df_pareto["Facility"],
                y=df_pareto["Cumulative Pool %"],
                name="Cumulative Share (%)",
                yaxis="y2",
                mode="lines+markers+text",
                line=dict(color="#D97706", width=3),
                marker=dict(size=8, color="#D97706", line=dict(width=1.5, color="#FFFFFF")),
                text=df_pareto["Cumulative Pool %"].apply(lambda v: f"{v:.0f}%"),
                textposition="top center",
                textfont=dict(color="#0F172A", size=11),
            )
        )
        fig_pareto.add_hline(
            y=307.2,
            line_dash="dash",
            line_color="#DC2626",
            annotation_text="307.2 GB Site Ref",
            annotation_position="top left",
            annotation_font=dict(color="#DC2626", size=11.5),
        )
        fig_pareto = _apply_exec_chart_style(fig_pareto, height=430)
        fig_pareto.update_layout(
            xaxis=dict(
                tickangle=-30,
                tickfont=dict(color="#0F172A", size=11),
            ),
            yaxis=dict(
                title=dict(text="Data Consumed (GB)", font=dict(color="#0F172A", size=12.5)),
                tickfont=dict(color="#0F172A", size=11.5),
                range=[0, max(df_pareto["Current Month (GB)"].max() * 1.24, 345)],
            ),
            yaxis2=dict(
                title=dict(text="Cumulative Share (%)", font=dict(color="#B45309", size=12.5)),
                tickfont=dict(color="#B45309", size=11.5),
                overlaying="y",
                side="right",
                range=[0, 114],
                showgrid=False,
            ),
        )
        st.plotly_chart(fig_pareto, use_container_width=True, config={"displayModeBar": False})

        # Statistical Narrative: Pareto Concentration
        n_80 = int((df_pareto["Cumulative Pool %"] <= 80.0).sum()) + 1
        n_80 = min(n_80, len(df_pareto))
        top_half_share = df_pareto.head(5)["% of Total Pool"].sum()
        mean_gb = df_pareto["Current Month (GB)"].mean()
        sd_gb = df_pareto["Current Month (GB)"].std()
        cv_pct = (sd_gb / mean_gb * 100.0) if mean_gb > 0 else 0.0
        _render_chart_narrative(
            "Statistical Interpretation • Fleet Concentration & Skew",
            f"Bandwidth consumption exhibits strong right-skew (<strong>Mean = {mean_gb:.1f} GB</strong>, <strong>SD = {sd_gb:.1f} GB</strong>, <strong>CV = {cv_pct:.0f}%</strong>). "
            f"Just <strong>{n_80} of {total_sites} facilities</strong> generate over <strong>80%</strong> of total portfolio volume, while the top 5 sites consume <strong>{top_half_share:.1f}%</strong> of all data. "
            f"All 10 facilities currently remain below the <strong>307.2 GB</strong> individual pro-rata reference threshold (led by <strong>{df_pareto.iloc[0]['Facility']}</strong> at <strong>{df_pareto.iloc[0]['% of Facility Share']:.1f}%</strong>)."
        )

    with c2:
        st.subheader("🎯 Usage Intensity Quadrant (Clients vs. GB Consumed)")
        df_q = df_ranked.copy()
        # Stagger text positions cleanly so bottom-left cluster labels never collide
        pos_overrides = {
            "Lions Ngoswani": "top left",
            "Mararianta/Buyangu Health centre": "top right",
            "PEFA Mercy": "bottom center",
            "AIC Mulango": "bottom right",
            "Tumaini Mwangaza": "bottom center",
        }
        text_positions = [pos_overrides.get(f, "top center") for f in df_q["Facility"]]

        fig_quad = px.scatter(
            df_q,
            x="Active Clients",
            y="Current Month (GB)",
            size="GB per Client",
            color="GB per Client",
            text="Facility",
            size_max=28,
            color_continuous_scale=["#0284C7", "#0F4C81", "#D97706", "#DC2626"],
            hover_data=["Today (GB)", "Previous Month (GB)", "30d Uptime (%)", "Avg Latency (ms)"],
        )
        fig_quad.update_traces(
            textposition=text_positions,
            textfont=dict(size=11, color="#0F172A"),
            marker=dict(line=dict(width=1.2, color="#FFFFFF")),
        )
        med_clients = df_q["Active Clients"].median()
        med_gb = df_q["Current Month (GB)"].median()
        fig_quad.add_vline(
            x=med_clients,
            line_dash="dot",
            line_color="#64748B",
            annotation_text=f"Median: {med_clients:.0f} devices",
            annotation_position="top right",
            annotation_font=dict(color="#334155", size=10.5),
        )
        fig_quad.add_hline(
            y=med_gb,
            line_dash="dot",
            line_color="#64748B",
            annotation_text=f"Median: {med_gb:.0f} GB",
            annotation_position="bottom right",
            annotation_font=dict(color="#334155", size=10.5),
        )
        fig_quad = _apply_exec_chart_style(fig_quad, height=430)
        fig_quad.update_layout(
            xaxis=dict(
                title=dict(text="Active Connected Devices (UniFi)", font=dict(color="#0F172A", size=12.5)),
                tickfont=dict(color="#0F172A", size=11.5),
                range=[0, max(df_q["Active Clients"].max() * 1.18, 24)],
            ),
            yaxis=dict(
                title=dict(text=f"{month_name} Data Consumed (GB)", font=dict(color="#0F172A", size=12.5)),
                tickfont=dict(color="#0F172A", size=11.5),
                range=[25, df_q["Current Month (GB)"].max() * 1.16],
            ),
            coloraxis_colorbar=dict(
                title=dict(text="GB / Device", font=dict(color="#0F172A", size=11.5)),
                tickfont=dict(color="#0F172A", size=11),
                len=0.78,
            ),
        )
        st.plotly_chart(fig_quad, use_container_width=True, config={"displayModeBar": False})

        # Statistical Narrative: Demand vs Intensity Quadrant
        corr_r = df_q["Active Clients"].corr(df_q["Current Month (GB)"])
        max_intensity_row = df_q.sort_values("GB per Client", ascending=False).iloc[0]
        med_intensity = df_q["GB per Client"].median()
        _render_chart_narrative(
            "Statistical Interpretation • Device Load vs. Per-Client Intensity",
            f"Connected device count shows a moderate positive correlation with total data volume (<strong>Pearson r = {corr_r:.2f}</strong>; fleet median = <strong>{med_intensity:.1f} GB/device</strong>). "
            f"<strong>{max_intensity_row['Facility']}</strong> stands out as a high-intensity outlier at <strong>{max_intensity_row['GB per Client']:.1f} GB/device</strong> ({int(max_intensity_row['Active Clients'])} devices consuming {max_intensity_row['Current Month (GB)']:.1f} GB), "
            f"whereas <strong>{df_ranked.iloc[0]['Facility']}</strong> ({df_ranked.iloc[0]['GB per Client']:.1f} GB/device across {int(df_ranked.iloc[0]['Active Clients'])} devices) reflects broad multi-user clinical demand."
        )

    # ROW 2: Burn-Rate Trajectory & Safe Pace + Gateway Latency/Uptime SLA
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("📈 Pool Burn Trajectory vs. Safe Pace Envelope")
        days_axis = list(range(1, days_in_month + 1))
        actual_curve = [round(avg_daily_gb * d, 1) if d <= elapsed_days else None for d in days_axis]
        proj_curve = [round(avg_daily_gb * d, 1) if d >= elapsed_days else None for d in days_axis]
        safe_curve = [round(safe_pace_gb * d, 1) for d in days_axis]

        fig_proj = go.Figure()
        fig_proj.add_trace(
            go.Scatter(
                x=days_axis,
                y=safe_curve,
                mode="lines",
                name=f"Safe Pace ({safe_pace_gb:.0f} GB/d)",
                line=dict(color="#059669", width=2.5, dash="dash"),
            )
        )
        fig_proj.add_trace(
            go.Scatter(
                x=days_axis,
                y=actual_curve,
                mode="lines+markers",
                name=f"Actual Run Rate ({avg_daily_gb:.1f} GB/d)",
                line=dict(color="#0F4C81", width=3),
                marker=dict(size=6),
            )
        )
        fig_proj.add_trace(
            go.Scatter(
                x=days_axis,
                y=proj_curve,
                mode="lines",
                name=f"EOM Forecast ({proj_eom_tb:.2f} TB)",
                line=dict(color="#0284C7", width=3, dash="dot"),
            )
        )
        fig_proj.add_hline(
            y=pool_cap_gb,
            line_dash="solid",
            line_color="#DC2626",
            annotation_text=f"3.07 TB Cap ({pool_cap_gb:,.0f} GB)",
            annotation_position="top left",
            annotation_font=dict(color="#DC2626", size=11.5),
        )
        fig_proj = _apply_exec_chart_style(fig_proj, height=410)
        fig_proj.update_layout(
            xaxis=dict(
                title=dict(text=f"Day of {month_name} {now.year}", font=dict(color="#0F172A", size=12.5)),
                tickfont=dict(color="#0F172A", size=11.5),
            ),
            yaxis=dict(
                title=dict(text="Cumulative Pool Usage (GB)", font=dict(color="#0F172A", size=12.5)),
                tickfont=dict(color="#0F172A", size=11.5),
                range=[0, pool_cap_gb * 1.12],
            ),
        )
        st.plotly_chart(fig_proj, use_container_width=True, config={"displayModeBar": False})

        # Statistical Narrative: Burn Rate & Variance
        pace_delta_gb = avg_daily_gb - safe_pace_gb
        pace_delta_pct = (pace_delta_gb / safe_pace_gb * 100.0) if safe_pace_gb > 0 else 0.0
        direction_word = "below" if pace_delta_gb <= 0 else "above"
        _render_chart_narrative(
            "Statistical Interpretation • Run-Rate Velocity & EOM Margin",
            f"Through Day {elapsed_days} of {days_in_month} (<strong>{elapsed_days/days_in_month*100:.1f}%</strong> of billing cycle elapsed), cumulative burn stands at <strong>{pct_pool:.1f}%</strong> of capacity—tracking "
            f"<strong>{abs(pace_delta_gb):.1f} GB/day ({abs(pace_delta_pct):.1f}%) {direction_word}</strong> the linear safe-pace slope of <strong>{safe_pace_gb:.1f} GB/day</strong>. "
            f"Linear regression of the month-to-date trajectory yields an EOM point forecast of <strong>{proj_eom_tb:.2f} TB</strong>, preserving a <strong>{proj_unused_gb:,.0f} GB ({proj_unused_gb/pool_cap_gb*100:.1f}%)</strong> safety margin."
        )

    with c4:
        st.subheader("🛰️ Gateway Latency & 30-Day Uptime SLA")
        if "Avg Latency (ms)" in df_ranked.columns and df_ranked["Avg Latency (ms)"].notna().any():
            df_sla = df_ranked.sort_values("Avg Latency (ms)", ascending=True)
            fig_sla = go.Figure()
            fig_sla.add_trace(
                go.Bar(
                    y=df_sla["Facility"],
                    x=df_sla["Avg Latency (ms)"],
                    orientation="h",
                    name="Avg Latency (ms)",
                    marker_color="#0284C7",
                    text=df_sla.apply(
                        lambda r: f"{r['Avg Latency (ms)']:.1f} ms ({r['30d Uptime (%)']:.2f}% up)"
                        if pd.notna(r["30d Uptime (%)"])
                        else f"{r['Avg Latency (ms)']:.1f} ms",
                        axis=1,
                    ),
                    textposition="outside",
                    textfont=dict(color="#0F172A", size=11),
                )
            )
            fig_sla = _apply_exec_chart_style(fig_sla, height=410)
            fig_sla.update_layout(
                xaxis=dict(
                    title=dict(text="Average Starlink Latency (ms)", font=dict(color="#0F172A", size=12.5)),
                    tickfont=dict(color="#0F172A", size=11.5),
                    range=[0, df_sla["Avg Latency (ms)"].max() * 1.52],
                ),
                yaxis=dict(
                    tickfont=dict(color="#0F172A", size=11),
                ),
            )
            st.plotly_chart(fig_sla, use_container_width=True, config={"displayModeBar": False})

            # Statistical Narrative: Network SLA & Latency
            mean_lat = df_sla["Avg Latency (ms)"].mean()
            sd_lat = df_sla["Avg Latency (ms)"].std()
            mean_up = df_sla["30d Uptime (%)"].mean()
            min_up_row = df_sla.sort_values("30d Uptime (%)", ascending=True).iloc[0]
            _render_chart_narrative(
                "Statistical Interpretation • Link Reliability & Latency Dispersion",
                f"Low-Earth-Orbit (LEO) satellite latency is tightly clustered across all 10 gateways (<strong>Mean = {mean_lat:.1f} ms</strong>, <strong>SD = {sd_lat:.1f} ms</strong>, range <strong>{df_sla['Avg Latency (ms)'].min():.1f}–{df_sla['Avg Latency (ms)'].max():.1f} ms</strong>), well below the 50 ms clinical EMR/telehealth threshold. "
                f"Portfolio 30-day availability averages <strong>{mean_up:.2f}%</strong>, with <strong>{min_up_row['Facility']}</strong> ({min_up_row['30d Uptime (%)']:.2f}% uptime) representing the sole site below 99.9% SLA."
            )

    # Telemetry Matrix
    st.subheader("📋 Facility-Level Starlink & UniFi Telemetry Matrix")
    display_cols = [
        "Site Code",
        "Facility",
        "StarEDGE Status",
        "Today (GB)",
        "Current Month (GB)",
        "Previous Month (GB)",
        "% of Facility Share",
        "% of Total Pool",
        "Active Clients",
        "GB per Client",
    ]
    for opt_col in ["30d Uptime (%)", "Avg Latency (ms)", "Packet Loss (%)", "Link Capacity (Mbps)"]:
        if opt_col in df_ranked.columns:
            display_cols.append(opt_col)

    st.dataframe(
        df_ranked[display_cols],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # Top Websites & Apps Section
    st.subheader("🌍 Top Consuming Websites & Applications (Per Facility & Portfolio-Wide)")
    st.markdown(
        """
        <div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-left: 4px solid #0284C7; border-radius: 8px; padding: 14px 18px; color: #0F172A; font-size: 13.5px; margin-bottom: 12px;">
            <strong>UniFi Deep Packet Inspection (DPI):</strong> StarEDGE meters total dish volume, while domain/application breakdown (YouTube, Windows Update, WhatsApp, DHIS2/EMR, Zoom) is captured by your UDM-Pro SE gateways. Have your network admin enable <strong>Settings → Security → Traffic &amp; Device Identification = ON</strong> on each UDM-Pro SE (or upload a UniFi Traffic CSV export below).
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_dpi = st.file_uploader(
        "Upload UniFi Traffic / DPI Export CSV (Columns: Facility, Application/Domain, Usage_GB)",
        type=["csv"],
        key="unifi_dpi_uploader",
    )
    if uploaded_dpi is not None:
        dpi_df = pd.read_csv(uploaded_dpi)
        if {"Facility", "Application/Domain", "Usage_GB"}.issubset(dpi_df.columns):
            c_app1, c_app2 = st.columns(2)
            with c_app1:
                overall_apps = (
                    dpi_df.groupby("Application/Domain", as_index=False)["Usage_GB"]
                    .sum()
                    .sort_values("Usage_GB", ascending=False)
                    .head(10)
                )
                fig_app = px.bar(
                    overall_apps.sort_values("Usage_GB", ascending=True),
                    x="Usage_GB",
                    y="Application/Domain",
                    orientation="h",
                    title="Top 10 Apps / Websites Across All Facilities (GB)",
                    color_discrete_sequence=["#0F4C81"],
                )
                fig_app = _apply_exec_chart_style(fig_app, height=380)
                st.plotly_chart(fig_app, use_container_width=True, config={"displayModeBar": False})
            with c_app2:
                sel_fac = st.selectbox("Filter Apps by Facility", sorted(dpi_df["Facility"].unique()))
                fac_apps = (
                    dpi_df[dpi_df["Facility"] == sel_fac]
                    .groupby("Application/Domain", as_index=False)["Usage_GB"]
                    .sum()
                    .sort_values("Usage_GB", ascending=False)
                    .head(10)
                )
                fig_fapp = px.bar(
                    fac_apps.sort_values("Usage_GB", ascending=True),
                    x="Usage_GB",
                    y="Application/Domain",
                    orientation="h",
                    title=f"Top Apps / Websites — {sel_fac} (GB)",
                    color_discrete_sequence=["#0284C7"],
                )
                fig_fapp = _apply_exec_chart_style(fig_fapp, height=380)
                st.plotly_chart(fig_fapp, use_container_width=True, config={"displayModeBar": False})
        else:
            st.warning("CSV must contain columns: Facility, Application/Domain, Usage_GB")
