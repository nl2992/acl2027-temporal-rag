"""Dev-set judge agreement and disagreement detail (for designing parser/notice fixes; dev only)."""
import json, sys, os, collections
sys.path.insert(0, "src/pilot")
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import common
J = sys.argv[1]; key = json.load(open(f"{J}/d_key.json")); ans = {}
for k in range(1, 7):
    f = f"{J}/d_answers_{k}.json"
    if os.path.exists(f): ans.update(json.load(open(f)))
C = common.C; show = lambda i: " ".join((C[i].get("dates_text") or "").split())[:150] if i in C else i
ag = collections.defaultdict(list); dis = []
for c, a in ans.items():
    ok = a["choice"] == key[c]["gold"]; ag[key[c]["intent"]].append(ok)
    if not ok: dis.append((c, key[c]["intent"], key[c]["gold"], a["choice"], a["confidence"], a.get("note", "")))
tot = [x for v in ag.values() for x in v]
print("answers", len(ans), "agreement %d/%d = %.2f" % (sum(tot), len(tot), sum(tot) / max(len(tot), 1)), {k: f"{sum(v)}/{len(v)}" for k, v in ag.items()})
for d in dis:
    print(f"\n{d[0]} {d[1]} conf={d[4]} | {d[5][:110]}\n   gold  {d[2]}: {show(d[2])}\n   judge {d[3]}: {show(d[3])}")
