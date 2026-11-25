#!/usr/bin/env bash
# Reproduce the exploratory two-clock pilot from scratch (network needed once for the Federal Register API; CPU only, stdlib only).
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 -I tests/test_pilot.py
python3 -I src/pilot/fr_families.py          # v1 families  -> data/pilot/families_raw.json
python3 -I src/pilot/fr_families_v2.py       # v2 families  -> data/pilot/families_new.json
python3 - <<'PY'                              # merge
import json
o = json.load(open("data/pilot/families_raw.json")); o.update(json.load(open("data/pilot/families_new.json")))
json.dump(o, open("data/pilot/families_all.json", "w"))
PY
python3 -I src/pilot/build_pilot.py          # corpus + cases
python3 -I src/pilot/verify_dates.py         # effective_on vs DATES text
python3 -I src/pilot/method_v1.py > data/pilot/method_v1_output.txt
python3 -I src/pilot/qtie_style.py > data/pilot/qtie_style_output.txt
python3 -I src/pilot/eval_natural.py draft_query_1   # uses the existing annotation sheet; draft_queries.py is NOT rerun here (it would overwrite sheets given to annotators)
