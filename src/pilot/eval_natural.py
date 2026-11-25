"""End-to-end on natural-language query text: router v2 picks intent; t,h come from case metadata (date parsing not yet implemented).
Uses lambda=1 chosen on dev in method_v1. Query sets: drafts (author-written, router-seen) -> replace with teammate rewrites via --col."""
import sys, json, csv, io, contextlib, statistics as st, collections
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
from router import route2
from dateparse import resolve
col = sys.argv[1] if len(sys.argv) > 1 else "draft_query_1"
key = {k["case_id"]: k for k in json.load(open("annotation/GOLD_KEY_do_not_share_with_annotators.json"))}
rows = [r for r in csv.DictReader(open("annotation/queries_to_rewrite.csv")) if r[col].strip()]
def run(method, q, c):
    it = route2(q) if method.startswith("B4_v2") else c["intent"]
    if method == "B4_v2router_parsed":   # t,h parsed from the query text; abstain to BM25 if no date found
        rs = resolve(q, it)
        if rs is None: s0 = bm25(q); return sorted(s0, key=s0.get, reverse=True)[:20]
        c = {**c, "t": rs[0].isoformat(), "h": rs[1].isoformat()}
    if method in ("B0", "B2", "B3"):
        s = bm25(q); top = sorted(s, key=s.get, reverse=True)[:20]; t, h = D(c["t"]), D(c["h"])
        if method == "B0": return top
        if method == "B2": return sorted([i for i in top if pub(i) <= h], key=lambda i: (pub(i), s[i]), reverse=True)
        return sorted([i for i in top if eff(i) <= t], key=lambda i: (eff(i), s[i]), reverse=True)
    s = bm25(q); pool = sorted(s, key=s.get, reverse=True)[:20]; zs = z(s, pool)
    ok = [i for i in pool if elig(i, c, it)]
    return sorted(ok, key=lambda i: zs[i] - 1.0 * math.log1p(gapdays(i, c, it) / 30), reverse=True)
out = collections.defaultdict(list)
for r in rows:
    k = key[r["case_id"]]; c = {"family": k["family"], "intent": k["intent"], "t": k["t"], "h": k["h"], "topic": k["topic"]}
    for m in ["B0", "B2", "B3", "B4_v2router", "B4_v2router_parsed", "B4_oracle_intent"]:
        rk = run(m, r[col], c); g = k["gold_doc"]
        out[m].append((k["split"], int(bool(rk) and rk[0] == g), int(bool(rk) and not admissible(rk[0], c))))
print(f"query column: {col}; n={len(rows)}; router acc {st.mean(route2(r[col]) == r['intended_semantics'] for r in rows):.2f}")
for m, v in out.items():
    print(f"{m:18} top1 all {st.mean(x[1] for x in v):.2f} | test {st.mean(x[1] for x in v if x[0]=='test'):.2f} | inadmissible {st.mean(x[2] for x in v):.2f}")
