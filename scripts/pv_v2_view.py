import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
TEXT_DARK = "#0F172A"
GRID_COLOR = "#E2E8F0"


def _apply_pv_theme(fig, height=400, margin=None):
    if margin is None:
        margin = dict(l=25, r=30, t=40, b=30)
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=margin,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        font=dict(family=FONT_FAMILY, color=TEXT_DARK, size=12),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor="#CBD5E1",
            tickfont=dict(color=TEXT_DARK, size=11.5),
            title_font=dict(color=TEXT_DARK, size=12, weight="bold"),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor="#CBD5E1",
            tickfont=dict(color=TEXT_DARK, size=11.5),
            title_font=dict(color=TEXT_DARK, size=12, weight="bold"),
        ),
        legend=dict(
            title=dict(font=dict(color=TEXT_DARK, size=12, weight="bold")),
            font=dict(color=TEXT_DARK, size=11.5),
            bgcolor="rgba(255,255,255,0.92)",
        ),
    )
    return fig


def render_chart_narrative(title, insight_html, action_html, accent="#0F2C59"):
    st.markdown(f"<div style=\"background:#F8FAFC;border:1px solid #CBD5E1;border-left:4px solid {accent};border-radius:8px;padding:10px 14px;margin-top:8px;margin-bottom:10px;\"><div style=\"font-size:11px;font-weight:800;color:{accent};text-transform:uppercase;margin-bottom:3px;\">M&E Takeaway — {title}</div><div style=\"font-size:12.5px;color:#0F172A;line-height:1.45;margin-bottom:4px;\">{insight_html}</div><div style=\"font-size:12px;color:#334155;\"><b>Next Step:</b> {action_html}</div></div>", unsafe_allow_html=True)

