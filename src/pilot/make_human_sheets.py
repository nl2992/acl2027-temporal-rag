"""Blank sheets for the human query study (see annotation/human_v2/TODO.md). Run from the repo root.
    python3 -B src/pilot/make_human_sheets.py writer          # writer_A.csv, writer_B.csv (60 cases each)
    python3 -B src/pilot/make_human_sheets.py labeller        # after writer files are in returned/: labeller_C.csv, labeller_D.csv
120 test5 cases, 30 per question type, at most two per rule family, fixed seed. No gold answers are written anywhere."""
import csv, json, os, sys, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["VALID_TO"] = "2"   # same validity level as the evaluation, so no-answer cases are sampled at their natural rate
from common import C, cases, gold

OUT = "annotation/human_v2"
INTENTS = ["current", "valid_at", "known_at", "valid_known"]
ASK = {"current": "Which version is in force today (23 November 2026)?",
       "valid_at": "Which version was in force on {t}? You may use anything published since.",
       "known_at": "Which was the most recent version published by {h}, even if not yet in force?",
       "valid_known": "Using only what had been published by {h}, which version was in force on {t}?"}

def picked():
    split = json.load(open("annotation/split_v5.json"))
    test = [c for c in cases if split.get(c["family"]) == "test5" and gold(c)]
    rng = random.Random(2027); used = collections.Counter(); out = []
    for it in ["known_at", "valid_known", "valid_at", "current"]:
        pool = [c for c in test if c["intent"] == it]; rng.shuffle(pool); n = 0
        for c in pool:
            if n < 30 and used[c["family"]] < 2: used[c["family"]] += 1; out.append(c); n += 1
        assert n == 30, (it, n)
    rng.shuffle(out)
    return [(f"H{k:03d}", c) for k, c in enumerate(out, 1)]

def links(cid, fam):
    ids = sorted(i for i in C if C[i]["family"] == fam); random.Random(cid).shuffle(ids)
    return " ; ".join(f"https://www.federalregister.gov/d/{i}" for i in ids)

def write(name, header, rows):
    path = f"{OUT}/{name}"
    assert not os.path.exists(path), f"{path} exists; refusing to overwrite"
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(header); w.writerows(rows)
    print(path, len(rows), "rows")

os.makedirs(OUT, exist_ok=True)
items = picked()
if sys.argv[1] == "writer":
    for name, part in (("writer_A.csv", items[:60]), ("writer_B.csv", items[60:])):
        write(name, ["case_id", "what_your_question_must_ask", "documents", "your_question", "notes"],
              [[cid, ASK[c["intent"]].format(t=c["t"], h=c["h"]), links(cid, c["family"]), "", ""] for cid, c in part])
else:
    q = {}
    for name in ("writer_A.csv", "writer_B.csv"):
        for r in csv.DictReader(open(f"{OUT}/returned/{name}")): q[r["case_id"]] = r["your_question"].strip()
    missing = [cid for cid, _ in items if not q.get(cid)]
    assert not missing, f"no question for {missing}"
    # C takes the first half, D the second; each also takes 20 of the other's rows for agreement
    for name, part in (("labeller_C.csv", items[:60] + items[60:80]), ("labeller_D.csv", items[60:] + items[:20])):
        part = list(part); random.Random(name).shuffle(part)
        write(name, ["case_id", "question", "documents", "best_document_number_or_NONE", "confidence_high_medium_low", "notes"],
              [[cid, q[cid], links(cid, c["family"]), "", "", ""] for cid, c in part])
