"""Second mining pass: more CFR parts, relaxed thresholds. Writes families_new.json (families not in v1)."""
import re, json, collections, datetime as dt, sys
sys.path.insert(0, "src/pilot")
from fr_explore import fetch
def norm(t):
    t = re.sub(r"\b(19|20)\d\d\b|\d+", "#", t.lower()); t = re.sub(r"[^a-z# ]", " ", t); return " ".join(t.split())
PARTS = [(12,1005),(12,1002),(12,1024),(12,1003),(12,1030),(12,1041),(12,226),(12,204),(12,217),(49,572),(49,573),(49,393),(40,63),(40,98),(40,80),(40,86),(40,52),(40,180),(40,141),(17,229),(17,230),(17,232),(17,242),(17,270),(42,405),(42,409),(42,418),(42,422),(42,424),(42,495),(42,438),(42,447),(42,457),(14,121),(14,25),(14,23),(14,119),(29,1926),(29,1915),(30,250),(33,165),(7,319),(7,205),(7,1),(9,94),(9,113),(10,429),(10,430),(21,101),(21,110),(21,117),(21,314),(26,31),(26,301),(24,3280),(24,5),(31,1010),(45,164),(45,170),(47,54),(47,64),(47,1),(16,1112),(15,774),(15,744),(19,10),(19,12),(8,274),(20,404),(5,2635),(5,1320)]
if __name__ == "__main__":
    old = json.load(open("data/pilot/families_raw.json"))
    fam = collections.defaultdict(list); seen = {d["document_number"] for v in old.values() for d in v}
    for tp in PARTS:
        try: rs = fetch(*tp, since="2010-01-01")
        except Exception as e: print("fail", tp, type(e).__name__); continue
        for d in rs:
            if d["document_number"] in seen or not d["effective_on"]: continue
            seen.add(d["document_number"]); fam[norm(d["title"])].append(d)
    new = {}
    for k, v in fam.items():
        if k in old: continue
        yrs = {d["publication_date"][:4] for d in v}
        lags = [(dt.date.fromisoformat(d["effective_on"]) - dt.date.fromisoformat(d["publication_date"])).days for d in v]
        if len(v) >= 4 and len(yrs) >= 3 and (sum(l >= 14 for l in lags) >= 2 or any(l <= -3 for l in lags)): new[k] = v
    print(len(fam), "families;", len(new), "new kept;", sum(len(v) for v in new.values()), "docs")
    json.dump(new, open("data/pilot/families_new.json", "w"))
