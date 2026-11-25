"""Mine recurring rule families (same normalized title) with real publication/effective gaps."""
import re, json, collections, datetime as dt, sys
sys.path.insert(0, "src/pilot")
from fr_explore import fetch
PARTS = [(12,1026),(49,571),(40,60),(17,240),(42,414),(14,91),(29,1910),(26,1),(42,423),(42,412),(42,413),(24,982),(10,431),(7,205)]
def norm(t):
    t = re.sub(r"\b(19|20)\d\d\b|\d+","#",t.lower()); t = re.sub(r"[^a-z# ]"," ",t)
    return " ".join(t.split())
fam = collections.defaultdict(list); seen=set()
for tp in PARTS:
    try: rs = fetch(*tp, since="2010-01-01")
    except Exception as e: print("fail",tp,e); continue
    for d in rs:
        if d["document_number"] in seen or not d["effective_on"]: continue
        seen.add(d["document_number"]); fam[norm(d["title"])].append(d)
keep = {}
for k,v in fam.items():
    yrs = {d["publication_date"][:4] for d in v}
    lags = [(dt.date.fromisoformat(d["effective_on"])-dt.date.fromisoformat(d["publication_date"])).days for d in v]
    if len(v)>=4 and len(yrs)>=3 and sum(l>=14 for l in lags)>=2:
        keep[k] = v
print(len(fam),"families;",len(keep),"kept")
for k,v in sorted(keep.items(), key=lambda x:-len(x[1]))[:25]:
    lags=[(dt.date.fromisoformat(d["effective_on"])-dt.date.fromisoformat(d["publication_date"])).days for d in v]
    print(len(v), min(lags), max(lags), "|", k[:90])
json.dump(keep, open("data/pilot/families_raw.json","w"))
