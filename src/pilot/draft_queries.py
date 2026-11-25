"""Draft natural-language queries (2 per case, no router keywords reused) for teammates to rewrite. Gold goes to a separate key file."""
import sys, csv, json, random
sys.path.insert(0, "src/pilot")
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
fmt = lambda s: D(s).strftime("%B %-d, %Y")
def short(c):
    x = c["topic"].replace("; ", ": ").strip()
    if len(x) > 85: x = x[:85].rsplit(" ", 1)[0]
    return x + (")" if x.count("(") > x.count(")") else "")
T = {"valid_at": ["According to the official record as it stands today, which version of the {x} rules governed on {t}?",
                  "Looking back from today, what {x} requirements actually applied on {t}?"],
     "known_at": ["On {h}, what was the most recent {x} rule that had been published?",
                  "An analyst checked the Federal Register on {h}: which {x} rule could they have found?"],
     "valid_known": ["Using only what had been published by {h}, which {x} rule was in force on {t}?",
                     "A compliance officer on {h} wants the {x} rule then in force on {t}, based only on what was public by then."],
     "current": ["Which {x} rule applies right now?", "What is the latest {x} requirement currently in force?"]}
random.seed(7); pick = []
for split_name, pool in [("test", test), ("dev", dev)]:
    for it in INTENTS:
        cs = [c for c in pool if c["intent"] == it]; random.shuffle(cs)
        pick += [(split_name, c) for c in cs[: (6 if it != "current" else 3)]]
rows, key = [], []
for n, (sp, c) in enumerate(pick, 1):
    cid = f"Q{n:03d}"; x = short(c)
    fam_docs = sorted([i for i in C if C[i]["family"] == c["family"]], key=lambda i: C[i]["publication_date"])
    rows.append({"case_id": cid, "topic": x, "intended_semantics": c["intent"], "target_time_t": c["t"], "info_horizon_h": c["h"] if c["intent"] != "valid_at" and c["intent"] != "current" else "(today / no limit)",
                 "draft_query_1": T[c["intent"]][0].format(x=x, t=fmt(c["t"]), h=fmt(c["h"])), "draft_query_2": T[c["intent"]][1].format(x=x, t=fmt(c["t"]), h=fmt(c["h"])),
                 "your_rewrite": "", "candidate_documents(url)": " ; ".join(f"https://www.federalregister.gov/d/{i}" for i in fam_docs),
                 "annotator_best_document": "", "annotator_notes": ""})
    key.append({"case_id": cid, "split": sp, "intent": c["intent"], "gold_doc": gold(c), "kind": c.get("kind", "gap"), "family": c["family"], "t": c["t"], "h": c["h"], "topic": c["topic"]})
with open("annotation/queries_to_rewrite.csv", "w", newline="") as f:
    w = csv.DictWriter(f, rows[0].keys()); w.writeheader(); w.writerows(rows)
json.dump(key, open("annotation/GOLD_KEY_do_not_share_with_annotators.json", "w"), indent=1)
print(len(rows), "cases;", {s: sum(k["split"] == s for k in key) for s in ("dev", "test")})
for r in rows[:2] + rows[8:10]: print(r["case_id"], r["intended_semantics"], "|", r["draft_query_1"])

import csv as _c
acc = [route(r["draft_query_%d" % k]) == r["intended_semantics"] for r in rows for k in (1, 2)]
print("router accuracy on drafted paraphrases: %.2f" % (sum(acc) / len(acc)))
from collections import Counter
print(Counter((r["intended_semantics"], route(r["draft_query_1"])) for r in rows))
