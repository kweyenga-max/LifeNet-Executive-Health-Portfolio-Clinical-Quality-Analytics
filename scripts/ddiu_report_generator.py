import io
import re
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from scripts import finance_analytics as fa

# LifeNet International Executive Color Palette
LN_NAVY = "#0A2540"
LN_TEAL = "#00A8CC"
LN_EMERALD = "#0D9488"
LN_AMBER = "#D97706"
LN_CRIMSON = "#DC2626"
LN_SLATE = "#2D3748"
LN_MUTED = "#64748B"
LN_BG = "#F7FAFC"
LN_BORDER = "#E2E8F0"

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

EXCLUDED_FACILITIES = {"sambocho", "mwihila"}


def _is_active_facility(name: str) -> bool:
    low = str(name).strip().lower()
    return not any(ex in low for ex in EXCLUDED_FACILITIES)


def _parse_period_label(label: str):
    m = re.match(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s*(20\d{2})$", str(label).strip())
    if not m:
        return None
    return m.group(1), int(m.group(2))


def _period_sort_key(label: str):
    parsed = _parse_period_label(label)
    if not parsed:
        return (0, 0)
    return (parsed[1], MONTH_ORDER.index(parsed[0]) + 1)


def _prev_month_label(label: str) -> str:
    parsed = _parse_period_label(label)
    if not parsed:
        return ""
    m_name, yr = parsed
    idx = MONTH_ORDER.index(m_name)
    if idx == 0:
        return f"December {yr - 1}"
    return f"{MONTH_ORDER[idx - 1]} {yr}"


def _yoy_month_label(label: str) -> str:
    parsed = _parse_period_label(label)
    if not parsed:
        return ""
    return f"{parsed[0]} {parsed[1] - 1}"


def get_available_reporting_periods(base_dir: Path | None = None) -> list[str]:
    base_dir = base_dir or Path(__file__).resolve().parent.parent
    pv_path = base_dir / "data" / "khis_pv_snapshot.csv.gz"
    if not pv_path.exists():
        return ["October 2026"]
    df_pv = pd.read_csv(pv_path)
    periods = sorted({str(p).strip() for p in df_pv["Period"].dropna()}, key=_period_sort_key)
    return periods or ["October 2026"]


def default_ddiu_period(base_dir: Path | None = None, ref_date: datetime | None = None) -> str:
    ref_date = ref_date or datetime.now()
    periods = get_available_reporting_periods(base_dir)
    if ref_date.month == 1:
        target = f"December {ref_date.year - 1}"
    else:
        target = f"{MONTH_ORDER[ref_date.month - 2]} {ref_date.year}"
    if target in periods:
        return target
    return periods[-1]


def build_ddiu_dataset(period_label: str, base_dir: Path | None = None) -> dict:
    base_dir = base_dir or Path(__file__).resolve().parent.parent
    prev_label = _prev_month_label(period_label)
    yoy_label = _yoy_month_label(period_label)

    df_pv = pd.read_csv(base_dir / "data" / "khis_pv_snapshot.csv.gz")
    df_pv = df_pv[df_pv["organisationunitname"].apply(_is_active_facility)].copy()
    df_pv["PV"] = pd.to_numeric(df_pv["PV"], errors="coerce")

    facilities = sorted(df_pv["organisationunitname"].dropna().unique().tolist())

    pv_curr = df_pv[df_pv["Period"] == period_label].set_index("organisationunitname")["PV"]
    pv_prev = df_pv[df_pv["Period"] == prev_label].set_index("organisationunitname")["PV"]
    pv_yoy = df_pv[df_pv["Period"] == yoy_label].set_index("organisationunitname")["PV"]

    df_kpi = pd.read_csv(base_dir / "data" / "khis_kpi_snapshot.csv.gz")
    df_kpi = df_kpi[df_kpi["organisationunitname"].apply(_is_active_facility)].copy()
    df_kpi = df_kpi.set_index("organisationunitname")

    def _get_kpi_series(indicator_prefix: str, target_period: str) -> pd.Series:
        p_parsed = _parse_period_label(target_period)
        if not p_parsed:
            return pd.Series(dtype=float)
        tm, ty = p_parsed
        for col in [f"{indicator_prefix} {tm} {ty}", f"{indicator_prefix} {tm}{ty}"]:
            if col in df_kpi.columns:
                return pd.to_numeric(df_kpi[col], errors="coerce")
        return pd.Series(dtype=float)

    norm_del = _get_kpi_series("MOH 711 Normal Deliveries", period_label)
    cs_del = _get_kpi_series("MOH 711 Caesarian Sections", period_label)
    breech_del = _get_kpi_series("MOH 711 Breach Delivery", period_label)
    assisted_del = _get_kpi_series("MOH 711 Assisted vaginal delivery", period_label)
    total_del = norm_del.add(cs_del, fill_value=0).add(breech_del, fill_value=0).add(assisted_del, fill_value=0)
    all_del_na = norm_del.isna() & cs_del.isna() & breech_del.isna() & assisted_del.isna()
    total_del[all_del_na] = np.nan

    live_births = _get_kpi_series("MOH 711 Live birth", period_label)
    fsb = _get_kpi_series("MOH 711 Fresh Still Birth", period_label)
    msb = _get_kpi_series("MOH 711 Macerated still Birth", period_label)
    low_apgar = _get_kpi_series("MOH 711 Births with low APGAR score", period_label)
    pph = _get_kpi_series("MOH 711 PPH (Post Partum Haemorrage) A", period_label)
    mat_deaths = _get_kpi_series("MOH 711 Rev 2020_Maternal deaths 20-24 Years", period_label).add(
        _get_kpi_series("MOH 711 Rev 2020_Maternal deaths 25+ Years", period_label), fill_value=0
    )
    neo_deaths = _get_kpi_series("MOH 711 Neonatal deaths 0-28 Days", period_label)

    fin_snap_path = base_dir / "data" / "monitrac_finance_snapshot.csv.gz"
    fin_rev = pd.Series(dtype=float)
    fin_exp = pd.Series(dtype=float)
    if fin_snap_path.exists():
        df_fin = pd.read_csv(fin_snap_path)
        df_fin = df_fin[df_fin["organisationunitname"].apply(_is_active_facility)].copy().set_index("organisationunitname")
        rev_col = f"kny - fr - Total revenu {period_label}"
        exp_col = f"kny - fr - Total expenses {period_label}"
        if rev_col in df_fin.columns:
            fin_rev = pd.to_numeric(df_fin[rev_col], errors="coerce")
        if exp_col in df_fin.columns:
            fin_exp = pd.to_numeric(df_fin[exp_col], errors="coerce")

    rows = []
    for fac in facilities:
        p_c = pv_curr.get(fac, np.nan)
        p_p = pv_prev.get(fac, np.nan)
        p_y = pv_yoy.get(fac, np.nan)
        mom_pct = ((p_c - p_p) / p_p * 100.0) if pd.notna(p_c) and pd.notna(p_p) and p_p > 0 else np.nan
        yoy_pct = ((p_c - p_y) / p_y * 100.0) if pd.notna(p_c) and pd.notna(p_y) and p_y > 0 else np.nan

        td_c = total_del.get(fac, np.nan)
        lb_c = live_births.get(fac, np.nan)
        fsb_c = fsb.get(fac, 0.0) if pd.notna(fsb.get(fac, np.nan)) else 0.0
        msb_c = msb.get(fac, 0.0) if pd.notna(msb.get(fac, np.nan)) else 0.0
        apgar_c = low_apgar.get(fac, 0.0) if pd.notna(low_apgar.get(fac, np.nan)) else 0.0
        pph_c = pph.get(fac, 0.0) if pd.notna(pph.get(fac, np.nan)) else 0.0
        md_c = mat_deaths.get(fac, 0.0) if pd.notna(mat_deaths.get(fac, np.nan)) else 0.0
        nd_c = neo_deaths.get(fac, 0.0) if pd.notna(neo_deaths.get(fac, np.nan)) else 0.0

        rev_c = fin_rev.get(fac, np.nan)
        exp_c = fin_exp.get(fac, np.nan)
        net_c = (rev_c - exp_c) if pd.notna(rev_c) and pd.notna(exp_c) else np.nan

        queries = []
        if pd.isna(p_c):
            queries.append("Missing KHIS PV")
        elif p_c == 0:
            queries.append("Zero KHIS PV reported")
        if pd.notna(mom_pct) and mom_pct <= -30.0:
            queries.append(f"Sharp PV drop ({mom_pct:+.1f}% MoM)")
        elif pd.notna(mom_pct) and mom_pct >= 50.0:
            queries.append(f"PV spike audit ({mom_pct:+.1f}% MoM)")
        if pd.notna(td_c) and pd.notna(lb_c) and abs(td_c - (lb_c + fsb_c + msb_c)) >= 3:
            queries.append(f"MOH 711 Delivery vs Birth mismatch ({int(td_c)} del vs {int(lb_c + fsb_c + msb_c)} births)")
        if pd.isna(rev_c) and pd.isna(exp_c):
            queries.append("Missing MoniTrac Finance")
        elif pd.notna(net_c) and net_c < 0:
            queries.append(f"Operating deficit (KES {net_c:,.0f})")
        if md_c > 0:
            queries.append(f"Maternal death audit ({int(md_c)})")
        if (fsb_c + nd_c) >= 2:
            queries.append(f"Perinatal mortality review ({int(fsb_c)} FSB, {int(nd_c)} Neo)")

        rows.append({
            "Facility": fac,
            "PV_Current": p_c,
            "PV_Prev": p_p,
            "PV_YoY": p_y,
            "PV_MoM_%": mom_pct,
            "PV_YoY_%": yoy_pct,
            "Total_Deliveries": td_c,
            "Live_Births": lb_c,
            "FSB": fsb_c,
            "MSB": msb_c,
            "Low_APGAR": apgar_c,
            "PPH": pph_c,
            "Maternal_Deaths": md_c,
            "Neonatal_Deaths": nd_c,
            "Revenue_KES": rev_c,
            "Expenses_KES": exp_c,
            "Net_Surplus_KES": net_c,
            "Queries": "; ".join(queries) if queries else "Clean",
            "Query_Count": len(queries),
        })

    fac_df = pd.DataFrame(rows)

    periods_all = get_available_reporting_periods(base_dir)
    if period_label in periods_all:
        end_pos = periods_all.index(period_label)
        trend_periods = periods_all[max(0, end_pos - 5): end_pos + 1]
    else:
        trend_periods = periods_all[-6:]

    trend_rows = []
    fin_map = {}
    if fin_snap_path.exists():
        for tp in trend_periods:
            rc, ec = f"kny - fr - Total revenu {tp}", f"kny - fr - Total expenses {tp}"
            rv = float(pd.to_numeric(df_fin[rc], errors="coerce").sum()) if rc in df_fin.columns else 0.0
            ex = float(pd.to_numeric(df_fin[ec], errors="coerce").sum()) if ec in df_fin.columns else 0.0
            fin_map[tp] = (rv, ex)

    for tp in trend_periods:
        pv_sum = float(df_pv[df_pv["Period"] == tp]["PV"].sum())
        del_sum = float(
            _get_kpi_series("MOH 711 Normal Deliveries", tp).sum()
            + _get_kpi_series("MOH 711 Caesarian Sections", tp).sum()
            + _get_kpi_series("MOH 711 Breach Delivery", tp).sum()
            + _get_kpi_series("MOH 711 Assisted vaginal delivery", tp).sum()
        )
        pph_t = int(_get_kpi_series("MOH 711 PPH (Post Partum Haemorrage) A", tp).sum())
        pph_d_t = int(_get_kpi_series("MOH 711 PPH (Post Partum Haemorrage)D", tp).sum())
        pph_succ_t = ((pph_t - pph_d_t) / pph_t * 100.0) if pph_t > 0 else 100.0
        apgar_t = int(_get_kpi_series("MOH 711 Births with low APGAR score", tp).sum())
        asph_t = int(_get_kpi_series("MOH 711 Rev 2020_Neonatal deaths due to Asphyxia", tp).sum())
        apgar_succ_t = (max(apgar_t - asph_t, 0) / apgar_t * 100.0) if apgar_t > 0 else 100.0
        md_t = int(
            _get_kpi_series("MOH 711 Rev 2020_Maternal deaths 20-24 Years", tp).sum()
            + _get_kpi_series("MOH 711 Rev 2020_Maternal deaths 25+ Years", tp).sum()
        )
        rev_t, exp_t = fin_map.get(tp, (0.0, 0.0))
        trend_rows.append({
            "Period": tp,
            "Short_Period": f"{tp.split()[0][:3]} '{tp.split()[1][2:]}",
            "Total_PV": pv_sum,
            "Total_Deliveries": del_sum,
            "PPH_Cases": pph_t,
            "PPH_Deaths": pph_d_t,
            "PPH_Success_Pct": round(pph_succ_t, 1),
            "Low_APGAR": apgar_t,
            "Asphyxia_Deaths": asph_t,
            "APGAR_Success_Pct": round(apgar_succ_t, 1),
            "Maternal_Deaths": md_t,
            "Revenue_KES": rev_t,
            "Expenses_KES": exp_t,
        })
    trend_df = pd.DataFrame(trend_rows)

    tot_pv = float(fac_df["PV_Current"].sum())
    tot_pv_prev = float(fac_df["PV_Prev"].sum())
    tot_pv_yoy = float(fac_df["PV_YoY"].sum())
    pv_mom_pct = ((tot_pv - tot_pv_prev) / tot_pv_prev * 100.0) if tot_pv_prev > 0 else 0.0
    pv_yoy_pct = ((tot_pv - tot_pv_yoy) / tot_pv_yoy * 100.0) if tot_pv_yoy > 0 else 0.0

    khis_reporting = int(fac_df["PV_Current"].notna().sum())
    fin_reporting = int(fac_df["Revenue_KES"].notna().sum())
    tot_del = int(fac_df["Total_Deliveries"].sum())
    tot_lb = int(fac_df["Live_Births"].sum())
    tot_fsb = int(fac_df["FSB"].sum())
    tot_msb = int(fac_df["MSB"].sum())
    tot_pph = int(fac_df["PPH"].sum())
    tot_apgar = int(fac_df["Low_APGAR"].sum())
    tot_md = int(fac_df["Maternal_Deaths"].sum())
    tot_nd = int(fac_df["Neonatal_Deaths"].sum())

    tot_rev = float(fac_df["Revenue_KES"].sum())
    tot_exp = float(fac_df["Expenses_KES"].sum())
    tot_net = tot_rev - tot_exp
    cost_coverage = (tot_rev / tot_exp * 100.0) if tot_exp > 0 else 0.0

    well_df = fac_df[
        (fac_df["PV_Current"].notna())
        & ((fac_df["PV_MoM_%"] >= 5.0) | (fac_df["PV_YoY_%"] >= 10.0))
        & ((fac_df["Net_Surplus_KES"].isna()) | (fac_df["Net_Surplus_KES"] >= 0))
    ].sort_values(by=["PV_YoY_%", "PV_Current"], ascending=[False, False]).head(8)

    follow_up_df = fac_df[fac_df["Query_Count"] > 0].sort_values(
        by=["Query_Count", "PV_Current"], ascending=[False, False]
    )

    action_items = []
    missing_khis = fac_df[fac_df["PV_Current"].isna()]["Facility"].tolist()
    if missing_khis:
        action_items.append({
            "Owner": "M&E Team",
            "Priority": "High",
            "Focus Area": "KHIS Reporting Completeness",
            "Facilities": ", ".join(missing_khis[:6]) + (f" (+{len(missing_khis)-6} more)" if len(missing_khis) > 6 else ""),
            "Action Required": f"Follow up with HRIOs/Facility In-Charges to verify and key missing {period_label} MOH 705/711 returns before lock.",
        })
    mismatch_facs = fac_df[fac_df["Queries"].str.contains("mismatch", case=False, na=False)]["Facility"].tolist()
    if mismatch_facs:
        action_items.append({
            "Owner": "M&E Team",
            "Priority": "High",
            "Focus Area": "MOH 711 Internal Consistency DQA",
            "Facilities": ", ".join(mismatch_facs[:5]),
            "Action Required": "Reconcile maternity register totals (Normal + C/S + Breech + Assisted) against Live Births + Stillbirths in KHIS.",
        })
    missing_fin = fac_df[fac_df["Revenue_KES"].isna() & fac_df["Expenses_KES"].isna()]["Facility"].tolist()
    if missing_fin:
        action_items.append({
            "Owner": "M&E & Finance Leads",
            "Priority": "High",
            "Focus Area": "MoniTrac Financial Submission Gap",
            "Facilities": ", ".join(missing_fin[:6]) + (f" (+{len(missing_fin)-6} more)" if len(missing_fin) > 6 else ""),
            "Action Required": f"Prompt facility administrators to upload {period_label} income & expense ledgers into MoniTrac.",
        })
    clinical_audit_facs = fac_df[
        (fac_df["Maternal_Deaths"] > 0) | ((fac_df["FSB"] + fac_df["Neonatal_Deaths"]) >= 2) | (fac_df["PPH"] >= 2)
    ]["Facility"].tolist()
    if clinical_audit_facs:
        action_items.append({
            "Owner": "Medical Mentors",
            "Priority": "Critical",
            "Focus Area": "MPDSR & EmONC Clinical Audit",
            "Facilities": ", ".join(clinical_audit_facs[:6]),
            "Action Required": "Conduct Maternal & Perinatal Death Surveillance (MPDSR) review, partograph audit, and PPH/newborn resuscitation coaching.",
        })
    deficit_facs = fac_df[fac_df["Net_Surplus_KES"] < 0].sort_values("Net_Surplus_KES")["Facility"].tolist()
    if deficit_facs:
        action_items.append({
            "Owner": "Management Mentors",
            "Priority": "Medium-High",
            "Focus Area": "Operating Deficit & Cost Recovery",
            "Facilities": ", ".join(deficit_facs[:6]),
            "Action Required": "Review SHA/insurance claim reimbursement delays, pharmaceutical stock leakage, and payroll-to-revenue ratios.",
        })
    pv_drop_facs = fac_df[fac_df["PV_MoM_%"] <= -25.0]["Facility"].tolist()
    if pv_drop_facs:
        action_items.append({
            "Owner": "Field Ops & Mentors",
            "Priority": "Medium",
            "Focus Area": "Patient Volume Retention",
            "Facilities": ", ".join(pv_drop_facs[:6]),
            "Action Required": "Investigate root causes of >25% MoM attendance drop (drug stockouts, staffing gaps, or outreach schedule).",
        })

    return {
        "period": period_label,
        "prev_period": prev_label,
        "yoy_period": yoy_label,
        "total_facilities": len(fac_df),
        "khis_reporting": khis_reporting,
        "fin_reporting": fin_reporting,
        "tot_pv": tot_pv,
        "pv_mom_pct": pv_mom_pct,
        "pv_yoy_pct": pv_yoy_pct,
        "tot_del": tot_del,
        "tot_lb": tot_lb,
        "tot_fsb": tot_fsb,
        "tot_msb": tot_msb,
        "tot_pph": tot_pph,
        "tot_apgar": tot_apgar,
        "tot_md": tot_md,
        "tot_nd": tot_nd,
        "tot_rev": tot_rev,
        "tot_exp": tot_exp,
        "tot_net": tot_net,
        "cost_coverage": cost_coverage,
        "facility_df": fac_df,
        "trend_df": trend_df,
        "well_df": well_df,
        "follow_up_df": follow_up_df,
        "action_df": pd.DataFrame(action_items),
    }


def _render_charts_png(data: dict) -> dict[str, io.BytesIO]:
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = LN_BORDER
    plt.rcParams["axes.linewidth"] = 0.8

    charts = {}
    trend = data["trend_df"]

    fig, ax1 = plt.subplots(figsize=(7.2, 2.7), dpi=220)
    x = np.arange(len(trend))
    bars = ax1.bar(x, trend["Total_PV"], width=0.52, color=LN_NAVY, alpha=0.9, label="Total Patient Visits (PV)")
    ax1.set_ylabel("Patient Visits", color=LN_NAVY, fontsize=8.5, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(trend["Short_Period"], fontsize=8.5, fontweight="bold", color=LN_SLATE)
    ax1.tick_params(axis="y", labelsize=8, labelcolor=LN_NAVY)
    ax1.grid(axis="y", linestyle="--", alpha=0.4, color="#CBD5E1")
    ax1.set_axisbelow(True)
    ax1.spines["top"].set_visible(False)

    for b in bars:
        h = b.get_height()
        if h > 0:
            ax1.text(b.get_x() + b.get_width() / 2, h + max(trend["Total_PV"].max() * 0.02, 50),
                     f"{int(h):,}", ha="center", va="bottom", fontsize=7.2, fontweight="bold", color=LN_NAVY)

    ax2 = ax1.twinx()
    ax2.plot(x, trend["Total_Deliveries"], color=LN_TEAL, marker="o", linewidth=2.2, markersize=5.5, label="Total Deliveries")
    for xi, val in zip(x, trend["Total_Deliveries"]):
        ax2.annotate(f"{int(val):,}", (xi, val), xytext=(0, 6), textcoords="offset points", ha="center", va="bottom", fontsize=7.0, fontweight="bold", color=LN_TEAL)
    ax2.set_ylabel("Deliveries", color=LN_TEAL, fontsize=8.5, fontweight="bold")
    ax2.tick_params(axis="y", labelsize=8, labelcolor=LN_TEAL)
    ax2.spines["top"].set_visible(False)
    ax2.set_ylim(0, max(trend["Total_Deliveries"].max() * 1.25, 10))

    ax1.set_title(f"Network Patient Visits & Maternity Deliveries Trend (Through {data['period']})",
                  fontsize=9.5, fontweight="bold", color=LN_NAVY, loc="left", pad=10)
    fig.tight_layout()
    buf1 = io.BytesIO()
    fig.savefig(buf1, format="png")
    plt.close(fig)
    buf1.seek(0)
    charts["pv_trend"] = buf1

    top_pv = data["facility_df"].dropna(subset=["PV_Current"]).sort_values("PV_Current", ascending=True).tail(10)
    fig, ax = plt.subplots(figsize=(7.2, 2.8), dpi=220)
    labels = [f[:28] + "..." if len(f) > 31 else f for f in top_pv["Facility"]]
    bar_colors = [LN_EMERALD if (pd.notna(v) and v >= 0) else LN_TEAL for v in top_pv["PV_MoM_%"]]
    bars = ax.barh(labels, top_pv["PV_Current"], color=bar_colors, height=0.62)
    ax.set_title(f"Top 10 High-Volume Partner Facilities — {data['period']} Patient Visits",
                 fontsize=9.5, fontweight="bold", color=LN_NAVY, loc="left", pad=8)
    ax.tick_params(axis="both", labelsize=7.8, labelcolor=LN_SLATE)
    ax.grid(axis="x", linestyle="--", alpha=0.4, color="#CBD5E1")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, max(top_pv["PV_Current"].max() * 1.18, 100))
    for b, (_, r) in zip(bars, top_pv.iterrows()):
        w = b.get_width()
        mom_txt = f" ({r['PV_MoM_%']:+.0f}%)" if pd.notna(r["PV_MoM_%"]) else ""
        ax.text(w + max(top_pv["PV_Current"].max() * 0.015, 10), b.get_y() + b.get_height() / 2,
                f"{int(w):,}{mom_txt}", va="center", fontsize=7.2, fontweight="bold", color=LN_SLATE)
    fig.tight_layout()
    buf2 = io.BytesIO()
    fig.savefig(buf2, format="png")
    plt.close(fig)
    buf2.seek(0)
    charts["top_facilities"] = buf2

    fig, ax = plt.subplots(figsize=(7.2, 2.5), dpi=220)
    w = 0.36
    bars_rev = ax.bar(x - w / 2, trend["Revenue_KES"] / 1e6, width=w, color=LN_EMERALD, label="Total Revenue (M KES)")
    bars_exp = ax.bar(x + w / 2, trend["Expenses_KES"] / 1e6, width=w, color=LN_AMBER, label="Total Expenses (M KES)")
    for b in bars_rev:
        h = b.get_height()
        ax.annotate(f"{h:.1f}M", (b.get_x() + b.get_width()/2, h), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=6.8, fontweight="bold", color=LN_EMERALD)
    for b in bars_exp:
        h = b.get_height()
        ax.annotate(f"{h:.1f}M", (b.get_x() + b.get_width()/2, h), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=6.8, fontweight="bold", color=LN_AMBER)
    ax.set_ylim(0, max(trend["Revenue_KES"].max(), trend["Expenses_KES"].max()) / 1e6 * 1.18)
    ax.set_xticks(x)
    ax.set_xticklabels(trend["Short_Period"], fontsize=8.5, fontweight="bold", color=LN_SLATE)
    ax.set_ylabel("KES (Millions)", fontsize=8.5, fontweight="bold", color=LN_NAVY)
    ax.set_title("MoniTrac Network Revenue vs. Operating Expenses (KES Millions)",
                 fontsize=9.5, fontweight="bold", color=LN_NAVY, loc="left", pad=8)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.4, color="#CBD5E1")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    buf3 = io.BytesIO()
    fig.savefig(buf3, format="png")
    plt.close(fig)
    buf3.seek(0)
    charts["finance_trend"] = buf3

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(7.2, 2.35), dpi=220)
    bars_pph = ax_l.bar(x, trend["PPH_Cases"], width=0.48, color=LN_AMBER, label="PPH Cases")
    for b in bars_pph:
        h = b.get_height()
        ax_l.annotate(f"{int(h)}", (b.get_x() + b.get_width()/2, h), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=6.8, fontweight="bold", color=LN_AMBER)
    ax_l.set_ylim(0, max(trend["PPH_Cases"].max(), 1) * 1.28)
    ax_l.set_xticks(x)
    ax_l.set_xticklabels(trend["Short_Period"], fontsize=7.5, fontweight="bold", color=LN_SLATE)
    ax_l.set_ylabel("PPH Cases", fontsize=7.8, fontweight="bold", color=LN_AMBER)
    ax_l.tick_params(axis="y", labelsize=7.5)
    ax_l.spines["top"].set_visible(False)
    ax_l2 = ax_l.twinx()
    ax_l2.plot(x, trend["PPH_Success_Pct"], color=LN_EMERALD, marker="o", linewidth=2, markersize=4.5, label="Survival %")
    for xi, pct in zip(x, trend["PPH_Success_Pct"]):
        ax_l2.annotate(f"{pct:.0f}%", (xi, pct), xytext=(0, 5), textcoords="offset points", ha="center", va="bottom", fontsize=6.5, fontweight="bold", color=LN_EMERALD)
    ax_l2.set_ylim(0, 118)
    ax_l2.set_ylabel("Survival %", fontsize=7.8, fontweight="bold", color=LN_EMERALD)
    ax_l2.tick_params(axis="y", labelsize=7.5)
    ax_l2.spines["top"].set_visible(False)
    ax_l.set_title("PPH Cases & Survival %", fontsize=8.8, fontweight="bold", color=LN_NAVY, loc="left")

    bars_apg = ax_r.bar(x, trend["Low_APGAR"], width=0.48, color=LN_NAVY, label="Low APGAR")
    for b in bars_apg:
        h = b.get_height()
        ax_r.annotate(f"{int(h)}", (b.get_x() + b.get_width()/2, h), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=6.8, fontweight="bold", color=LN_NAVY)
    ax_r.set_ylim(0, max(trend["Low_APGAR"].max(), 1) * 1.28)
    ax_r.set_xticks(x)
    ax_r.set_xticklabels(trend["Short_Period"], fontsize=7.5, fontweight="bold", color=LN_SLATE)
    ax_r.set_ylabel("Low APGAR Births", fontsize=7.8, fontweight="bold", color=LN_NAVY)
    ax_r.tick_params(axis="y", labelsize=7.5)
    ax_r.spines["top"].set_visible(False)
    ax_r2 = ax_r.twinx()
    ax_r2.plot(x, trend["APGAR_Success_Pct"], color=LN_TEAL, marker="o", linewidth=2, markersize=4.5, label="Resusc. %")
    for xi, pct in zip(x, trend["APGAR_Success_Pct"]):
        ax_r2.annotate(f"{pct:.0f}%", (xi, pct), xytext=(0, 5), textcoords="offset points", ha="center", va="bottom", fontsize=6.5, fontweight="bold", color=LN_TEAL)
    ax_r2.set_ylim(0, 118)
    ax_r2.set_ylabel("Resusc. Success %", fontsize=7.8, fontweight="bold", color=LN_TEAL)
    ax_r2.tick_params(axis="y", labelsize=7.5)
    ax_r2.spines["top"].set_visible(False)
    ax_r.set_title("Low APGAR & Resuscitation %", fontsize=8.8, fontweight="bold", color=LN_NAVY, loc="left")

    fig.tight_layout()
    buf4 = io.BytesIO()
    fig.savefig(buf4, format="png")
    plt.close(fig)
    buf4.seek(0)
    charts["emonc_trend"] = buf4

    return charts


