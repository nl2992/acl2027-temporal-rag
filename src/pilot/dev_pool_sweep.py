"""DEV-only sweep: candidate pool size and gate width for B4 v2. Motivated by dev error analysis (most errors are gold missing from the pool or removed by the gate)."""
import sys, io, contextlib, statistics as st
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
def gated_p(c, delta, K):
    q = query(c); it = route(q); s = bm25(q); pool = sorted(s, key=s.get, reverse=True)[:K]; zs = z(s, pool); zmax = max(zs.values())
    ok = [i for i in pool if elig(i, c, it) and zs[i] >= zmax - delta]
    return sorted(ok, key=lambda i: (gapdays(i, c, it), *tie(i), -zs[i]))
print("dev n =", len(dev), "  top1 by (pool K, delta)")
for K in (20, 50, 100, 200):
    print(f"K={K:3d} " + "  ".join(f"d={d}: {st.mean(score(gated_p(c, d, K), c)[0] for c in dev):.3f}" for d in (1.0, 1.5, 2.0, 3.0)))
