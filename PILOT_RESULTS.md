> **Superseded for current numbers by EXPERIMENT_RESULTS.md and METHOD_V1.md** (this file is the v0 pilot on 14 families / 100 rules; kept as the first failure-mode evidence).

# Pilot results (v0, 2026-11-23)

Code: `src/pilot/fr_explore.py`, `fr_families.py`, `build_pilot.py`, `run_pilot.py` (CPU, stdlib only). Data: `data/pilot/` (100 Federal Register final rules in 14 recurring families, 212 cases).

**Timestamp availability (real):** across 8 CFR parts surveyed, most rules with an effective date are published before it (e.g. 12 CFR 1026: 70/86 positive lag, 0 negative; 14 CFR 91: 39 positive, 13 negative/retroactive). Corrections exist but are sparse (0-6 per part).

**Baselines** (top-1 / violation rate / nDCG@10; BM25 on title+abstract, top-20 pool, pool recall of gold 0.97+):

| method | current (14) | valid_at (65) | known_at (66) | valid_known (65) |
|---|---|---|---|---|
| B0 BM25 | .36/.00/.63 | .17/.72/.45 | .26/.33/.52 | .17/.72/.45 |
| B1 recency | .29/.00/.57 | .00/1.0/.12 | .05/.91/.26 | .00/1.0/.12 |
| B2 pub cutoff | .29/.00/.57 | .00/1.0/.12 | .88/.00/.95 | .00/.98/.46 |
| B3 valid filter | .36/.00/.60 | .52/.00/.76 | .00/.00/.00 | .52/.00/.76 |
| B4 routed (oracle intent) | .36/.00/.60 | .52/.00/.76 | .88/.00/.95 | .52/.00/.76 |

**Reading.** The failure mode is real in this data: the publication-cutoff rule (B2) is perfect-ish for known_at but 100% inadmissible on valid_at; the validity filter (B3) is the reverse (0.00 on known_at). Neither single clock works across intents; routing is required. Probes were cases where the rule was announced but not yet effective, so the clocks disagree on gold in all 198 non-current cases.

**Caveats (important).**
1. Gold labels are computed from the same timestamps the rules use, so B4's admissibility is by construction. This pilot shows the failure mode of single clocks and timestamp availability, not method quality. Gate to pass next: text-verified timestamps and human relevance on ~40 cases (second annotator on a subset).
2. valid_known never differs from valid_at here: all probes are positive-lag. Retroactive rules (4 in corpus) and corrections are not yet probed, so that intent is untested.
3. B4 top-1 is only 0.52 on valid_at despite 0.97 pool recall: it sorts by date and ignores family relevance, so cross-family distractors win. Method v1 must combine semantic score with eligibility. This is a hypothesis from the numbers, not yet checked.
4. Intent is oracle-labelled; no router yet.

**Gate: partial pass.** Real problem shown; method value not yet shown.

**Next (week 1-2):** (a) add retroactive and corrected-rule probes and verify effective dates against rule text for ~40 cases; (b) method v1 with semantic + eligibility scoring and a keyword intent router; (c) split by family for dev/test; (d) a TimelyRAG-style temporal-distance baseline as B6 approximation.
