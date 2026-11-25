"""Method v1: intent router + hard two-clock eligibility + (semantic z-score - lambda * log temporal gap).
Dev/test split by rule family; lambda tuned on dev only. B6 = TimelyRAG-style soft temporal-distance approximation (NOT a reproduction)."""
import sys, json, math, random, hashlib, collections, statistics as st, re
sys.path.insert(0, "src/pilot")
from common import *
INTENTS = ["current", "valid_at", "known_at", "valid_known"]
def route(q):  # keyword router; written from intent definitions, not tuned on results
    ql = q.lower()
    if "current" in ql: return "current"
    if "as known then" in ql: return "valid_known"
    if "announced" in ql: return "known_at"
    return "valid_at"
def z(s, ids):
    v = [s[i] for i in ids]; m = st.mean(v); sd = st.pstdev(v) or 1.0
    return {i: (s[i] - m) / sd for i in ids}
def gapdays(i, c, it):
    t, h = D(c["t"]), D(c["h"])
    ref, clock = (h, pub(i)) if it == "known_at" else (t, eff(i))
    return max((ref - clock).days, 0)
def elig(i, c, it):
    t, h = D(c["t"]), D(c["h"])
    if it == "current": return eff(i) <= h and pub(i) <= h
    if it == "known_at": return pub(i) <= h
    if it == "valid_at": return eff(i) <= t
    return eff(i) <= t and pub(i) <= h
def twoclock(c, lam, router=True):
    q = query(c); it = route(q) if router else c["intent"]
    s = bm25(q); pool = sorted(s, key=s.get, reverse=True)[:20]; zs = z(s, pool)
    ok = [i for i in pool if elig(i, c, it)]
    return sorted(ok, key=lambda i: zs[i] - lam * math.log1p(gapdays(i, c, it) / 30), reverse=True)
def b6(c, lam):  # soft symmetric distance of publication time to target time, no eligibility
    s = bm25(query(c)); pool = sorted(s, key=s.get, reverse=True)[:20]; zs = z(s, pool); t = D(c["t"])
    return sorted(pool, key=lambda i: zs[i] - lam * math.log1p(abs((t - pub(i)).days) / 30), reverse=True)
def score(rk, c):
    g = gold(c); r = rk
    return (int(bool(r) and r[0] == g), int(bool(r) and not admissible(r[0], c)), 1 / math.log2(r.index(g) + 2) if g in r[:10] else 0.0)
import os
split1 = json.load(open("annotation/split_v1.json"))   # frozen before expansion: 9 dev / 5 test families
fams = sorted({c["family"] for c in cases})
split3 = json.load(open("annotation/split_v3.json")) if os.path.exists("annotation/split_v3.json") else {}
split = {f: split1.get(f) or split3.get(f) or ("test2" if int(hashlib.md5(f.encode()).hexdigest(), 16) % 3 == 0 else "dev2") for f in fams}
dev = [c for c in cases if split[c["family"]] in ("dev", "dev2") and gold(c)]   # lambda selection: all dev families (never test)
test = [c for c in cases if split[c["family"]] in ("test", "test2") and gold(c)]
test3 = [c for c in cases if split[c["family"]] == "test3" and gold(c)]
test1 = [c for c in test if split[c["family"]] == "test"]; test2 = [c for c in test if split[c["family"]] == "test2"]
print("families:", {v: sum(x == v for x in split.values()) for v in ("dev", "test", "dev2", "test2")}, "| cases dev/test1/test2:", len(dev), len(test1), len(test2))
GRID = [0, .25, .5, 1, 2, 4]
def mean_top1(fn, cs): return st.mean(score(fn(c), c)[0] for c in cs)
lam4 = max(GRID, key=lambda l: mean_top1(lambda c: twoclock(c, l), dev))
lam6 = max(GRID, key=lambda l: mean_top1(lambda c: b6(c, l), dev))
print("dev-selected lambda: B4", lam4, " B6", lam6)
M = {"B0_bm25": lambda c: rank("B0_bm25", c), "B2_pubcut": lambda c: rank("B2_pubcut", c), "B3_validfilter": lambda c: rank("B3_validtime", c),
     "B6_soft_dist(approx)": lambda c: b6(c, lam6), "B4v1_routed_text": lambda c: twoclock(c, lam4), "B4v1_oracle_intent": lambda c: twoclock(c, lam4, False),
     "B4v1_no_semantic(lam=big)": lambda c: twoclock(c, 100.0)}
