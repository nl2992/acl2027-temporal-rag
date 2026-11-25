"""Fresh confirmatory family batch (test3): CFR titles not used in v1/v2 mining, same relaxed thresholds and normalizer.
Written before any result on these families is seen; the frozen config (lambda=2, delta=1.5, router v2) is applied afterwards."""
import json, collections, datetime as dt, sys, urllib.parse, urllib.request
sys.path.insert(0, "src/pilot")
from fr_families_v2 import norm
B = "https://www.federalregister.gov/api/v1/documents.json"
F = ["document_number","title","publication_date","effective_on","corrections","correction_of","cfr_references","html_url"]
TITLES = [50, 33, 46, 47, 7, 9, 10, 15, 21, 24, 31, 45, 13, 16, 19, 20, 22, 23, 28, 30, 34, 36, 37, 38, 41, 43, 44, 48]
old = json.load(open("data/pilot/families_all.json")); seen = {d["document_number"] for v in old.values() for d in v}
fam = collections.defaultdict(list)
for t in TITLES:
    for page in range(1, 6):
        q = [("conditions[type][]","RULE"),("conditions[cfr][title]",t),("conditions[publication_date][gte]","2012-01-01"),("conditions[publication_date][lte]","2026-10-31"),("per_page","1000"),("page",page),("order","oldest")] + [("fields[]", f) for f in F]
        try: r = json.load(urllib.request.urlopen(B + "?" + urllib.parse.urlencode(q), timeout=90))
        except Exception as e: print("fail", t, page, type(e).__name__); break
        for d in r.get("results", []):
            if d["document_number"] in seen or not d["effective_on"]: continue
            seen.add(d["document_number"]); fam[norm(d["title"])].append(d)
        if page >= r.get("total_pages", 1): break
new = {}
for k, v in fam.items():
    if k in old: continue
    yrs = {d["publication_date"][:4] for d in v}
    lags = [(dt.date.fromisoformat(d["effective_on"]) - dt.date.fromisoformat(d["publication_date"])).days for d in v]
    if len(v) >= 4 and len(yrs) >= 3 and (sum(l >= 14 for l in lags) >= 2 or any(l <= -3 for l in lags)): new[k] = v
print(len(fam), "families seen;", len(new), "kept;", sum(len(v) for v in new.values()), "docs")
json.dump(new, open("data/pilot/families_v3.json", "w")); json.dump({k: "test3" for k in new}, open("annotation/split_v3.json", "w"), indent=1)
