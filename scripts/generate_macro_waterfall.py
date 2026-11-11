import pandas as pd
import matplotlib.pyplot as plt

# 1. Load verified comparison report
df = pd.read_excel("PV_Q3_2025_vs_2026_Comparison.xlsx")

# 2. Extract Start and End Totals
start_total = df[df['organisationunitname'] == 'TOTAL / OVERALL PV']['Q3_2025'].values[0]
end_total = df[df['organisationunitname'] == 'TOTAL / OVERALL PV']['Q3_2026'].values[0]

# 3. Separate facility-level data to sum overall Gains vs Declines
facility_df = df[df['organisationunitname'] != 'TOTAL / OVERALL PV'].copy()

total_gains = facility_df[facility_df['Absolute_Variance'] > 0]['Absolute_Variance'].sum()
total_declines = facility_df[facility_df['Absolute_Variance'] < 0]['Absolute_Variance'].sum()

# 4. Construct Macro Waterfall Structure
categories = ['Q3 2025 Total PV', 'Total Volume Gains', 'Total Volume Declines', 'Q3 2026 Total PV']
changes = [start_total, total_gains, total_declines, end_total]

# Compute bottom baselines for waterfall bars
bottoms = [
    0,                                  # Q3 2025 Start
    start_total,                        # Gains start on top of 2025 baseline
    start_total + total_gains + total_declines, # Declines sit at peak before dropping
    0                                   # Q3 2026 End
]

# Adjust decline bottom position so bar hangs downward correctly
bottoms[2] = start_total + total_gains + total_declines

# 5. Render Plot
fig, ax = plt.subplots(figsize=(10, 6))

colors = ['#1f77b4', '#2ca02c', '#d62728', '#1f77b4'] # Blue, Green, Red, Blue

bars = ax.bar(categories, changes, bottom=bottoms, color=colors, edgecolor='black', width=0.45)

# Add numerical values above/below each bar
for i, (bar, val) in enumerate(zip(bars, changes)):
    if i == 0 or i == len(changes) - 1:
        y_pos = val + 3000
        label_str = f"{int(val):,}"
    elif val >= 0:
        y_pos = bottoms[i] + val + 3000
        label_str = f"+{int(val):,}"
    else:
        y_pos = bottoms[i] - 7000
        label_str = f"{int(val):,}"
            
    ax.text(bar.get_x() + bar.get_width() / 2, y_pos, label_str,
            ha='center', va='bottom', fontsize=11, fontweight='bold')

# 6. Styling
plt.title("Overall Patient Volume (PV) Movement: Q3 2025 to Q3 2026", fontsize=14, fontweight='bold', pad=20)
plt.ylabel("Total Patient Volume (Visits)", fontsize=11, fontweight='bold')
plt.ylim(0, 240000)
plt.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
output_chart = "PV_Q3_Macro_Waterfall_Chart.png"
plt.savefig(output_chart, dpi=300)
print(f"✅ Macro Waterfall chart saved as '{output_chart}'")
plt.show()