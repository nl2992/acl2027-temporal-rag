"""Pilot baselines B0-B4 on Federal Register two-clock cases. CPU only, metadata-derived labels."""
import json, math, re, collections, datetime as dt, random
D = dt.date.fromisoformat
C = json.load(open("data/pilot/corpus.json")); cases = json.load(open("data/pilot/cases.json"))
tok = lambda s: re.findall(r"[a-z0-9]+", s.lower())
docs = {i: tok(d["title"] + " " + d["abstract"]) for i, d in C.items()}
N = len(docs); avg = sum(map(len, docs.values())) / N
df = collections.Counter(w for t in docs.values() for w in set(t))
import functools
@functools.lru_cache(maxsize=None)
def bm25(q, k1=1.2, b=0.75):
    qs = tok(q); out = {}
    for i, t in docs.items():
        tf = collections.Counter(t); s = 0
        for w in qs:
            if w in tf:
                s += math.log(1 + (N - df[w] + .5) / (df[w] + .5)) * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(t) / avg))
        out[i] = s
    return out
import os, sys
sys.path.insert(0, os.path.dirname(__file__) or ".")
from dateparse import find_dates
VTL = int(os.environ.get("VALID_TO", "0") or 0)   # 1: valid-to semantics; 2: plus time-of-day windows, notice handling and deterministic tie-breaks
VT = VTL >= 1   # valid-to semantics: a rule is in force only until the end date stated in its own DATES text
V2 = VTL >= 2
pub = lambda i: D(C[i]["publication_date"]); eff = lambda i: D(C[i]["effective_on"])
_ENDW = re.compile(r"\b(through|until)\b", re.I)
@functools.lru_cache(maxsize=None)
def vto(i):
    """End of validity parsed from the rule's DATES statement ('through <date>', 'until <date>'); None if open-ended or unparseable."""
    t = " ".join((C[i].get("dates_text") or "").split()); m = _ENDW.search(t)
    if V2 and re.search(r"\bfrom\b[^.]{0,60}\b(a\.m\.|p\.m\.|midnight|noon|hours)[^.]{0,60}\b(to|until|through)\b", t, re.I):
        ds = [d for _, d, _ in find_dates(t)]
        if ds and max(ds) >= eff(i): return max(ds)   # a time-of-day window ends on the last date mentioned (the same day for one-day windows)
    if not m:   # "effective from <time or date> to <time or date> on <date>" (same sentence, short span)
        m = re.search(r"\bfrom\b(?:(?!\. [A-Z]).){0,120}?\b(to)\b", t)
        if not m: return None
        m = re.compile(r"\bto\b").search(t, m.start(1))
    ds = [d for _, d, _ in find_dates(t[m.start():])]
    if not ds: return None
    v = max(ds); return v if v >= eff(i) else None
_NOTICE_TITLE = re.compile(r"\bwithdrawal\b|\bdelay of (the )?(effective|compliance|applicability)\b|\bpostponement\b|\bextension of (the )?effective\b|\bcorrecting amendment", re.I)
_NOTICE_DATES = re.compile(r"\bthis correction\b|\bcorrecting amendment\b", re.I)
def is_notice(i):
    """Notices that patch, withdraw or postpone another rule are not versions of their own (level 2)."""
    return bool(_NOTICE_TITLE.search(C[i]["title"]) or _NOTICE_DATES.search(C[i].get("dates_text") or ""))
def tie(i):
    """Deterministic tie-break among rules with the same date: later publication, then higher document number (level 2); neutral otherwise."""
    if not V2: return (0, 0)
    m = re.search(r"(\d+)$", i); return (-pub(i).toordinal(), -(int(m.group(1)) if m else 0))
def inforce(i, t): return eff(i) <= t and (not VT or vto(i) is None or t <= vto(i)) and not (V2 and is_notice(i))
def gold(c):
    t, h = D(c["t"]), D(c["h"]); fam = [i for i in C if C[i]["family"] == c["family"]]
    it = c["intent"]
    num = lambda i: int(re.search(r"(\d+)$", i).group(1)) if re.search(r"(\d+)$", i) else 0
    if it == "known_at": ok = [i for i in fam if pub(i) <= h]; key = (lambda i: (pub(i), num(i))) if V2 else pub
    else:
        ok = [i for i in fam if inforce(i, t) and (it == "valid_at" or pub(i) <= h)]; key = (lambda i: (eff(i), pub(i), num(i))) if V2 else eff
    return max(ok, key=key) if ok else ("NONE" if VT else None)
def admissible(i, c):  # constraint satisfaction of a returned doc under the query semantics
    t, h = D(c["t"]), D(c["h"]); it = c["intent"]
    if it == "known_at": return pub(i) <= h
    if it == "valid_at": return inforce(i, t)
    return inforce(i, t) and pub(i) <= h
def query(c):
    t = D(c["t"]).strftime("%B %d, %Y")
    return {"valid_at": f"{c['topic']} rule legally in effect on {t}",
            "known_at": f"{c['topic']} latest rule announced as of {t}",
            "valid_known": f"{c['topic']} rule in effect on {t} as known then",
            "current": f"{c['topic']} current rule"}[c["intent"]]

def rank(method, c):
    s = bm25(query(c)); top = sorted(s, key=s.get, reverse=True)[:20]
    t, h = D(c["t"]), D(c["h"])
    if method == "B0_bm25": return top
    if method == "B1_recency": return sorted(top, key=lambda i: (pub(i), s[i]), reverse=True)
    if method == "B2_pubcut": return sorted([i for i in top if pub(i) <= h], key=lambda i: (pub(i), s[i]), reverse=True)
    if method == "B3_validtime": return sorted([i for i in top if inforce(i, t)], key=lambda i: (eff(i), s[i]), reverse=True)
    if method == "B3b_valid+pubcut": return sorted([i for i in top if inforce(i, t) and pub(i) <= h], key=lambda i: (eff(i), s[i]), reverse=True)
    if method == "B4_twoclock":  # intent-routed (oracle intent in pilot)
        it = c["intent"]
        if it == "known_at": return rank("B2_pubcut", c)
        if it == "valid_at": return rank("B3_validtime", c)
        return rank("B3b_valid+pubcut", c)
