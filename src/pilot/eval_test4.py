"""Confirmatory run on test4 (100 families never used before). Config chosen on DEV only after dev error analysis: pool K=50, delta=1.5 (lambda=2 for v1).
Baselines reported at their original K=20 and at K=50 so the larger pool does not favour our method alone."""
import sys, io, contextlib, statistics as st, math, random
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
def pool_of(q, K): s = bm25(q); return s, sorted(s, key=s.get, reverse=True)[:K]
def meth(name, c, K):
    q = query(c); s, p = pool_of(q, K); t, h = D(c["t"]), D(c["h"]); zs = z(s, p)
    if name == "B0": return p
    if name == "B2": return sorted([i for i in p if pub(i) <= h], key=lambda i: (pub(i), s[i]), reverse=True)
    if name == "B3": return sorted([i for i in p if eff(i) <= t], key=lambda i: (eff(i), s[i]), reverse=True)
    if name == "B6": return sorted(p, key=lambda i: zs[i] - 4.0 * math.log1p(abs((t - pub(i)).days) / 30), reverse=True)
    it = route(q)
    if name == "v1": return sorted([i for i in p if elig(i, c, it)], key=lambda i: zs[i] - 2.0 * math.log1p(gapdays(i, c, it) / 30), reverse=True)
    zmax = max(zs.values()); ok = [i for i in p if elig(i, c, it) and zs[i] >= zmax - 1.5]
    return sorted(ok, key=lambda i: (gapdays(i, c, it), -zs[i]))
print("test4: families", len({c['family'] for c in test4}), "cases", len(test4))
R = {}
for K in (20, 50):
    for m in ("B0", "B2", "B3", "B6", "v1", "v2"):
        R[(m, K)] = {id(c): score(meth(m, c, K), c) for c in test4}
print(f"{'method':10} {'K':>3}" + "".join(f"{it:>20}" for it in INTENTS) + f"{'ALL':>20}   top1/viol/ndcg")
for (m, K), r in R.items():
    row = f"{m:10} {K:3d}"
    for it in INTENTS + ["ALL"]:
        v = [r[id(c)] for c in test4 if it == "ALL" or c["intent"] == it]; row += f"  {st.mean(x[0] for x in v):4.2f}/{st.mean(x[1] for x in v):4.2f}/{st.mean(x[2] for x in v):4.2f}"
    print(row)
rows = {f"{m}@{K}": r for (m, K), r in R.items()}
random.seed(5)
def cboot(a, b, B=2000):
    byf = {}
    for c in test4: byf.setdefault(c["family"], []).append(rows[a][id(c)][0] - rows[b][id(c)][0])
    F = list(byf); ms = sorted(st.mean([x for f in random.choices(F, k=len(F)) for x in byf[f]]) for _ in range(B))
    allv = [x for f in F for x in byf[f]]; return st.mean(allv), ms[int(.025 * B)], ms[int(.975 * B)]
for b in ("B0@20", "B2@20", "B3@20", "B6@20", "B2@50", "B3@50", "B6@50", "v1@50", "v2@20"):
    print(f"cluster bootstrap v2@50 - {b}: %.3f [%.3f, %.3f]" % cboot("v2@50", b))
