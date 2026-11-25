"""Collect Federal Register correction notices (document_number 'C1-...' with correction_of) and their originals for the same CFR parts."""
import json, re, sys, urllib.request, urllib.parse, collections
sys.path.insert(0, "src/pilot")
src = open("src/pilot/fr_families_v2.py").read(); m = re.search(r"PARTS = (\[.*?\])\n", src, re.S)
PARTS = eval(m.group(1)) + [(12,1026),(49,571),(40,60),(17,240),(42,414),(14,91),(29,1910),(26,1),(42,412),(42,413),(42,423)]
B = "https://www.federalregister.gov/api/v1/documents"
F = ["document_number","title","publication_date","effective_on","correction_of","abstract","dates"]
def get(url, retries=2):
    for k in range(retries + 1):
        try: return json.load(urllib.request.urlopen(url, timeout=60))
        except Exception: pass
    return {}
out = {}
for t, p in PARTS:
    page = 1
    while True:
        q = [("conditions[type][]","RULE"),("conditions[cfr][title]",t),("conditions[cfr][part]",p),("conditions[correction]","1"),("conditions[publication_date][gte]","2010-01-01"),("per_page","200"),("page",page)] + [("fields[]", f) for f in F]
        r = get(B + ".json?" + urllib.parse.urlencode(q))
        for d in r.get("results", []): out[d["document_number"]] = d
        if page >= r.get("total_pages", 1): break
        page += 1
chains = []
for k, d in out.items():
    oid = (d.get("correction_of") or "").rsplit("/", 1)[-1]
    if not oid: continue
    o = get(f"{B}/{oid}.json?" + urllib.parse.urlencode([("fields[]", f) for f in F[:4] + ["abstract", "dates", "type"]]))
    if o.get("document_number"): chains.append({"original": o, "correction": d})
print(len(out), "correction notices;", len(chains), "with retrievable original")
json.dump(chains, open("data/pilot/correction_chains.json", "w"), indent=1)
lag = [(__import__("datetime").date.fromisoformat(c["correction"]["publication_date"]) - __import__("datetime").date.fromisoformat(c["original"]["publication_date"])).days for c in chains]
print("lag (days) min/median/max:", min(lag), sorted(lag)[len(lag)//2], max(lag)); print(collections.Counter(c["original"].get("type") for c in chains))
print("corrections with own effective_on:", sum(bool(c["correction"].get("effective_on")) for c in chains), " with abstract:", sum(bool(c["correction"].get("abstract")) for c in chains))
