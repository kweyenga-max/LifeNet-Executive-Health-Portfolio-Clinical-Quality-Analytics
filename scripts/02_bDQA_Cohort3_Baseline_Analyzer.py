import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import openpyxl

# Set executive visual styling
sns.set_theme(style="whitegrid")
plt.rcParams.update(
    {
        "font.size": 11,
        "font.family": "sans-serif",
        "figure.titlesize": 14,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    }
)

# 1. Reconciled Data Extraction (Q4 2025 Baseline Across 13 Facilities)
indicators = [
    "Total OPD",
    "Inpatient Admissions",
    "Total Deliveries",
    "Live Births",
    "1st ANC Visits",
    "4th ANC Visits",
    "PNC 24HRS",
]
tier1_reg = [4508, 568, 507, 504, 270, 275, 325]
tier2_sum = [13755, 915, 497, 498, 289, 296, 431]
tier3_khis = [19563, 938, 512, 508, 294, 301, 439]

# -------------------------------------------------------------
# Figure 1: Tri-Platform Data Volume Reconciliation (Log Scale)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(indicators))
width = 0.25

rects1 = ax.bar(
    x - width, tier1_reg, width, label="Tier 1: Primary Register", color="#102C57"
)
rects2 = ax.bar(
    x, tier2_sum, width, label="Tier 2: Summary Sheet Tally", color="#0096C7"
)
rects3 = ax.bar(
    x + width, tier3_khis, width, label="Tier 3: KHIS System Online", color="#D90429"
)

ax.set_ylabel("Recorded Volume / Patient Count (Log Scale)")
ax.set_title("Figure 1: Tri-Platform Data Volume Reconciliation (Q4 2025 Baseline)")
ax.set_xticks(x)
ax.set_xticklabels(indicators, rotation=25, ha="right")
ax.set_yscale("log")
ax.legend()


def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(
            f"{int(height):,}",
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            rotation=90,
        )


autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

plt.tight_layout()
plt.savefig("01_bDQA_Cohort3_Baseline_Platform_Reconciliation.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# Figure 2: Facility Tally & Upload Accuracy Rates
# -------------------------------------------------------------
facilities = [
    "Friends Kaptama",
    "Mundoli HF",
    "Chimoi HF",
    "Kolanya SA",
    "Lwanga HF",
    "Buyangu HF",
    "St Pius Musoli",
    "Ingotse Disp",
    "Khasoko HF",
    "Eregi Mission",
    "Namboboto Disp",
    "Namasoli HF",
    "Mission of Mercy",
]
match_rates = [
    98.5,
    91.0,
    91.6,
    94.2,
    98.9,
    85.2,
    73.9,
    62.4,
    45.0,
    62.2,
    55.4,
    40.2,
    19.2,
]

fig, ax = plt.subplots(figsize=(10, 6))
colors = [
    "#28A745" if m >= 90 else "#FFC107" if m >= 70 else "#D90429" for m in match_rates
]

bars = ax.barh(facilities, match_rates, color=colors)
ax.set_xlabel("Tier 2 (Summary) to Tier 3 (KHIS) Data Concordance Rate (%)")
ax.set_title(
    "Figure 2: Data Accuracy & Reporting Completeness Rates Across 13 Health Facilities"
)
ax.set_xlim(0, 110)
ax.axvline(
    90, color="#102C57", linestyle="--", label="90% Target Concordance Threshold"
)

for bar in bars:
    w = bar.get_width()
    ax.annotate(
        f"{w:.1f}%",
        xy=(w, bar.get_y() + bar.get_height() / 2),
        xytext=(5, 0),
        textcoords="offset points",
        ha="left",
        va="center",
        fontsize=9,
        fontweight="bold",
    )

ax.legend(loc="lower right")
plt.tight_layout()
plt.savefig("02_bDQA_Cohort3_Baseline_Facility_Accuracy.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# Figure 3: Baseline Maternal Continuum of Care Reporting Gaps
# -------------------------------------------------------------
continuum_stages = [
    "1st ANC Visit",
    "1st Trimester ANC",
    "4th ANC Visit",
    "8th ANC Visit",
    "PNC 24HRS",
    "PNC 6 Weeks",
    "PNC 6 Months",
]
p_reg = [270, 48, 275, 14, 325, 352, 172]
s_khis = [294, 62, 301, 45, 439, 512, 496]

fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(continuum_stages))

ax.plot(
    x,
    p_reg,
    marker="o",
    linewidth=2.5,
    label="Tier 1: Primary Register",
    color="#102C57",
)
ax.plot(
    x,
    s_khis,
    marker="s",
    linewidth=2.5,
    linestyle="--",
    label="Tier 3: KHIS Online System",
    color="#D90429",
)

ax.set_ylabel("Number of Patients Recorded")
ax.set_title(
    "Figure 3: Baseline Maternal Continuum of Care Reporting Gaps (ANC to PNC)"
)
ax.set_xticks(x)
ax.set_xticklabels(continuum_stages, rotation=20, ha="right")
ax.legend()

for i, txt in enumerate(p_reg):
    ax.annotate(
        str(txt),
        (x[i], p_reg[i]),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
        fontsize=9,
        fontweight="bold",
        color="#102C57",
    )

for i, txt in enumerate(s_khis):
    ax.annotate(
        str(txt),
        (x[i], s_khis[i]),
        textcoords="offset points",
        xytext=(0, -15),
        ha="center",
        fontsize=9,
        fontweight="bold",
        color="#D90429",
    )

plt.tight_layout()
plt.savefig("03_bDQA_Cohort3_Baseline_Maternal_Continuum.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# Figure 4: Maternity & Newborn Care Cascade
# -------------------------------------------------------------
cascade_stages = [
    "Deliveries",
    "Live Births",
    "Initiated BF <1hr",
    "Low Birth Weight (<2.5kg)",
]
c_reg = [507, 504, 368, 12]
c_khis = [512, 508, 482, 38]

fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(cascade_stages))
width = 0.35

rects1 = ax.bar(
    x - width / 2, c_reg, width, label="Tier 1: Primary Register", color="#0096C7"
)
rects2 = ax.bar(
    x + width / 2, c_khis, width, label="Tier 3: KHIS System", color="#102C57"
)

ax.set_ylabel("Number of Cases")
ax.set_title(
    "Figure 4: Maternity & Newborn Care Cascade (Deliveries -> Live Births -> Early BF)"
)
ax.set_xticks(x)
ax.set_xticklabels(cascade_stages)
ax.legend()

autolabel(rects1)
autolabel(rects2)

plt.tight_layout()
plt.savefig("04_bDQA_Cohort3_Baseline_Clinical_Cascade.png", dpi=300)
plt.close()

print("All 4 charts generated and exported successfully!")
