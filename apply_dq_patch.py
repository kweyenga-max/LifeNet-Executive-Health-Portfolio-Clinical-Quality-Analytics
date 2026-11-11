cat << "EOF" > apply_dq_patch.py
import json
import os

app_path = "app.py"

with open(app_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

start_idx = None
end_idx = None

for idx, line in enumerate(lines):
    if (
        'active_tab == "🚨 Data Quality Audits"' in line
        or 'active_tab == "\\U0001f6a8 Data Quality Audits"' in line
    ):
        start_idx = idx
    elif (
        'active_tab == "🔍 Facility Inspector"' in line
        or 'active_tab == "\\U0001f50d Facility Inspector"' in line
    ):
        end_idx = idx

if start_idx is not None and end_idx is not None:
    tab_code = """elif active_tab == "🚨 Data Quality Audits":
    import json
    import os

    st.markdown("<h2 style='color:#0F172A; font-weight:800;'>🚨 KHIS Data Quality & Field Verification Workspace</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B;'>Real-time anomaly tracking, Program Officer field findings, and Sub-County M&E escalation management.</p>", unsafe_allow_html=True)

    if kpi_issues.empty:
        st.success("🎉 No data quality issues flagged across reporting periods!")
    else:
        COMMENTS_FILE = "data/data_quality_comments.json"
        os.makedirs("data", exist_ok=True)
        if os.path.exists(COMMENTS_FILE):
            try:
                with open(COMMENTS_FILE, "r", encoding="utf-8") as cf:
                    comments_db = json.load(cf)
            except Exception:
                comments_db = {}
        else:
            comments_db = {}

        df_issues = kpi_issues.copy()

        df_issues["Record_ID"] = df_issues.apply(
            lambda r: f"{r.get('Year','')}_{r.get('Month','')}_{r.get('Facility','')}_{r.get('Issue Category','')}", axis=1
        )

        df_issues["Status"] = df_issues["Record_ID"].map(lambda x: comments_db.get(x, {}).get("status", "🔴 Unverified"))
        df_issues["PO_Notes"] = df_issues["Record_ID"].map(lambda x: comments_db.get(x, {}).get("notes", "--"))
        df_issues["Updated_By"] = df_issues["Record_ID"].map(lambda x: comments_db.get(x, {}).get("updated_by", "--"))

        st.markdown("#### 🔍 Filter & Audit Controls")
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)

        with col_f1:
            all_facs = ["All Facilities"] + sorted(df_issues["Facility"].dropna().unique().tolist())
            sel_fac = st.selectbox("🏥 Filter Facility", all_facs)

        with col_f2:
            all_years = ["All Years"] + sorted([str(y) for y in df_issues["Year"].dropna().unique().tolist()])
            sel_year = st.selectbox("📅 Filter Year", all_years)

        with col_f3:
            all_cats = ["All Categories"] + sorted(df_issues["Issue Category"].dropna().unique().tolist())
            sel_cat = st.selectbox("🏷️ Issue Category", all_cats)

        with col_f4:
            all_statuses = ["All Statuses", "🔴 Unverified", "🟡 Under Sub-County Review", "🟢 KHIS Corrected"]
            sel_status = st.selectbox("📌 Resolution Status", all_statuses)

        filtered_df = df_issues.copy()
        if sel_fac != "All Facilities":
            filtered_df = filtered_df[filtered_df["Facility"] == sel_fac]
        if sel_year != "All Years":
            filtered_df = filtered_df[filtered_df["Year"].astype(str) == sel_year]
        if sel_cat != "All Categories":
            filtered_df = filtered_df[filtered_df["Issue Category"] == sel_cat]
        if sel_status != "All Statuses":
            filtered_df = filtered_df[filtered_df["Status"] == sel_status]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🚨 Flagged Anomalies", len(filtered_df))
        m2.metric("🔴 Pending Field Review", len(filtered_df[filtered_df["Status"] == "🔴 Unverified"]))
        m3.metric("🟡 In Sub-County Review", len(filtered_df[filtered_df["Status"] == "🟡 Under Sub-County Review"]))
        m4.metric("🟢 KHIS Corrected", len(filtered_df[filtered_df["Status"] == "🟢 KHIS Corrected"]))

        st.markdown("---")

        st.markdown("### 📋 Anomaly Audit Log")
        display_cols = [c for c in ["Year", "Month", "Facility", "Issue Category", "Description", "Status", "PO_Notes", "Updated_By"] if c in filtered_df.columns]
        st.dataframe(filtered_df[display_cols], hide_index=True, use_container_width=True)

        st.markdown("---")

        st.markdown("### ✍️ Program Officer Field Action & Comment Engine")
        st.info("💡 Program Officers can select an anomaly below, add field verification findings, and flag for Sub-County KHIS correction.")

        if not filtered_df.empty:
            record_options = filtered_df["Record_ID"].tolist()
            selected_rec_id = st.selectbox(
                "Target Anomaly Record for Action:", 
                record_options,
                format_func=lambda x: f"{x.split('_')[2]} | {x.split('_')[1]} {x.split('_')[0]} — {x.split('_')[3]}"
            )

            rec_row = filtered_df[filtered_df["Record_ID"] == selected_rec_id].iloc[0]

            with st.form("field_comment_form", clear_on_submit=False):
                c_a1, c_a2 = st.columns(2)
                with c_a1:
                    st.write(f"**Facility:** {rec_row.get('Facility','')}")
                    st.write(f"**Period:** {rec_row.get('Month','')} {rec_row.get('Year','')}")
                    st.write(f"**Anomaly Description:** {rec_row.get('Description','')}")

                with c_a2:
                    current_status = rec_row.get("Status", "🔴 Unverified")
                    status_options = ["🔴 Unverified", "🟡 Under Sub-County Review", "🟢 KHIS Corrected"]
                    status_idx = status_options.index(current_status) if current_status in status_options else 0
                    new_status = st.selectbox("Update Anomaly Status:", status_options, index=status_idx)
                    officer_name = st.text_input("Program Officer Name / Role:", value=rec_row.get("Updated_By", "") if rec_row.get("Updated_By") != "--" else "")

                po_notes_input = st.text_area(
                    "Field Verification Findings & Sub-County Action Notes:",
                    value=rec_row.get("PO_Notes", "") if rec_row.get("PO_Notes") != "--" else "",
                    placeholder="Enter register check details, cause of entry discrepancy, or sub-county follow-up status..."
                )

                submit_btn = st.form_submit_button("💾 Save Field Audit Record")

                if submit_btn:
                    comments_db[selected_rec_id] = {
                        "status": new_status,
                        "notes": po_notes_input if po_notes_input.strip() else "--",
                        "updated_by": officer_name if officer_name.strip() else "Program Officer"
                    }
                    with open(COMMENTS_FILE, "w", encoding="utf-8") as cf:
                        json.dump(comments_db, cf, indent=4)
                    st.success("✅ Verification record saved successfully!")
                    st.rerun()

            with st.expander("📤 Generate Sub-County KHIS Correction Brief"):
                st.markdown("**Draft brief for Sub-County Health Records Officer (SCHRIO):**")
                brief_text = f\"\"\"SUB-COUNTY KHIS DATA CORRECTION BRIEF
----------------------------------------------------
Facility: {rec_row.get('Facility','')}
Reporting Period: {rec_row.get('Month','')} {rec_row.get('Year','')}
Issue Category: {rec_row.get('Issue Category','')}

KHIS Anomaly Flag:
{rec_row.get('Description','')}

Program Officer Field Audit Findings:
{po_notes_input if po_notes_input.strip() else 'Awaiting field visit verification notes.'}

Resolution Status: {new_status}
Logged By: {officer_name if officer_name.strip() else 'M&E Team'}
----------------------------------------------------\"\"\"
                st.code(brief_text, language="markdown")
"""

    new_lines = [line + "\n" for line in tab_code.split("\n")]
    updated_lines = lines[:start_idx] + new_lines + lines[end_idx:]

    with open(app_path, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print("✅ Successfully updated Tab 4 in app.py!")
else:
    print(f"⚠️ Block targets not found: start_idx={start_idx}, end_idx={end_idx}")
EOF