def generate_ddiu_pdf_bytes(period_label: str, base_dir: Path | None = None) -> bytes:
    data = build_ddiu_dataset(period_label, base_dir=base_dir)
    charts = _render_charts_png(data)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    c_navy = colors.HexColor(LN_NAVY)
    c_teal = colors.HexColor(LN_TEAL)
    c_emerald = colors.HexColor(LN_EMERALD)
    c_amber = colors.HexColor(LN_AMBER)
    c_crimson = colors.HexColor(LN_CRIMSON)
    c_dark = colors.HexColor(LN_SLATE)
    c_light = colors.HexColor(LN_BG)
    c_border = colors.HexColor(LN_BORDER)

    styles = getSampleStyleSheet()
    s_title = ParagraphStyle("LNTitle", parent=styles["Heading1"], fontSize=16, leading=20, textColor=colors.white, spaceAfter=2)
    s_sub = ParagraphStyle("LNSub", parent=styles["Normal"], fontSize=9.2, leading=12, textColor=colors.HexColor("#CBD5E1"))
    s_sec = ParagraphStyle("LNSec", parent=styles["Heading2"], fontSize=11.5, leading=15, textColor=c_navy, spaceBefore=10, spaceAfter=4)
    s_body = ParagraphStyle("LNBody", parent=styles["Normal"], fontSize=8.8, leading=12.5, textColor=c_dark, spaceAfter=4)
    s_cell = ParagraphStyle("LNCell", parent=styles["Normal"], fontSize=7.6, leading=9.8, textColor=c_dark)
    s_cell_hdr = ParagraphStyle("LNCellHdr", parent=styles["Normal"], fontSize=7.8, leading=10, textColor=colors.white, fontName="Helvetica-Bold")

    story = []

    banner_tbl = Table(
        [[
            Paragraph("<b>LIFENET INTERNATIONAL — MONTHLY DDIU &amp; M&amp;E EXECUTIVE BRIEF</b>", s_title),
        ], [
            Paragraph(
                f"Reporting Period: <b>{data['period']}</b> &nbsp;|&nbsp; Network Scope: <b>{data['total_facilities']} Active Partner Facilities</b> &nbsp;|&nbsp; Generated: {datetime.now().strftime('%d %b %Y')}",
                s_sub,
            )
        ]],
        colWidths=[7.15 * inch],
    )
    banner_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_navy),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (0, 0), 12),
        ("BOTTOMPADDING", (0, 1), (0, 1), 12),
    ]))
    story.append(banner_tbl)
    story.append(Spacer(1, 10))

    kpi_cards = [
        [
            Paragraph("<b>TOTAL PATIENT VISITS</b>", ParagraphStyle("k1", fontSize=7.2, textColor=colors.HexColor(LN_MUTED))),
            Paragraph("<b>MATERNITY DELIVERIES</b>", ParagraphStyle("k2", fontSize=7.2, textColor=colors.HexColor(LN_MUTED))),
            Paragraph("<b>REPORTING COMPLETENESS</b>", ParagraphStyle("k3", fontSize=7.2, textColor=colors.HexColor(LN_MUTED))),
            Paragraph("<b>NETWORK SOLVENCY</b>", ParagraphStyle("k4", fontSize=7.2, textColor=colors.HexColor(LN_MUTED))),
        ],
        [
            Paragraph(f"<b>{int(data['tot_pv']):,}</b><br/><font size=7.5 color='{LN_EMERALD if data['pv_mom_pct']>=0 else LN_CRIMSON}'>{data['pv_mom_pct']:+.1f}% MoM | {data['pv_yoy_pct']:+.1f}% YoY</font>", s_body),
            Paragraph(f"<b>{data['tot_del']:,}</b><br/><font size=7.5 color='{LN_SLATE}'>{data['tot_lb']:,} Live Births | {data['tot_fsb']+data['tot_msb']} SB</font>", s_body),
            Paragraph(f"<b>KHIS: {data['khis_reporting']}/{data['total_facilities']}</b><br/><font size=7.5 color='{LN_TEAL}'>Finance: {data['fin_reporting']}/{data['total_facilities']} HFs</font>", s_body),
            Paragraph(f"<b>{data['cost_coverage']:.1f}%</b><br/><font size=7.5 color='{LN_EMERALD if data['tot_net']>=0 else LN_CRIMSON}'>Net: KES {data['tot_net']:,.0f}</font>", s_body),
        ],
    ]
    kpi_tbl = Table(kpi_cards, colWidths=[1.78 * inch] * 4)
    kpi_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_light),
        ("BOX", (0, 0), (-1, -1), 0.8, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, c_border),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Portfolio Utilization &amp; Maternal Clinical Trajectory", s_sec))
    story.append(HRFlowable(width="100%", thickness=1, color=c_teal, spaceAfter=6))
    story.append(Image(charts["pv_trend"], width=7.1 * inch, height=2.65 * inch))
    story.append(Spacer(1, 6))
    story.append(Image(charts["emonc_trend"], width=7.1 * inch, height=2.25 * inch))
    story.append(Spacer(1, 4))
    story.append(Image(charts["top_facilities"], width=7.1 * inch, height=2.55 * inch))

    story.append(Paragraph("2. Partner Highlights — What Facilities Did Well", s_sec))
    story.append(HRFlowable(width="100%", thickness=1, color=c_emerald, spaceAfter=6))
    well = data["well_df"]
    if not well.empty:
        well_rows = [[
            Paragraph("Facility Name", s_cell_hdr),
            Paragraph(f"{data['period']} PV", s_cell_hdr),
            Paragraph("MoM %", s_cell_hdr),
            Paragraph("YoY %", s_cell_hdr),
            Paragraph("Deliveries", s_cell_hdr),
            Paragraph("Net Balance (KES)", s_cell_hdr),
        ]]
        for _, r in well.iterrows():
            net_str = f"{r['Net_Surplus_KES']:,.0f}" if pd.notna(r["Net_Surplus_KES"]) else "Pending"
            well_rows.append([
                Paragraph(f"<b>{r['Facility']}</b>", s_cell),
                Paragraph(f"{int(r['PV_Current']):,}", s_cell),
                Paragraph(f"{r['PV_MoM_%']:+.1f}%" if pd.notna(r["PV_MoM_%"]) else "—", s_cell),
                Paragraph(f"{r['PV_YoY_%']:+.1f}%" if pd.notna(r["PV_YoY_%"]) else "—", s_cell),
                Paragraph(f"{int(r['Total_Deliveries']):,}" if pd.notna(r["Total_Deliveries"]) else "0", s_cell),
                Paragraph(net_str, s_cell),
            ])
        wt = Table(well_rows, colWidths=[2.45 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch, 0.9 * inch, 1.25 * inch])
        wt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_emerald),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_light]),
            ("GRID", (0, 0), (-1, -1), 0.5, c_border),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(wt)

    story.append(PageBreak())

    story.append(Paragraph("3. MoniTrac Financial Solvency &amp; Cost Coverage", s_sec))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceAfter=6))
    story.append(Paragraph(
        f"Across <b>{data['fin_reporting']} reporting facilities</b> in {data['period']}, total operating revenue reached "
        f"<b>KES {data['tot_rev']:,.0f}</b> against operating expenses of <b>KES {data['tot_exp']:,.0f}</b> "
        f"(Cost Coverage: <b>{data['cost_coverage']:.1f}%</b>; Net Portfolio Surplus: <b>KES {data['tot_net']:,.0f}</b>).",
        s_body,
    ))
    story.append(Image(charts["finance_trend"], width=7.1 * inch, height=2.45 * inch))
    story.append(Spacer(1, 8))

    story.append(Paragraph("4. Data Quality Audit (DQA) &amp; Facility Queries", s_sec))
    story.append(HRFlowable(width="100%", thickness=1, color=c_amber, spaceAfter=6))
    fu = data["follow_up_df"].head(16)
    if not fu.empty:
        fu_rows = [[
            Paragraph("Facility Name", s_cell_hdr),
            Paragraph("PV", s_cell_hdr),
            Paragraph("Deliveries", s_cell_hdr),
            Paragraph("Identified DQA / Clinical / Financial Queries", s_cell_hdr),
        ]]
        for _, r in fu.iterrows():
            pv_s = f"{int(r['PV_Current']):,}" if pd.notna(r["PV_Current"]) else "Missing"
            del_s = f"{int(r['Total_Deliveries']):,}" if pd.notna(r["Total_Deliveries"]) else "—"
            fu_rows.append([
                Paragraph(f"<b>{r['Facility']}</b>", s_cell),
                Paragraph(pv_s, s_cell),
                Paragraph(del_s, s_cell),
                Paragraph(r["Queries"], s_cell),
            ])
        ft = Table(fu_rows, colWidths=[2.15 * inch, 0.75 * inch, 0.85 * inch, 3.4 * inch])
        ft.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_amber),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_light]),
            ("GRID", (0, 0), (-1, -1), 0.5, c_border),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(ft)

    story.append(Spacer(1, 10))

    story.append(Paragraph("5. DDIU Action Plan — M&amp;E and Field Mentorship Deliverables", s_sec))
    story.append(HRFlowable(width="100%", thickness=1, color=c_crimson, spaceAfter=6))
    act = data["action_df"]
    if not act.empty:
        act_rows = [[
            Paragraph("Lead Team", s_cell_hdr),
            Paragraph("Priority", s_cell_hdr),
            Paragraph("Target Facilities", s_cell_hdr),
            Paragraph("Specific DDIU Action Required (Before Next 15th Cycle)", s_cell_hdr),
        ]]
        for _, r in act.iterrows():
            act_rows.append([
                Paragraph(f"<b>{r['Owner']}</b>", s_cell),
                Paragraph(r["Priority"], s_cell),
                Paragraph(r["Facilities"], s_cell),
                Paragraph(r["Action Required"], s_cell),
            ])
        at = Table(act_rows, colWidths=[1.25 * inch, 0.85 * inch, 2.05 * inch, 3.0 * inch])
        at.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_navy),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_light]),
            ("GRID", (0, 0), (-1, -1), 0.5, c_border),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(at)

    doc.build(story)
    buf.seek(0)
    return buf.read()


def save_monthly_ddiu_report(period_label: str | None = None, base_dir: Path | None = None) -> Path:
    base_dir = base_dir or Path(__file__).resolve().parent.parent
    period_label = period_label or default_ddiu_period(base_dir)
    out_dir = base_dir / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = period_label.replace(" ", "_")
    out_path = out_dir / f"LifeNet_DDIU_Report_{safe_name}.pdf"
    pdf_bytes = generate_ddiu_pdf_bytes(period_label, base_dir=base_dir)
    out_path.write_bytes(pdf_bytes)
    return out_path


if __name__ == "__main__":
    p = save_monthly_ddiu_report()
    print(f"Generated LifeNet DDIU Executive Report: {p}")
