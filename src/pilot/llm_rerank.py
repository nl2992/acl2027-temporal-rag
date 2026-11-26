"""LLM re-ranker baseline through the Claude Code CLI (`claude -p`, all tools disabled, run from an empty folder). Run from the repo root:
    python3 -B src/pilot/llm_rerank.py smoke    # 8 dev cases, checks the plumbing only
    python3 -B src/pilot/llm_rerank.py run      # 120 test5 cases (30 per intent, seed 12), two candidate sets
    python3 -B src/pilot/llm_rerank.py score
Add --codexq to run/score for the Codex-written stand-in questions. Add --codex to any stage to use the Codex CLI instead (results in reports/llm_rerank_codex/).
Candidate sets: 'gated' = the BM25 pool v2 sees (top 50 after the semantic gate, before eligibility); 'top20' = plain BM25 top 20.
The model gets the query text, today's date and, per candidate, title, publication date, effective date and DATES statement.
It gets no intent label, family or gold. One fixed prompt, not tuned on test5. Raw replies are kept in reports/llm_rerank/."""
import os, sys, json, random, subprocess, tempfile, re, shutil, collections, statistics as st
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "controls_test5.py")).read().split('print(f"scorer')[0])
assert not DENSE
sys.path.insert(0, HERE); import codex_call
CODEX = "--codex" in sys.argv   # same prompt and cases through `codex exec` instead of `claude -p`

OUT, MODEL, BATCH, DL = "reports/llm_rerank", "sonnet", 8, 1.5
# the CLI is often installed in ~/.local/bin, which not every shell has on PATH; CLAUDE_BIN overrides
CLAUDE = os.environ.get("CLAUDE_BIN") or shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
if CODEX: OUT, MODEL = "reports/llm_rerank_codex", "gpt-6.1-sol"
SYSTEM = """You pick which official rule answers each question. Today is November 23, 2026.
Judge only from the information given. A rule is published on one date, takes effect on its effective date, and may end on a date stated in its DATES text.
Notices that only correct, withdraw or postpone another rule are not versions of their own. If several rules qualify, choose the most recent one.
If no candidate qualifies, answer NONE.
Reply with one JSON object only, mapping each case id to the chosen document id or "NONE". No other text."""

def sample(cs, per, seed):
    rng = random.Random(seed); picked = []
    for it in INTENTS:
        x = [c for c in cs if c["intent"] == it]; rng.shuffle(x); picked += x[:per]
    rng.shuffle(picked); return picked

def candidates(c, mode):
    q = query(c)
    if mode == "gated":
        _, z = pool(q, 50); mx = max(z.values()); ids = [i for i in z if z[i] >= mx - DL]
    else:
        ids = list(pool(q, 20)[0])
    random.Random(q + mode).shuffle(ids); return ids   # no retrieval-rank hint

def block(n, c, mode):
    lines = [f"### case C{n:03d}", f"question: {query(c)}", "candidates:"]
    for i in candidates(c, mode):
        d = C[i]
        lines.append(f"- id {i} | {d['title'][:160]} | published {d['publication_date']} | effective {d['effective_on']} | DATES: {' '.join((d.get('dates_text') or '').split())[:200]}")
    return "\n".join(lines)

def call(args):
    path, prompt = args
    if os.path.exists(path): return
    if CODEX: codex_call.call(path, SYSTEM + "\n\n" + prompt, MODEL); return
    with tempfile.TemporaryDirectory() as empty:
        p = subprocess.run([CLAUDE, "-p", "--model", MODEL, "--tools", "", "--system-prompt", SYSTEM, "--output-format", "json",
                            "--no-session-persistence", "--setting-sources", "", "--strict-mcp-config"],
                           input=prompt, capture_output=True, text=True, cwd=empty, timeout=600)
    try:
        r = json.loads(p.stdout); assert not r.get("is_error"), r.get("result")
        ans = json.loads(re.search(r"\{.*\}", r["result"], re.S).group(0))
    except Exception as e:
        print("FAILED", path, p.returncode, str(e)[:200], p.stderr[:300], p.stdout[:300]); return
    json.dump({"answers": ans, "models": list(r.get("modelUsage", {})), "raw": r["result"], "prompt_chars": len(prompt)}, open(path, "w"), indent=1)

def jobs(tag, picked, mode):
    out = []
    for b in range(0, len(picked), BATCH):
        prompt = "\n\n".join(block(b + k + 1, c, mode) for k, c in enumerate(picked[b:b + BATCH]))
        out.append((f"{OUT}/{tag}_{mode}_{b // BATCH:02d}.json", prompt))
    return out

