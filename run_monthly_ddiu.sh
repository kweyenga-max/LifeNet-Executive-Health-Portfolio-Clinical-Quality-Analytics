#!/usr/bin/env bash
set -euo pipefail
cd /Users/kelvinobiweyenga/Documents/Python_Projects
mkdir -p reports
echo "=== DDIU Run Started: $(date) ==="
./sync_khis.sh
.venv/bin/python -m scripts.send_ddiu_email
echo "=== DDIU Run Completed: $(date) ==="
