"""A7: Re3-STYLE conceptual baseline (not a reproduction; Re3 arXiv 2509.01306 v1 is a learned query-aware gate over relevance and recency).
Here: score = z(BM25) + g(q) * freshness(d), freshness = -log1p(max(today - publication_date, 0)/30); the gate g is a per-query-type constant
(date-free vs dated query), chosen on dev families only. No target time t, no horizon h, no eligibility; it can only prefer newer or older documents.
Evaluated on test1+test2 and the fresh test3 (selection never touches either)."""
import sys, io, contextlib, statistics as st, math
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
TODAY = D("2026-11-23")
from dateparse import find_dates
def re3(c, g_cur, g_hist):
    q = query(c); s = bm25(q); pool = sorted(s, key=s.get, reverse=True)[:20]; zs = z(s, pool)
    g = g_hist if find_dates(q) else g_cur
    return sorted(pool, key=lambda i: zs[i] - g * math.log1p(max((TODAY - pub(i)).days, 0) / 30), reverse=True)
G = [-2, -1, -0.5, 0, 0.25, 0.5, 1, 2, 4]   # negative = prefer older documents
dev_cur = [c for c in dev if c["intent"] == "current"]; dev_hist = [c for c in dev if c["intent"] != "current"]
g_cur = max(G, key=lambda g: mean_top1(lambda c: re3(c, g, 0), dev_cur)); g_hist = max(G, key=lambda g: mean_top1(lambda c: re3(c, 0, g), dev_hist))
print("dev-selected gates: current", g_cur, " dated", g_hist)
for nm, cs in [("test1+test2", test), ("test3 (fresh)", test3)]:
    print(nm, f"n={len(cs)}  top1/inadmissible by intent")
    for it in INTENTS + ["ALL"]:
        v = [score(re3(c, g_cur, g_hist), c) for c in cs if it == "ALL" or c["intent"] == it]
        print(f"   {it:12} {st.mean(x[0] for x in v):.2f} / {st.mean(x[1] for x in v):.2f}")
