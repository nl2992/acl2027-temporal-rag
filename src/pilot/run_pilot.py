"""Pilot baselines B0-B4 on Federal Register two-clock cases. CPU only, metadata-derived labels."""
import json, math, re, collections, datetime as dt, random
D = dt.date.fromisoformat
C = json.load(open("data/pilot/corpus.json")); cases = json.load(open("data/pilot/cases.json"))
tok = lambda s: re.findall(r"[a-z0-9]+", s.lower())
docs = {i: tok(d["title"] + " " + d["abstract"]) for i, d in C.items()}
N = len(docs); avg = sum(map(len, docs.values())) / N
df = collections.Counter(w for t in docs.values() for w in set(t))
def bm25(q, k1=1.2, b=0.75):
    qs = tok(q); out = {}
    for i, t in docs.items():
        tf = collections.Counter(t); s = 0
        for w in qs:
            if w in tf:
                s += math.log(1 + (N - df[w] + .5) / (df[w] + .5)) * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(t) / avg))
        out[i] = s
    return out
pub = lambda i: D(C[i]["publication_date"]); eff = lambda i: D(C[i]["effective_on"])
def gold(c):
    t, h = D(c["t"]), D(c["h"]); fam = [i for i in C if C[i]["family"] == c["family"]]
    it = c["intent"]
    if it == "known_at": ok = [i for i in fam if pub(i) <= h]; key = pub
    else:
        ok = [i for i in fam if eff(i) <= t and (it == "valid_at" or pub(i) <= h)]; key = eff
    return max(ok, key=key) if ok else None
def admissible(i, c):  # constraint satisfaction of a returned doc under the query semantics
    t, h = D(c["t"]), D(c["h"]); it = c["intent"]
    if it == "known_at": return pub(i) <= h
    if it == "valid_at": return eff(i) <= t
    return eff(i) <= t and pub(i) <= h
def query(c):
    t = D(c["t"]).strftime("%B %d, %Y")
    return {"valid_at": f"{c['topic']} rule legally in effect on {t}",
            "known_at": f"{c['topic']} latest rule announced as of {t}",
            "valid_known": f"{c['topic']} rule in effect on {t} as known then",
            "current": f"{c['topic']} current rule"}[c["intent"]]
def rank(method, c):
    s = bm25(query(c)); top = sorted(s, key=s.get, reverse=True)[:20]
    t, h = D(c["t"]), D(c["h"])
    if method == "B0_bm25": return top
    if method == "B1_recency": return sorted(top, key=lambda i: (pub(i), s[i]), reverse=True)
    if method == "B2_pubcut": return sorted([i for i in top if pub(i) <= h], key=lambda i: (pub(i), s[i]), reverse=True)
    if method == "B3_validtime": return sorted([i for i in top if eff(i) <= t], key=lambda i: (eff(i), s[i]), reverse=True)
    if method == "B3b_valid+pubcut": return sorted([i for i in top if eff(i) <= t and pub(i) <= h], key=lambda i: (eff(i), s[i]), reverse=True)
    if method == "B4_twoclock":  # intent-routed (oracle intent in pilot)
        it = c["intent"]
        if it == "known_at": return rank("B2_pubcut", c)
        if it == "valid_at": return rank("B3_validtime", c)
        return rank("B3b_valid+pubcut", c)
M = ["B0_bm25", "B1_recency", "B2_pubcut", "B3_validtime", "B3b_valid+pubcut", "B4_twoclock"]
res = collections.defaultdict(lambda: collections.defaultdict(list))
for c in cases:
    g = gold(c)
    if g is None: continue
    for m in M:
        r = rank(m, c)
        top1 = r[0] if r else None
        res[m][c["intent"]].append((int(top1 == g), int(top1 is not None and not admissible(top1, c)), 1 / math.log2(r.index(g) + 2) if g in r[:10] else 0))
print(f"{'method':18}" + "".join(f"{it:>26}" for it in ["current", "valid_at", "known_at", "valid_known"]))
print(f"{'':18}" + "  top1 / viol / ndcg  (n)".rjust(26) * 4)
for m in M:
    row = f"{m:18}"
    for it in ["current", "valid_at", "known_at", "valid_known"]:
        v = res[m][it]; n = len(v)
        row += f"  {sum(x[0] for x in v)/n:5.2f}/{sum(x[1] for x in v)/n:5.2f}/{sum(x[2] for x in v)/n:5.2f} ({n:3d})"
    print(row)
# how often do the clocks disagree on gold?
dis = collections.Counter()
for c in cases:
    if c["intent"] != "current":
        cc = {**c}; gs = {}
        for it in ["valid_at", "known_at", "valid_known"]: gs[it] = gold({**c, "intent": it})
        dis[(gs["valid_at"] != gs["known_at"], gs["valid_at"] != gs["valid_known"])] += 1
print("disagreement (valid!=known, valid!=valid_known) counts:", dict(dis))