# need rank() for B0/B2/B3 from run_pilot-equivalents
rows = {}
for name, fn in M.items(): rows[name] = {id(c): score(fn(c), c) for c in test}
print("\nTEST (held-out families)  top1 / violation / nDCG@10")
print(f"{'method':28}" + "".join(f"{it:>20}" for it in INTENTS) + f"{'ALL':>20}")
for name in M:
    row = f"{name:28}"
    for it in INTENTS + ["ALL"]:
        v = [rows[name][id(c)] for c in test if it == "ALL" or c["intent"] == it]
        n = len(v); row += f"  {sum(x[0] for x in v)/n:4.2f}/{sum(x[1] for x in v)/n:4.2f}/{sum(x[2] for x in v)/n:4.2f}"
    print(row)
random.seed(1)
def boot(a, b, B=2000):
    d = [rows[a][id(c)][0] - rows[b][id(c)][0] for c in test]; n = len(d)
    ms = sorted(st.mean(random.choices(d, k=n)) for _ in range(B)); return st.mean(d), ms[int(.025 * B)], ms[int(.975 * B)]
print("\npaired bootstrap, top1 difference (mean, 95% CI), n_test =", len(test))
for b in ["B0_bm25", "B2_pubcut", "B3_validfilter", "B6_soft_dist(approx)", "B4v1_oracle_intent"]:
    print(f"B4v1_routed_text - {b}: %.3f [%.3f, %.3f]" % boot("B4v1_routed_text", b))
print("router accuracy vs labelled intent (test+dev): %.3f" % st.mean(route(query(c)) == c["intent"] for c in dev + test))

# family-cluster bootstrap on the fresh confirmatory split (test2 only; not used for any selection)
def cboot(a, b, cs, B=2000):
    byf = {}
    for c in cs: byf.setdefault(c["family"], []).append(rows[a][id(c)][0] - rows[b][id(c)][0])
    F = list(byf); ms = []
    for _ in range(B):
        d = [x for f in random.choices(F, k=len(F)) for x in byf[f]]; ms.append(st.mean(d))
    ms.sort(); allv = [x for f in F for x in byf[f]]; return st.mean(allv), ms[int(.025 * B)], ms[int(.975 * B)]
print("\nFAMILY-CLUSTER bootstrap, test2 only (n cases=%d, families=%d), top-1 diff of B4v1_routed_text" % (len(test2), len({c['family'] for c in test2})))
for b in ["B0_bm25", "B2_pubcut", "B3_validfilter", "B6_soft_dist(approx)", "B4v1_no_semantic(lam=big)"]:
    print(f"  - {b}: %.3f [%.3f, %.3f]" % cboot("B4v1_routed_text", b, test2))
for nm, cs in [("test1 (orig 5 fam)", test1), ("test2 (35 new fam)", test2)]:
    print(nm, "B4 top1 %.2f | B3 %.2f | B2 %.2f | B6 %.2f" % tuple(st.mean(rows[m][id(c)][0] for c in cs) for m in ["B4v1_routed_text", "B3_validfilter", "B2_pubcut", "B6_soft_dist(approx)"]))
# error taxonomy for B4 on test2 (counts only; no per-case test inspection beyond category)
cat = collections.Counter()
for c in test2:
    r = twoclock(c, lam4); g = gold(c)
    if r and r[0] != g: cat["wrong version, same family" if C[r[0]]["family"] == C[g]["family"] else "other family"] += 1
    elif not r: cat["no eligible candidate"] += 1
print("B4 errors on test2:", dict(cat), "of", len(test2))

