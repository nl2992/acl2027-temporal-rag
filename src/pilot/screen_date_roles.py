"""Screen for rules whose effective_on is really an end date: every mention of it in DATES follows 'through'/'until'
(within 60 characters) and an earlier date is also stated. A screen, not an audit. Run from the repo root."""
import os, sys, re, json
os.environ["VALID_TO"] = "2"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import C, cases, eff, find_dates
hit = []
for i, d in C.items():
    t = " ".join((d.get("dates_text") or "").split()); ds = find_dates(t); e = eff(i)
    pos = [p for p, x, _ in ds if x == e]
    if pos and all(re.search(r"\b(through|until)\b.{0,60}$", t[:p], re.I) for p in pos) and any(x < e for _, x, _ in ds): hit.append(i)
split = json.load(open("annotation/split_v5.json"))
fam = {C[i]["family"] for i in hit if split.get(C[i]["family"]) == "test5"}
n = sum(split.get(c["family"]) == "test5" and c["family"] in fam for c in cases)
print(f"rules flagged {len(hit)} of {len(C)}; in test5 {sum(split.get(C[i]['family']) == 'test5' for i in hit)} rules, {len(fam)} families, {n} cases in those families")
for i in sorted(hit): print(i, C[i]["effective_on"], " ".join(C[i]["dates_text"].split())[:150])
