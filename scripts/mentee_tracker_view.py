import math
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from scripts.mentee_tracker_adapter import MENTOR_REGISTRY, MODULE_LABELS, sync_monitrac_mentees


def _wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 0.0
    p = k / n
    denom = 1.0 + (z * z) / n
    center = (p + (z * z) / (2.0 * n)) / denom
    half = (z * math.sqrt((p * (1.0 - p) + (z * z) / (4.0 * n)) / n)) / denom
    return max(0.0, (center - half) * 100.0), min(100.0, (center + half) * 100.0)


def _gini_coefficient(values: np.ndarray) -> float:
    arr = np.sort(np.asarray(values, dtype=float))
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return float((np.sum((2 * index - n - 1) * arr)) / (n * np.sum(arr)))


def _kpi_card(title: str, value: str, sub: str, accent: str = "#0F2C59") -> str:
    return f"""
    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-top:4px solid {accent};border-radius:10px;padding:15px 17px;box-shadow:0 1px 3px rgba(15,23,42,0.05);height:100%;">
        <div style="font-size:11px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#64748B;">{title}</div>
        <div style="font-size:26px;font-weight:800;color:#0F172A;margin:6px 0 4px 0;line-height:1.15;">{value}</div>
        <div style="font-size:12px;color:#475569;line-height:1.4;">{sub}</div>
    </div>
    """


