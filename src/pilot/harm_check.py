"""A6: does temporal routing hurt ordinary (non-temporal, topic-only) retrieval? One query per held-out family (test1+test2), two phrasings,
binary relevance = any document of the same family (all versions answer a topic question). Metrics @10: nDCG, precision of returned docs, recall of min(10,|family|).
Settings frozen from the main experiment (lambda=2, delta=1.5); nothing tuned here."""
import sys, io, contextlib, statistics as st, math
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
TODAY = D("2026-11-23")
fams_t = sorted({c["family"] for c in test})
fam_docs = {f: {i for i in C if C[i]["family"] == f} for f in fams_t}
topic = {f: next(c["topic"] for c in cases if c["family"] == f) for f in fams_t}
def pool(q):
    s = bm25(q); p = sorted(s, key=s.get, reverse=True)[:20]; return s, p, z(s, p)
def ranks(q):
    s, p, zs = pool(q); zmax = max(zs.values())
    cur = [i for i in p if eff(i) <= TODAY and pub(i) <= TODAY]
    return {"B0_bm25": p[:10],
            "always_valid_filter_latest": sorted(cur, key=lambda i: eff(i), reverse=True)[:10],
            "B4v1_routed(current, lam=2)": sorted(cur, key=lambda i: zs[i] - 2.0 * math.log1p(max((TODAY - eff(i)).days, 0) / 30), reverse=True)[:10],
            "B4v2_routed(current, gate=1.5)": sorted([i for i in cur if zs[i] >= zmax - 1.5], key=lambda i: (max((TODAY - eff(i)).days, 0), -zs[i]))[:10]}
def metrics(r, rel):
    g = sum(1 / math.log2(k + 2) for k, i in enumerate(r) if i in rel); ideal = sum(1 / math.log2(k + 2) for k in range(min(10, len(rel))))
    return (g / ideal if ideal else 0, sum(i in rel for i in r) / len(r) if r else 0, sum(i in rel for i in r) / min(10, len(rel)))
tpl = ["{x}", "Which rules cover {x}?"]
agg = {}
for f in fams_t:
    for t in tpl:
        for m, r in ranks(t.format(x=topic[f])).items(): agg.setdefault(m, []).append(metrics(r, fam_docs[f]))
print(f"families {len(fams_t)}, queries {len(fams_t)*len(tpl)}")
print(f"{'method':32} nDCG@10  P@10(returned)  Recall@min(10,|fam|)")
for m, v in agg.items():
    print(f"{m:32} {st.mean(x[0] for x in v):.2f}     {st.mean(x[1] for x in v):.2f}            {st.mean(x[2] for x in v):.2f}")
