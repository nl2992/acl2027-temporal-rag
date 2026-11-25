"""Build pilot corpus + cases from Federal Register families (metadata only, no gold-derived timestamps)."""
import json, re, random, datetime as dt, urllib.parse, urllib.request, urllib.error

import time
def _get(u, tries=8):
    for k in range(tries):
        try: return json.load(urllib.request.urlopen(u, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code != 429 or k == tries - 1: raise
            time.sleep(5 * (k + 1))
D = dt.date.fromisoformat
fam = json.load(open("data/pilot/families_all.json"))
# drop families dominated by negative/zero lag noise; keep those with clear pub<eff gaps
EXCLUDE = {"2015-13717", "2023-23882", "2015-10055", "2023-12630"}  # API effective_on (2015-07-27) contradicts its own DATES text (June 10, 2015); 2023-23882 and 2015-10055 likewise conflict with their DATES text (found when verifying test4)
fam = {k: [d for d in v if d["document_number"] not in EXCLUDE] for k, v in fam.items()}
fam = {k: v for k, v in fam.items() if len(v) >= 4}
corpus = {}
for k, v in fam.items():
    for d in v: corpus[d["document_number"]] = {**d, "family": k}
ids = list(corpus)
for i in range(0, len(ids), 20):
    u = "https://www.federalregister.gov/api/v1/documents/" + ",".join(ids[i:i+20]) + ".json?fields[]=abstract&fields[]=document_number"
    for r in _get(u)["results"]:
        corpus[r["document_number"]]["abstract"] = r.get("abstract") or ""
json.dump(corpus, open("data/pilot/corpus.json","w"), indent=1)
# cases
cases = []
today = D("2026-11-23")
random.seed(0)
for k, v in fam.items():
    v = sorted(v, key=lambda d: d["publication_date"])
    topic = re.sub(r"\s+", " ", v[-1]["title"]).strip()
    for d in v[1:]:
        p, e = D(d["publication_date"]), D(d["effective_on"])
        if e - p >= dt.timedelta(days=14):          # the interesting gap: announced but not yet effective
            mid = p + (e - p) / 2
            for intent, t, h in [("valid_at", mid, today), ("known_at", mid, mid), ("valid_known", mid, mid)]:
                cases.append({"family": k, "topic": topic, "intent": intent, "t": t.isoformat(), "h": h.isoformat(), "probe_doc": d["document_number"]})
    for i, d in enumerate(v[1:], 1):
        p, e = D(d["publication_date"]), D(d["effective_on"])
        if p - e >= dt.timedelta(days=3):           # retroactive: effective before publication
            mid = e + (p - e) / 2
            for intent, h in [("valid_at", today), ("valid_known", mid)]:
                cases.append({"family": k, "topic": topic, "intent": intent, "t": mid.isoformat(), "h": h.isoformat(), "probe_doc": d["document_number"], "kind": "retroactive"})
    cases.append({"family": k, "topic": topic, "intent": "current", "t": today.isoformat(), "h": today.isoformat(), "probe_doc": None})
json.dump(cases, open("data/pilot/cases.json","w"), indent=1)
print(len(corpus), "docs", len(cases), "cases")
