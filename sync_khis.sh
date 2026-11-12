#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi
python -c 'from scripts.khis_adapter import get_live_pv_and_kpi_frames; df_pv, df_kpi = get_live_pv_and_kpi_frames(force_live=True); print("Synced PV rows:", len(df_pv), "| Periods:", sorted(df_pv["Period"].unique()) if not df_pv.empty else []); print("Synced KPI shape:", df_kpi.shape)'
if git diff --quiet data/khis_pv_snapshot.csv.gz data/khis_kpi_snapshot.csv.gz; then
  echo "No new KHIS changes to push."
else
  git add data/khis_pv_snapshot.csv.gz data/khis_kpi_snapshot.csv.gz
  git commit -m "Refresh KHIS analytics snapshot ($(date +%Y-%m-%d))"
  git push origin main
fi
