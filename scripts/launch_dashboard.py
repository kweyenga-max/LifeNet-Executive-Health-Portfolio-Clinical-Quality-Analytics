import os
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

# 1. Load Data
excel_file = "PV_Q3_2025_vs_2026_Comparison.xlsx"
if not os.path.exists(excel_file):
    print(f"❌ Error: Could not find '{excel_file}' in the current folder.")
    sys.exit(1)

df = pd.read_excel(excel_file, engine="openpyxl")
total_row = df[df['organisationunitname'] == 'TOTAL / OVERALL PV'].iloc[0]
facility_df = df[df['organisationunitname'] != 'TOTAL / OVERALL PV'].copy()

# 2. Compute Waterfall Values
gains = facility_df[facility_df['Absolute_Variance'] > 0]['Absolute_Variance'].sum()
declines = facility_df[facility_df['Absolute_Variance'] < 0]['Absolute_Variance'].sum()

# 3. Create Plots
fig_wf = go.Figure(go.Waterfall(
    name="PV Movement",
    orientation="v",
    measure=["absolute", "relative", "relative", "total"],
    x=["Q3 2025 Total", "Total Gains", "Total Declines", "Q3 2026 Total"],
    text=[f"{int(total_row['Q3_2025']):,}", f"+{int(gains):,}", f"{int(declines):,}", f"{int(total_row['Q3_2026']):,}"],
    textposition="outside",
    y=[total_row['Q3_2025'], gains, declines, total_row['Q3_2026']],
    decreasing={"marker": {"color": "#d62728"}},
    increasing={"marker": {"color": "#2ca02c"}},
    totals={"marker": {"color": "#1f77b4"}}
))
fig_wf.update_layout(title="<b>Macro Volume Movement</b>", height=400, margin=dict(l=20, r=20, t=40, b=20))

top10 = facility_df.sort_values(by='Q3_2026', ascending=True).tail(10)
fig_bar = go.Figure(go.Bar(
    x=top10['Q3_2026'],
    y=top10['organisationunitname'],
    orientation='h',
    text=top10['Q3_2026'].apply(lambda x: f"{int(x):,}"),
    textposition='auto',
    marker_color='#1f77b4'
))
fig_bar.update_layout(title="<b>Top 10 Facilities (Q3 2026 Volume)</b>", height=400, margin=dict(l=20, r=20, t=40, b=20))

wf_html = fig_wf.to_html(full_html=False, include_plotlyjs='cdn')
bar_html = fig_bar.to_html(full_html=False, include_plotlyjs=False)

# 4. Generate Data Table HTML
table_rows = ""
for _, row in facility_df.iterrows():
    var_color = "green" if row['Absolute_Variance'] >= 0 else "red"
    var_prefix = "+" if row['Absolute_Variance'] > 0 else ""
    table_rows += f"""
    <tr>
        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{row['organisationunitname']}</td>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{int(row['Q3_2025']):,}</td>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{int(row['Q3_2026']):,}</td>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right; color: {var_color}; font-weight: bold;">{var_prefix}{int(row['Absolute_Variance']):,}</td>
        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right; color: {var_color}; font-weight: bold;">{row['Growth_%']:.2f}%</td>
    </tr>
    """

# 5. Full HTML Template
full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Health Facility PV Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 30px; background-color: #f8f9fa; color: #333; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .metrics-container {{ display: flex; justify-content: space-between; margin-bottom: 30px; gap: 15px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; text-align: center; }}
        .card-title {{ font-size: 14px; color: #666; text-transform: uppercase; margin-bottom: 10px; }}
        .card-value {{ font-size: 26px; font-weight: bold; color: #1f77b4; }}
        .grid {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .col {{ flex: 1; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th {{ background: #1f77b4; color: white; padding: 12px; text-align: left; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 Health Facility Patient Volume Dashboard</h1>
        <h3>Q3 2025 vs. Q3 2026 Performance Analysis</h3>
    </div>

    <div class="metrics-container">
        <div class="card"><div class="card-title">Q3 2025 Total PV</div><div class="card-value">{int(total_row['Q3_2025']):,}</div></div>
        <div class="card"><div class="card-title">Q3 2026 Total PV</div><div class="card-value">{int(total_row['Q3_2026']):,}</div></div>
        <div class="card"><div class="card-title">Absolute Variance</div><div class="card-value" style="color: #2ca02c;">+{int(total_row['Absolute_Variance']):,}</div></div>
        <div class="card"><div class="card-title">Overall Growth Rate</div><div class="card-value" style="color: #2ca02c;">{total_row['Growth_%']:.2f}%</div></div>
    </div>

    <div class="grid">
        <div class="col">{wf_html}</div>
        <div class="col">{bar_html}</div>
    </div>

    <h2>🔍 Facility Performance Inspector</h2>
    <table>
        <thead>
            <tr>
                <th>Facility Name</th>
                <th style="text-align: right;">Q3 2025 PV</th>
                <th style="text-align: right;">Q3 2026 PV</th>
                <th style="text-align: right;">Variance</th>
                <th style="text-align: right;">Growth Rate (%)</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
</body>
</html>
"""

# Save standalone HTML page
output_html = "dashboard.html"
with open(output_html, "w", encoding="utf-8") as f:
    f.write(full_html)

# 6. Serve and Launch Browser
PORT = 8080
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass

server = HTTPServer(('127.0.0.1', PORT), QuietHandler)
thread = threading.Thread(target=server.serve_forever)
thread.daemon = True
thread.start()

print(f"✅ Interactive Dashboard generated successfully!")
print(f"🚀 Opening dashboard in browser at http://127.0.0.1:{PORT}/dashboard.html")

webbrowser.open(f"http://127.0.0.1:{PORT}/dashboard.html")

input("\n📌 Dashboard is live! Press Enter in this terminal to stop the local server...")
server.shutdown()