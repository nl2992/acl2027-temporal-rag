"""A4b feasibility probe: UK statutory instruments (legislation.gov.uk, Open Government Licence v3). Made date vs ComingIntoForce, family structure. Probe only, no model run."""
import re, json, urllib.request, collections, datetime as dt, statistics as st
def get(u):
    try: return urllib.request.urlopen(u, timeout=60).read().decode("utf8", "ignore")
    except Exception: return ""
ents = []
for yr in (2018, 2019, 2020, 2021, 2022):
    for page in (1, 2):
        x = get(f"https://www.legislation.gov.uk/uksi/{yr}/data.feed?results-count=100&page={page}")
        for e in x.split("<entry>")[1:]:
            m = re.search(r"<id>http://www.legislation.gov.uk/id/uksi/(\d+)/(\d+)</id>.*?<title>(.*?)</title>", e, re.S)
            if m: ents.append((m.group(1), m.group(2), m.group(3)))
print(len(ents), "feed entries")
rows = []
for yr, n, title in ents[:400]:
    x = get(f"https://www.legislation.gov.uk/uksi/{yr}/{n}/made/data.xml")
    mm = re.search(r'<ukm:Made Date="([\d-]+)"', x); cf = re.findall(r'<ukm:ComingIntoForce>\s*<ukm:DateTime Date="([\d-]+)"', x)
    if mm: rows.append({"id": f"uksi/{yr}/{n}", "title": title, "made": mm.group(1), "cif": cf[0] if cf else None, "n_cif": len(cf)})
json.dump(rows, open("data/pilot/uk_probe.json", "w"))
with_cif = [r for r in rows if r["cif"]]
lags = [(dt.date.fromisoformat(r["cif"]) - dt.date.fromisoformat(r["made"])).days for r in with_cif]
print(len(rows), "SIs parsed;", len(with_cif), "have ComingIntoForce;", "lag<0:", sum(l < 0 for l in lags), "0-6d:", sum(0 <= l < 7 for l in lags), "7-27d:", sum(7 <= l < 28 for l in lags), ">=28d:", sum(l >= 28 for l in lags), "median", st.median(lags) if lags else None)
norm = lambda t: re.sub(r"\s+", " ", re.sub(r"\(No\. ?\d+\)|\b(19|20)\d\d\b|\d+", "#", t.lower())).strip()
fam = collections.Counter(norm(r["title"]) for r in with_cif)
print("families (normalized title) with >=4 members:", sum(v >= 4 for v in fam.values()), "largest:", fam.most_common(4))
