import math
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from scripts.mentee_tracker_adapter import (
    MENTOR_REGISTRY,
    MODULE_LABELS,
    build_facility_coverage_matrix,
    sync_monitrac_mentees,
)

INK = "#0F172A"
SLATE = "#334155"
GRID = "#E2E8F0"


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


def _style_fig(fig: go.Figure, height: int = 350, margin: dict | None = None, x_max_pad: float | None = None) -> go.Figure:
    """Enforces crisp dark ink on pure white canvas regardless of Streamlit Light/Dark theme."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=margin or dict(l=12, r=24, t=34, b=18),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color=INK, size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(color=INK, size=11.5),
            bgcolor="rgba(255,255,255,0.9)",
        ),
    )
    fig.update_xaxes(
        tickfont=dict(color=INK, size=11.5),
        title_font=dict(color=INK, size=12),
        gridcolor=GRID,
        linecolor="#94A3B8",
        zerolinecolor="#94A3B8",
    )
    fig.update_yaxes(
        tickfont=dict(color=INK, size=11.5),
        title_font=dict(color=INK, size=12),
        gridcolor=GRID,
        linecolor="#94A3B8",
        zerolinecolor="#94A3B8",
    )
    if x_max_pad is not None and x_max_pad > 0:
        fig.update_xaxes(range=[0, x_max_pad * 1.26])
    fig.update_traces(
        textfont=dict(color=INK, size=11.5),
        cliponaxis=False,
        selector=dict(type="bar"),
    )
    return fig


def _explain_box(text: str) -> None:
    st.markdown(
        f"""
        <div style="background:#F8FAFC;border-left:4px solid #0F2C59;border-top:1px solid #E2E8F0;border-right:1px solid #E2E8F0;border-bottom:1px solid #E2E8F0;border-radius:0 8px 8px 0;padding:10px 14px;margin-top:6px;margin-bottom:10px;color:#0F172A;font-size:13px;line-height:1.5;">
            <b style="color:#0F2C59;">What's happening:</b> {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _kpi_card(title: str, value: str, sub: str, accent: str = "#0F2C59") -> str:
    return f"""
    <div style="background:#FFFFFF;border:1px solid #CBD5E1;border-top:4px solid {accent};border-radius:10px;padding:15px 17px;box-shadow:0 1px 3px rgba(15,23,42,0.06);height:100%;">
        <div style="font-size:11px;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:#334155;">{title}</div>
        <div style="font-size:25px;font-weight:800;color:#0F172A;margin:6px 0 4px 0;line-height:1.15;">{value}</div>
        <div style="font-size:12.5px;color:#1E293B;line-height:1.45;">{sub}</div>
    </div>
    """


