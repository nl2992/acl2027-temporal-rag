"""Agreement of blind judges with the valid-to gold on the pristine test5 cases (confirmatory)."""
import json, sys, os, collections
J = sys.argv[1]; key = json.load(open(f"{J}/p5_key.json")); ans = {}
for k in range(1, 7):
    f = f"{J}/p5_answers_{k}.json"
    if os.path.exists(f): ans.update(json.load(open(f)))
print("answers", len(ans), "of", len(key))
ag = collections.defaultdict(list); conf = collections.defaultdict(list); dis = []
for c, a in ans.items():
    ok = a["choice"] == key[c]["gold"]; ag[key[c]["intent"]].append(ok); conf[a["confidence"]].append(ok)
    if not ok: dis.append((c, key[c]["intent"], key[c]["gold"], a["choice"], a["confidence"], a.get("note", "")[:100]))
tot = [x for v in ag.values() for x in v]
if tot: print("overall agreement %d/%d = %.2f" % (sum(tot), len(tot), sum(tot) / len(tot)))
for it, v in ag.items(): print(f"  {it:12} {sum(v)}/{len(v)} = {sum(v)/len(v):.2f}")
for k, v in conf.items(): print("  confidence", k, f"{sum(v)}/{len(v)}")
nn = [(a["choice"] == "NONE", key[c]["gold"] == "NONE") for c, a in ans.items()]
print("judge NONE:", sum(x for x, _ in nn), " gold NONE:", sum(y for _, y in nn), " both NONE:", sum(x and y for x, y in nn))
for d in dis: print(d)
