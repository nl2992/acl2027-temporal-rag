"""Codex stand-in for the human query study (annotation/human_v2/TODO.md). These are MODEL outputs, never human data. Run from the repo root:
    python3 -B src/pilot/codex_sim.py write      # writers A, B (two models)
    python3 -B src/pilot/codex_sim.py label      # labellers C, D (two models), 40 cases shared
    python3 -B src/pilot/codex_sim.py score      # add --dense (use .venv/bin/python) for the dense scorer
Each role gets the instructions the people get, and the title, publication date and DATES statement of the linked rules (what the web page shows).
No intent label, effective-date field, gold or code is given. The scoring below was written before any Codex output was read."""
import os, sys, csv, json, random, re, collections, statistics as st
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
DENSE_FLAG = "--dense" in sys.argv
exec(open(os.path.join(HERE, "controls_test5.py")).read().split('print(f"scorer')[0])   # splits, retrieval, run(), cboot()
sys.path.insert(0, HERE)
import codex_call

SHEETS, OUT, RAW = "annotation/human_v2", "annotation/codex_sim", "reports/codex_sim/raw"
MODELS = {"A": "gpt-6.1-sol", "B": "gpt-6.1-terra", "C": "gpt-6.1-sol", "D": "gpt-6-astra"}
_src = open(os.path.join(HERE, "make_human_sheets.py")).read()
exec(_src[_src.index("ASK = {"):_src.index("def write(")])
ITEMS = picked(); CASE = dict(ITEMS)
ids_of = lambda s: [u.rsplit("/", 1)[-1] for u in s.split(" ; ")]

def rows(path): return list(csv.DictReader(open(path)))
def doc_line(i): d = C[i]; return f"- {i} | {d['title']} | published {d['publication_date']} | DATES: {' '.join((d.get('dates_text') or '').split())[:400]}"
def words(s): return re.findall(r"[a-z0-9]+", s.lower())

def problems(q, c, ids):
    """The writing rules from the TODO, checked mechanically."""
    out, w = [], words(q)
    grams = {tuple(t[k:k + 4]) for i in ids for t in [words(C[i]["title"])] for k in range(len(t) - 3)}
    if any(tuple(w[k:k + 4]) in grams for k in range(len(w) - 3)): out.append("copies more than three consecutive title words")
    if any(i in q for i in ids): out.append("contains a document number")
    if re.search(r"valid time|known time|publication time", q, re.I): out.append("uses a banned term")
    need = {"valid_at": ["t"], "known_at": ["h"], "valid_known": ["t", "h"], "current": []}[c["intent"]]
    if any(c[k][:4] not in q and c[k][2:4] not in q for k in need): out.append("a required date is missing")
    return out

WRITE = """You are writing search questions for a study, as a person would ask a colleague. Today is 23 November 2026.
For each case you are told what the question must ask and are shown some official rules that are versions of one recurring rule.
Write one question per case.
- Keep the meaning and the exact date(s). Write the date any way you like.
- Say enough to identify the rule: the product, species, place, bridge, agency or programme.
- Do not copy the title. No more than three words in a row from it.
- No document numbers and no links.
- Do not use the words "valid time", "known time" or "publication time".
- Do not reuse the wording of the instruction for what to ask. Vary your phrasing between cases.
Reply with one JSON object only, mapping each case id to your question."""

LABEL = """You are choosing which official rule answers each question. Today is 23 November 2026. Judge only from the information shown.
- "Published by" a day means the publication date is on or before that day.
- "In force" means the rule has taken effect and has not ended, been withdrawn or been postponed.
- If several rules qualify, choose the most recent one. If none does, answer NONE.
Reply with one JSON object only, mapping each case id to {"answer": document number or "NONE", "confidence": "high" | "medium" | "low", "note": short text, may be empty}."""

def batches(letter, parts, size, build):
    jobs = [(f"{RAW}/{letter}_{b // size:02d}.json", build(parts[b:b + size])) for b in range(0, len(parts), size)]
    with ThreadPoolExecutor(4) as ex: ok = list(ex.map(lambda j: codex_call.call(j[0], j[1], MODELS[letter]), jobs))
    assert all(ok), f"{letter}: {ok.count(False)} calls failed; run again to retry them"
    ans = {}
    for p, _ in jobs: ans.update(json.load(open(p))["answers"])
    return ans

