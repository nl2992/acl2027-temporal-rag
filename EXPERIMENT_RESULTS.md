# Experiment results (2026-11-23; exploratory, template queries, metadata-derived gold)

Code: `src/pilot/method_v1.py` -> `data/pilot/method_v1_output.txt` (gitignored; rerun to regenerate). CPU only. Hardware: Apple M4, 16 GB.

**Held-out (test1 5 fam + test2 35 fam; 431 cases), top-1 / inadmissible / nDCG@10**

| method | current | valid_at | known_at | valid_known | all |
|---|---|---|---|---|---|
| B0 BM25 | .12/.00/.52 | .19/.49/.55 | .19/.28/.56 | .17/.50/.54 | .18/.39/.54 |
| B2 pub cutoff | .30/.00/.58 | .02/.98/.17 | .81/.00/.92 | .01/.91/.45 | .27/.58/.52 |
| B3 valid filter | .35/.00/.60 | .42/.00/.70 | .00/.02/.00 | .38/.07/.67 | .28/.03/.48 |
| B6 soft temporal distance (approx.) | .40/.00/.66 | .05/.93/.41 | .83/.10/.93 | .00/.99/.39 | .30/.62/.58 |
| B4v1 (eligibility + lambda*gap, lambda=2) | .53/.00/.75 | .62/.00/.82 | .93/.00/.97 | .55/.00/.79 | .68/.00/.85 |
| **B4v2 (semantic-gated eligibility, delta=1.5)** | .85 | .86 | .88 | .84 | **.86** (test1 .97, test2 .84) |

(B4v2 per-intent top-1 only; inadmissible 0.00 by construction.)

**Uncertainty.** Family-cluster bootstrap on test2 (35 families, 363 cases), B4v1 minus baseline top-1 (95% CI): B0 +.50 [.40,.58]; B2 +.38 [.31,.45]; B3 +.39 [.33,.46]; B6 +.37 [.28,.45]; B4v1 minus no-semantic +.14 [.08,.21]. B4v2 minus B4v1 +.18 [.10,.27]; B4v2 minus B3 +.57 [.47,.66] (from the same run).

**Findings.** (1) Each single-clock baseline is inadmissible on the intents it does not model (B2 98% on valid_at; B3 0.00 top-1 on known_at). (2) Routing + eligibility removes inadmissible results. (3) How semantic and temporal scores are combined matters: lambda re-selected on all dev (0.5 -> 2) lost 7 points on test and moved errors from same-family-wrong-version to other-family (105 of 363); a semantic gate fixes most of that (outcomes on test2: 305 correct, 24 wrong version, 27 other family, 7 none eligible). Selection protocol: lambda/delta chosen on dev only, tuned once; the earlier dev-only-v1 lambda run is kept in `method_v1_output_lam_dev_only.txt` (B4v1 0.75 overall).

**Not yet established.** Human-judged relevance; independent queries; Q-TIE baseline; correction chains; any non-Federal-Register source; the router on rewrites from other people (router v2 0.98 on drafts it was written after seeing, 1.00 on a 20-item set it was revised on; independent score pending); date parsing on the drafts matches metadata 83/84 (misses are router errors) and 7/7 hand-written format/two-date cases.

## Q-TIE-style conceptual baseline (2026-11-23)
`src/pilot/qtie_style.py`. **Not a reproduction**: the official repository (github.com/ssoy0701/Q-TIE, linked from arXiv 2609.23880) returned HTTP 404 on 2026-11-23 and the repo owner's public list has no such project, so the authors' code and TIE checkpoint were unavailable. Implemented from the abstract only: the query's temporal constraint becomes an interval (here the single date, via our regex parser, standing in for the learned TIE model), documents' timestamps are compared to it as a separate signal and combined with the semantic score; no information horizon. lambda picked on dev only (4 in both variants).

Held-out (431 cases) top-1 / inadmissible: pub-date variant 0.30 / 0.62; effective-date variant 0.30 / 0.58. Per intent (pub): current .40, valid_at .05 (93% inadmissible), known_at .83, valid_known .00 (99%). Essentially identical to B6 and far below B4v2 (0.86).

**Correction after reading the paper (A9):** the real Q-TIE handles one-sided intervals ("as of", "by", "before"), so this point-interval stand-in understates it; B2 and B3 (hard cutoffs on a single document clock) are fairer approximations of a one-sided-interval method (see LITERATURE_POSITIONING.md). **Why, and what this does not show.** A symmetric distance-to-point score has no direction: it picks the nearest timestamp, which is often the next version rather than the latest one before t. A learned interval model could emit half-open intervals ("by t" -> (-inf, t]); with a hard interval this reduces to our B2/B3 cutoffs, which fail on the other intent. So the likely outcome for the real Q-TIE is single-clock behaviour, but this run does not test it. Required before a paper claim: the real Q-TIE code, or its authors' released predictions.