def render_pv_story_card(col, title, icon, primary_val, badge_text, badge_type, narrative):
    badge_bg = "#DCFCE7" if badge_type == "good" else ("#FEF3C7" if badge_type == "warn" else "#FEE2E2")
    badge_fg = "#166534" if badge_type == "good" else ("#92400E" if badge_type == "warn" else "#991B1B")
    border_accent = "#0D9488" if badge_type == "good" else ("#D97706" if badge_type == "warn" else "#DC2626")

    with col:
        st.markdown(
            f'''
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-top:4px solid {border_accent};
                        border-radius:10px; padding:14px 16px; box-shadow:0 2px 6px rgba(15,23,42,0.05); height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <span style="font-size:11px; font-weight:800; color:#475569; text-transform:uppercase; letter-spacing:0.6px;">{title}</span>
                    <span style="font-size:18px;">{icon}</span>
                </div>
                <div style="font-size:25px; font-weight:800; color:#0F172A; line-height:1.15; margin-bottom:6px;">{primary_val}</div>
                <div style="margin-bottom:8px;">
                    <span style="background:{badge_bg}; color:{badge_fg}; font-size:11px; font-weight:700;
                                 padding:3px 9px; border-radius:999px; display:inline-block;">{badge_text}</span>
                </div>
                <div style="font-size:11.5px; color:#334155; line-height:1.45; border-top:1px dashed #E2E8F0; padding-top:7px;">
                    {narrative}
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )


def render_pv_v2_dashboard(facility_pv_df, tot_base, tot_focus, abs_var, growth_pct, focus_year, comparison_year, selected_period):
    st.markdown(
        f'''
        <div style="background:linear-gradient(135deg, #0F2C59 0%, #1E3A8A 100%); padding:18px 22px;
                    border-radius:10px; color:#FFFFFF; margin-bottom:16px;">
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:1.2px; color:#5EEAD4; font-weight:700;">
                Network Utilization & Statistical Demand Intelligence
            </div>
            <div style="font-size:21px; font-weight:800; margin-top:2px;">
                Outpatient Attendance & Facility Utilization Story ({focus_year} Focus vs. {comparison_year} Baseline — {selected_period})
            </div>
            <div style="font-size:12.5px; color:#E2E8F0; margin-top:4px;">
                Evaluating network demand shifts, 45° growth parity cones, Pareto 80/20 volume concentration, and non-parametric facility medians.
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    if facility_pv_df is None or facility_pv_df.empty:
        st.warning("No Patient Volume records available for the selected period.")
        return

    df = facility_pv_df.copy()
    df["PV_2025"] = pd.to_numeric(df["PV_2025"], errors="coerce").fillna(0)
    df["PV_2026"] = pd.to_numeric(df["PV_2026"], errors="coerce").fillna(0)
    df["Absolute_Variance"] = df["PV_2026"] - df["PV_2025"]
    df["Growth_%"] = np.where(
        df["PV_2025"] > 0,
        (df["Absolute_Variance"] / df["PV_2025"]) * 100,
        np.where(df["PV_2026"] > 0, 100.0, 0.0),
    )

    gaining = df[df["Absolute_Variance"] > 0].sort_values("Absolute_Variance", ascending=False)
    dropping = df[df["Absolute_Variance"] < 0].sort_values("Absolute_Variance", ascending=True)
    tot_gains = int(gaining["Absolute_Variance"].sum())
    tot_drops = int(dropping["Absolute_Variance"].sum())

    top_g_name = gaining.iloc[0]["organisationunitname"] if not gaining.empty else "N/A"
    top_g_val = int(gaining.iloc[0]["Absolute_Variance"]) if not gaining.empty else 0
    top_g_pct = float(gaining.iloc[0]["Growth_%"]) if not gaining.empty else 0.0

    top_d_name = dropping.iloc[0]["organisationunitname"] if not dropping.empty else "N/A"
    top_d_val = int(dropping.iloc[0]["Absolute_Variance"]) if not dropping.empty else 0
    top_d_pct = float(dropping.iloc[0]["Growth_%"]) if not dropping.empty else 0.0

    med_base = float(df["PV_2025"].median())
    med_focus = float(df["PV_2026"].median())
    iqr_focus = float(df["PV_2026"].quantile(0.75) - df["PV_2026"].quantile(0.25))

    pareto_df = df.sort_values("PV_2026", ascending=False).reset_index(drop=True)
    pareto_df["Cum_Vol"] = pareto_df["PV_2026"].cumsum()
    pareto_df["Cum_Pct"] = np.where(tot_focus > 0, (pareto_df["Cum_Vol"] / tot_focus) * 100, 0.0)
    pareto_80_count = min(int((pareto_df["Cum_Pct"] <= 80.0).sum()) + 1, len(pareto_df))
    top_site_share = (pareto_df.iloc[0]["PV_2026"] / tot_focus * 100) if tot_focus > 0 else 0.0

    c1, c2, c3 = st.columns(3)
    render_pv_story_card(
        c1,
        f"Total Outpatient Attendance ({focus_year})",
        "🏥",
        f"{int(tot_focus):,}",
        f"{'↑' if abs_var >= 0 else '↓'} {int(abs_var):+,} ({growth_pct:+.2f}% vs {comparison_year})",
        "good" if abs_var >= 0 else "bad",
        f"<b>Network Throughput:</b> Served <b>{int(tot_focus):,}</b> patients across <b>{len(df)}</b> active sites vs. <b>{int(tot_base):,}</b> in {comparison_year}.",
    )
    render_pv_story_card(
        c2,
        "Expansion Engines (Gaining Sites)",
        "🚀",
        f"+{tot_gains:,}",
        f"{len(gaining)} of {len(df)} Sites Expanding ({len(gaining)/max(1,len(df))*100:.0f}%)",
        "good",
        f"<b>Top Volume Driver:</b> Led by <i>{top_g_name}</i> (<b>+{top_g_val:,}</b> | +{top_g_pct:.1f}%), driving network demand expansion.",
    )
    render_pv_story_card(
        c3,
        "Contraction Watchlist (Dropping Sites)",
        "🔻",
        f"{tot_drops:,}",
        f"{len(dropping)} of {len(df)} Sites Contracting ({len(dropping)/max(1,len(df))*100:.0f}%)",
        "warn" if abs(tot_drops) <= tot_gains else "bad",
        f"<b>Primary Attrition Site:</b> Steepest drop at <i>{top_d_name}</i> (<b>{top_d_val:,}</b> | {top_d_pct:.1f}%), offsetting {abs(tot_drops)/max(1,tot_gains)*100:.0f}% of gains.",
    )

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)
    med_delta = med_focus - med_base
    render_pv_story_card(
        c4,
        "Median Facility Volume (Non-Parametric)",
        "📐",
        f"{int(med_focus):,} <span style='font-size:14px; color:#475569;'>pts / site</span>",
        f"Median Shift: {med_delta:+,.0f} vs {comparison_year} | IQR: {int(iqr_focus):,}",
        "good" if med_delta >= 0 else "warn",
        f"<b>Distribution Takeaway:</b> Typical facility attendance moved from <b>{int(med_base):,}</b> to <b>{int(med_focus):,}</b>, confirming {'broad-based' if med_delta >= 0 else 'outlier-skewed'} performance.",
    )
    render_pv_story_card(
        c5,
        "Pareto 80/20 Network Concentration",
        "⚖️",
        f"{pareto_80_count} <span style='font-size:15px; color:#0D9488;'>of {len(df)} sites</span>",
        "Generate 80% of Total Network Volume",
        "good",
        f"<b>Load Concentration:</b> Top anchor <i>{pareto_df.iloc[0]['organisationunitname']}</i> alone accounts for <b>{top_site_share:.1f}%</b> ({int(pareto_df.iloc[0]['PV_2026']):,}) of network attendance.",
    )
    above_20 = int((df["Growth_%"] >= 20.0).sum())
    below_20 = int((df["Growth_%"] <= -20.0).sum())
    render_pv_story_card(
        c6,
        "Structural Growth Cone (±20% Band)",
        "🎯",
        f"{above_20} <span style='font-size:14px; color:#0D9488;'>High-Growth</span> · {below_20} <span style='font-size:14px; color:#DC2626;'>Alert</span>",
        f"{len(df) - above_20 - below_20} Sites Within ±20% Stability Band",
        "good" if above_20 >= below_20 else "warn",
        f"<b>Structural Shift:</b> <b>{above_20}</b> facilities grew ≥20% YoY while <b>{below_20}</b> contracted ≥20%, warranting targeted supportive supervision.",
    )

    st.markdown("---")

    col_parity, col_pareto = st.columns([1.05, 1.1])
    with col_parity:
        st.markdown(f"#### 🎯 45° Parity & ±20% Growth Cone ({comparison_year} vs. {focus_year})")
        max_axis = max(df["PV_2025"].max(), df["PV_2026"].max()) * 1.12
        x_line = np.linspace(0, max_axis, 100)

        fig_parity = go.Figure()
        fig_parity.add_trace(
            go.Scatter(
                x=np.concatenate([x_line, x_line[::-1]]),
                y=np.concatenate([x_line * 1.20, (x_line * 0.80)[::-1]]),
                fill="toself",
                fillcolor="rgba(148, 163, 184, 0.16)",
                line=dict(color="rgba(255,255,255,0)"),
                name="±20% Stability Cone",
                hoverinfo="skip",
            )
        )
        fig_parity.add_trace(
            go.Scatter(
                x=[0, max_axis],
                y=[0, max_axis],
                mode="lines",
                line=dict(color="#475569", width=1.8, dash="dash"),
                name="1:1 Parity (0% Change)",
                hoverinfo="skip",
            )
        )

        df["Regime"] = np.where(
            df["Growth_%"] >= 20.0,
            "High Growth (≥+20%)",
            np.where(df["Growth_%"] <= -20.0, "Contraction Alert (≤-20%)", "Stable Band (±20%)"),
        )
        regime_colors = {
            "High Growth (≥+20%)": "#0D9488",
            "Stable Band (±20%)": "#2563EB",
            "Contraction Alert (≤-20%)": "#DC2626",
        }
        for regime, grp in df.groupby("Regime"):
            fig_parity.add_trace(
                go.Scatter(
                    x=grp["PV_2025"],
                    y=grp["PV_2026"],
                    mode="markers",
                    name=regime,
                    marker=dict(
                        size=np.clip(np.sqrt(grp["PV_2026"]) * 0.32, 8, 22),
                        color=regime_colors[regime],
                        opacity=0.88,
                        line=dict(width=1.2, color="#FFFFFF"),
                    ),
                    customdata=np.stack([grp["organisationunitname"], grp["Absolute_Variance"], grp["Growth_%"]], axis=-1),
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        f"{comparison_year}: %{{x:,.0f}}<br>"
                        f"{focus_year}: %{{y:,.0f}}<br>"
                        "Net Shift: <b>%{customdata[1]:+,.0f} (%{customdata[2]:+.1f}%)</b><extra></extra>"
                    ),
                )
            )

        label_sites = df[
            (df["PV_2026"] >= df["PV_2026"].nlargest(4).min())
            | (df["Absolute_Variance"].abs() >= df["Absolute_Variance"].abs().nlargest(4).min())
        ].drop_duplicates("organisationunitname")

        fig_parity.add_trace(
            go.Scatter(
                x=label_sites["PV_2025"],
                y=label_sites["PV_2026"],
                mode="text",
                text=label_sites["organisationunitname"].str.slice(0, 20),
                textposition="top center",
                textfont=dict(color=TEXT_DARK, size=10),
                showlegend=False,
                hoverinfo="skip",
            )
        )

        _apply_pv_theme(fig_parity, height=420)
        fig_parity.update_xaxes(
            title=dict(text=f"{comparison_year} Baseline Attendance", font=dict(color=TEXT_DARK, size=12, weight="bold")),
            range=[0, max_axis],
        )
        fig_parity.update_yaxes(
            title=dict(text=f"{focus_year} Focus Attendance", font=dict(color=TEXT_DARK, size=12, weight="bold")),
            range=[0, max_axis],
        )
        fig_parity.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="left", x=0))
        st.plotly_chart(fig_parity, use_container_width=True)
        render_chart_narrative("Year-on-Year Volume Shift", f"<b>{above_20} sites</b> grew over 20% (led by <i>{top_g_name}</i> at +{top_g_pct:.1f}%), <b>{len(df)-above_20-below_20}</b> stayed within ±20%, and <b>{below_20}</b> dropped over 20% (steepest at <i>{top_d_name}</i>, {top_d_pct:.1f}%).", f"Check the <b>{below_20} red sites</b> for real patient attrition, staff turnover, or missing DHIS2 entries.", "#0D9488")

    with col_pareto:
        st.markdown(f"#### ⚖️ Pareto 80/20 Network Concentration Curve ({focus_year})")
        fig_pareto = go.Figure()
        bar_colors = ["#0F2C59" if pct <= 80.0 else "#94A3B8" for pct in pareto_df["Cum_Pct"]]

        fig_pareto.add_trace(
            go.Bar(
                x=pareto_df["organisationunitname"],
                y=pareto_df["PV_2026"],
                name=f"{focus_year} Attendance",
                marker_color=bar_colors,
                customdata=np.stack([pareto_df["Cum_Pct"], pareto_df["Growth_%"]], axis=-1),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    f"{focus_year} Volume: <b>%{{y:,.0f}}</b><br>"
                    "Cumulative Share: <b>%{customdata[0]:.1f}%</b><br>"
                    "YoY Growth: %{customdata[1]:+.1f}%<extra></extra>"
                ),
            )
        )
        fig_pareto.add_trace(
            go.Scatter(
                x=pareto_df["organisationunitname"],
                y=pareto_df["Cum_Pct"],
                mode="lines+markers",
                name="Cumulative % Share",
                yaxis="y2",
                line=dict(color="#D97706", width=2.8),
                marker=dict(size=5, color="#D97706"),
                hoverinfo="skip",
            )
        )
        fig_pareto.add_hline(
            y=80.0,
            yref="y2",
            line_dash="dash",
            line_color="#DC2626",
            annotation_text=f"80% Volume Threshold ({pareto_80_count} Sites)",
            annotation_font=dict(color="#991B1B", size=11, weight="bold"),
        )

        _apply_pv_theme(fig_pareto, height=420, margin=dict(l=25, r=45, t=40, b=70))
        fig_pareto.update_xaxes(tickangle=-45, tickfont=dict(color=TEXT_DARK, size=9.5))
        fig_pareto.update_yaxes(
            title=dict(text=f"{focus_year} Patient Volume", font=dict(color=TEXT_DARK, size=12, weight="bold")),
        )
        fig_pareto.update_layout(
            yaxis2=dict(
                title=dict(text="Cumulative Share (%)", font=dict(color="#B45309", size=12, weight="bold")),
                overlaying="y",
                side="right",
                range=[0, 105],
                tickfont=dict(color="#B45309", size=11),
                showgrid=False,
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="left", x=0),
        )
        st.plotly_chart(fig_pareto, use_container_width=True)
        top3_n=", ".join(pareto_df.head(3)["organisationunitname"].tolist()); top3_s=(pareto_df.head(3)["PV_2026"].sum()/tot_focus*100) if tot_focus>0 else 0.0
        render_chart_narrative("Where Our Patient Load Sits (80/20 Rule)", f"<b>{pareto_80_count} of our {len(df)} sites</b> (navy bars) bring in <b>80% of all visits</b>, and our top 3 sites (<i>{top3_n}</i>) carry <b>{top3_s:.1f}%</b> of total load.", f"Prevent stockouts and staffing gaps in those <b>{pareto_80_count} core sites</b> first—any disruption there hits network totals immediately.", "#0F2C59")

    st.markdown("---")

    col_dumb, col_dist = st.columns([1.35, 0.85])
    with col_dumb:
        st.markdown(f"#### 🧬 Facility Attendance Vector Dumbbell ({comparison_year} → {focus_year})")
        dumb_mode = st.radio(
            "Select Facility Cohort:",
            ["Top 15 by Volume", "Top 15 Gainers (+)", "Top 15 Droppers (-)", "All Active Facilities"],
            horizontal=True,
            key="pv_v2_dumb_mode",
        )
        if dumb_mode == "Top 15 by Volume":
            d_df = df.nlargest(15, "PV_2026").sort_values("PV_2026", ascending=True)
        elif dumb_mode == "Top 15 Gainers (+)":
            d_df = gaining.head(15).sort_values("Absolute_Variance", ascending=True)
        elif dumb_mode == "Top 15 Droppers (-)":
            d_df = dropping.head(15).sort_values("Absolute_Variance", ascending=False)
        else:
            d_df = df.sort_values("PV_2026", ascending=True)

        if not d_df.empty:
            fig_dumb = go.Figure()
            for _, row in d_df.iterrows():
                seg_color = "#0D9488" if row["Absolute_Variance"] >= 0 else "#DC2626"
                fig_dumb.add_trace(
                    go.Scatter(
                        x=[row["PV_2025"], row["PV_2026"]],
                        y=[row["organisationunitname"], row["organisationunitname"]],
                        mode="lines",
                        line=dict(color=seg_color, width=3),
                        showlegend=False,
                        hoverinfo="skip",
                    )
                )

            fig_dumb.add_trace(
                go.Scatter(
                    x=d_df["PV_2025"],
                    y=d_df["organisationunitname"],
                    mode="markers",
                    name=f"{comparison_year} Baseline",
                    marker=dict(size=9, color="#94A3B8", line=dict(width=1.2, color="#475569")),
                    hovertemplate=f"<b>%{{y}}</b><br>{comparison_year}: %{{x:,.0f}}<extra></extra>",
                )
            )
            max_point = np.maximum(d_df["PV_2025"], d_df["PV_2026"])
            fig_dumb.add_trace(
                go.Scatter(
                    x=d_df["PV_2026"],
                    y=d_df["organisationunitname"],
                    mode="markers",
                    name=f"{focus_year} Focus",
                    marker=dict(
                        size=11,
                        color=["#0D9488" if v >= 0 else "#DC2626" for v in d_df["Absolute_Variance"]],
                        line=dict(width=1.5, color="#FFFFFF"),
                    ),
                    hovertemplate=f"<b>%{{y}}</b><br>{focus_year}: %{{x:,.0f}}<extra></extra>",
                )
            )
            fig_dumb.add_trace(
                go.Scatter(
                    x=max_point + max_point.max() * 0.03,
                    y=d_df["organisationunitname"],
                    mode="text",
                    text=[
                        f"{int(v):+,} ({g:+.1f}%)"
                        for v, g in zip(d_df["Absolute_Variance"], d_df["Growth_%"])
                    ],
                    textposition="middle right",
                    textfont=dict(color=TEXT_DARK, size=10.5, weight="bold"),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

            _apply_pv_theme(fig_dumb, height=max(430, len(d_df) * 28), margin=dict(l=10, r=95, t=35, b=30))
            fig_dumb.update_xaxes(
                title=dict(text="Patient Attendance Volume", font=dict(color=TEXT_DARK, size=12, weight="bold")),
                range=[0, max_point.max() * 1.24],
            )
            fig_dumb.update_yaxes(tickfont=dict(color=TEXT_DARK, size=11.5))
            fig_dumb.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="left", x=0))
            st.plotly_chart(fig_dumb, use_container_width=True)
            render_chart_narrative(f"Site-by-Site Movement ({dumb_mode})", f"In this group of <b>{len(d_df)} sites</b>, <b>{int((d_df["Absolute_Variance"]>0).sum())} gained patients</b> (teal) and <b>{len(d_df)-int((d_df["Absolute_Variance"]>0).sum())} lost ground</b> (red), a net shift of <b>{int(d_df["Absolute_Variance"].sum()):+,} visits</b> vs. {comparison_year}.", "Switch to <b>Top 15 Droppers (-)</b> to flag sites for support visits this month, or <b>Top 15 Gainers (+)</b> to see what is working.", "#2563EB")

    with col_dist:
        st.markdown(f"#### 📦 Facility Cohort Distribution ({comparison_year} vs. {focus_year})")
        fig_box = go.Figure()
        fig_box.add_trace(
            go.Box(
                y=df["PV_2025"],
                name=f"{comparison_year} Baseline",
                boxpoints="all",
                jitter=0.35,
                pointpos=-1.6,
                marker=dict(color="#64748B", size=7, opacity=0.75),
                line=dict(color="#475569", width=2),
                fillcolor="rgba(148, 163, 184, 0.25)",
                text=df["organisationunitname"],
                hovertemplate=f"<b>%{{text}}</b><br>{comparison_year}: %{{y:,.0f}}<extra></extra>",
            )
        )
        fig_box.add_trace(
            go.Box(
                y=df["PV_2026"],
                name=f"{focus_year} Focus",
                boxpoints="all",
                jitter=0.35,
                pointpos=-1.6,
                marker=dict(color="#0D9488", size=7, opacity=0.82),
                line=dict(color="#0F2C59", width=2),
                fillcolor="rgba(13, 148, 136, 0.22)",
                text=df["organisationunitname"],
                hovertemplate=f"<b>%{{text}}</b><br>{focus_year}: %{{y:,.0f}}<extra></extra>",
            )
        )
        _apply_pv_theme(fig_box, height=495, margin=dict(l=20, r=20, t=35, b=30))
        fig_box.update_yaxes(
            title=dict(text="Attendance per Facility", font=dict(color=TEXT_DARK, size=12, weight="bold")),
        )
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
        q25_f, q75_f = float(df["PV_2026"].quantile(0.25)), float(df["PV_2026"].quantile(0.75))
        render_chart_narrative("Is Growth Network-Wide or Just a Few Big Sites?", f"Our typical (median) site rose from <b>{int(med_base):,}</b> to <b>{int(med_focus):,} visits</b> (<b>{med_delta:+,.0f} per site</b>), and the whole middle box moved up (<b>{int(q25_f):,}–{int(q75_f):,}</b>)—confirming broad clinic growth.", f"Check in on smaller clinics below <b>{int(q25_f):,} visits</b> to see if they need community mobilization support.", "#0D9488")

    st.markdown("---")

    export_df = pareto_df[["organisationunitname", "PV_2025", "PV_2026", "Absolute_Variance", "Growth_%", "Cum_Pct"]].copy()
    h1, h2 = st.columns([3, 1])
    h1.markdown(f"<div style=\"font-size:17px;font-weight:800;color:#0F172A;\">📋 Executive Facility Utilization Matrix ({comparison_year} vs. {focus_year})</div>", unsafe_allow_html=True)
    h2.download_button("⬇️ Download PV Matrix (CSV)", export_df.to_csv(index=False).encode("utf-8"), f"PV_Matrix_{focus_year}.csv", "text/csv", use_container_width=True)
    mx = max(1.0, float(export_df["PV_2026"].max()))
    rows = "".join([f"<tr style=\"background:{'#FFFFFF' if i%2==0 else '#F8FAFC'};border-bottom:1px solid #E2E8F0;\"><td style=\"padding:8px 12px;font-weight:600;color:#0F172A;\">{i+1}. {r['organisationunitname']}</td><td style=\"padding:8px 12px;text-align:right;color:#334155;\">{int(r['PV_2025']):,}</td><td style=\"padding:8px 12px;min-width:170px;\"><div style=\"display:flex;align-items:center;gap:8px;\"><div style=\"flex:1;background:#E2E8F0;height:8px;border-radius:999px;overflow:hidden;\"><div style=\"width:{min(100.0,float(r['PV_2026'])/mx*100):.1f}%;background:{'#0F2C59' if r['Cum_Pct']<=80 else '#64748B'};height:100%;\"></div></div><span style=\"font-weight:700;color:#0F172A;\">{int(r['PV_2026']):,}</span></div></td><td style=\"padding:8px 12px;text-align:right;font-weight:700;color:{'#166534' if r['Absolute_Variance']>0 else '#991B1B'};\">{int(r['Absolute_Variance']):+,}</td><td style=\"padding:8px 12px;text-align:right;font-weight:700;color:{'#166534' if r['Growth_%']>0 else '#991B1B'};\">{float(r['Growth_%']):+.2f}%</td><td style=\"padding:8px 12px;text-align:right;color:#334155;\">{float(r['Cum_Pct']):.1f}%</td></tr>" for i, r in export_df.iterrows()])
    st.markdown(f"<div style=\"max-height:440px;overflow-y:auto;border:1px solid #CBD5E1;border-radius:10px;background:#FFFFFF;\"><table style=\"width:100%;border-collapse:collapse;font-size:12.5px;\"><thead style=\"position:sticky;top:0;background:#0F2C59;color:#FFFFFF;\"><tr><th style=\"padding:10px 12px;text-align:left;\">Facility Name</th><th style=\"padding:10px 12px;text-align:right;\">{comparison_year} Baseline</th><th style=\"padding:10px 12px;text-align:left;\">{focus_year} Attendance</th><th style=\"padding:10px 12px;text-align:right;\">Net Shift</th><th style=\"padding:10px 12px;text-align:right;\">YoY Growth</th><th style=\"padding:10px 12px;text-align:right;\">Cum. Share</th></tr></thead><tbody>{rows}</tbody></table></div>", unsafe_allow_html=True)
