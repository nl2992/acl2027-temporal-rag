# Method v1 and first held-out result (2026-11-23)

Code: `src/pilot/method_v1.py` (+ `common.py`, `build_pilot.py`, `verify_dates.py`). Output: `data/pilot/method_v1_output.txt`. CPU only, stdlib, deterministic apart from the bootstrap seed.

**Method.** Keyword intent router -> (t, h) -> hard eligibility (known_at: pub<=h; valid_at: eff<=t; valid_known: both; current: both at today) -> rank by `z(BM25) - lambda * log1p(gap_days/30)` where the gap is measured on the clock the intent uses. lambda chosen on dev families only (grid 0..4, dev top-1 -> 1.0).

**Data.** 100 Federal Register final rules, 14 families, 220 cases (incl. 8 retroactive-effective probes). All 100 `effective_on` values appear verbatim in each rule's DATES text (`verify_dates.py`). Split by family: 9 dev / 5 test families, 150 / 68 cases (alternating over sorted family keys; an md5 split gave 13/1 and was discarded before any results were looked at). Only 8 of the 14 families have more than a handful of cases; 4 documents are retroactive and they look like delay/correction notices whose effective_on is the original rule date.

**Held-out results (test, n=68; top-1 / inadmissible-top-1 / nDCG@10).**

| method | current (5) | valid_at (22) | known_at (19) | valid_known (22) | all |
|---|---|---|---|---|---|
| B0 BM25 | .20/.00/.58 | .27/.55/.58 | .42/.11/.72 | .27/.55/.60 | .31/.38/.62 |
| B2 pub cutoff | .40/.00/.70 | .00/1.0/.16 | .84/.00/.94 | .00/1.0/.44 | .26/.65/.51 |
| B3 valid filter | .40/.00/.70 | .55/.00/.79 | .00/.00/.00 | .50/.05/.76 | .37/.01/.55 |
| B6 soft temporal distance (approximation, not a reproduction) | .80/.00/.87 | .09/.86/.56 | .84/.11/.93 | .05/.91/.53 | .34/.60/.67 |
| **B4 v1 (routed)** | .80/.00/.93 | .86/.00/.94 | 1.00/.00/1.00 | .86/.00/.94 | **.90/.00/.96** |
| B4 without semantic term | .40/.00/.71 | .55/.00/.79 | .84/.00/.94 | .50/.00/.76 | .60/.00/.82 |

Paired bootstrap top-1 gain of B4 over B0 / B2 / B3 / B6: +0.59 [0.47, 0.69], +0.63 [0.52, 0.75], +0.53 [0.40, 0.66], +0.56 [0.44, 0.68]. Over families the CIs resample cases, not families, so they are optimistic (5 test families).

**What this supports.** Single-clock and soft-distance rankers produce inadmissible top results on 38-65% of queries; two-clock eligibility removes them and the semantic term adds +0.30 top-1 over eligibility+date alone.

**What it does not support (strongest objection).** (1) Gold and eligibility use the same timestamps, so zero violations are by construction; the real evidence is B4's top-1 vs. the baselines, which depends on gold being "latest eligible version", a definition we chose. (2) Intent labels come from our own query templates; router accuracy 1.0 is circular. (3) Queries are templated, BM25 is over title+abstract only, relevance is single-gold. (4) Routing is only shown necessary here because B2/B3 each fail on the other's intent. A one-clock method with a per-query switch is exactly B4, so novelty rests on the problem framing, the data and the evaluation, not the model.

**Next.** Natural-language queries written by teammates (not templated) with a second annotator on a subset; human judgment of which document answers each query using rule text; more families, including corrected rules; test real Q-TIE/TimelyRAG-style baselines; a learned or LLM intent router checked against paraphrases. Frozen test split: keep the current 5 test families untouched from here on.

## Update: intent router v2 and natural-language queries (2026-11-23)

`src/pilot/router.py` (cue patterns from the intent definitions), `src/pilot/eval_natural.py`. v1 keyword router: 0.36 on drafted paraphrases (always valid_at). v2: first pass 0.98 on the drafts (but written after seeing them) and 0.65 on 20 fresh paraphrases; after one revision of the cue lists it scores 1.00 on those 20, which are now router-dev, not evidence. **No independent router number exists until teammates' rewrites are scored; do not edit the router after that.**

End-to-end on the 42 drafted cases with natural query text (t,h still taken from case metadata, date parsing not built): B4 with v2 router top-1 0.81 / 0.83 (two paraphrases), oracle intent 0.83 / 0.86, B0 0.24 / 0.19, B2 0.31, B3 0.43. Router errors cost about 2-3 points. Drafts and gold are by the same author, so treat as an engineering check.
