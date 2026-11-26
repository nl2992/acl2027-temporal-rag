"""Analyses added after ARIS review round 1 (post hoc; every setting is the frozen or dev-chosen one). Run from the repo root:
    python3 -B src/pilot/review_fixes.py            # BM25
    .venv/bin/python -B src/pilot/review_fixes.py --dense
1. Two-date probes: each test5 valid-known case with t kept and h moved to t-180 and t+365 days (h capped at today).
2. How often a correct/withdraw/postpone notice is the known-at gold answer or v2's known-at top result.
3. On the Codex-written questions: which router errors change v2's answer.
Added after round 2:
4. Two-date probes: exact (t, h) recovery by the parser (true intent given), and v2 with true intent and dates (diagnostic only).
5. Families whose rules cite CFR parts with no overlap (title clusters that are not one version chain), and results without them."""
import os, sys, csv, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "controls_test5.py")).read().split('print(f"scorer')[0])
from common import is_notice

G = [(K, d) for K in KS for d in DELTAS]
cfg = {n: dev_pick(n, G) for n in ("B2", "B3")}
nr = dev_pick("v2", G, fixed="valid_known")
SW = {it: max(("B3", "B2"), key=lambda n: top1(evaluate(lambda c: run(n, c, *cfg[n]), [c for c in dev if route2(query(c)) == it]))) for it in INTENTS}
K, DL = FROZEN
print(f"scorer: {'bge-small-en-v1.5' if DENSE else 'BM25'}")

template = common.query
def two_date(c): return f"{c['topic']} rule in effect on {D(c['t']):%B %d, %Y} as known on {D(c['h']):%B %d, %Y}"
base = [c for c in test if c["intent"] == "valid_known"]
for off in (-180, 365):
    new = []
    for c in base:
        h = min(D(c["t"]) + dt.timedelta(days=off), TODAY)
        if h != D(c["t"]): new.append({**c, "h": h.isoformat()})
    for c in new: GOLD[id(c)] = gold(c)
    query = two_date
    print(f"\n## two-date probes, h = t{off:+d} days: {len(new)} cases, no answer {st.mean(GOLD[id(c)] == 'NONE' for c in new):.3f}, "
          f"router says valid_known {st.mean(route2(query(c)) == 'valid_known' for c in new):.3f}, "
          f"gold differs from the h=t gold {st.mean(GOLD[id(c)] != gold({**c, 'h': c['t']}) for c in new):.3f}")
    SYS = {"B2 gated": lambda c: run("B2", c, *cfg["B2"]), "B3 gated": lambda c: run("B3", c, *cfg["B3"]),
           "require both clocks, no router": lambda c: run("v2", c, *nr, fixed="valid_known"),
           "router over B2/B3 gated": lambda c: run(SW[route2(query(c))], c, *cfg[SW[route2(query(c))]]),
           "v2": lambda c: run("v2", c, K, DL)}
    for name, fn in SYS.items():
        r = evaluate(fn, new); print(f"  {name:34} top1 {top1(r):.3f}  inadm {st.mean(x[1] for x in r):.3f}")
    print(f"  parser returns the right (t, h) with the true intent: {st.mean(resolve(query(c), 'valid_known') == (D(c['t']), D(c['h'])) for c in new):.3f}")
    r = evaluate(lambda c: run("v2", c, K, DL, mode="meta", fixed="valid_known"), new)
    print(f"  {'diagnostic: v2, true intent and dates':34} top1 {top1(r):.3f}  inadm {st.mean(x[1] for x in r):.3f}")
query = template

ka = [c for c in test if c["intent"] == "known_at"]
print(f"\n## notices on known-at cases ({len(ka)}): gold is a notice in {sum(GOLD[id(c)] != 'NONE' and is_notice(GOLD[id(c)]) for c in ka)}, "
      f"v2 top result is a notice in {sum(bool(r) and is_notice(r[0]) for r in (run('v2', c, K, DL) for c in ka))}")

src = open(os.path.join(HERE, "make_human_sheets.py")).read()
exec(src[src.index("ASK = {"):src.index("def write(")])
HQ = {r["case_id"]: r["your_question"] for L in "AB" for r in csv.DictReader(open(f"annotation/codex_sim/writer_{L}.csv"))}
print("\n## router errors on Codex-written questions: errors / errors that change v2's top result / hit with routed, with true intent")
for it in INTENTS:
    err = chg = a = b = 0
    for cid, c in picked():
        if c["intent"] != it: continue
        q = HQ[cid]
        x = run("v2", c, K, DL, q=q)[:1]; y = run("v2", c, K, DL, q=q, fixed=it)[:1]
        a += outcome(x, c)[0]; b += outcome(y, c)[0]
        if route2(q) != it: err += 1; chg += x != y
    print(f"  {it:12} {err:2d} / {chg:2d} / {a} vs {b} of 30")

import ast, collections
def parts(i):
    r = C[i].get("cfr_references"); r = ast.literal_eval(r) if isinstance(r, str) else r or []
    return {(str(x.get("title")), str(x.get("part"))) for x in r}
members = collections.defaultdict(list)
for i in C: members[C[i]["family"]].append(i)
def mixed(ids):   # more than one connected component under "shares a CFR part"
    groups = []
    for i in ids:
        p = parts(i)
        for g in [g for g in groups if g & p]: p |= g; groups.remove(g)
        groups.append(p)
    return len(groups) > 1
bad = {f for f, v in members.items() if mixed(v)}
tf = {c["family"] for c in test}; keep = [c for c in test if c["family"] not in bad]
print(f"\n## families with non-overlapping CFR parts: {len(bad)} of {len(members)}; in test5 {len(bad & tf)} of {len(tf)} ({len(test) - len(keep)} cases)")
for name, fn in (("B3 gated", lambda c: run("B3", c, *cfg["B3"])), ("router over B2/B3 gated", lambda c: run(SW[route2(query(c))], c, *cfg[SW[route2(query(c))]])),
                 ("v2", lambda c: run("v2", c, K, DL))):
    print(f"  without them ({len(keep)} cases) {name:26} top1 {top1(evaluate(fn, keep)):.3f}")
