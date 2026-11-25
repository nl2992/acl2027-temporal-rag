"""Cue-based intent router v2. Written from the intent definitions (valid / known / retrospective cues); no learned weights."""
import re
MONTH = r"(january|february|march|april|may|june|july|august|september|october|november|december)"
HAS_DATE = re.compile(rf"\b{MONTH}\s+\d{{1,2}},?\s+\d{{4}}\b|\b(19|20)\d\d\b|\b\d{{1,2}}/\d{{1,2}}/\d{{2,4}}\b", re.I)
VALID = re.compile(r"\b(in (force|effect)|effective|applied|applies|governed|governing|legally|binding|required|requirements?|enforceable|operative)\b", re.I)
KNOWN = re.compile(r"\b(published|announced|publicly|public|available|could (have|they)|had (been|appeared)|disclosed|released|knowable|known|on the record|visible|found|seen|issued|put out|existed|anyone could read|on the federal register)\b", re.I)
RESTRICT = re.compile(r"\b(only|solely|as known then|at that time|at the time|by then|without (later|subsequent|hindsight)|using what|based on what|what was (public|known|available)|restricting|ignoring (anything|everything)|limited to|material public)\b", re.I)
NOW = re.compile(r"\b(right now|currently|at present|nowadays|these days|presently|current)\b", re.I)
RETRO = re.compile(r"\b(hindsight|retrospective(ly)?|looking back|taken into account|as we now know|whole record|from today|later (evidence|corrections?))\b", re.I)
def route2(q):
    if not HAS_DATE.search(q): return "current"
    if RETRO.search(q) and not RESTRICT.search(q): return "valid_at"
    v, k, r = bool(VALID.search(q)), bool(KNOWN.search(q)), bool(RESTRICT.search(q))
    if v and r: return "valid_known"
    if k and not v: return "known_at"
    if k and v and not r and re.search(r"regardless of when it took effect|not yet (in effect|effective)", q, re.I): return "known_at"
    if k and v and re.search(r"\b(by|as of|on)\b.*\b(published|public|announced)\b", q, re.I): return "valid_known"
    return "valid_at"
