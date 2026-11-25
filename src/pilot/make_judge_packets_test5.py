"""Blind judging packets: natural-language question + all candidate rules of the family (publication date and the rule's own DATES statement; the shared title is given once).
The question uses plain wording only (no formal definitions, no intent labels, no metadata field names). Gold key is written separately and never shown to judges.
Confirmatory variant (valid-to semantics, VALID_TO=1): 120 cases from test5 only (30 per intent), seed 12."""
import sys, io, contextlib, json, random, datetime as dt
sys.path.insert(0, "src/pilot")
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("src/pilot/method_v1.py").read())
OUT = sys.argv[1]
fmt = lambda s: D(s).strftime("%B %-d, %Y")
Q = {"valid_at": "Looking back from today, which rule governed {x} on {t}? (Later publications and corrections may be used to establish what applied then.)",
     "known_at": "On {h}, which was the most recent {x} rule that had been published by then?",
     "valid_known": "Using only what had been published by {h}, which {x} rule was in force on {t}?",
     "current": "Which {x} rule is in force today ({h})?"}
random.seed(12); picked = []
for it in INTENTS:
    for pool in (test5,):
        cs = [c for c in pool if c["intent"] == it]; random.shuffle(cs); picked += cs[:30]
random.shuffle(picked); packets = []; key = {}
for n, c in enumerate(picked, 1):
    x = c["topic"]; cand = sorted([i for i in C if C[i]["family"] == c["family"]], key=lambda i: C[i]["publication_date"])
    random.shuffle(cand)
    packets.append({"case": f"J{n:03d}", "question": Q[c["intent"]].format(x=x, t=fmt(c["t"]), h=fmt(c["h"])),
                    "rule_title": x, "candidates": [{"id": i, "published": fmt(C[i]["publication_date"]), "dates_statement": " ".join((C[i].get("dates_text") or "").split())[:200]} for i in cand]})
    key[f"J{n:03d}"] = {"gold": gold(c), "intent": c["intent"], "family": c["family"], "split": split[c["family"]]}
for k in range(6):
    json.dump(packets[k * 20:(k + 1) * 20], open(f"{OUT}/p5_packet_{k+1}.json", "w"), indent=1)
json.dump(key, open(f"{OUT}/p5_key.json", "w"))
print(len(packets), "cases;", sum(len(p["candidates"]) for p in packets) / len(packets), "mean candidates")
