"""Controls on test5 (level-2 validity). Run from the repo root:
    python3 -B src/pilot/controls_test5.py            # BM25, stdlib only
    .venv/bin/python -B src/pilot/controls_test5.py --dense
Primary setting: intent from the cue router (router.route2), t and h from the regex parser (dateparse.resolve); no case metadata.
Rules without a router parse the query without knowing the intent (the one date is both t and h; no date means today).
Every pool size K and gate width delta is chosen on dev families only. These controls were added after test5 had been evaluated,
so they are post hoc, although no setting is chosen on test5."""
import os, sys, json, math, re, random, hashlib, functools, collections, statistics as st
os.environ["VALID_TO"] = "2"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import C, cases, D, pub, eff, inforce, tie, gold, admissible, query
from router import route2
from dateparse import resolve, find_dates, TODAY

DENSE = "--dense" in sys.argv
INTENTS = ["current", "valid_at", "known_at", "valid_known"]
KS, DELTAS, KMAX = (20, 50, 100), (0.5, 1.0, 1.5, 2.0, 3.0), 100
FROZEN = (100, 1.5) if DENSE else (50, 1.5)   # the paper's configuration

split = {}
for n in (1, 3, 4, 5): split.update(json.load(open(f"annotation/split_v{n}.json")))
for f in {c["family"] for c in cases}:
    split.setdefault(f, "test2" if int(hashlib.md5(f.encode()).hexdigest(), 16) % 3 == 0 else "dev2")
dev = [c for c in cases if split[c["family"]] in ("dev", "dev2") and gold(c)]
test = [c for c in cases if split[c["family"]] == "test5" and gold(c)]
GOLD = {id(c): gold(c) for c in dev + test}

if DENSE:
    from sentence_transformers import SentenceTransformer
    M = SentenceTransformer("BAAI/bge-small-en-v1.5", device="mps")
    ids = list(C)
    E = M.encode([C[i]["title"] + ". " + (C[i].get("abstract") or "") for i in ids], batch_size=64, normalize_embeddings=True, show_progress_bar=False)
    def scores(q):
        v = M.encode(["Represent this sentence for searching relevant passages: " + q], normalize_embeddings=True, show_progress_bar=False)[0]
        return dict(zip(ids, (E @ v).tolist()))
else:
    scores = common.bm25

@functools.lru_cache(maxsize=None)
def top(q):
    s = scores(q)
    return tuple((i, s[i]) for i in sorted(s, key=s.get, reverse=True)[:KMAX])

def pool(q, K):
    p = top(q)[:K]; v = [x for _, x in p]; m = st.mean(v); sd = st.pstdev(v) or 1.0
    return dict(p), {i: (x - m) / sd for i, x in p}

def elig(i, t, h, it):
    if it == "current": return inforce(i, h) and pub(i) <= h
    if it == "known_at": return pub(i) <= h
    if it == "valid_at": return inforce(i, t)
    return inforce(i, t) and pub(i) <= h

def gap(i, t, h, it):
    ref, clock = (h, pub(i)) if it == "known_at" else (t, eff(i))
    return max((ref - clock).days, 0)

def blind_dates(q):
    """(t, h) for a system with no router."""
    return resolve(q, "valid_known") or (TODAY, TODAY)

def inputs(c, q, mode, fixed=None):
    """Return (intent, t, h). mode: 'parsed' (router + parser) or 'meta' (template keywords + case metadata, as first reported)."""
    if mode == "meta":
        ql = q.lower()
        it = fixed or ("current" if "current" in ql else "valid_known" if "as known then" in ql else "known_at" if "announced" in ql else "valid_at")
        return it, D(c["t"]), D(c["h"])
    it = fixed or route2(q)
    rs = resolve(q, it)
    return (it, *rs) if rs else (it, None, None)

