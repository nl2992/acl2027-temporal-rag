"""Dense-retriever replication (bge-small-en-v1.5 via sentence-transformers, Apple MPS). Same pipeline as BM25, semantic scores replaced by cosine similarity.
Gate width delta selected on DEV for the dense scorer (grid below); lambda=2 and the router are unchanged. Reports test3 and test4 (never used for selection)."""
import sys, io, contextlib, functools, statistics as st, math, random
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
import numpy as np
from sentence_transformers import SentenceTransformer
M = SentenceTransformer("BAAI/bge-small-en-v1.5", device="mps")
ids = list(C); texts = [(C[i]["title"] + ". " + (C[i].get("abstract") or "")) for i in ids]
E = M.encode(texts, batch_size=64, normalize_embeddings=True, show_progress_bar=False); idx = {i: k for k, i in enumerate(ids)}
PFX = "Represent this sentence for searching relevant passages: "
@functools.lru_cache(maxsize=None)
def dense(q, *a, **k):
    v = M.encode([PFX + q], normalize_embeddings=True)[0]; s = E @ v; return {i: float(s[idx[i]]) for i in ids}
bm25 = dense   # override the lexical scorer used by every method in this namespace
def meth(name, c, K, delta=1.5):
    q = query(c); s = bm25(q); p = sorted(s, key=s.get, reverse=True)[:K]; t, h = D(c["t"]), D(c["h"]); zs = z(s, p)
    if name == "B0": return p
    if name == "B2": return sorted([i for i in p if pub(i) <= h], key=lambda i: (pub(i), s[i]), reverse=True)
    if name == "B3": return sorted([i for i in p if inforce(i, t)], key=lambda i: (eff(i), s[i]), reverse=True)
    if name == "B6": return sorted(p, key=lambda i: zs[i] - 4.0 * math.log1p(abs((t - pub(i)).days) / 30), reverse=True)
    it = route(q)
    if name == "v1": return sorted([i for i in p if elig(i, c, it)], key=lambda i: zs[i] - 2.0 * math.log1p(gapdays(i, c, it) / 30), reverse=True)
    zmax = max(zs.values()); ok = [i for i in p if elig(i, c, it) and zs[i] >= zmax - delta]
    return sorted(ok, key=lambda i: (gapdays(i, c, it), *tie(i), -zs[i]))
mt = lambda cs, K, d: st.mean(score(meth("v2", c, K, d), c)[0] for c in cs)
print("DEV sweep (dense) top-1 by (K, delta):")
best = None
for K in (20, 50, 100):
    row = []
    for d in (0.5, 1.0, 1.5, 2.0, 3.0):
        a = mt(dev, K, d); row.append(f"d={d}: {a:.3f}")
        if best is None or a > best[0]: best = (a, K, d)
    print(f"K={K:3d} " + "  ".join(row))
_, Kb, db = best; print("dev-selected (dense): K =", Kb, " delta =", db)
random.seed(5)
import os
SETS = {"test3": test3, "test4": test4, "test5": test5}
for nm, cs in [(k, SETS[k]) for k in os.environ.get("SETS", "test3,test4").split(",")]:
    R = {}
    for m in ("B0", "B2", "B3", "B6", "v1"): R[m] = {id(c): score(meth(m, c, Kb), c) for c in cs}
    R["v2"] = {id(c): score(meth("v2", c, Kb, db), c) for c in cs}
    print(f"\n{nm} (dense, K={Kb}, delta={db}) n={len(cs)}  overall top-1 / inadmissible / ndcg;  by intent top-1: cur valid known v-k")
    for m, r in R.items():
        o = [r[id(c)] for c in cs]; by = [st.mean(r[id(c)][0] for c in cs if c["intent"] == it) for it in INTENTS]
        print(f"  {m:3} {st.mean(x[0] for x in o):.2f} / {st.mean(x[1] for x in o):.2f} / {st.mean(x[2] for x in o):.2f}    " + " ".join(f"{b:.2f}" for b in by))
    def cb(a, b, B=2000):
        byf = {}
        for c in cs: byf.setdefault(c["family"], []).append(R[a][id(c)][0] - R[b][id(c)][0])
        F = list(byf); ms = sorted(st.mean([x for f in random.choices(F, k=len(F)) for x in byf[f]]) for _ in range(B)); allv = [x for f in F for x in byf[f]]
        return st.mean(allv), ms[int(.025 * B)], ms[int(.975 * B)]
    for b in ("B3", "B6", "B2", "v1"): print(f"  cluster bootstrap v2 - {b}: %.3f [%.3f, %.3f]" % cb("v2", b))