def answers(tag, mode):
    ans, models = {}, set()
    for f in sorted(os.listdir(OUT)):
        if f.startswith(f"{tag}_{mode}_"):
            r = json.load(open(f"{OUT}/{f}")); ans.update(r["answers"]); models.update(r.get("models") or [r["model"]])
    return ans, models

TEST = sample(test, 30, 12)
stage = sys.argv[1]
if "--codexq" in sys.argv:   # the 120 stand-in study cases with the Codex-written questions (src/pilot/codex_sim.py); not human data
    import csv
    src = open(os.path.join(HERE, "make_human_sheets.py")).read(); exec(src[src.index("ASK = {"):src.index("def write(")].replace("def picked", "def study_cases"))
    HQ = {r["case_id"]: r["your_question"] for L in "AB" for r in csv.DictReader(open(f"annotation/codex_sim/writer_{L}.csv"))}
    items = study_cases(); TEST = [c for _, c in items]; BY = {id(c): HQ[i] for i, c in items}
    query = lambda c: BY[id(c)]
    OUT += "_codexq"
    assert stage != "smoke"
os.makedirs(OUT, exist_ok=True)
if stage in ("smoke", "run"):
    if not CODEX and not os.path.isfile(CLAUDE): sys.exit(f"claude CLI not found at {CLAUDE}; set CLAUDE_BIN to its full path")
    if not CODEX and os.environ.get("CLAUDECODE"): sys.exit("This shell is inside a Claude Code session, where claude will not start. Run it from Terminal.app.")
    todo = []
    for mode in ("gated", "top20"):
        todo += jobs("smoke", sample(dev, 2, 1), mode) if stage == "smoke" else jobs("test5", TEST, mode)
    print(len(todo), "calls,", sum(len(p) for _, p in todo), "prompt characters")
    with ThreadPoolExecutor(4) as ex: list(ex.map(call, todo))
    for mode in ("gated", "top20"):
        a, m = answers("smoke" if stage == "smoke" else "test5", mode); print(mode, len(a), "answers", m)
else:
    rows = {}
    for mode in ("gated", "top20"):
        ans, models = answers("test5", mode)
        assert len(ans) == len(TEST), f"{mode}: {len(ans)} of {len(TEST)} answers"
        r, bad, inpool = [], 0, []
        for n, c in enumerate(TEST, 1):
            a = str(ans[f"C{n:03d}"]); cand = candidates(c, mode); g = GOLD[id(c)]
            inpool.append(g == "NONE" or g in cand)
            if a != "NONE" and a not in cand: bad += 1; r.append((0, 0)); continue
            r.append(outcome([] if a == "NONE" else [a], c))
        rows[f"LLM re-ranker, {mode}"] = r
        print(f"{mode}: models {sorted(models)} | mean candidates {st.mean(len(candidates(c, mode)) for c in TEST):.1f} | gold available {st.mean(inpool):.3f} | invalid ids {bad}")
    # the other systems on the same 120 cases
    CFG = {"B2": (100, 1.5), "B3": (50, 1.5)}   # dev-chosen in router_switch.py
    SW = {"current": "B3", "valid_at": "B3", "known_at": "B2", "valid_known": "B3"}
    rows["B3 gated"] = evaluate(lambda c: run("B3", c, *CFG["B3"]), TEST)
    rows["router over B2/B3 gated"] = evaluate(lambda c: run(SW[route2(query(c))], c, *CFG[SW[route2(query(c))]]), TEST)
    rows["v2"] = evaluate(lambda c: run("v2", c, 50, DL), TEST)
    print(f"\n{len(TEST)} test5 cases")
    for k, r in rows.items():
        by = " ".join(f"{it} {st.mean(x[0] for x, c in zip(r, TEST) if c['intent'] == it):.2f}" for it in INTENTS)
        print(f"{k:28} top1 {top1(r):.3f}  inadm {st.mean(x[1] for x in r):.3f}  | {by}")
    def boot(a, b, B=4000):
        byf = collections.defaultdict(list)
        for x, y, c in zip(rows[a], rows[b], TEST): byf[c["family"]].append(x[0] - y[0])
        F = list(byf); rng = random.Random(5)
        ms = sorted(st.mean([d for f in rng.choices(F, k=len(F)) for d in byf[f]]) for _ in range(B))
        return st.mean(d for f in F for d in byf[f]), ms[int(.025 * B)], ms[int(.975 * B)]
    print("\nfamily-cluster bootstrap, top-1 difference")
    for a in ("LLM re-ranker, gated", "LLM re-ranker, top20"):
        print(f"  {a} minus v2: %.3f [%.3f, %.3f]" % boot(a, "v2"))
