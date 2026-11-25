"""Ablation on the fresh test3 batch with FROZEN settings (lambda=2, delta=1.5): isolates routing, eligibility and the semantic gate.
Variants: full v2; no routing (one fixed intent for every query: valid_at / known_at); no eligibility (gate + date gap only); no semantic term (eligibility + gap only)."""
import sys, io, contextlib, statistics as st, math
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
def run(c, intent=None, eligible=True, gate=1.5):
    q = query(c); it = intent or route(q); s = bm25(q); pool = sorted(s, key=s.get, reverse=True)[:20]; zs = z(s, pool); zmax = max(zs.values())
    ok = [i for i in pool if (elig(i, c, it) if eligible else True) and zs[i] >= zmax - gate]
    return sorted(ok, key=lambda i: (gapdays(i, c, it), *tie(i), -zs[i]))
V = {"B4 v2 (full: routing + eligibility + gate)": lambda c: run(c),
     "- routing (always valid-at)": lambda c: run(c, "valid_at"),
     "- routing (always known-at)": lambda c: run(c, "known_at"),
     "- eligibility (gate + gap only)": lambda c: run(c, eligible=False),
     "- semantic gate (eligibility + gap)": lambda c: run(c, gate=1e9)}
print("test3, n =", len(test3))
for n, fn in V.items():
    v = [score(fn(c), c) for c in test3]
    print(f"{n:48} top1 {st.mean(x[0] for x in v):.2f}  inadmissible {st.mean(x[1] for x in v):.2f}")
