"""Compare blind-judge answers with (a) the original metadata gold and (b) the valid-to gold ('NONE' when nothing was in force).
CAUTION: the 120 judged cases come from test3/test4, so after this check those two sets no longer count as untouched for the valid-to semantics; test5 is the clean confirmatory set for it."""
import sys, io, contextlib, json, random, collections
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
import common
J = sys.argv[1]
random.seed(11); picked = []
for it in INTENTS:
    for pool in (test3, test4):
        cs = [c for c in pool if c["intent"] == it]; random.shuffle(cs); picked += cs[:15]
random.shuffle(picked)
ans = {}
for k in range(1, 7): ans.update(json.load(open(f"{J}/answers_{k}.json")))
res = collections.defaultdict(lambda: [0, 0, 0])
for n, c in enumerate(picked, 1):
    cid = f"J{n:03d}"; a = ans[cid]["choice"]; common.VT = False; g0 = gold(c); common.VT = True; g1 = gold(c); common.VT = False
    for key, g in (("old", g0), ("valid_to", g1)):
        res[(key, c["intent"])][0] += int(a == g); res[(key, c["intent"])][1] += 1
    res[("changed_gold", c["intent"])][0] += int(g0 != g1); res[("changed_gold", c["intent"])][1] += 1
    res[("gold_NONE", c["intent"])][0] += int(g1 == "NONE"); res[("gold_NONE", c["intent"])][1] += 1
for key in ("old", "valid_to", "changed_gold", "gold_NONE"):
    tot = [sum(res[(key, it)][0] for it in INTENTS), sum(res[(key, it)][1] for it in INTENTS)]
    print(f"{key:13} overall {tot[0]}/{tot[1]} = {tot[0]/tot[1]:.2f}   " + "  ".join(f"{it} {res[(key, it)][0]}/{res[(key, it)][1]}" for it in INTENTS))