def run(name, c, K, delta=None, mode="parsed", q=None, fixed=None, family_only=False, lam=None):
    q = q or query(c); s, z = pool(q, K)
    cand = list(s)
    if family_only:   # oracle: candidates are exactly the gold rule's family
        full = scores(q); cand = [i for i in C if C[i]["family"] == c["family"]]
        s = {i: full[i] for i in cand}; z = {i: 0.0 for i in cand}
    zmax = max(z.values())
    if delta is not None: cand = [i for i in cand if z[i] >= zmax - delta]
    if name == "B0": return cand
    if name in ("B2", "B3", "B6", "qtie_pub", "qtie_eff", "re3"):
        t, h = (D(c["t"]), D(c["h"])) if mode == "meta" else blind_dates(q)
        if name == "B2": return sorted([i for i in cand if pub(i) <= h], key=lambda i: (pub(i), s[i]), reverse=True)
        if name == "B3": return sorted([i for i in cand if inforce(i, t)], key=lambda i: (eff(i), s[i]), reverse=True)
        if name == "B6": return sorted(cand, key=lambda i: z[i] - 4.0 * math.log1p(abs((t - pub(i)).days) / 30), reverse=True)
        if name == "re3":   # lam = (gate for date-free queries, gate for dated queries)
            g = lam[1] if find_dates(q) else lam[0]
            return sorted(cand, key=lambda i: z[i] - g * math.log1p(max((TODAY - pub(i)).days, 0) / 30), reverse=True)
        clock = pub if name == "qtie_pub" else eff
        return sorted(cand, key=lambda i: z[i] - lam * math.log1p(abs((t - clock(i)).days) / 30), reverse=True)
    it, t, h = inputs(c, q, mode, fixed)
    if t is None: return []
    if name == "no_elig": return sorted(cand, key=lambda i: (gap(i, t, h, it), *tie(i), -z[i]))
    if name == "no_elig_abs":   # as no_elig, but later documents are not given a zero gap
        d = lambda i: abs(((h - pub(i)) if it == "known_at" else (t - eff(i))).days)
        return sorted(cand, key=lambda i: (d(i), *tie(i), -z[i]))
    ok = [i for i in cand if elig(i, t, h, it)]
    if name == "v1": return sorted(ok, key=lambda i: z[i] - 2.0 * math.log1p(gap(i, t, h, it) / 30), reverse=True)
    return sorted(ok, key=lambda i: (gap(i, t, h, it), *tie(i), -z[i]))   # v2

def outcome(rk, c):
    g = GOLD[id(c)]
    ok = (not rk) if g == "NONE" else bool(rk) and rk[0] == g
    return (int(ok), int(bool(rk) and not admissible(rk[0], c)))

def evaluate(fn, cs=test): return [outcome(fn(c), c) for c in cs]
def top1(r): return st.mean(x[0] for x in r)

RESULTS = {}
def report(label, fn):
    r = evaluate(fn); RESULTS[label] = r
    by = " ".join(f"{it} {st.mean(x[0] for x, c in zip(r, test) if c['intent'] == it):.2f}" for it in INTENTS)
    print(f"{label:52} top1 {top1(r):.3f}  inadm {st.mean(x[1] for x in r):.3f}  | {by}")

def dev_pick(name, grid, **kw):
    """grid: list of (K, delta); ties go to the first entry."""
    return max(grid, key=lambda g: top1(evaluate(lambda c: run(name, c, g[0], g[1], **kw), dev)))

def cboot(a, b, B=2000):
    byf = collections.defaultdict(list)
    for x, y, c in zip(RESULTS[a], RESULTS[b], test): byf[c["family"]].append(x[0] - y[0])
    F = list(byf); rng = random.Random(5)
    ms = sorted(st.mean([d for f in rng.choices(F, k=len(F)) for d in byf[f]]) for _ in range(B))
    return st.mean(d for f in F for d in byf[f]), ms[int(.025 * B)], ms[int(.975 * B)]

print(f"scorer: {'bge-small-en-v1.5' if DENSE else 'BM25'} | dev cases {len(dev)} | test5 cases {len(test)}, families {len({c['family'] for c in test})}")
none = sum(GOLD[id(c)] == "NONE" for c in test)
print(f"gold NONE {none} ({none / len(test):.3f} = top-1 of always abstaining)")
kind = collections.Counter("fishery/quota" if re.search("fisher|quota", c["topic"], re.I) else "drawbridge" if "drawbridge" in c["topic"].lower() else "other" for c in test)
print("test5 topics:", dict(kind))
print("router accuracy on template queries:", round(st.mean(route2(query(c)) == c["intent"] for c in test), 3))

