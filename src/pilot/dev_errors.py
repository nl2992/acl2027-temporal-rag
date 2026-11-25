"""Error analysis of B4 v2 (delta=1.5) on DEV families only (test1/test2/test3 untouched)."""
import sys, io, contextlib, collections
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
cat = collections.Counter(); ex = collections.defaultdict(list)
for c in dev:
    r = gated(c, 1.5); g = gold(c); it = route(query(c))
    if r and r[0] == g: cat["correct"] += 1; continue
    if not r: k = "no eligible candidate"
    else:
        p = r[0]; same = C[p]["family"] == C[g]["family"]
        if not same: k = "other family"
        else:
            key = (lambda i: pub(i)) if it == "known_at" else (lambda i: eff(i))
            if key(p) == key(g): k = "same family, tie on the intent's clock (another rule with the same date)"
            elif g not in r: k = "same family, gold removed by gate/pool"
            else: k = "same family, other version ranked first"
    cat[k] += 1; ex[k].append((c["intent"], g, r[0] if r else None))
n = len(dev); print("dev cases", n)
for k, v in cat.most_common(): print(f"{v:5d} {v/n:5.2f}  {k}")
for k in ex:
    if k != "correct": print("\n", k, ex[k][:3])
