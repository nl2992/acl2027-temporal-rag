"""Extract target time t and information horizon h from query text given the routed intent. Pure regex, no gold access.
Returns None when no absolute date is found for a dated intent (caller falls back to semantic ranking)."""
import re, datetime as dt
TODAY = dt.date(2026, 11, 23)
MON = {m: i for i, m in enumerate("january february march april may june july august september october november december".split(), 1)}
MON.update({k[:3]: v for k, v in list(MON.items())}); MON["sept"] = 9
M = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sept?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?"
PATS = [  # (regex, builder) ordered most specific first; spans are removed once matched
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), lambda g: (int(g[0]), int(g[1]), int(g[2]))),
    (re.compile(rf"\b{M}\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})\b", re.I), lambda g: (int(g[2]), MON[g[0].lower().rstrip('.')], int(g[1]))),
    (re.compile(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+{M},?\s+(\d{{4}})\b", re.I), lambda g: (int(g[2]), MON[g[1].lower().rstrip('.')], int(g[0]))),
    (re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b"), lambda g: (int(g[2]), int(g[0]), int(g[1]))),
]
def find_dates(q):
    out, s = [], q
    for rx, f in PATS:
        for m in list(rx.finditer(s)):
            try: out.append((m.start(), dt.date(*f(m.groups())), s[max(0, m.start() - 40):m.start()].lower()))
            except ValueError: pass
        s = rx.sub(lambda m: " " * len(m.group(0)), s)
    return sorted(out)
H_CUE = re.compile(r"(by|as of|until|before|published by|public by|released by|issued by|checked[^.]*on|on|had been[^.]*by)\W*$")
def resolve(q, intent):
    ds = find_dates(q)
    if intent == "current": return TODAY, TODAY
    if not ds: return None
    if intent == "valid_at": return ds[0][1], TODAY
    if intent == "known_at": d = ds[0][1]; return d, d
    if len(ds) == 1: return ds[0][1], ds[0][1]
    # two dates: the one introduced by a knowledge cue ("by/as of ... published/public/known") is h; else earlier = t, later = h
    hs = [x for x in ds if re.search(r"\b(by|as of|until|before)\W*$", x[2]) or re.search(r"(public|published|known|released)\W*(by|as of)\W*$", x[2])]
    h = hs[0][1] if hs else max(x[1] for x in ds)
    t = [x[1] for x in ds if x[1] != h or len(set(y[1] for y in ds)) == 1]
    return (min(t) if t else h), h