def write():
    os.makedirs(OUT, exist_ok=True); os.makedirs(RAW, exist_ok=True)
    for letter in "AB":
        sheet = rows(f"{SHEETS}/writer_{letter}.csv")
        def block(r):   # "open a few of the links": the first three in the sheet's shuffled order
            return f"### {r['case_id']}\nthe question must ask: {r['what_your_question_must_ask']}\nrules:\n" + "\n".join(map(doc_line, ids_of(r["documents"])[:3]))
        ans = batches(letter, sheet, 10, lambda rs: WRITE + "\n\n" + "\n\n".join(map(block, rs)))
        bad = [(r, problems(str(ans.get(r["case_id"], "")), CASE[r["case_id"]], ids_of(r["documents"]))) for r in sheet]
        bad = [(r, p) for r, p in bad if p or not ans.get(r["case_id"])]
        sent_back = len(bad)
        if bad:   # the owner "sends those rows back" once
            p = f"{RAW}/{letter}_retry.json"
            assert codex_call.call(p, WRITE + "\n\nYour earlier questions for these cases broke a rule. Rewrite them.\n\n" + "\n\n".join(
                f"{block(r)}\nearlier question: {ans.get(r['case_id'])}\nproblem: {', '.join(pr)}" for r, pr in bad), MODELS[letter])
            ans.update(json.load(open(p))["answers"])
        left = 0
        with open(f"{OUT}/writer_{letter}.csv", "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["case_id", "what_your_question_must_ask", "documents", "your_question", "notes"])
            for r in sheet:
                q = str(ans[r["case_id"]]).strip(); pr = problems(q, CASE[r["case_id"]], ids_of(r["documents"])); left += bool(pr)
                w.writerow([r["case_id"], r["what_your_question_must_ask"], r["documents"], q, f"model={MODELS[letter]}; " + "; ".join(pr)])
        print(f"writer {letter} ({MODELS[letter]}): {len(sheet)} questions, {sent_back} sent back, {left} still break a rule (kept)")

def questions():
    return {r["case_id"]: r["your_question"] for L in "AB" for r in rows(f"{OUT}/writer_{L}.csv")}

def label():
    q = questions()
    for letter, part in (("C", ITEMS[:60] + ITEMS[60:80]), ("D", ITEMS[60:] + ITEMS[:20])):
        part = list(part); random.Random(letter).shuffle(part)
        def block(item):
            cid, c = item; ids = sorted(i for i in C if C[i]["family"] == c["family"]); random.Random(cid).shuffle(ids)
            return f"### {cid}\nquestion: {q[cid]}\nrules:\n" + "\n".join(map(doc_line, ids))
        ans = batches(letter, part, 5, lambda xs: LABEL + "\n\n" + "\n\n".join(map(block, xs)))
        with open(f"{OUT}/labeller_{letter}.csv", "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["case_id", "question", "best_document_number_or_NONE", "confidence_high_medium_low", "notes"])
            for cid, c in part:
                a = ans[cid]; w.writerow([cid, q[cid], a["answer"], a.get("confidence", ""), f"model={MODELS[letter]}; {a.get('note', '')}"])
        print(f"labeller {letter} ({MODELS[letter]}): {len(part)} answers")

def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b); pe = sum(ca[k] * cb[k] for k in ca) / n ** 2
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0

def score():
    G = [(K, d) for K in KS for d in DELTAS]
    cfg = {n: dev_pick(n, G) for n in ("B2", "B3")}            # all settings chosen on dev template queries, as before
    nr = dev_pick("v2", G, fixed="valid_known")
    SW = {}
    for it in INTENTS:
        cs = [c for c in dev if route2(common.query(c)) == it]
        SW[it] = max(("B3", "B2"), key=lambda n: top1(evaluate(lambda c: run(n, c, *cfg[n]), cs)))
    K, DL = FROZEN
    hq = questions(); cids = [i for i, _ in ITEMS]; cs = [CASE[i] for i in cids]
    cid_of = {id(CASE[i]): i for i in cids}; template = common.query
    lab = {L: {r["case_id"]: r["best_document_number_or_NONE"].strip() for r in rows(f"{OUT}/labeller_{L}.csv")} for L in "CD"}
    shared = [i for i in cids if i in lab["C"] and i in lab["D"]]
    po, k = kappa([lab["C"][i] for i in shared], [lab["D"][i] for i in shared])
    ref = {}   # labeller answer; disagreements on shared cases are left out, not adjudicated
    for i in cids:
        a = {lab[L][i] for L in "CD" if i in lab[L]}
        if len(a) == 1: ref[i] = a.pop()
    key = {i: GOLD[id(CASE[i])] for i in cids}
    print(f"scorer: {'bge-small-en-v1.5' if DENSE else 'BM25'} | {len(cids)} cases | CODEX stand-in, not human data")
    print(f"labellers on {len(shared)} shared cases: agreement {po:.3f}, Cohen's kappa {k:.3f}")
    print(f"labeller answer vs metadata key: {st.mean(ref[i] == key[i] for i in ref):.3f} on {len(ref)} cases (disagreements left out: {len(cids) - len(ref)})")
    for L in "CD": print(f"  labeller {L} vs key: {st.mean(v == key[i] for i, v in lab[L].items()):.3f}")
    miss = collections.Counter(("key NONE" if key[i] == "NONE" else "labeller NONE" if ref[i] == "NONE" else "different document") for i in ref if ref[i] != key[i])
    print("  disagreements with the key:", dict(miss))
    print(f"router accuracy: template {st.mean(route2(template(c)) == c['intent'] for c in cs):.3f}, codex-written {st.mean(route2(hq[cid_of[id(c)]]) == c['intent'] for c in cs):.3f}")
    def dates_ok(c):
        r = resolve(hq[cid_of[id(c)]], c["intent"])
        need = {"current": (), "valid_at": (0,), "known_at": (1,), "valid_known": (0, 1)}[c["intent"]]
        return bool(r) and all(str(r[j]) == (c["t"], c["h"])[j] for j in need)
    print(f"parser finds the required dates (true intent given): {st.mean(map(dates_ok, cs)):.3f}")
    SYS = {"B2 gated": lambda c: run("B2", c, *cfg["B2"]), "B3 gated": lambda c: run("B3", c, *cfg["B3"]),
           "require both clocks, no router": lambda c: run("v2", c, *nr, fixed="valid_known"),
           "router over B2/B3 gated": lambda c: run(SW[route2(common_q(c))], c, *cfg[SW[route2(common_q(c))]]),
           "v1": lambda c: run("v1", c, K), "v2": lambda c: run("v2", c, K, DL),
           "v2, oracle intent and dates": lambda c: run("v2", c, K, DL, mode="meta", fixed=c["intent"])}
    out = {}
    for wording, fn in (("template", template), ("codex-written", lambda c: hq[cid_of[id(c)]])):
        globals()["query"] = fn; globals()["common_q"] = fn
        print(f"\n## {wording} questions, same {len(cs)} cases")
        print(f"{'system':34} {'vs key':>7} {'vs labels':>10}   by question type (vs key)")
        for name, s in SYS.items():
            top = {i: (lambda r: r[0] if r else "NONE")(s(CASE[i])) for i in cids}
            hit = {i: int(top[i] == key[i]) for i in cids}
            out[wording, name] = hit
            by = " ".join(f"{it} {st.mean(hit[i] for i in cids if CASE[i]['intent'] == it):.2f}" for it in INTENTS)
            print(f"{name:34} {st.mean(hit.values()):7.3f} {st.mean(top[i] == ref[i] for i in ref):10.3f}   {by}")
    print("\nfamily-cluster bootstrap on codex-written questions, top-1 vs key")
    def boot(a, b, B=4000):
        byf = collections.defaultdict(list)
        for i in cids: byf[CASE[i]["family"]].append(a[i] - b[i])
        F = list(byf); rng = random.Random(5)
        ms = sorted(st.mean([d for f in rng.choices(F, k=len(F)) for d in byf[f]]) for _ in range(B))
        return st.mean(d for f in F for d in byf[f]), ms[int(.025 * B)], ms[int(.975 * B)]
    for other in ("router over B2/B3 gated", "B3 gated", "require both clocks, no router"):
        print(f"  v2 minus {other:32} %.3f [%.3f, %.3f]" % boot(out["codex-written", "v2"], out["codex-written", other]))

{"write": write, "label": label, "score": score}[[a for a in sys.argv[1:] if not a.startswith("--")][0]]()
