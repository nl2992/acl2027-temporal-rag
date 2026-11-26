"""Control: the cue router switching between the two gated single-clock baselines (no method of ours behind it). Run from the repo root:
    python3 -B src/pilot/router_switch.py            # BM25
    .venv/bin/python -B src/pilot/router_switch.py --dense
B2 and B3 keep the pool size and gate chosen for each on dev; which of the two serves each routed intent is also chosen on dev."""
import os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "controls_test5.py")).read()
exec(src.split('print(f"scorer')[0])   # definitions only: splits, retrieval, run(), evaluate(), cboot()

GRID = [(K, d) for K in KS for d in DELTAS]
CFG = {n: dev_pick(n, GRID) for n in ("B2", "B3")}
routed = lambda c: route2(query(c))
SWITCH = {}
for it in INTENTS:
    cs = [c for c in dev if routed(c) == it]
    SWITCH[it] = max(("B3", "B2"), key=lambda n: top1(evaluate(lambda c: run(n, c, *CFG[n]), cs)))
print(f"scorer: {'bge-small-en-v1.5' if DENSE else 'BM25'}")
print("gated baseline settings (K, delta):", CFG)
print("dev-chosen baseline per routed intent:", SWITCH)
K, DL = FROZEN
report("B2 gated", lambda c: run("B2", c, *CFG["B2"]))
report("B3 gated", lambda c: run("B3", c, *CFG["B3"]))
report("router over B2/B3 gated", lambda c: run(SWITCH[routed(c)], c, *CFG[SWITCH[routed(c)]]))
report("v2", lambda c: run("v2", c, K, DL))
print("v2 minus router-over-baselines: %.3f [%.3f, %.3f]" % cboot("v2", "router over B2/B3 gated"))
