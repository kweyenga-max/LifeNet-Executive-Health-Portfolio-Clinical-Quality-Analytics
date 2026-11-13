import os
import numpy as np
import pandas as pd
try:
    from scipy import stats
except ImportError:
    stats = None
from scripts.monitrac_adapter import _get_active_38_roster, _norm_key, _rolling_12_pe_codes, sync_monitrac_pss

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PV_SNAP_PATH = os.path.join(BASE_DIR, "data", "khis_pv_snapshot.csv.gz")


def _load_12m_pv_by_facility(roster, pe_12m):
    """Map trailing 12-month Patient Volume per facility for risk-prioritizing unassessed PSS sites."""
    pv_map = {}
    if not os.path.exists(PV_SNAP_PATH):
        return pv_map
    try:
        df_pv = pd.read_csv(PV_SNAP_PATH, compression="gzip")
        if df_pv.empty:
            return pv_map
        norm_to_can = {_norm_key(f): f for f in roster}
        fac_col = next((c for c in ["Facility", "organisationunitname", "OrgUnit", "Facility Name"] if c in df_pv.columns), None)
        if not fac_col:
            return pv_map
        sub = df_pv.copy()
        # Filter to rolling 12-month periods using Period ("November 2025") or YYYYMM
        month_names = ["January","February","March","April","May","June","July","August","September","October","November","December"]
        pe_labels = {f"{month_names[int(c[4:6])-1]} {c[:4]}" for c in pe_12m}
        if "Period" in sub.columns:
            sub = sub[sub["Period"].astype(str).isin(pe_labels | set(pe_12m))]
        elif "periodid" in sub.columns:
            sub = sub[sub["periodid"].astype(str).isin(set(pe_12m))]

        # Sum numeric attendance columns (or Value column if long format)
        if "Value" in sub.columns:
            sub["_pv_val"] = pd.to_numeric(sub["Value"], errors="coerce").fillna(0)
        else:
            num_cols = [c for c in sub.columns if c not in {fac_col, "Period", "periodid", "Year", "Month", "County", "SubCounty", "Code"} and pd.api.types.is_numeric_dtype(sub[c])]
            sub["_pv_val"] = sub[num_cols].sum(axis=1) if num_cols else 0

        sub["Canonical"] = sub[fac_col].map(lambda x: norm_to_can.get(_norm_key(x)))
        sub = sub[sub["Canonical"].notna()]
        pv_map = sub.groupby("Canonical")["_pv_val"].sum().to_dict()
    except Exception:
        pass
    return pv_map


