import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the verified comparison report
df = pd.read_excel("PV_Q3_2025_vs_2026_Comparison.xlsx")

# Extract Start Total (Q3 2025) and End Total (Q3 2026)
start_total = df[df['organisationunitname'] == 'TOTAL / OVERALL PV']['Q3_2025'].values[0]
end_total = df[df['organisationunitname'] == 'TOTAL / OVERALL PV']['Q3_2026'].values[0]

# Filter out the total row for facility-level breakdowns
facility_df = df[df['organisationunitname'] != 'TOTAL / OVERALL PV'].copy()

# Sort by Absolute_Variance descending
facility_df = facility_df.sort_values(by='Absolute_Variance', ascending=False)

# Top 5 positive drivers
top_gainers = facility_df.head(5)[['organisationunitname', 'Absolute_Variance']]

# Specific data anomaly (Mwatate Healthcare Centre)
mwatate_val = facility_df[facility_df['organisationunitname'].str.contains('Mwatate', case=False, na=False)]['Absolute_Variance'].values[0]

# Group remaining facilities into "Other Net Changes"
tracked_names = list(top_gainers['organisationunitname']) + ['Mwatate Healthcare Centre']
remaining_df = facility_df[~facility_df['organisationunitname'].str.contains('Mwatate', case=False, na=False)]
remaining_df = remaining_df[~remaining_df['organisationunitname'].isin(top_gainers['organisationunitname'])]
other_net_val = remaining_df['Absolute_Variance'].sum()

# Construct Waterfall Data Structure
categories = ['Q3 2025 Total'] + list(top_gainers['organisationunitname']) + ['Mwatate (Missing Data)', 'Other Net Changes', 'Q3 2026 Total']
changes = [start_total] + list(top_gainers['Absolute_Variance']) + [mwatate_val, other_net_val, end_total]

# Shorten category names for clean display on plot
short_labels = [
    'Q3 2025 Total',
    'Mary Immaculate',
    'Butula Mission',
    'Mt Kenya (ACK)',
    'Mission of Mercy',
    'Kimende Orthodox',
    'Mwatate Gap',
    'Other Net Changes',
    'Q3 2026 Total'
]

# Calculate bottom baselines for waterfall blocks
bottoms = [0] * len(changes)
current_total = start_total

for i in range(1, len(changes) - 1):
    if changes[i] >= 0:
        bottoms[i] = current_total
        current_total += changes[i]
    else:
        current_total += changes[i]
        bottoms[i] = current_total

# Set up canvas
fig, ax = plt.subplots(figsize=(12, 7))

# Define colors (Blue for totals, Green for gains, Red for drops)
colors = []
for i, val in enumerate(changes):
    if i == 0 or i == len(changes) - 1:
        colors.append('#1f77b4')  # Navy/Blue for Totals
    elif val >= 0:
        colors.append('#2ca02c')  # Green for positive drivers
    else:
        colors.append('#d62728')  # Red for negative drivers

# Plot bars
bars = ax.bar(short_labels, changes, bottom=bottoms, color=colors, edgecolor='black', width=0.55)

# Add value labels above/below bars
for i, (bar, val) in enumerate(zip(bars, changes)):
    if i == 0 or i == len(changes) - 1:
        y_pos = val + 2000
        label_str = f"{int(val):,}"
    else:
        if val >= 0:
            y_pos = bottoms[i] + val + 1500
            label_str = f"+{int(val):,}"
        else:
            y_pos = bottoms[i] - 3500
            label_str = f"{int(val):,}"
            
    ax.text(bar.get_x() + bar.get_width() / 2, y_pos, label_str,
            ha='center', va='bottom', fontsize=9, fontweight='bold')

# Styling and Labels
plt.title("Patient Volume (PV) Waterfall: Q3 2025 vs Q3 2026 (+11.62% Growth)", fontsize=14, fontweight='bold', pad=20)
plt.ylabel("Patient Volume (Visits)", fontsize=11, fontweight='bold')
plt.xticks(rotation=25, ha='right', fontsize=10)
plt.ylim(0, 220000)
plt.grid(axis='y', linestyle='--', alpha=0.5)

# Save chart image and show
plt.tight_layout()
output_chart = "PV_Q3_Waterfall_Chart.png"
plt.savefig(output_chart, dpi=300)
print(f"✅ Waterfall chart saved successfully as '{output_chart}'")
plt.show()