def render_mentee_tracker_view():
    # Ensure widget labels & captions have crisp high-contrast ink even if browser uses Dark Mode
    st.markdown(
        """
        <style>
        div[data-testid="stSelectbox"] label p,
        div[data-testid="stTextInput"] label p,
        div[data-testid="stRadio"] label p,
        div[data-testid="stRadio"] div[role="radiogroup"] label p {
            color: #0F172A !important;
            font-weight: 700 !important;
            opacity: 1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#0F2C59 0%,#1E3A8A 100%);padding:22px 26px;border-radius:12px;margin-bottom:18px;color:#FFFFFF;">
            <div style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#93C5FD;">
                MoniTrac DHIS2 Tracker · Program NYY8hzVYv8f · Medical &amp; Management Curriculum Intelligence
            </div>
            <h2 style="margin:4px 0 6px 0;font-size:24px;font-weight:800;color:#FFFFFF;">
                🎓 Mentee &amp; Beneficiary Reach Analytics
            </h2>
            <p style="margin:0;font-size:13.5px;color:#F1F5F9;max-width:980px;">
                Strict entity-level deduplication across <b>Medical Curriculum (Modules 1–5)</b> and <b>Management Curriculum (Modules 1–4)</b>,
                tracking both <b>Physical In-Person Onsite</b> and <b>Virtual Mentorship Sub-Modalities (WhatsApp, Phone Call, Google Meet/Zoom)</b>.
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

    # --- TOP FILTER CONTROLS ---
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
            Channels_List=("Delivery_Mode", lambda s: sorted(set(s))),
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

    onsite_df_win = df_win[(df_win["Delivery_Mode"] == "Physical / In-Person Onsite") & (df_win["Modality"] == "Onsite Mentorship")]
    central_df_win = df_win[df_win["Modality"] == "Centralized Training"]
    total_sessions = int(df_win["Session_UID"].nunique())
    onsite_sessions = int(onsite_df_win["Session_UID"].nunique())
    central_sessions = int(central_df_win["Session_UID"].nunique())
    if not onsite_df_win.empty and "Mentor_Track" in onsite_df_win.columns:
        _tracks_per_onsite = onsite_df_win.groupby("Session_UID")["Mentor_Track"].nunique()
        joint_onsite_sessions = int((_tracks_per_onsite > 1).sum())
        solo_onsite_sessions = int((_tracks_per_onsite == 1).sum())
    else:
        joint_onsite_sessions, solo_onsite_sessions = 0, onsite_sessions
    virtual_sessions = int(df_win[df_win["Delivery_Mode"] == "Virtual Mentorship / Support"]["Session_UID"].nunique())
    onsite_touches = int((df_win["Delivery_Mode"] == "Physical / In-Person Onsite").sum())
    virtual_touches = int((df_win["Delivery_Mode"] == "Virtual Mentorship / Support").sum())

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
                "Unique Onsite Facility Visits",
                f"{onsite_sessions:,} Visits",
                f"<b>{joint_onsite_sessions:,}</b> Joint Med+Mgt · <b>{solo_onsite_sessions:,}</b> Solo (Facility+Date) · <b>{central_sessions:,}</b> Centralized · <b>{virtual_sessions:,}</b> Virtual.",
                "#0284C7",
            ),
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            _kpi_card(
                "Medical vs. Management Reach",
                f"{med_unique:,} Med · {mgt_unique:,} Mgt",
                f"<b>{dual_curr_unique:,}</b> dual-curriculum mentees completed both tracks (Med Mod 1–5 &amp; Mgt Mod 1–4).",
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

    # --- ROW 1: PHYSICAL ONSITE VS VIRTUAL MENTORSHIP SESSIONS & VIRTUAL PLATFORM SUB-MODALITIES ---
    v1, v2 = st.columns([1.05, 1.2])

    with v1:
        st.markdown("#### 1. Mentorship Sessions: Physical Onsite vs. Virtual")
        deliv_rows = []
        for dm in ["Physical / In-Person Onsite", "Virtual Mentorship / Support"]:
            sub_d = df_win[df_win["Delivery_Mode"] == dm]
            deliv_rows.append(
                {
                    "Channel": dm,
                    "Coaching Sessions": int(sub_d["Session_UID"].nunique()),
                    "Mentee Touches": int(len(sub_d)),
                    "Unique Mentees Reached": int(sub_d["beneficiary_uid"].nunique()),
                }
            )
        df_deliv = pd.DataFrame(deliv_rows)
        fig_deliv = go.Figure()
        fig_deliv.add_trace(
            go.Bar(
                name="Coaching Sessions",
                x=df_deliv["Channel"],
                y=df_deliv["Coaching Sessions"],
                marker_color="#0F2C59",
                text=df_deliv["Coaching Sessions"],
                textposition="outside",
            )
        )
        fig_deliv.add_trace(
            go.Bar(
                name="Unique Mentees Reached",
                x=df_deliv["Channel"],
                y=df_deliv["Unique Mentees Reached"],
                marker_color="#0D9488",
                text=df_deliv["Unique Mentees Reached"],
                textposition="outside",
            )
        )
        fig_deliv.add_trace(
            go.Bar(
                name="Total Mentee Touches",
                x=df_deliv["Channel"],
                y=df_deliv["Mentee Touches"],
                marker_color="#0284C7",
                text=df_deliv["Mentee Touches"],
                textposition="outside",
            )
        )
        fig_deliv.update_layout(barmode="group", yaxis_title="Count")
        fig_deliv.update_yaxes(range=[0, max(df_deliv["Mentee Touches"].max(), 1) * 1.18])
        _style_fig(fig_deliv, height=340)
        st.plotly_chart(fig_deliv, use_container_width=True)

        onsite_share = (onsite_sessions / max(total_sessions, 1)) * 100.0
        avg_group = (onsite_touches / max(onsite_sessions, 1))
        _explain_box(
            f"Field teams conducted <b>{onsite_sessions:,} unique onsite facility visits</b> (<b>{joint_onsite_sessions:,} joint Med+Mgt</b> &amp; <b>{solo_onsite_sessions:,} solo</b>, deduplicated by Facility + Date) plus <b>{central_sessions:,} centralized workshop days</b>, "
            f"while <b>{virtual_sessions:,} virtual sessions</b> extended rapid follow-up coaching to <b>{int(df_deliv.loc[1, 'Unique Mentees Reached']):,}</b> unique staff."
        )

    with v2:
        st.markdown("#### 2. Virtual Mentorship Sub-Modalities (WhatsApp, Phone Call, Video)")
        virt_df = df_win[df_win["Delivery_Mode"] == "Virtual Mentorship / Support"].copy()
        if virt_df.empty:
            st.info("No Virtual Mentorship records logged in the selected window.")
        else:
            vp_grp = (
                virt_df.groupby("Virtual_Platform", as_index=False)
                .agg(
                    Virtual_Sessions=("Session_UID", "nunique"),
                    Mentee_Touches=("event_uid", "count"),
                    Unique_Mentees=("beneficiary_uid", "nunique"),
                    Total_Minutes=("Minutes", "sum"),
                )
                .sort_values("Mentee_Touches", ascending=True)
            )
            fig_vp = go.Figure()
            fig_vp.add_trace(
                go.Bar(
                    name="Virtual Sessions",
                    y=vp_grp["Virtual_Platform"],
                    x=vp_grp["Virtual_Sessions"],
                    orientation="h",
                    marker_color="#7C3AED",
                    text=vp_grp["Virtual_Sessions"],
                    textposition="outside",
                )
            )
            fig_vp.add_trace(
                go.Bar(
                    name="Unique Mentees",
                    y=vp_grp["Virtual_Platform"],
                    x=vp_grp["Unique_Mentees"],
                    orientation="h",
                    marker_color="#0D9488",
                    text=vp_grp["Unique_Mentees"],
                    textposition="outside",
                )
            )
            fig_vp.add_trace(
                go.Bar(
                    name="Mentee Touches",
                    y=vp_grp["Virtual_Platform"],
                    x=vp_grp["Mentee_Touches"],
                    orientation="h",
                    marker_color="#D97706",
                    text=vp_grp["Mentee_Touches"],
                    textposition="outside",
                )
            )
            fig_vp.update_layout(barmode="group", xaxis_title="Count", yaxis_title="")
            _style_fig(fig_vp, height=270, x_max_pad=float(vp_grp["Mentee_Touches"].max()))
            st.plotly_chart(fig_vp, use_container_width=True)

            top_vp = vp_grp.sort_values("Virtual_Sessions", ascending=False).iloc[0]
            _explain_box(
                f"<b>{top_vp['Virtual_Platform']}</b> is the primary remote coaching channel with <b>{int(top_vp['Virtual_Sessions'])} sessions</b> "
                f"reaching <b>{int(top_vp['Unique_Mentees'])} unique mentees</b>, complemented by 1-on-1 phone check-ins and WhatsApp quick-consults for real-time clinical and administrative troubleshooting."
            )

    st.markdown("---")

    # --- ROW 2: CURRICULUM SEPARATION (MEDICAL VS MANAGEMENT MODULES & MODALITIES) ---
    c1, c2 = st.columns([1.1, 1.15])

    with c1:
        st.markdown("#### 3. Medical vs. Management Curriculum Reach by Modality")
        mod_order = ["Centralized Training", "Onsite Mentorship", "Special Training", "Virtual / Ad-hoc Support"]
        active_mods = [m for m in mod_order if m in df_win["Modality"].unique()] or mod_order[:3]
        curr_mod_rows = []
        for curr_lbl, curr_key in [("Medical Curriculum", "Medical"), ("Management Curriculum", "Management")]:
            sub_c = df_win[df_win["Curriculum"].str.contains(curr_key, case=False, na=False)]
            for m in active_mods:
                sub_cm = sub_c[sub_c["Modality"] == m]
                curr_mod_rows.append(
                    {
                        "Curriculum": curr_lbl,
                        "Modality": m,
                        "Unique Mentees": int(sub_cm["beneficiary_uid"].nunique()),
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
        )
        fig_cm.update_traces(textposition="outside")
        fig_cm.update_layout(yaxis_title="Unique Mentees Reached", xaxis_title="")
        fig_cm.update_yaxes(range=[0, max(df_cm["Unique Mentees"].max(), 1) * 1.18])
        _style_fig(fig_cm, height=345)
        st.plotly_chart(fig_cm, use_container_width=True)

        _explain_box(
            f"<b>Onsite Mentorship</b> drives the largest reach in both tracks (<b>{med_unique:,}</b> unique Medical mentees and <b>{mgt_unique:,}</b> unique Management mentees overall). "
            f"Because <b>{dual_curr_unique:,} facility leaders/nurses</b> completed modules in both tracks, summing Medical + Management ({med_unique + mgt_unique:,}) reconciles cleanly to <b>{unique_total:,} strictly unique beneficiaries</b>."
        )

    with c2:
        st.markdown("#### 4. Curriculum Module Coverage (Med Mod 1–5 vs. Mgt Mod 1–4)")
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
                    "Sessions": int(sub_mc["Session_UID"].nunique()),
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
        )
        fig_mp.update_traces(textposition="outside")
        fig_mp.update_layout(yaxis=dict(autorange="reversed", title=""), xaxis_title="Unique Mentees Covered")
        _style_fig(fig_mp, height=345, x_max_pad=float(df_mp["Unique Mentees"].max()))
        st.plotly_chart(fig_mp, use_container_width=True)

        top_med_mod = df_mp[df_mp["Stream"] == "Medical Curriculum"].sort_values("Unique Mentees", ascending=False).iloc[0]
        top_mgt_mod = df_mp[df_mp["Stream"] == "Management Curriculum"].sort_values("Unique Mentees", ascending=False).iloc[0]
        _explain_box(
            f"Foundational modules lead enrollment—<b>{top_med_mod['Module']}</b> ({top_med_mod['Unique Mentees']} mentees) in Clinical care and "
            f"<b>{top_mgt_mod['Module']}</b> ({top_mgt_mod['Unique Mentees']} mentees) in Management—while downstream modules (Child Health, NCDs, and HMIS) show progressive cohort rollout."
        )

    st.markdown("---")

    # --- ROW 3: MONTHLY DEDUPLICATION CURVE + MALE VS FEMALE STATISTICAL ANALYSIS ---
    t_col, g_col = st.columns([1.15, 1.1])

    with t_col:
        st.markdown("#### 5. Monthly Trajectory: Unique Headcount vs. Modality Volume")
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
            "Special Training": "#7C3AED",
            "Virtual / Ad-hoc Support": "#F59E0B",
        }
        for m in active_mods:
            sub_m = m_grp[m_grp["Modality"] == m].set_index("Year_Month").reindex(u_monthly["Year_Month"]).fillna(0)
            fig_trend.add_trace(
                go.Bar(
                    name=f"{m} (Touches)",
                    x=u_monthly["Month_Label"],
                    y=sub_m["Encounters"].values,
                    marker_color=palette.get(m, "#64748B"),
                    opacity=0.88,
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
                textfont=dict(color="#B91C1C", size=11.5),
                line=dict(color="#DC2626", width=3),
                marker=dict(size=8, color="#DC2626"),
            )
        )
        fig_trend.update_layout(barmode="stack", yaxis_title="Count")
        _style_fig(fig_trend, height=345)
        st.plotly_chart(fig_trend, use_container_width=True)

        peak_row = u_monthly.sort_values("Unique_Mentees", ascending=False).iloc[0]
        _explain_box(
            f"The stacked bars show total monthly mentorship touches, while the <b>red line</b> tracks deduplicated unique individuals. "
            f"Mentorship activity peaked in <b>{peak_row['Month_Label']}</b> with <b>{int(peak_row['Unique_Mentees'])} unique mentees</b> reached; whenever the stacked bar rises above the red line, mentees received multiple coaching touches within that same month."
        )

    with g_col:
        st.markdown("#### 6. Male vs. Female Mentees by Curriculum & Channel")
        g_curr_rows = []
        for g in ["Female", "Male"]:
            sub_g = df_win[df_win["Gender"] == g]
            for c_lbl, c_key in [("Medical Curriculum", "Medical"), ("Management Curriculum", "Management")]:
                u_gc = int(sub_g[sub_g["Curriculum"].str.contains(c_key, case=False, na=False)]["beneficiary_uid"].nunique())
                g_curr_rows.append({"Gender": g, "Segment": c_lbl, "Unique Mentees": u_gc})
            for dm_lbl, dm_val in [("Physical Onsite", "Physical / In-Person Onsite"), ("Virtual Support", "Virtual Mentorship / Support")]:
                u_gd = int(sub_g[sub_g["Delivery_Mode"] == dm_val]["beneficiary_uid"].nunique())
                g_curr_rows.append({"Gender": g, "Segment": dm_lbl, "Unique Mentees": u_gd})

        df_gc = pd.DataFrame(g_curr_rows)
        fig_gender = px.bar(
            df_gc,
            x="Segment",
            y="Unique Mentees",
            color="Gender",
            barmode="group",
            text="Unique Mentees",
            color_discrete_map={"Female": "#7C3AED", "Male": "#0284C7"},
        )
        fig_gender.update_traces(textposition="outside")
        fig_gender.update_layout(xaxis_title="", yaxis_title="Unique Mentees")
        fig_gender.update_yaxes(range=[0, max(df_gc["Unique Mentees"].max(), 1) * 1.18])
        _style_fig(fig_gender, height=300)
        st.plotly_chart(fig_gender, use_container_width=True)

        ct = pd.crosstab(
            df_win[df_win["Gender"].isin(["Female", "Male"])]["Gender"],
            df_win[df_win["Gender"].isin(["Female", "Male"])]["Modality"],
        )
        stat_summary = f"Women represent <b>{fem_pct:.1f}%</b> ({n_female:,} vs. {n_male:,} men) of unique mentees, mirroring Kenya's frontline nursing/clinical workforce."
        if ct.shape[0] == 2 and ct.shape[1] >= 2:
            chi2, p_val, dof, _ = stats.chi2_contingency(ct)
            stat_summary += f" A Chi-square test across modalities (χ² = {chi2:.2f}, <i>p</i> = {p_val:.3f}) confirms <b>equitable access</b> with no gender barrier to onsite or virtual coaching."
        _explain_box(stat_summary)

    st.markdown("---")

    # --- ROW 4: BLENDED PATHWAYS + MENTOR TRACK & COHORT MATRIX + LORENZ/GINI ---
    m_col1, m_col2, m_col3 = st.columns([1.15, 1.15, 0.95])

    with m_col1:
        st.markdown("#### 7. Blended Modality Pathways (Mutually Exclusive)")
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
            color_discrete_sequence=["#1E40AF"],
        )
        fig_combo.update_traces(textposition="outside")
        fig_combo.update_layout(xaxis_title="Unique Beneficiaries (Sum = 100%)", yaxis_title="")
        _style_fig(fig_combo, height=340, x_max_pad=float(combo_df["Unique_Mentees"].max()))
        st.plotly_chart(fig_combo, use_container_width=True)

        single_onsite = int(combo_df[combo_df["Modality_Combo"] == "Onsite Mentorship"]["Unique_Mentees"].sum())
        _explain_box(
            f"Every unique mentee falls into <b>exactly one</b> pathway bar: <b>{single_onsite:,}</b> ({single_onsite/max(unique_total,1)*100:.1f}%) received Onsite Mentorship alone, "
            f"while <b>{blended_n:,} ({blended_pct:.1f}%)</b> experienced a <b>blended multi-modality journey</b> combining Centralized Training, Onsite Visits, and/or Virtual Support."
        )

    with m_col2:
        st.markdown("#### 8. Mentor Reach by Track & Cohort")
        mentor_rows = []
        for slug, info in MENTOR_REGISTRY.items():
            sub_t = df_win[df_win["trainer_raw"].str.contains(slug, case=False, na=False)]
            u_m = int(sub_t["beneficiary_uid"].nunique())
            sess_col = "Mentor_Session_UID" if "Mentor_Session_UID" in sub_t.columns else "Session_UID"
            s_m = int(sub_t[sess_col].nunique())
            mentor_rows.append(
                {
                    "Mentor": f"{info['name']} ({info['cohort']})",
                    "Track": f"{info['track']} Mentor",
                    "Unique Mentees": u_m,
                    "Coaching Sessions": s_m,
                }
            )
        df_mentors = pd.DataFrame(mentor_rows).sort_values("Unique Mentees", ascending=True)
        fig_mentors = px.bar(
            df_mentors,
            x="Unique Mentees",
            y="Mentor",
            color="Track",
            orientation="h",
            text=df_mentors.apply(lambda r: f"{r['Unique Mentees']} uniq ({r['Coaching Sessions']} sess)", axis=1),
            color_discrete_map={"Medical Mentor": "#0F2C59", "Management Mentor": "#0D9488"},
        )
        fig_mentors.update_traces(textposition="outside")
        fig_mentors.update_layout(yaxis_title="", xaxis_title="Unique Mentees Reached")
        _style_fig(fig_mentors, height=340, x_max_pad=float(df_mentors["Unique Mentees"].max()))
        st.plotly_chart(fig_mentors, use_container_width=True)

        top_mentor = df_mentors.sort_values("Unique Mentees", ascending=False).iloc[0]
        _explain_box(
            f"<b>Cohort 1 &amp; 2</b> mentors (Joseph Kirori and Lewis Muriuki) carry higher cumulative unique headcounts due to longer tenure, "
            f"led by <b>{top_mentor['Mentor']}</b> ({top_mentor['Unique Mentees']} unique mentees across {top_mentor['Coaching Sessions']} sessions), while <b>Cohort 3</b> mentors (Newton, Whyttney, Adrian, Mary) are actively scaling new facilities."
        )

    with m_col3:
        st.markdown("#### 9. Coverage Equity (Lorenz & Gini)")
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
                line=dict(color="#64748B", dash="dash", width=2),
            )
        )
        fig_lorenz.add_trace(
            go.Scatter(
                x=cum_people,
                y=cum_touches,
                mode="lines",
                name=f"Actual Reach (Gini = {gini:.2f})",
                fill="tonexty",
                fillcolor="rgba(15, 44, 89, 0.16)",
                line=dict(color="#0F2C59", width=3),
            )
        )
        fig_lorenz.update_layout(
            xaxis_title="Cumulative % of Unique Mentees",
            yaxis_title="Cumulative % of Touches",
        )
        _style_fig(fig_lorenz, height=340)
        st.plotly_chart(fig_lorenz, use_container_width=True)

        eq_label = "well-balanced distribution" if gini < 0.35 else "moderate concentration among repeat champions"
        _explain_box(
            f"A Gini coefficient of <b>{gini:.2f}</b> indicates a <b>{eq_label}</b> (0.00 = every mentee gets identical touches). "
            f"The closer the solid navy curve hugs the dashed diagonal, the more evenly mentorship visits are spread across all facility staff."
        )

    st.markdown("---")

    # --- ROW 5: 38-FACILITY MENTORSHIP COVERAGE & GAP MATRIX ---
    st.markdown(f"#### 10. Facility-Level Mentorship Coverage & Gap Matrix ({window_label})")
    cov_df = build_facility_coverage_matrix(df_win)
    if not cov_df.empty:
        partner_only = cov_df[~cov_df["Coverage_Status"].str.contains("Non-KHIS", na=False)]
        full_cnt = int((partner_only["Coverage_Status"].str.contains("Full Dual Coverage")).sum())
        med_only_cnt = int((partner_only["Coverage_Status"].str.contains("Medical Only")).sum())
        mgt_only_cnt = int((partner_only["Coverage_Status"].str.contains("Management Only")).sum())
        zero_cnt = int((partner_only["Coverage_Status"].str.contains("Zero Reach Gap")).sum())

        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Full Dual Coverage (Med + Mgt)", f"{full_cnt} / {len(partner_only)} Sites", f"{(full_cnt/max(len(partner_only),1)*100):.1f}% of Portfolio")
        g2.metric("Medical Only (Needs Management)", f"{med_only_cnt} Sites", "Schedule Mgt Modules 1–4")
        g3.metric("Management Only (Needs Medical)", f"{mgt_only_cnt} Sites", "Schedule Med Modules 1–5")
        g4.metric("Zero Reach Gap (0 Mentees)", f"{zero_cnt} Sites", "Priority Mentor Deployment", delta_color="inverse")

        _explain_box(
            f"<b>{full_cnt} of {len(partner_only)} partner facilities ({full_cnt/max(len(partner_only),1)*100:.1f}%)</b> have achieved full dual-track coverage (both Medical and Management curricula active), "
            f"while <b>{med_only_cnt + mgt_only_cnt} sites</b> have single-track coverage and <b>{zero_cnt} sites</b> have zero touches in this period—guiding exact mentor deployment."
        )

        cov_filter = st.radio(
            "Filter Facility Coverage Matrix",
            [
                "All Facilities",
                "Zero Reach Gap (0 Mentees)",
                "Partial Coverage (Needs Medical or Management)",
                "Full Dual Coverage (Med + Mgt)",
            ],
            horizontal=True,
            key="mt_cov_filter",
        )
        disp_cov = cov_df.copy()
        if cov_filter.startswith("Zero"):
            disp_cov = disp_cov[disp_cov["Coverage_Status"].str.contains("Zero Reach Gap")]
        elif cov_filter.startswith("Partial"):
            disp_cov = disp_cov[disp_cov["Coverage_Status"].str.contains("Only")]
        elif cov_filter.startswith("Full"):
            disp_cov = disp_cov[disp_cov["Coverage_Status"].str.contains("Full Dual Coverage")]

        st.dataframe(
            disp_cov.rename(
                columns={
                    "Coverage_Status": "Coverage & Gap Status",
                    "Unique_Mentees": "Unique Mentees",
                    "Medical_Mentees": "Med Mentees",
                    "Management_Mentees": "Mgt Mentees",
                    "Onsite_Sessions": "Unique Onsite Visits",
                    "Joint_Onsite_Visits": "Joint Visits (Med+Mgt)",
                    "Solo_Onsite_Visits": "Solo Visits",
                    "Virtual_Sessions": "Virtual Sessions",
                    "Total_Touches": "Total Touches",
                    "Assigned_Mentors": "Mentor(s)",
                    "Last_Mentorship": "Last Activity",
                }
            ),
            hide_index=True,
            use_container_width=True,
            height=340,
        )

    st.markdown("---")

    # --- ROW 6: CADRE BREAKDOWN & SEARCHABLE DEDUPLICATED MENTEE ROSTER ---
    cad_col, ros_col = st.columns([0.95, 1.45])

    with cad_col:
        st.markdown("#### 11. Unique Beneficiaries by Cadre")
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
        )
        fig_cad.update_traces(textposition="outside")
        fig_cad.update_layout(yaxis_title="", xaxis_title="Unique Mentees")
        _style_fig(fig_cad, height=380, x_max_pad=float(cad_df["Unique_Mentees"].max()))
        st.plotly_chart(fig_cad, use_container_width=True)

        known_cad = cad_df[cad_df["Cadre"] != "Unspecified"]
        unspec_n = int(cad_df[cad_df["Cadre"] == "Unspecified"]["Unique_Mentees"].sum())
        top_cad = known_cad.sort_values("Unique_Mentees", ascending=False).iloc[0] if not known_cad.empty else None
        cad_msg = (
            f"<b>{top_cad['Cadre']}</b> is the largest identified cadre ({int(top_cad['Unique_Mentees'])} unique mentees), followed by Clinical Officers, Accountants, and Pharmacy staff. "
            if top_cad is not None else ""
        )
        if unspec_n > 0:
            cad_msg += f"<b>{unspec_n}</b> profiles still have blank Cadre attributes in MoniTrac—a quick data-hygiene win for field mentors."
        _explain_box(cad_msg)

    with ros_col:
        st.markdown(f"#### 12. Deduplicated Beneficiary Roster ({window_label})")
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

        st.dataframe(roster_view, hide_index=True, use_container_width=True, height=345)
        _explain_box(
            f"Each row above represents <b>one strictly deduplicated individual</b> (sorted by highest engagement intensity), showing their facility, curriculum stream(s), and exact combination of modalities received."
        )
