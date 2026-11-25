"""Q-TIE-STYLE CONCEPTUAL BASELINE (not a reproduction; official repo github.com/ssoy0701/Q-TIE returned 404 on 2026-11-23).
Idea taken from the abstract: map the query's temporal constraint to an interval <t_start, t_end>, score documents' timestamps against it
as a separate signal, combine with semantic score. Here the 'TIE model' is our regex date parser (interval = [t, t]; current = [today, today]).
Two variants differ only in which document clock is compared: publication date (typical document timestamp) or effective date.
No horizon h is modelled, as in the abstract. lambda chosen on dev families only."""
import sys, io, contextlib, statistics as st, math
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
def qtie(c, lam, clock):
    q = query(c); s = bm25(q); pool = sorted(s, key=s.get, reverse=True)[:20]; zs = z(s, pool)
    t = D(c["t"]) if c["intent"] != "known_at" else D(c["h"])   # the one date in the query
    if c["intent"] == "valid_at": t = D(c["t"])
    f = (lambda i: pub(i)) if clock == "pub" else (lambda i: eff(i))
    return sorted(pool, key=lambda i: zs[i] - lam * math.log1p(abs((t - f(i)).days) / 30), reverse=True)
res = {}
for clock in ("pub", "eff"):
    lam = max(GRID + [8], key=lambda l: mean_top1(lambda c: qtie(c, l, clock), dev))
    r = {id(c): score(qtie(c, lam, clock), c) for c in test}; res[clock] = (lam, r)
    print(f"Q-TIE-style[{clock}] lambda={lam}")
    for it in INTENTS + ["ALL"]:
        v = [r[id(c)] for c in test if it == "ALL" or c["intent"] == it]
        print(f"  {it:12} top1 {st.mean(x[0] for x in v):.2f}  inadmissible {st.mean(x[1] for x in v):.2f}  nDCG {st.mean(x[2] for x in v):.2f}  (n={len(v)})")
for nm, cs in [("test1", test1), ("test2", test2)]:
    print(nm, " ".join(f"Qtie[{k}] {st.mean(res[k][1][id(c)][0] for c in cs):.2f}" for k in res), f"B4v2 {st.mean(score(gated(c, d4), c)[0] for c in cs):.2f}" if False else "")
