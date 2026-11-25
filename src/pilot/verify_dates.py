"""Check API effective_on against the rule's own DATES text (independent source field)."""
import json, urllib.request, urllib.error, time, datetime as dt
def _get(u, tries=8):
    for k in range(tries):
        try: return json.load(urllib.request.urlopen(u, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code != 429 or k == tries - 1: raise
            time.sleep(5 * (k + 1))

C = json.load(open("data/pilot/corpus.json")); ids = list(C); out = {}
for i in range(0, len(ids), 20):
    u = "https://www.federalregister.gov/api/v1/documents/" + ",".join(ids[i:i+20]) + ".json?fields[]=dates&fields[]=document_number&fields[]=correction_of&fields[]=corrections"
    for r in _get(u)["results"]:
        out[r["document_number"]] = r
fmt = lambda s: dt.date.fromisoformat(s).strftime("%B %-d, %Y")
ok, bad = [], []
for i, r in out.items():
    txt = (r.get("dates") or "")
    (ok if fmt(C[i]["effective_on"]) in txt else bad).append(i)
    C[i]["dates_text"] = txt; C[i]["has_correction"] = bool(r.get("corrections")); C[i]["is_correction"] = bool(r.get("correction_of"))
json.dump(C, open("data/pilot/corpus.json", "w"), indent=1)
print(f"effective_on found in DATES text: {len(ok)}/{len(C)}")
for i in bad[:25]: print(i, C[i]["publication_date"], C[i]["effective_on"], "|", C[i]["dates_text"][:110].replace("\n"," "))