## A3: correction chains (2026-11-23; `src/pilot/fr_corrections.py`, `eval_corrections.py`)
160 Federal Register correction notices with retrievable originals (CFR parts as in the v2 mining); 106 chains kept after requiring a unique original title and a >=7-day lag, 212 cases. Corrections have no effective date, so only the publication/horizon clock matters. Intents: known_at with h between original and correction (gold = original; correction not yet public) and retrospective with h = today (gold = correction notice, treated as the corrected record). Text = title + first 2.5k characters of the rule. delta=1.5 reused from the main experiment, nothing tuned here; single run.

| method | known_at top-1 | retrospective top-1 |
|---|---|---|
| B0 BM25 | .60 | .37 |
| B1 recency | .00 | .12 |
| B2a cutoff at t (single clock, h=t), gated | .99 | **.00** (99% returns the superseded original) |
| B4 cutoff at routed h, ungated | .90 | .12 |
| **B4 cutoff at routed h, semantic-gated** | .99 | .87 |

Reading: a plain publication cutoff works if it is applied at the right horizon; the failure is applying h=t to a retrospective query, which returns the uncorrected text for every case. Without the semantic gate the latest unrelated document wins (retrospective .12), as in the main experiment. Caveats: gold treats the correction notice as the best evidence (a correction is a patch, not a replacement, so both documents are arguably needed: judge with humans); unique-title filtering keeps 106 of 160; no human check. This supports the claim that h must be modelled separately from t, not a claim that a new model is needed.

## A4a: fresh confirmatory batch test3 (2026-11-23; `fr_families_v3.py`, `method_v1.py`)
Mined from CFR titles not used earlier (7, 9, 10, 13, 15, 16, 19-24, 28, 30, 31, 33, 34, 36-38, 41, 43-48, 50), same thresholds and normalizer as v2; 327 families qualified, 100 sampled with a fixed seed (3) *before* any evaluation on them (`annotation/split_v3.json`); 1,080 documents, 1,393 cases; merged into the shared corpus (1,870 documents; all effective dates match their DATES text). Frozen config (lambda=2, delta=1.5, router v2, no selection on test3). Because the corpus grew, earlier numbers moved slightly (test2: B4v1 .66 -> .69, B4v2 .84 -> .85).

| method (test3, top-1 / inadmissible / nDCG) | current | valid_at | known_at | valid_known | all |
|---|---|---|---|---|---|
| B0 BM25 | .26/.00/.52 | .27/.39/.50 | .17/.41/.46 | .11/.59/.41 | .19/.44/.46 |
| B2 pub cutoff | .27/.06/.52 | .03/.97/.18 | .77/.00/.84 | .33/.43/.59 | .30/.52/.48 |
| B3 valid filter | .29/.00/.53 | .61/.00/.75 | .02/.02/.02 | .23/.43/.58 | .33/.16/.53 |
| B6 soft distance (approx.) | .41/.06/.66 | .41/.51/.61 | .77/.12/.84 | .06/.91/.42 | .35/.55/.59 |
| B4v1 (lambda 2) | .62/.00/.76 | .64/.00/.78 | .83/.00/.86 | .57/.00/.74 | **.65**/.00/.78 |
| B4v2 gated (delta 1.5) | .80/.00/.85 | .69/.00/.71 | .77/.00/.77 | .65/.00/.67 | **.70**/.00/.72 |

Family-cluster bootstrap (100 families), top-1 difference: B4v2 - B3 +.37 [.24,.53]; B4v2 - B2 +.40 [.29,.54]; B4v2 - B6 +.35 [.25,.47]; B4v1 - B3 +.32 [.25,.39]; **B4v2 - B4v1 +.05 [-.03,.14]**.

**What replicated and what did not.** The headline holds on fresh families: two-clock eligibility beats every single-clock baseline by ~.3-.4 top-1 and removes inadmissible results. The semantic-gate advantage over plain lambda-weighting (+.18 on test2) shrank to +.05 with a CI spanning zero, and absolute accuracy fell (0.86 -> 0.70); the earlier number was optimistic because the gate was designed after looking at test2 aggregate error categories. Per intent the gate helps `current` (.62 -> .80) but not `known_at` (.83 -> .77). With the bigger corpus the dev-selected delta moved to 2 (frozen 1.5 used). Report test3 as the confirmatory estimate; do not claim the gate beats lambda-weighting. Remaining error analysis on test3 is deliberately not done yet (would contaminate it); use test3 only for final tables.