def render_mentee_tracker_view():
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#0F2C59 0%,#1E3A8A 100%);padding:22px 26px;border-radius:12px;margin-bottom:18px;color:#FFFFFF;">
            <div style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#93C5FD;">
                MoniTrac DHIS2 Tracker · Program NYY8hzVYv8f · Medical &amp; Management Curriculum Intelligence
            </div>
            <h2 style="margin:4px 0 6px 0;font-size:24px;font-weight:800;color:#FFFFFF;">
                🎓 Mentee &amp; Beneficiary Reach Analytics
            </h2>
            <p style="margin:0;font-size:13.5px;color:#E2E8F0;max-width:980px;">
                Strict entity-level deduplication across <b>Medical Curriculum (Modules 1–5)</b> and <b>Management Curriculum (Modules 1–4)</b>, spanning
                <b>Centralized Training</b>, <b>Onsite Mentorship</b>, and <b>Virtual / Ad-hoc Support (WhatsApp &amp; Phone)</b>.
                Every mentee is counted under each curriculum and modality they experienced, while counted <b>strictly once</b> in Monthly, Quarterly, and Annual Unique Beneficiary totals.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = sync_monitrac_mentees(force_live=False)
    if df.empty:
        st.warning("No MoniTrac Mentee Tracker records found. Click **🔄 Sync All Live KHIS Data** in the sidebar or run `./sync_khis.sh`.")
        return

    # --- TOP FILTER CONTROLS (5 COLUMNS INCLUDING CURRICULUM) ---
    f1, f2, f3, f4, f5 = st.columns([0.95, 1.15, 1.1, 1.15, 1.25])
    years = sorted(df["Year"].dropna().unique().astype(int).tolist(), reverse=True)
    with f1:
        sel_year = st.selectbox("Reporting Year", ["All Years"] + [str(y) for y in years], index=0, key="mt_year")

    df_yr = df if sel_year == "All Years" else df[df["Year"] == int(sel_year)].copy()

    with f2:
        granularity = st.selectbox(
            "Deduplication Window",
            ["Annual / Selected Scope", "Quarterly", "Monthly"],
            index=0,
            help="Reporting window within which each mentee is counted strictly once.",
            key="mt_gran",
        )

    with f3:
        if granularity == "Monthly":
            periods = (
                df_yr[["Year_Month", "Month_Label"]]
                .drop_duplicates()
                .sort_values("Year_Month", ascending=False)["Month_Label"]
                .tolist()
            )
            sel_period = st.selectbox("Select Month", periods, index=0 if periods else None, key="mt_month")
            df_win = df_yr[df_yr["Month_Label"] == sel_period].copy() if sel_period else df_yr.copy()
            window_label = sel_period or "Selected Month"
        elif granularity == "Quarterly":
            quarters = sorted(
                df_yr["Quarter_Label"].dropna().unique().tolist(),
                key=lambda q: (int(q.split()[1]), int(q.split()[0][1])),
                reverse=True,
            )
            sel_period = st.selectbox("Select Quarter", quarters, index=0 if quarters else None, key="mt_qtr")
            df_win = df_yr[df_yr["Quarter_Label"] == sel_period].copy() if sel_period else df_yr.copy()
            window_label = sel_period or "Selected Quarter"
        else:
            sel_period = sel_year
            df_win = df_yr.copy()
            window_label = f"FY {sel_year}" if sel_year != "All Years" else "All Cumulative Periods"

    with f4:
        curr_filter = st.selectbox(
            "Curriculum Stream",
            [
                "All Curricula (Medical + Management)",
                "Medical Curriculum (Mod 1–5)",
                "Management Curriculum (Mod 1–4)",
            ],
            index=0,
            key="mt_curr",
        )

    with f5:
        track_filter = st.selectbox(
            "Mentor Track / Cohort",
            [
                "All Mentors & Cohorts",
                "Medical Mentors (Newton, Whyttney, Joseph)",
                "Management Mentors (Mary, Lewis, Adrian)",
                "Cohort 3 (Newton, Mary, Whyttney, Adrian)",
                "Cohort 1 & 2 (Joseph, Lewis)",
            ],
            index=0,
            key="mt_track",
        )

    if curr_filter.startswith("Medical"):
        df_win = df_win[df_win["Curriculum"].str.contains("Medical", case=False, na=False)]
        df_yr = df_yr[df_yr["Curriculum"].str.contains("Medical", case=False, na=False)]
    elif curr_filter.startswith("Management"):
        df_win = df_win[df_win["Curriculum"].str.contains("Management", case=False, na=False)]
        df_yr = df_yr[df_yr["Curriculum"].str.contains("Management", case=False, na=False)]

    if track_filter.startswith("Medical"):
        df_win = df_win[df_win["trainer_raw"].str.contains("newton-byegon|whyttney-claire|joseph-kirori", case=False, na=False)]
        df_yr = df_yr[df_yr["trainer_raw"].str.contains("newton-byegon|whyttney-claire|joseph-kirori", case=False, na=False)]
    elif track_filter.startswith("Management"):
        df_win = df_win[df_win["trainer_raw"].str.contains("mary-wanyama|lewis-muriuki|adrian-nyolde", case=False, na=False)]
        df_yr = df_yr[df_yr["trainer_raw"].str.contains("mary-wanyama|lewis-muriuki|adrian-nyolde", case=False, na=False)]
    elif track_filter.startswith("Cohort 3"):
        df_win = df_win[df_win["trainer_raw"].str.contains("newton-byegon|mary-wanyama|whyttney-claire|adrian-nyolde", case=False, na=False)]
        df_yr = df_yr[df_yr["trainer_raw"].str.contains("newton-byegon|mary-wanyama|whyttney-claire|adrian-nyolde", case=False, na=False)]
    elif track_filter.startswith("Cohort 1 & 2"):
        df_win = df_win[df_win["trainer_raw"].str.contains("joseph-kirori|lewis-muriuki", case=False, na=False)]
        df_yr = df_yr[df_yr["trainer_raw"].str.contains("joseph-kirori|lewis-muriuki", case=False, na=False)]

    if df_win.empty:
        st.info("No mentorship records match the active filter combination.")
        return

    # --- PERSON-LEVEL DEDUPLICATION IN ACTIVE WINDOW ---
    def _person_curriculum_profile(curricula_series: pd.Series) -> str:
        has_med = any("Medical" in str(c) for c in curricula_series)
        has_mgt = any("Management" in str(c) for c in curricula_series)
        if has_med and has_mgt:
            return "Both Curricula (Medical + Management)"
        if has_med:
            return "Medical Curriculum Only"
        if has_mgt:
            return "Management Curriculum Only"
        return "Unspecified"

    person_df = (
        df_win.groupby("beneficiary_uid", as_index=False)
        .agg(
            Mentee_Name=("mentee_name", "first"),
            Gender=("Gender", lambda s: next((x for x in s if x in ("Female", "Male")), "Unspecified")),
            Cadre=("Cadre", lambda s: next((x for x in s if x != "Unspecified"), "Unspecified")),
            Primary_Facility=("facility_name", lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]),
            County=("county", "first"),
            Total_Encounters=("event_uid", "count"),
            Distinct_Modalities=("Modality", "nunique"),
            Modalities_List=("Modality", lambda s: sorted(set(s))),
            Curriculum_Profile=("Curriculum", _person_curriculum_profile),
            Mentors_List=("Mentors", lambda s: ", ".join(sorted({m.strip() for x in s for m in str(x).split(",") if m.strip()}))),
            Cohorts_List=("Mentor_Cohort", lambda s: ", ".join(sorted(set(s)))),
            Last_Touch=("event_date", "max"),
        )
    )
    person_df["Modality_Combo"] = person_df["Modalities_List"].apply(lambda lst: " + ".join(lst))

    unique_total = len(person_df)
    total_touches = len(df_win)
    dup_removed = total_touches - unique_total
    mean_touches = float(person_df["Total_Encounters"].mean())
    med_touches = float(person_df["Total_Encounters"].median())
    iqr_touches = float(person_df["Total_Encounters"].quantile(0.75) - person_df["Total_Encounters"].quantile(0.25))

    med_unique = int(df_win[df_win["Curriculum"].str.contains("Medical", case=False, na=False)]["beneficiary_uid"].nunique())
    mgt_unique = int(df_win[df_win["Curriculum"].str.contains("Management", case=False, na=False)]["beneficiary_uid"].nunique())
    dual_curr_unique = int((person_df["Curriculum_Profile"] == "Both Curricula (Medical + Management)").sum())

    known_gender = person_df[person_df["Gender"].isin(["Female", "Male"])]
    n_female = int((known_gender["Gender"] == "Female").sum())
    n_male = int((known_gender["Gender"] == "Male").sum())
    n_known_g = len(known_gender)
    fem_pct = (n_female / n_known_g * 100.0) if n_known_g > 0 else 0.0
    ci_lo, ci_hi = _wilson_ci(n_female, n_known_g)

    blended_n = int((person_df["Distinct_Modalities"] >= 2).sum())
    blended_pct = (blended_n / unique_total * 100.0) if unique_total > 0 else 0.0
    facilities_reached = int(df_win["facility_name"].nunique())

    # --- 5 DEDUPLICATED KPI CARDS ---
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(
            _kpi_card(
                f"Unique Beneficiaries ({window_label})",
                f"{unique_total:,}",
                f"Deduplicated from <b>{total_touches:,}</b> touches ({dup_removed:,} repeats collapsed) across <b>{facilities_reached}</b> sites.",
                "#0F2C59",
            ),
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            _kpi_card(
                "Medical Curriculum Reach",
                f"{med_unique:,}",
                f"Unique mentees trained/mentored in <b>Med Modules 1–5</b> ({(med_unique/unique_total*100 if unique_total else 0):.1f}% of cohort).",
                "#1D4ED8",
            ),
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            _kpi_card(
                "Management Curriculum Reach",
                f"{mgt_unique:,}",
                f"Unique mentees trained/mentored in <b>Mgt Modules 1–4</b> ({dual_curr_unique:,} also completed Medical modules).",
                "#0D9488",
            ),
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            _kpi_card(
                "Female vs. Male Unique Reach",
                f"{fem_pct:.1f}% F / {100.0 - fem_pct:.1f}% M" if n_known_g else "N/A",
                f"<b>{n_female:,}</b> Female vs. <b>{n_male:,}</b> Male unique mentees (95% CI: {ci_lo:.1f}%–{ci_hi:.1f}%).",
                "#7C3AED",
            ),
            unsafe_allow_html=True,
        )
    with k5:
        st.markdown(
            _kpi_card(
                "Dose & Multi-Modality",
                f"{mean_touches:.2f}× · {blended_pct:.0f}%",
                f"Mean touches (Median {med_touches:.1f}×, IQR {iqr_touches:.1f}) · <b>{blended_n:,}</b> reached via ≥2 modalities.",
                "#D97706",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # --- ROW 1: CURRICULUM SEPARATION (MEDICAL VS MANAGEMENT MODULES & MODALITIES) ---
    c1, c2 = st.columns([1.15, 1.1])

    with c1:
        st.markdown("#### 1. Medical vs. Management Curriculum Reach by Modality")
        mod_order = ["Centralized Training", "Onsite Mentorship", "Virtual / Ad-hoc (WhatsApp & Phone)"]
        curr_mod_rows = []
        for curr_lbl, curr_key in [("Medical Curriculum", "Medical"), ("Management Curriculum", "Management")]:
            sub_c = df_win[df_win["Curriculum"].str.contains(curr_key, case=False, na=False)]
            for m in mod_order:
                sub_cm = sub_c[sub_c["Modality"] == m]
                curr_mod_rows.append(
                    {
                        "Curriculum": curr_lbl,
                        "Modality": m,
                        "Unique Mentees": int(sub_cm["beneficiary_uid"].nunique()),
                        "Total Encounters": int(len(sub_cm)),
                    }
                )
        df_cm = pd.DataFrame(curr_mod_rows)
        fig_cm = px.bar(
            df_cm,
            x="Modality",
            y="Unique Mentees",
            color="Curriculum",
            barmode="group",
            text="Unique Mentees",
            color_discrete_map={"Medical Curriculum": "#1E3A8A", "Management Curriculum": "#0D9488"},
            height=350,
        )
        fig_cm.update_traces(textposition="outside")
        fig_cm.update_layout(
            margin=dict(l=10, r=10, t=20, b=15),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            yaxis_title="Unique Mentees Reached",
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_cm, use_container_width=True)
        st.caption(
            f"Overall deduplication check: **{med_unique:,}** Medical + **{mgt_unique:,}** Management − **{dual_curr_unique:,}** Dual-Curriculum overlap = **{unique_total:,}** total unique beneficiaries."
        )

    with c2:
        st.markdown("#### 2. Curriculum Module Coverage (Med Mod 1–5 vs. Mgt Mod 1–4)")
        mod_code_order = [
            "med-mod-1", "med-mod-2", "med-mod-3", "med-mod-4", "med-mod-5",
            "mgt-mod-1", "mgt-mod-2", "mgt-mod-3", "mgt-mod-4",
        ]
        mod_prog_rows = []
        for code in mod_code_order:
            sub_mc = df_win[df_win["modules"].astype(str).str.contains(code, case=False, na=False)]
            mod_prog_rows.append(
                {
                    "Module": MODULE_LABELS.get(code, code),
                    "Stream": "Medical Curriculum" if code.startswith("med-") else "Management Curriculum",
                    "Unique Mentees": int(sub_mc["beneficiary_uid"].nunique()),
                    "Sessions": int(len(sub_mc)),
                }
            )
        df_mp = pd.DataFrame(mod_prog_rows)
        fig_mp = px.bar(
            df_mp,
            x="Unique Mentees",
            y="Module",
            color="Stream",
            orientation="h",
            text=df_mp.apply(lambda r: f"{r['Unique Mentees']} ({r['Sessions']} sess)", axis=1),
            color_discrete_map={"Medical Curriculum": "#1E3A8A", "Management Curriculum": "#0D9488"},
            height=350,
        )
        fig_mp.update_traces(textposition="outside")
        fig_mp.update_layout(
            margin=dict(l=10, r=55, t=20, b=15),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            yaxis=dict(autorange="reversed", title=""),
            xaxis_title="Unique Mentees Covered",
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_mp, use_container_width=True)

    st.markdown("---")

    # --- ROW 2: MONTHLY DEDUPLICATION CURVE + MALE VS FEMALE STATISTICAL ANALYSIS ---
    t_col, g_col = st.columns([1.15, 1.1])

    with t_col:
        st.markdown("#### 3. Monthly Trajectory: Unique Headcount vs. Modality Volume")
        m_grp = (
            df_yr.groupby(["Year_Month", "Month_Label", "Modality"], as_index=False)
            .agg(Encounters=("event_uid", "count"))
        )
        u_monthly = (
            df_yr.groupby(["Year_Month", "Month_Label"], as_index=False)
            .agg(Unique_Mentees=("beneficiary_uid", "nunique"))
            .sort_values("Year_Month")
        )

        fig_trend = go.Figure()
        palette = {
            "Centralized Training": "#1E40AF",
            "Onsite Mentorship": "#0D9488",
            "Virtual / Ad-hoc (WhatsApp & Phone)": "#F59E0B",
        }
        for m in mod_order:
            sub_m = m_grp[m_grp["Modality"] == m].set_index("Year_Month").reindex(u_monthly["Year_Month"]).fillna(0)
            fig_trend.add_trace(
                go.Bar(
                    name=f"{m} (Touches)",
                    x=u_monthly["Month_Label"],
                    y=sub_m["Encounters"].values,
                    marker_color=palette[m],
                    opacity=0.82,
                )
            )
        fig_trend.add_trace(
            go.Scatter(
                name="Unique Beneficiaries (Deduplicated)",
                x=u_monthly["Month_Label"],
                y=u_monthly["Unique_Mentees"],
                mode="lines+markers+text",
                text=u_monthly["Unique_Mentees"],
                textposition="top center",
                line=dict(color="#DC2626", width=3),
                marker=dict(size=8, color="#DC2626"),
            )
        )
        fig_trend.update_layout(
            barmode="stack",
            height=350,
            margin=dict(l=10, r=10, t=20, b=15),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            yaxis_title="Count",
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with g_col:
        st.markdown("#### 4. Male vs. Female Mentees by Curriculum & Modality")
        g_curr_rows = []
        for g in ["Female", "Male"]:
            sub_g = df_win[df_win["Gender"] == g]
            for c_lbl, c_key in [("Medical Curriculum", "Medical"), ("Management Curriculum", "Management")]:
                u_gc = int(sub_g[sub_g["Curriculum"].str.contains(c_key, case=False, na=False)]["beneficiary_uid"].nunique())
                g_curr_rows.append({"Gender": g, "Curriculum": c_lbl, "Unique Mentees": u_gc})
            for m in mod_order:
                u_gm = int(sub_g[sub_g["Modality"] == m]["beneficiary_uid"].nunique())
                g_curr_rows.append({"Gender": g, "Curriculum": m.split(" (")[0], "Unique Mentees": u_gm})

        df_gc = pd.DataFrame(g_curr_rows)
        fig_gender = px.bar(
            df_gc,
            x="Curriculum",
            y="Unique Mentees",
            color="Gender",
            barmode="group",
            text="Unique Mentees",
            color_discrete_map={"Female": "#7C3AED", "Male": "#0284C7"},
            height=305,
        )
        fig_gender.update_traces(textposition="outside")
        fig_gender.update_layout(
            margin=dict(l=10, r=10, t=15, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            xaxis_title="",
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_gender, use_container_width=True)

        ct = pd.crosstab(
            df_win[df_win["Gender"].isin(["Female", "Male"])]["Gender"],
            df_win[df_win["Gender"].isin(["Female", "Male"])]["Modality"],
        )
        stat_notes = []
        if ct.shape[0] == 2 and ct.shape[1] >= 2:
            chi2, p_val, dof, _ = stats.chi2_contingency(ct)
            sig_lbl = "statistically significant gender difference" if p_val < 0.05 else "no statistically significant gender skew"
            stat_notes.append(f"**Modality × Gender ($\chi^2$):** $\chi^2={chi2:.2f}$ (df={dof}, $p={p_val:.3f}$) → *{sig_lbl}*.")
        f_doses = person_df[person_df["Gender"] == "Female"]["Total_Encounters"].values
        m_doses = person_df[person_df["Gender"] == "Male"]["Total_Encounters"].values
        if len(f_doses) >= 3 and len(m_doses) >= 3:
            u_stat, u_pval = stats.mannwhitneyu(f_doses, m_doses, alternative="two-sided")
            stat_notes.append(
                f"**Touch Dose by Gender (Mann-Whitney $U$):** Female mean **{f_doses.mean():.2f}** vs. Male **{m_doses.mean():.2f}** ($U={u_stat:.0f}$, $p={u_pval:.3f}$)."
            )
        if stat_notes:
            st.info("  \n".join(stat_notes))

    st.markdown("---")

    # --- ROW 3: BLENDED PATHWAYS + MENTOR TRACK & COHORT MATRIX + LORENZ/GINI ---
    m_col1, m_col2, m_col3 = st.columns([1.1, 1.15, 1.0])

    with m_col1:
        st.markdown("#### 5. Blended Modality Pathways (Mutually Exclusive)")
        combo_df = (
            person_df.groupby("Modality_Combo", as_index=False)
            .agg(Unique_Mentees=("beneficiary_uid", "count"), Mean_Touches=("Total_Encounters", "mean"))
            .sort_values("Unique_Mentees", ascending=True)
        )
        combo_df["Share_%"] = (combo_df["Unique_Mentees"] / unique_total * 100.0).round(1)
        fig_combo = px.bar(
            combo_df,
            x="Unique_Mentees",
            y="Modality_Combo",
            orientation="h",
            text=combo_df.apply(lambda r: f"{int(r['Unique_Mentees'])} ({r['Share_%']:.1f}%)", axis=1),
            color="Mean_Touches",
            color_continuous_scale="Blues",
            height=330,
        )
        fig_combo.update_traces(textposition="outside")
        fig_combo.update_layout(
            margin=dict(l=10, r=45, t=20, b=10),
            xaxis_title="Unique Beneficiaries (Sum = 100%)",
            yaxis_title="",
            coloraxis_colorbar_title="Avg Touches",
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_combo, use_container_width=True)

    with m_col2:
        st.markdown("#### 6. Mentor Reach by Track & Cohort")
        mentor_rows = []
        for slug, info in MENTOR_REGISTRY.items():
            sub_t = df_win[df_win["trainer_raw"].str.contains(slug, case=False, na=False)]
            u_m = int(sub_t["beneficiary_uid"].nunique())
            e_m = int(len(sub_t))
            mentor_rows.append(
                {
                    "Mentor": f"{info['name']} ({info['cohort']})",
                    "Track": f"{info['track']} Mentor",
                    "Unique Mentees": u_m,
                    "Total Sessions": e_m,
                }
            )
        df_mentors = pd.DataFrame(mentor_rows).sort_values("Unique Mentees", ascending=True)
        fig_mentors = px.bar(
            df_mentors,
            x="Unique Mentees",
            y="Mentor",
            color="Track",
            orientation="h",
            text=df_mentors.apply(lambda r: f"{r['Unique Mentees']} uniq ({r['Total Sessions']} sess)", axis=1),
            color_discrete_map={"Medical Mentor": "#0F2C59", "Management Mentor": "#0D9488"},
            height=330,
        )
        fig_mentors.update_traces(textposition="outside")
        fig_mentors.update_layout(
            margin=dict(l=10, r=55, t=20, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            yaxis_title="",
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_mentors, use_container_width=True)

    with m_col3:
        st.markdown("#### 7. Coverage Equity (Lorenz & Gini)")
        doses = np.sort(person_df["Total_Encounters"].values)
        gini = _gini_coefficient(doses)
        cum_people = np.insert(np.arange(1, len(doses) + 1) / len(doses) * 100.0, 0, 0.0)
        cum_touches = np.insert(np.cumsum(doses) / doses.sum() * 100.0, 0, 0.0) if doses.sum() > 0 else np.zeros_like(cum_people)

        fig_lorenz = go.Figure()
        fig_lorenz.add_trace(
            go.Scatter(
                x=[0, 100],
                y=[0, 100],
                mode="lines",
                name="Perfect Equality (Gini = 0)",
                line=dict(color="#94A3B8", dash="dash"),
            )
        )
        fig_lorenz.add_trace(
            go.Scatter(
                x=cum_people,
                y=cum_touches,
                mode="lines",
                name=f"Actual Reach (Gini = {gini:.2f})",
                fill="tonexty",
                fillcolor="rgba(15, 44, 89, 0.14)",
                line=dict(color="#0F2C59", width=2.5),
            )
        )
        fig_lorenz.update_layout(
            height=330,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis_title="Cumulative % of Unique Mentees",
            yaxis_title="Cumulative % of Touches",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_lorenz, use_container_width=True)

    st.markdown("---")

    # --- ROW 4: CADRE BREAKDOWN & SEARCHABLE DEDUPLICATED MENTEE ROSTER ---
    cad_col, ros_col = st.columns([0.95, 1.45])

    with cad_col:
        st.markdown("#### 8. Unique Beneficiaries by Cadre")
        cad_df = (
            person_df.groupby("Cadre", as_index=False)
            .agg(Unique_Mentees=("beneficiary_uid", "count"))
            .sort_values("Unique_Mentees", ascending=True)
            .tail(12)
        )
        fig_cad = px.bar(
            cad_df,
            x="Unique_Mentees",
            y="Cadre",
            orientation="h",
            text="Unique_Mentees",
            color_discrete_sequence=["#0F2C59"],
            height=380,
        )
        fig_cad.update_traces(textposition="outside")
        fig_cad.update_layout(
            margin=dict(l=10, r=30, t=15, b=10),
            yaxis_title="",
            xaxis_title="Unique Mentees",
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_cad, use_container_width=True)

    with ros_col:
        st.markdown(f"#### 9. Deduplicated Beneficiary Roster ({window_label})")
        search_q = st.text_input(
            "Filter roster by Mentee Name, Facility, Curriculum, Mentor, or Cadre",
            placeholder="e.g., Diwopa, Medical, Management, Nurse, Newton, Mary...",
            key="mt_roster_search",
        )
        roster_view = person_df[
            [
                "Mentee_Name",
                "Gender",
                "Cadre",
                "Primary_Facility",
                "Curriculum_Profile",
                "Total_Encounters",
                "Modality_Combo",
                "Mentors_List",
                "Cohorts_List",
                "Last_Touch",
            ]
        ].rename(
            columns={
                "Mentee_Name": "Mentee Name",
                "Primary_Facility": "Facility",
                "Curriculum_Profile": "Curriculum Stream",
                "Total_Encounters": "Touches",
                "Modality_Combo": "Modalities Received",
                "Mentors_List": "Mentor(s)",
                "Cohorts_List": "Cohort",
                "Last_Touch": "Last Activity",
            }
        ).sort_values(["Touches", "Mentee Name"], ascending=[False, True])

        if search_q.strip():
            q_low = search_q.strip().lower()
            mask = roster_view.apply(lambda r: q_low in " | ".join(str(v).lower() for v in r.values), axis=1)
            roster_view = roster_view[mask]

        st.dataframe(roster_view, hide_index=True, use_container_width=True, height=335)