# ---- B4v2: semantic-gated eligibility. Keep candidates within delta z-units of the best semantic score in the pool,
# then pick by temporal gap among the eligible ones. delta chosen on dev families only (same protocol as lambda).
def gated(c, delta):
    q = query(c); it = route(q); s = bm25(q); pool = sorted(s, key=s.get, reverse=True)[:20]; zs = z(s, pool); zmax = max(zs.values())
    ok = [i for i in pool if elig(i, c, it) and zs[i] >= zmax - delta]
    return sorted(ok, key=lambda i: (gapdays(i, c, it), -zs[i]))
DG = [0.25, 0.5, 1, 1.5, 2, 3, 100]
d4 = max(DG, key=lambda d: mean_top1(lambda c: gated(c, d), dev))
print("\nB4v2 gated: dev-selected delta =", d4)
for nm, cs in [("test1", test1), ("test2", test2)]:
    print(nm, "B4v2 top1 %.2f viol %.2f | B4v1 %.2f" % (st.mean(score(gated(c, d4), c)[0] for c in cs), st.mean(score(gated(c, d4), c)[1] for c in cs), st.mean(rows["B4v1_routed_text"][id(c)][0] for c in cs)))
rows["B4v2_gated"] = {id(c): score(gated(c, d4), c) for c in test}
for it in INTENTS: print(" ", it, "B4v2 top1 %.2f" % st.mean(rows["B4v2_gated"][id(c)][0] for c in test if c["intent"] == it))
print("cluster bootstrap test2 B4v2 - B4v1: %.3f [%.3f, %.3f]" % cboot("B4v2_gated", "B4v1_routed_text", test2))
print("cluster bootstrap test2 B4v2 - B3: %.3f [%.3f, %.3f]" % cboot("B4v2_gated", "B3_validfilter", test2))
cat = collections.Counter()
for c in test2:
    r = gated(c, d4); g = gold(c)
    cat["ok" if r and r[0] == g else ("none eligible" if not r else ("same family wrong version" if C[r[0]]["family"] == C[g]["family"] else "other family"))] += 1
print("B4v2 outcomes test2:", dict(cat))

# ---- test3: fresh confirmatory batch, FROZEN config set before mining (lambda=2, delta=1.5, router v2); nothing selected on it.
FL, FD = 2.0, 1.5
if test3:
    r3 = {"B0_bm25": lambda c: rank("B0_bm25", c), "B2_pubcut": lambda c: rank("B2_pubcut", c), "B3_validfilter": lambda c: rank("B3_validtime", c),
          "B6_soft_dist(approx)": lambda c: b6(c, 4.0), "B4v1_frozen(lam=2)": lambda c: twoclock(c, FL), "B4v2_frozen(delta=1.5)": lambda c: gated(c, FD)}
    R3 = {m: {id(c): score(fn(c), c) for c in test3} for m, fn in r3.items()}
    print("\nTEST3 (fresh batch, frozen config): families", len({c['family'] for c in test3}), "cases", len(test3), " [B6 lambda=4 = value selected on dev earlier]")
    print(f"{'method':26}" + "".join(f"{it:>20}" for it in INTENTS) + f"{'ALL':>20}   top1/viol/ndcg")
    for m in R3:
        row = f"{m:26}"
        for it in INTENTS + ["ALL"]:
            v = [R3[m][id(c)] for c in test3 if it == "ALL" or c["intent"] == it]; row += f"  {st.mean(x[0] for x in v):4.2f}/{st.mean(x[1] for x in v):4.2f}/{st.mean(x[2] for x in v):4.2f}"
        print(row)
    rows.update(R3)
    for a, b in [("B4v2_frozen(delta=1.5)", "B4v1_frozen(lam=2)"), ("B4v2_frozen(delta=1.5)", "B3_validfilter"), ("B4v2_frozen(delta=1.5)", "B2_pubcut"), ("B4v2_frozen(delta=1.5)", "B6_soft_dist(approx)"), ("B4v1_frozen(lam=2)", "B3_validfilter")]:
        print(f"cluster bootstrap test3 {a} - {b}: %.3f [%.3f, %.3f]" % cboot(a, b, test3))
