"""A3: correction chains. Original O (published p0) and its later correction notice K (published pk). 
Intents: known_at (h between p0 and pk) -> gold O (K not yet public); retrospective (h=today, t after p0) -> gold K (corrected record).
No effective_on is used (corrections have none), so this isolates the information-horizon clock. Single pass, no tuning."""
import json, re, math, random, urllib.request, urllib.parse, datetime as dt, collections, statistics as st
D = dt.date.fromisoformat; TODAY = dt.date(2026, 11, 23)
chains = json.load(open("data/pilot/correction_chains.json"))
seen = collections.Counter(re.sub(r"\W+", " ", c["original"]["title"].lower()) for c in chains)
chains = [c for c in chains if seen[re.sub(r"\W+", " ", c["original"]["title"].lower())] == 1 and (D(c["correction"]["publication_date"]) - D(c["original"]["publication_date"])).days >= 7]
ids = [x for c in chains for x in (c["original"]["document_number"], c["correction"]["document_number"])]
txt = {}
for i in range(0, len(ids), 20):
    u = "https://www.federalregister.gov/api/v1/documents/" + ",".join(ids[i:i+20]) + ".json?fields[]=document_number&fields[]=raw_text_url"
    for r in json.load(urllib.request.urlopen(u, timeout=60))["results"]:
        try: txt[r["document_number"]] = urllib.request.urlopen(r["raw_text_url"], timeout=60).read().decode("utf8", "ignore")[:2500]
        except Exception: txt[r["document_number"]] = ""
tok = lambda s: re.findall(r"[a-z0-9]+", s.lower())
doc = {}
for c in chains:
    for k in ("original", "correction"):
        d = c[k]; doc[d["document_number"]] = {"pub": D(d["publication_date"]), "toks": tok(d["title"] + " " + txt.get(d["document_number"], ""))}
N = len(doc); avg = sum(len(v["toks"]) for v in doc.values()) / N; df = collections.Counter(w for v in doc.values() for w in set(v["toks"]))
def bm25(q):
    qs = tok(q); out = {}
    for i, v in doc.items():
        tf = collections.Counter(v["toks"]); s = 0
        for w in qs:
            if w in tf: s += math.log(1 + (N - df[w] + .5) / (df[w] + .5)) * tf[w] * 2.2 / (tf[w] + 1.2 * (.25 + .75 * len(v["toks"]) / avg))
        out[i] = s
    return out
cases = []
for c in chains:
    o, k = c["original"], c["correction"]; p0, pk = D(o["publication_date"]), D(k["publication_date"]); mid = p0 + (pk - p0) / 2
    topic = re.sub(r"\s+", " ", o["title"]).strip()
    cases.append({"intent": "known_at", "q": f"{topic} latest published as of {mid:%B %-d, %Y}", "t": mid, "h": mid, "gold": o["document_number"], "bad": k["document_number"]})
    cases.append({"intent": "retrospective", "q": f"{topic} according to the record as corrected, in force on {mid:%B %-d, %Y}", "t": mid, "h": TODAY, "gold": k["document_number"], "bad": o["document_number"]})
def rank(m, c):
    s = bm25(c["q"]); top = sorted(s, key=s.get, reverse=True)[:20]
    if m == "B0_bm25": return top
    if m == "B1_recency": return sorted(top, key=lambda i: (doc[i]["pub"], s[i]), reverse=True)
    if m == "B2a_cutoff_at_t(single clock, h=t)": return sorted([i for i in top if doc[i]["pub"] <= c["t"]], key=lambda i: (doc[i]["pub"], s[i]), reverse=True)
    if m.endswith("(gated)"):
        v = list(s.values()); mu = st.mean(v); sd = st.pstdev(v) or 1.0
        zs = {i: (s[i] - mu) / sd for i in top}; zmax = max(zs.values()); cut = c["t"] if m.startswith("B2a") else c["h"]
        return sorted([i for i in top if doc[i]["pub"] <= cut and zs[i] >= zmax - 1.5], key=lambda i: (doc[i]["pub"], zs[i]), reverse=True)
    h = c["h"]   # B2b / B4: cutoff at the information horizon h (given by the routed intent), latest first
    return sorted([i for i in top if doc[i]["pub"] <= h], key=lambda i: (doc[i]["pub"], s[i]), reverse=True)
print('delta=1.5 fixed from the main-experiment dev selection; not tuned on chains')
print(f"chains {len(chains)} (unique titles, lag>=7d), cases {len(cases)}")
for m in ["B0_bm25", "B1_recency", "B2a_cutoff_at_t(single clock, h=t)", "B4_horizon_h(routed)", "B2a_cutoff_at_t(gated)", "B4_horizon_h(gated)"]:
    row = f"{m:36}"
    for it in ("known_at", "retrospective"):
        v = [(lambda r: (int(bool(r) and r[0] == c["gold"]), int(bool(r) and r[0] == c["bad"])))(rank(m, c)) for c in cases if c["intent"] == it]
        row += f"  {it}: top1 {st.mean(x[0] for x in v):.2f} wrong-sibling {st.mean(x[1] for x in v):.2f}"
    print(row)
