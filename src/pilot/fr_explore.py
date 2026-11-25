"""Explore Federal Register final rules per CFR part: publication vs effective lag, corrections."""
import json, sys, urllib.parse, urllib.request, datetime as dt
B = "https://www.federalregister.gov/api/v1/documents.json"
F = ["document_number","title","publication_date","effective_on","corrections","correction_of","cfr_references","html_url"]
def fetch(title, part, since="2015-01-01", until="2026-10-31"):
    out, page = [], 1
    while True:
        q = [("conditions[type][]","RULE"),("conditions[cfr][title]",title),("conditions[cfr][part]",part),
             ("conditions[publication_date][gte]",since),("conditions[publication_date][lte]",until),
             ("per_page","1000"),("page",str(page)),("order","oldest")] + [("fields[]",f) for f in F]
        r = json.load(urllib.request.urlopen(B+"?"+urllib.parse.urlencode(q), timeout=60))
        out += r["results"]
        if page >= r.get("total_pages",1): break
        page += 1
    return out
if __name__ == "__main__":
    for t,p in [(12,1026),(21,172),(49,571),(40,60),(17,240),(29,1910),(42,414),(14,91)]:
        rs = fetch(t,p)
        lags = []
        for d in rs:
            if d["effective_on"]:
                lags.append((dt.date.fromisoformat(d["effective_on"])-dt.date.fromisoformat(d["publication_date"])).days)
        nc = sum(1 for d in rs if d["corrections"])
        pos = sum(1 for l in lags if l>0); neg = sum(1 for l in lags if l<0)
        print(f"{t} CFR {p}: n={len(rs)} with_eff={len(lags)} lag>0={pos} lag<0={neg} corrected={nc}", flush=True)