## A4b: second-source feasibility probe, UK statutory instruments (2026-11-23; `src/pilot/uk_probe.py`, no model run)
Source: legislation.gov.uk (Open Government Licence v3; confirm attribution terms before release). First 400 of 799 SIs from 2018-2022 feed pages: 370 parsed, 128 expose a `ComingIntoForce` date in the XML metadata; made-to-in-force lag: 0 negative, 25 within 0-6 days, 39 within 7-27, 64 at 28+ days (median 27.5). So the two clocks do disagree, as in the Federal Register. But normalized-title families with >=4 members: 0 in this sample (largest: 2). UK SIs mostly amend a parent Act through one-off instruments rather than recurring versioned documents; the version structure lives in consolidated point-in-time texts, whose publication ("editorial effect") dates are not recorded by the source. Also the "known" clock would be made/laid date, not official publication, and only 35% of SIs expose a machine-readable in-force date.
**Decision (autonomous, reversible):** do not build a second-domain benchmark now; the family/version structure and the known-time proxy would need new design work that cannot be validated before 4 Jan. Mention as future work and a limitation. If the team wants a second domain, EU/EUR-Lex consolidated versions or state-level registers are alternatives to probe.

## A5: missing effective dates (2026-11-23; `src/pilot/robust_missing.py`)
Random fraction p of documents lose `effective_on` (publication date kept); gold and inadmissibility use true dates; B4v2 gated, delta=1.5 frozen; test1+test2 only (n=431; test3 untouched); mean of 3 mask seeds. strict = masked documents ineligible for effective-time intents (empty result = abstention, scored as a miss); proxy = fall back to effective := publication date.

| p masked | strict top-1 / inadmissible | proxy top-1 / inadmissible |
|---|---|---|
| 0.0 | .87 / .00 | .87 / .00 |
| 0.1 | .82 / .00 | .82 / .05 |
| 0.3 | .71 / .00 | .72 / .15 |
| 0.5 | .58 / .00 | .60 / .29 |
| 0.8 | .39 / .00 | .46 / .44 |
| 1.0 | .26 / .00 | .36 / .55 |

Semantic-only BM25 on the same cases: .18. Reading: with strict handling accuracy degrades roughly linearly with missing data and the method never returns an inadmissible document (it abstains instead); the publication-date proxy buys 1-10 points of top-1 at the price of 5-55% inadmissible results, i.e. it re-creates the single-clock failure. At 100% missing, known_at queries (publication clock only) still work, so strict stays above BM25 (.26 vs .18). This answers the prompt's missing-timestamp question with a simple abstain-vs-proxy comparison; it does not test confidence-aware or learned imputation and masking is random (real missingness is likely systematic by agency/document type). Do not claim uncertainty-aware retrieval as novel (IA-RAG).

## A6: harm to ordinary (non-temporal) queries (2026-11-23; `src/pilot/harm_check.py`)
40 held-out families (test1+test2), 2 topic-only phrasings each (the bare family title; "Which rules cover <title>?"), 80 queries; relevant = any document of the family. Frozen settings (lambda=2, delta=1.5); the router sends date-free queries to `current`. Test3 untouched.

| method | nDCG@10 | P@10 (of returned) | Recall@min(10,|family|) |
|---|---|---|---|
| BM25 | .98 | .57 | .98 |
| always-on validity filter, latest first | .46 | .33 | .56 |
| B4v1 routed (current, lambda 2) | .78 | .52 | .90 |
| B4v2 routed (current, gate 1.5) | .92 | .89 | .95 |

Reading: always applying a temporal rule to every query is harmful (nDCG .98 -> .46) because recency ordering lifts other families' recent documents; routing plus the semantic gate keeps most of the ordinary-query quality (nDCG .92, recall .95) and returns cleaner lists (precision .89), at a cost of ~6 nDCG points. Caveats: the topic query is the family title itself, so BM25 is near ceiling, which makes this an easy and favourable test for BM25; relevance is the family, not a human judgment; the router is date-free -> current, so a vague historical query without a date would be routed to current.

## A7: Re3-style conceptual baseline (2026-11-23; `src/pilot/re3_style.py`)
**Approximation, not a reproduction** of Re3 (arXiv 2509.01306 v1; learned query-aware gate between relevance and recency). Here: score = z(BM25) + g * freshness(publication date, relative to today), with g a constant per query type (date-free vs dated) chosen on dev families only (g=+0.5 for current, g=-1, i.e. prefer older, for dated queries). No target time, no horizon, no eligibility.

| set | current | valid_at | known_at | valid_known | all (top-1 / inadmissible) |
|---|---|---|---|---|---|
| test1+test2 (431) | .47/.00 | .18/.24 | .10/.15 | .15/.27 | **.18 / .20** |
| test3 fresh (1,393) | .60/.02 | .23/.19 | .11/.14 | .13/.35 | **.20 / .23** |

For reference on test3: BM25 .19/.44, best single-clock baseline .35/.55 (B6) or .33/.16 (B3), B4v1 .65/.00, B4v2 .70/.00. Reading: a recency/relevance gate helps current queries (.26 -> .60 on test3 vs BM25) but cannot express "the latest version published/effective by a past date", so dated queries stay near BM25 level. Caveats: constant gates, not a learned model; freshness measured on publication only.