def get_pss_me_analytics(force_live=False):
    roster = _get_active_38_roster()
    pe_12m = _rolling_12_pe_codes()
    first_6m_codes = set(pe_12m[:6])

    window_label = f"{pe_12m[0][:4]}-{pe_12m[0][4:]} to {pe_12m[-1][:4]}-{pe_12m[-1][4:]}"
    first_6m_label = f"Prior 6M ({pe_12m[0][:4]}-{pe_12m[0][4:]}..{pe_12m[5][:4]}-{pe_12m[5][4:]})"
    recent_6m_label = f"Recent 6M ({pe_12m[6][:4]}-{pe_12m[6][4:]}..{pe_12m[-1][:4]}-{pe_12m[-1][4:]})"

    pv_map = _load_12m_pv_by_facility(roster, pe_12m)

    df = sync_monitrac_pss(force_live=force_live)
    if df.empty:
        return {"empty": True, "roster": roster, "df": df, "window_label": window_label}

    df = df[df["organisationunitname"].isin(roster)].copy()
    df["periodid"] = df["periodid"].astype(str)
    df = df[df["periodid"].isin(pe_12m)].copy()
    df["Net_Satisfaction_Score"] = pd.to_numeric(df["Net_Satisfaction_Score"], errors="coerce")
    df = df[df["Net_Satisfaction_Score"].notna()].copy()
    df["Year"] = df["periodid"].str[:4].astype(int)
    df["Month_Num"] = df["periodid"].str[4:6].astype(int)
    df["Quarter"] = "Q" + ((df["Month_Num"] - 1) // 3 + 1).astype(str) + " " + df["Year"].astype(str)
    df["Half_Window"] = np.where(df["periodid"].isin(first_6m_codes), "Prior 6M", "Recent 6M")

    s_prior6 = df[df["Half_Window"] == "Prior 6M"]["Net_Satisfaction_Score"]
    s_recent6 = df[df["Half_Window"] == "Recent 6M"]["Net_Satisfaction_Score"]

    if len(s_prior6) >= 2 and len(s_recent6) >= 2:
        t_stat, p_val_t = stats.ttest_ind(s_prior6, s_recent6, equal_var=False)
        u_stat, p_val_u = stats.mannwhitneyu(s_prior6, s_recent6)
    else:
        t_stat, p_val_t, u_stat, p_val_u = np.nan, np.nan, np.nan, np.nan

    # Monthly SPC Control Band across Past 12 Months
    m_spc = (
        df.groupby(["periodid", "periodname"], as_index=False)
        .agg(
            Surveys=("Net_Satisfaction_Score", "count"),
            Facilities=("organisationunitname", "nunique"),
            Mean=("Net_Satisfaction_Score", "mean"),
            Median=("Net_Satisfaction_Score", "median"),
            SD=("Net_Satisfaction_Score", "std"),
            Min=("Net_Satisfaction_Score", "min"),
            Max=("Net_Satisfaction_Score", "max"),
        )
        .sort_values("periodid")
        .reset_index(drop=True)
    )
    m_spc["SD"] = m_spc["SD"].fillna(0.0)
    m_spc["Upper_1SD"] = np.minimum(m_spc["Mean"] + m_spc["SD"], 100.0)
    m_spc["Lower_1SD"] = np.maximum(m_spc["Mean"] - m_spc["SD"], 0.0)

    # Paired Longitudinal Cohort within Rolling 12M (Prior 6M vs Recent 6M)
    facs_p6 = set(df[df["Half_Window"] == "Prior 6M"]["organisationunitname"])
    facs_r6 = set(df[df["Half_Window"] == "Recent 6M"]["organisationunitname"])
    both_facs = sorted(facs_p6 & facs_r6)

    cohort_rows = []
    for fac in both_facs:
        sub = df[df["organisationunitname"] == fac]
        mp6 = sub[sub["Half_Window"] == "Prior 6M"]["Net_Satisfaction_Score"].mean()
        mr6 = sub[sub["Half_Window"] == "Recent 6M"]["Net_Satisfaction_Score"].mean()
        delta = mr6 - mp6
        status = "Improved (>= +2%)" if delta >= 2.0 else ("Declined (<= -2%)" if delta <= -2.0 else "Stable (+/- 2%)")
        cohort_rows.append({
            "Facility": fac,
            "Prior_6M_Mean": round(mp6, 2),
            "Recent_6M_Mean": round(mr6, 2),
            "Delta": round(delta, 2),
            "Trajectory": status,
        })
    cohort_df = pd.DataFrame(cohort_rows).sort_values("Delta", ascending=False) if cohort_rows else pd.DataFrame()

    # Surveillance Coverage Classification & Risk-Prioritized Pending Register
    assessed_12m = facs_p6 | facs_r6
    only_r6 = sorted(facs_r6 - facs_p6)
    only_p6 = sorted(facs_p6 - facs_r6)
    unassessed_12m = sorted(set(roster) - assessed_12m)

    med_pv = np.median(list(pv_map.values())) if pv_map else 0

    pending_rows = []
    for fac in unassessed_12m:
        fac_pv = int(pv_map.get(fac, 0))
        if fac_pv > 0 and fac_pv >= med_pv:
            tier = "P1 — High-Volume Blind Spot"
            action = "Immediate Baseline PSS (High outpatient volume with zero patient-voice data)"
        elif fac_pv > 0:
            tier = "P2 — Standard Baseline Gap"
            action = "Schedule Baseline PSS Round Within Current Quarter"
        else:
            tier = "P2 — Unassessed Partner Site"
            action = "Verify Active Service Status & Conduct Baseline PSS"
        pending_rows.append({
            "Priority_Tier": tier,
            "Facility": fac,
            "12M_Surveillance_Status": "Zero PSS in Past 12 Months",
            "12M_Outpatient_PV": pd.NA if fac_pv <= 0 else int(round(fac_pv)),
            "Last_Survey_in_12M": "None",
            "Last_Net_Patient_Satisfaction_%": np.nan,
            "Decision_Action": action,
        })
    for fac in only_p6:
        sub = df[df["organisationunitname"] == fac].sort_values("periodid")
        last_r = sub.iloc[-1]
        last_sc = float(last_r["Net_Satisfaction_Score"])
        fac_pv = int(pv_map.get(fac, 0))
        if last_sc < 75.0:
            tier = "P1 — Clinical Quality & Follow-Up Alert"
            action = "Urgent 6-Month Re-Assessment & Mentor QI Review (<75% Prior Score)"
        else:
            tier = "P3 — Semi-Annual Renewal Due"
            action = "Conduct Scheduled 6-Month Follow-Up PSS"
        pending_rows.append({
            "Priority_Tier": tier,
            "Facility": fac,
            "12M_Surveillance_Status": "Assessed in Prior 6M Only (>6M Ago)",
            "12M_Outpatient_PV": pd.NA if fac_pv <= 0 else int(round(fac_pv)),
            "Last_Survey_in_12M": last_r["periodname"],
            "Last_Net_Patient_Satisfaction_%": round(last_sc, 2),
            "Decision_Action": action,
        })
    pending_df = pd.DataFrame(pending_rows)
    if not pending_df.empty and "12M_Outpatient_PV" in pending_df.columns:
        pending_df["12M_Outpatient_PV"] = pending_df["12M_Outpatient_PV"].astype("Int64")
    if not pending_df.empty:
        pending_df = pending_df.sort_values(
            by=["Priority_Tier", "12M_Outpatient_PV", "Facility"],
            ascending=[True, False, True],
            na_position="last",
        ).reset_index(drop=True)

    # Facility Master Summary Table (All 38 in Past 12M)
    fac_summary_rows = []
    for fac in roster:
        sub = df[df["organisationunitname"] == fac].sort_values("periodid")
        fac_pv = int(pv_map.get(fac, 0))
        if sub.empty:
            fac_summary_rows.append({
                "Facility": fac,
                "12M_Status": "Pending 12M Assessment",
                "12M_Rounds": 0,
                "12M_Outpatient_PV": pd.NA if fac_pv <= 0 else int(round(fac_pv)),
                "Prior_6M_Mean_%": np.nan,
                "Recent_6M_Mean_%": np.nan,
                "12M_Net_Patient_Satisfaction_%": np.nan,
                "Latest_Period": "—",
                "Latest_Score_%": np.nan,
            })
        else:
            mp6 = sub[sub["Half_Window"] == "Prior 6M"]["Net_Satisfaction_Score"].mean()
            mr6 = sub[sub["Half_Window"] == "Recent 6M"]["Net_Satisfaction_Score"].mean()
            ov = sub["Net_Satisfaction_Score"].mean()
            latest = sub.iloc[-1]
            tier = (
                "Exemplary (>=90%)" if ov >= 90
                else ("Strong (80-89.9%)" if ov >= 80 else ("Moderate (70-79.9%)" if ov >= 70 else "Needs Attention (<70%)"))
            )
            fac_summary_rows.append({
                "Facility": fac,
                "12M_Status": tier,
                "12M_Rounds": int(len(sub)),
                "12M_Outpatient_PV": pd.NA if fac_pv <= 0 else int(round(fac_pv)),
                "Prior_6M_Mean_%": round(mp6, 2) if pd.notna(mp6) else np.nan,
                "Recent_6M_Mean_%": round(mr6, 2) if pd.notna(mr6) else np.nan,
                "12M_Net_Patient_Satisfaction_%": round(ov, 2),
                "Latest_Period": latest["periodname"],
                "Latest_Score_%": round(float(latest["Net_Satisfaction_Score"]), 2),
            })
    fac_summary_df = pd.DataFrame(fac_summary_rows)
    if not fac_summary_df.empty and "12M_Outpatient_PV" in fac_summary_df.columns:
        fac_summary_df["12M_Outpatient_PV"] = fac_summary_df["12M_Outpatient_PV"].astype("Int64")
    fac_summary_df = fac_summary_df.sort_values(
        by=["12M_Net_Patient_Satisfaction_%", "Facility"], ascending=[False, True], na_position="last"
    )

    return {
        "empty": False,
        "roster": roster,
        "window_label": window_label,
        "first_6m_label": first_6m_label,
        "recent_6m_label": recent_6m_label,
        "df": df,
        "s_prior6": s_prior6,
        "s_recent6": s_recent6,
        "t_stat": t_stat,
        "p_val_t": p_val_t,
        "u_stat": u_stat,
        "p_val_u": p_val_u,
        "m_spc": m_spc,
        "cohort_df": cohort_df,
        "both_count": len(both_facs),
        "only_r6_count": len(only_r6),
        "only_p6_count": len(only_p6),
        "never_count": len(unassessed_12m),
        "assessed_count": len(assessed_12m),
        "unassessed_list": unassessed_12m,
        "only_p6_list": only_p6,
        "pending_df": pending_df,
        "fac_summary_df": fac_summary_df,
    }


def generate_pss_chart_insights(bundle):
    """Build dynamic, data-grounded M&E specialist narrative insights for each PSS chart & unassessed sites."""
    if bundle.get("empty", True):
        return {}

    df = bundle["df"]
    s_p6 = bundle["s_prior6"]
    s_r6 = bundle["s_recent6"]
    cohort_df = bundle["cohort_df"]
    m_spc = bundle["m_spc"]
    fac_df = bundle["fac_summary_df"]
    pending_df = bundle["pending_df"]
    win = bundle["window_label"]

    ov_mean = float(df["Net_Satisfaction_Score"].mean())
    ov_med = float(df["Net_Satisfaction_Score"].median())
    ov_sd = float(df["Net_Satisfaction_Score"].std()) if len(df) > 1 else 0.0
    n_total = len(df)
    pct_above_80 = float((df["Net_Satisfaction_Score"] >= 80.0).mean() * 100.0)
    pct_below_70 = float((df["Net_Satisfaction_Score"] < 70.0).mean() * 100.0)

    # 1. Distribution & Hypothesis Test Insight (Chart A)
    p6_mean = float(s_p6.mean()) if len(s_p6) else np.nan
    r6_mean = float(s_r6.mean()) if len(s_r6) else np.nan
    p6_iqr = float(s_p6.quantile(0.75) - s_p6.quantile(0.25)) if len(s_p6) else np.nan
    r6_iqr = float(s_r6.quantile(0.75) - s_r6.quantile(0.25)) if len(s_r6) else np.nan
    delta_6m = r6_mean - p6_mean if (pd.notna(p6_mean) and pd.notna(r6_mean)) else np.nan
    p_t = bundle["p_val_t"]

    if pd.notna(p_t) and p_t < 0.05:
        sig_verdict = f"statistically significant shift ($p = {p_t:.3f} < 0.05$)"
    elif pd.notna(p_t):
        sig_verdict = f"statistically stable performance ($p = {p_t:.3f} >= 0.05$; observed variance reflects normal sampling dispersion rather than systemic drift)"
    else:
        sig_verdict = "insufficient sample size in one half-window for parametric hypothesis testing"

    iqr_note = ""
    if pd.notna(p6_iqr) and pd.notna(r6_iqr):
        if r6_iqr < p6_iqr:
            iqr_note = f"Interquartile spread tightened from **{p6_iqr:.1f} pp** (Prior 6M) to **{r6_iqr:.1f} pp** (Recent 6M), confirming narrower facility-to-facility inequality."
        else:
            iqr_note = f"Interquartile spread widened from **{p6_iqr:.1f} pp** (Prior 6M) to **{r6_iqr:.1f} pp** (Recent 6M), signaling growing divergence between top-tier clinics and lagging sites."

    chart_a_insight = (
        f"**Parametric vs. Non-Parametric Readout ({win}):** Across **{n_total} valid survey rounds**, the network achieved a mean satisfaction of **{ov_mean:.2f}%** "
        f"(SD = {ov_sd:.2f} pp) and a median of **{ov_med:.2f}%**, with **{pct_above_80:.1f}%** of rounds clearing the **80% quality benchmark** and **{pct_below_70:.1f}%** falling in the sub-70% alert zone. "
        f"Comparing Recent 6M (**{r6_mean:.2f}%**, n={len(s_r6)}) against Prior 6M (**{p6_mean:.2f}%**, n={len(s_p6)}) shows a **{delta_6m:+.2f} pp** change—indicating {sig_verdict}. {iqr_note}"
    )

    # 2. Longitudinal Paired Cohort Insight (Chart B)
    if not cohort_df.empty:
        imp_df = cohort_df[cohort_df["Delta"] >= 2.0]
        dec_df = cohort_df[cohort_df["Delta"] <= -2.0]
        stb_df = cohort_df[(cohort_df["Delta"] > -2.0) & (cohort_df["Delta"] < 2.0)]
        top_gain = cohort_df.iloc[0]
        top_drop = cohort_df.iloc[-1]
        paired_net_shift = float(cohort_df["Delta"].mean())
        chart_b_insight = (
            f"**Within-Facility Longitudinal Control (n={len(cohort_df)} Paired Sites):** Isolating the exact same facilities assessed in both halves eliminates composition bias and reveals a net paired mean change of **{paired_net_shift:+.2f} pp**. "
            f"**{len(imp_df)} facilities improved** (>= +2.0 pp), led by **{top_gain['Facility']}** ({top_gain['Prior_6M_Mean']:.1f}% -> {top_gain['Recent_6M_Mean']:.1f}%, **{top_gain['Delta']:+.1f} pp**); "
            f"**{len(stb_df)} remained stable** (+/- 2.0 pp); and **{len(dec_df)} declined** (<= -2.0 pp), steepest at **{top_drop['Facility']}** ({top_drop['Prior_6M_Mean']:.1f}% -> {top_drop['Recent_6M_Mean']:.1f}%, **{top_drop['Delta']:+.1f} pp**). "
            "Declining paired sites require targeted Medical/Management Mentor root-cause review of wait times, drug stockouts, and staff attitude."
        )
    else:
        chart_b_insight = (
            "**Paired Cohort Note:** Fewer than 2 facilities have repeat surveys spanning both the Prior 6M and Recent 6M windows. "
            "Scheduling semi-annual follow-up rounds at previously surveyed sites will unlock paired within-facility impact tracking."
        )

    # 3. Surveillance Coverage & Unassessed Facility Blind-Spot Insight (Chart C)
    assessed = bundle["assessed_count"]
    never = bundle["never_count"]
    only_p6 = bundle["only_p6_count"]
    only_r6 = bundle["only_r6_count"]
    both = bundle["both_count"]
    cov_pct = assessed / 38.0 * 100.0
    p1_sites = pending_df[pending_df["Priority_Tier"].str.startswith("P1")]["Facility"].tolist() if not pending_df.empty else []
    p1_txt = (
        f" High-priority blind spots requiring immediate deployment: **{', '.join(p1_sites[:6])}**{' (+' + str(len(p1_sites)-6) + ' more)' if len(p1_sites) > 6 else ''}."
        if p1_sites else ""
    )
    chart_c_insight = (
        f"**Surveillance Completeness & Blind-Spot Risk:** **{assessed} of 38 active partner facilities ({cov_pct:.1f}%)** recorded at least one PSS round in the past 12 months "
        f"(**{both}** longitudinal repeat sites, **{only_r6}** recent-6M entrants, and **{only_p6}** assessed only in the prior 6 months). "
        f"**{never} facilities ({100 - cov_pct:.1f}%)** have zero 12-month PSS coverage, creating patient-experience blind spots where service bottlenecks can erode outpatient retention undetected.{p1_txt}"
    )

    # 4. Monthly SPC Control Band Insight (Chart D)
    if not m_spc.empty:
        peak_m = m_spc.loc[m_spc["Mean"].idxmax()]
        low_m = m_spc.loc[m_spc["Mean"].idxmin()]
        below_floor_mos = m_spc[m_spc["Mean"] < 80.0]["periodname"].tolist()
        floor_txt = (
            f"Monthly network means dipped below the 80% quality floor in **{', '.join(below_floor_mos)}**."
            if below_floor_mos
            else "Every surveyed month maintained a network mean above the **80% quality floor**."
        )
        chart_d_insight = (
            f"**Statistical Process Control (SPC) Stability:** Across **{len(m_spc)} active reporting months**, monthly network satisfaction peaked in **{peak_m['periodname']}** "
            f"(**{peak_m['Mean']:.1f}%**, n={int(peak_m['Surveys'])}) and dipped lowest in **{low_m['periodname']}** (**{low_m['Mean']:.1f}%**, n={int(low_m['Surveys'])}). "
            f"{floor_txt} Months with wide +/- 1 SD shaded bands reflect heterogeneous facility cohorts rather than uniform network shifts—always verify sample size ($n$) alongside monthly means."
        )
    else:
        chart_d_insight = "No monthly SPC points available in the selected window."

    # 5. Executive Synthesis & Unassessed Facility Decision Matrix
    assessed_facs = fac_df[fac_df["12M_Rounds"] > 0]
    top_3 = assessed_facs.head(3)["Facility"].tolist() if not assessed_facs.empty else []
    low_alert = assessed_facs[assessed_facs["12M_Net_Patient_Satisfaction_%"] < 75.0]["Facility"].tolist() if not assessed_facs.empty else []
    unassessed_names = bundle.get("unassessed_list", [])
    overdue_names = bundle.get("only_p6_list", [])

    exec_summary = (
        f"### 📋 M&E Specialist Executive Synthesis & Decision Brief ({win})\n"
        f"- **Network Quality Standing:** LifeNet Kenya's active partner network sustains a **{ov_mean:.2f}%** rolling 12-month patient satisfaction mean (median **{ov_med:.2f}%**), led by **{', '.join(top_3) if top_3 else 'N/A'}**.\n"
        f"- **Clinical & Mentor QI Escalations:** {'Immediate mentor root-cause coaching is warranted for sub-75% facilities: **' + ', '.join(low_alert) + '**.' if low_alert else 'All assessed facilities currently average >= 75.0% over the rolling 12-month window.'}\n"
        f"- **Unassessed Facility Blind Spots ({never} Sites with Zero 12M PSS):** **{', '.join(unassessed_names) if unassessed_names else 'None'}** have no recorded PSS in MoniTrac over the past 12 months. Deploy M&E/Mentor exit-interview rounds to high-volume unassessed sites first so patient-experience risks are captured before outpatient volume declines.\n"
        f"- **Semi-Annual Renewal Queue ({only_p6} Sites >6 Months Since Last PSS):** **{', '.join(overdue_names) if overdue_names else 'None'}** were last surveyed in the prior 6-month window and are due for their semi-annual follow-up round."
    )

    return {
        "exec_summary": exec_summary,
        "chart_a": chart_a_insight,
        "chart_b": chart_b_insight,
        "chart_c": chart_c_insight,
        "chart_d": chart_d_insight,
    }
