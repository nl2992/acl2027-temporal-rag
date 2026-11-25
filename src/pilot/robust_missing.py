"""A5: robustness to missing effective dates. A random fraction p of documents lose effective_on (publication date kept). Gold and admissibility use TRUE dates.
Fallbacks for a masked doc under intents that need effective time: strict = drop it (the query may then return nothing = abstain, scored as a miss); proxy = assume effective_on := publication date.
Evaluated on test1+test2 (already analysed earlier; test3 untouched). B4v2 gated, delta=1.5 frozen. 3 mask seeds."""
import sys, io, contextlib, random, statistics as st, math
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
def run(c, masked, mode, delta=1.5):
    q = query(c); it = route(q); s = bm25(q); pool = sorted(s, key=s.get, reverse=True)[:20]; zs = z(s, pool); zmax = max(zs.values())
    t, h = D(c["t"]), D(c["h"]); out = []
    for i in pool:
        if zs[i] < zmax - delta: continue
        known_eff = None if i in masked else eff(i)
        if it == "known_at": ok = pub(i) <= h; gap = (h - pub(i)).days
        else:
            e = known_eff
            if e is None:
                if mode == "strict": continue
                e = pub(i)                       # proxy and open: use publication date as the effective-time estimate
            ok = e <= t and (it == "valid_at" or pub(i) <= h) if it != "current" else (e <= h and pub(i) <= h)
            gap = (t - e).days
        if ok: out.append((max(gap, 0), -zs[i], i))
    return [i for _, _, i in sorted(out)]
def evaluate(p, mode, seed):
    rnd = random.Random(seed); masked = {i for i in C if rnd.random() < p}
    v = []
    for c in test:
        r = run(c, masked, mode); v.append((int(bool(r) and r[0] == gold(c)), int(bool(r) and not admissible(r[0], c))))
    return st.mean(x[0] for x in v), st.mean(x[1] for x in v)
print(f"{'p(masked)':>9} | " + " | ".join(f"{m:>16}" for m in ("strict drop", "proxy eff:=pub")) + "   (top1 / true-inadmissible, mean of 3 seeds, n=%d)" % len(test))
for p in (0.0, 0.1, 0.3, 0.5, 0.8, 1.0):
    row = f"{p:9.1f} | "
    for mode in ("strict", "proxy"):
        rs = [evaluate(p, mode, sd) for sd in (11, 12, 13)]; row += f"{st.mean(r[0] for r in rs):6.2f} / {st.mean(r[1] for r in rs):5.2f}  | "
    print(row)
rs = {m: [evaluate(0.3, m, sd) for sd in (11, 12, 13)] for m in ("strict", "proxy")}
print("B0 semantic-only reference top1 on same cases: %.2f" % st.mean(score(rank("B0_bm25", c), c)[0] for c in test))
