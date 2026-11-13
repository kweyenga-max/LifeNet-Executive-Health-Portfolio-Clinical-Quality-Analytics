#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi
python -c '
from scripts.khis_adapter import get_live_pv_and_kpi_frames
from scripts.monitrac_adapter import sync_monitrac_finance, sync_monitrac_pss

df_pv, df_kpi = get_live_pv_and_kpi_frames(force_live=True)
print("Synced KHIS PV rows:", len(df_pv), "| Periods:", sorted(df_pv["Period"].unique()) if not df_pv.empty else [])
print("Synced KHIS KPI shape:", df_kpi.shape)

df_fin = sync_monitrac_finance(force_live=True)
print("Synced MoniTrac Finance facilities:", len(df_fin), "| Columns:", list(df_fin.columns))

df_pss = sync_monitrac_pss(force_live=True)
print("Synced MoniTrac PSS rows (Past 12M):", len(df_pss), "| Facilities:", df_pss["organisationunitname"].nunique() if not df_pss.empty else 0)
'
if git diff --quiet data/khis_pv_snapshot.csv.gz data/khis_kpi_snapshot.csv.gz data/monitrac_finance_snapshot.csv.gz data/monitrac_pss_snapshot.csv.gz; then
  echo "No new KHIS or MoniTrac changes to push."
else
  git add data/khis_pv_snapshot.csv.gz data/khis_kpi_snapshot.csv.gz data/monitrac_finance_snapshot.csv.gz data/monitrac_pss_snapshot.csv.gz
  git commit -m "Refresh KHIS and MoniTrac analytics snapshots ($(date +%Y-%m-%d))"
  git push origin main
fi