print("\n## main table (router + parser)")
PICK = {}
for name in ("B0", "B2", "B3", "B6"):
    g0 = dev_pick(name, [(K, None) for K in KS]); g1 = dev_pick(name, [(K, d) for K in KS for d in DELTAS])
    PICK[name] = (g0, g1)
    report(f"{name} ungated", lambda c: run(name, c, g0[0]))
    report(f"{name} gated", lambda c: run(name, c, g1[0], g1[1]))
    print(f"    dev-selected: ungated K={g0[0]}, gated K={g1[0]} delta={g1[1]}")
b = dev_pick("v2", [(K, d) for K in KS for d in DELTAS], fixed="valid_known")
report("require both clocks, no router", lambda c: run("v2", c, b[0], b[1], fixed="valid_known"))
print(f"    dev-selected: K={b[0]} delta={b[1]}")
K, DL = FROZEN
v2pick = dev_pick("v2", [(k, d) for k in KS for d in DELTAS])
print(f"v2 dev-selected K={v2pick[0]} delta={v2pick[1]}; reported with the frozen K={K} delta={DL}")
report("v1", lambda c: run("v1", c, K))
report("v2", lambda c: run("v2", c, K, DL))

print("\n## ablation (router + parser)")
for label, name, kw in [("fixed valid_at", "v2", dict(delta=DL, fixed="valid_at")), ("fixed known_at", "v2", dict(delta=DL, fixed="known_at")),
                        ("fixed valid_known", "v2", dict(delta=DL, fixed="valid_known")), ("no eligibility", "no_elig", dict(delta=DL)),
                        ("no eligibility, absolute gap", "no_elig_abs", dict(delta=DL)), ("no semantic gate", "v2", dict(delta=None))]:
    report(label, lambda c: run(name, c, K, **kw))

print("\n## diagnostics")
report("v2, oracle intent and dates (case metadata)", lambda c: run("v2", c, K, DL, mode="meta", fixed=c["intent"]))
report("v2, template keywords + metadata (first reported)", lambda c: run("v2", c, K, DL, mode="meta"))
report("v2, oracle family", lambda c: run("v2", c, K, family_only=True))
report("v2, title cut to 4 words", lambda c: run("v2", c, K, DL, q=query({**c, "topic": " ".join(c["topic"].split()[:4])})))

print("\n## Q-TIE-style and Re3-style stand-ins (not reproductions); strength chosen on dev, K=20")
for name in ("qtie_pub", "qtie_eff"):
    lam = max((0, .25, .5, 1, 2, 4, 8), key=lambda l: top1(evaluate(lambda c: run(name, c, 20, lam=l), dev)))
    report(f"{name} (lambda={lam})", lambda c: run(name, c, 20, lam=lam))
G = (-2, -1, -.5, 0, .25, .5, 1, 2, 4)
dcur = [c for c in dev if c["intent"] == "current"]; dold = [c for c in dev if c["intent"] != "current"]
gc = max(G, key=lambda g: top1(evaluate(lambda c: run("re3", c, 20, lam=(g, 0)), dcur)))
gh = max(G, key=lambda g: top1(evaluate(lambda c: run("re3", c, 20, lam=(0, g)), dold)))
report(f"re3 (gates {gc}, {gh})", lambda c: run("re3", c, 20, lam=(gc, gh)))

print("\n## family-cluster bootstrap, top-1 of v2 minus")
for other in ["v1", "require both clocks, no router"] + [f"{n} {g}" for n in ("B0", "B2", "B3", "B6") for g in ("ungated", "gated")] + ["no semantic gate"]:
    print(f"  {other:36} %.3f [%.3f, %.3f]" % cboot("v2", other))

summary = {label: {"top1": top1(r), "inadmissible": st.mean(x[1] for x in r),
                   **{it: st.mean(x[0] for x, c in zip(r, test) if c["intent"] == it) for it in INTENTS}}
           for label, r in RESULTS.items()}
with open(f"reports/pilot_controls_test5_{'dense' if DENSE else 'bm25'}.json", "w") as fh:
    json.dump({"abstain_always": none / len(test), "n": len(test), "methods": summary}, fh, indent=1)
