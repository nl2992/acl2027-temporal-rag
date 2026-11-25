"""Pilot baselines B0-B4 on Federal Register two-clock cases. CPU only, metadata-derived labels."""
import json, math, re, collections, datetime as dt, random
D = dt.date.fromisoformat
C = json.load(open("data/pilot/corpus.json")); cases = json.load(open("data/pilot/cases.json"))
tok = lambda s: re.findall(r"[a-z0-9]+", s.lower())
docs = {i: tok(d["title"] + " " + d["abstract"]) for i, d in C.items()}
N = len(docs); avg = sum(map(len, docs.values())) / N
df = collections.Counter(w for t in docs.values() for w in set(t))
import functools
@functools.lru_cache(maxsize=None)
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
