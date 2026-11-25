"""Judge agreement with gold under validity level 1 vs level 2, for a judged sample: 'dev' (d_ files, seed 13) or 'test5' (p5_ files, seed 12)."""
import sys, io, contextlib, json, random, collections
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
import common
J, which = sys.argv[1], sys.argv[2]
pool, seed, per, pre = (dev, 13, 30, "d_") if which == "dev" else (test5, 12, 30, "p5_")
random.seed(seed); picked = []
for it in INTENTS:
    cs = [c for c in pool if c["intent"] == it]; random.shuffle(cs); picked += cs[:per]
random.shuffle(picked)
ans = {}
for k in range(1, 7): ans.update(json.load(open(f"{J}/{pre}answers_{k}.json")))
def setlevel(L):
    common.VTL = L; common.VT = L >= 1; common.V2 = L >= 2; common.vto.cache_clear()
for L in (1, 2):
    setlevel(L); res = collections.defaultdict(lambda: [0, 0])
    for n, c in enumerate(picked, 1):
        g = gold(c); a = ans[f"J{n:03d}"]["choice"]; res[c["intent"]][0] += int(a == g); res[c["intent"]][1] += 1
    tot = (sum(v[0] for v in res.values()), sum(v[1] for v in res.values()))
    print(f"{which} level {L}: {tot[0]}/{tot[1]} = {tot[0]/tot[1]:.3f}   " + "  ".join(f"{it} {res[it][0]}/{res[it][1]}" for it in INTENTS))
# per-case differences between levels
setlevel(1); g1 = {n: gold(c) for n, c in enumerate(picked, 1)}; setlevel(2); g2 = {n: gold(c) for n, c in enumerate(picked, 1)}
for n, c in enumerate(picked, 1):
    a = ans[f"J{n:03d}"]["choice"]
    if g1[n] != g2[n]:
        print(f"J{n:03d} {c['intent']:12} L1 gold {g1[n]} ({'agree' if a == g1[n] else 'dis'})  L2 gold {g2[n]} ({'agree' if a == g2[n] else 'dis'})  judge {a} | {ans[f'J{n:03d}']['note'][:90]}")
