# Mission checklist vs. original prompt (reviewed 2026-11-23)
Legend: DONE, PARTIAL, TODO-auto (I can do it), BLOCKED-human (needs the team).

## Days 1-2 / orientation
- DONE repo + branches listed, Mac checked (M4, 16 GB), deadline verified (4 Jan 2027), RESEARCH_DIRECTION.md.
- DONE-PARTIAL (A9, 2026-11-23: Q-TIE, IA-RAG, legal-RAG, bitemporal memory read in full; TEMPS/HoH/MRAG/TimeR4/Re3 body/FRESCO body still unread) literature pass: abstracts/snippets only; full text of bitemporal graph papers, the legal-RAG paper, TEMPS, HoH, MRAG not read. (remaining reading: TEMPS, HoH, MRAG, TimeR4, Re3/FRESCO bodies = TODO-auto A9b)
- DONE (A10, 2026-11-23: branch holds logs, manifests, summaries and scripts only; no candidate pools or predictions) `origin/codex/experiment-backup` only listed, not mined for reusable candidates (prompt: reuse cached pools if exist; none on this Mac).

## Pilot / data
- DONE 790 verified rules, 105 families, 1291 cases; DATES-text check 790/790.
- PARTIAL 42 hand-drafted natural-language cases; human rewrites + second annotator BLOCKED-human (annotation/ASSIGNMENTS.md).
- DONE (A3, 2026-11-23, 106 chains) retrospective-with-correction cases (rules with `corrections`/`correction_of`); currently barely exercised.
- DONE (A4a fresh batch test3; A4b UK SI probe: feasible gaps but no version families, deferred, see EXPERIMENT_RESULTS.md) second source/domain for generality (e.g. legislation.gov.uk in-force versions or EUR-Lex), check reuse terms.

## Method / baselines (B0-B6)
- DONE B0-B4, B6-approx, Q-TIE-style (labelled), router v2, date parser, gated B4v2.
- DONE (A5, 2026-11-23; strict-drop vs proxy, see EXPERIMENT_RESULTS.md) missing/unreliable timestamp robustness: mask effective_on at rates 10/30/50%, compare "use semantic rank when unknown" vs abstention vs fallback.
- DONE (A6, 2026-11-23, see EXPERIMENT_RESULTS.md) harm check on ordinary (non-temporal / current) queries and always-on filtering vs routing.
- DONE (A7, 2026-11-23, labelled approximation) Re3-style recency/conflict baseline (conceptual, labelled) and learned/LLM-free router comparison.

## Evaluation integrity
- DONE family-level splits, dev-only selection, cluster bootstrap, oracle separated.
- PARTIAL test2 no longer pristine for B4v2 (design saw aggregate error categories). -> need fresh family batch (A4 supplies it) or human set. Freeze it before inspecting.
- BLOCKED-human relevance judgments, agreement/kappa, router scored once on rewrites.

## Deliverable files
- DONE LITERATURE_POSITIONING, DATASET_SPEC, EXPERIMENT_RESULTS, DECISION_LOG, PAPER_OUTLINE, METHOD_V1, RESEARCH_DIRECTION.
- DONE (A1, 2026-11-23) PILOT_RESULTS.md is stale (v0, 14 families): add pointer/update. AGENTS.md requires reports/progress.md and reports/experiment_log.md entries + brief protocol amendment for the pivot.
- DONE (A2, 2026-11-23; unit tests 4/4 pass; run_all.sh not run end-to-end) reproducibility: `src/pilot/run_all.sh`, unit tests for dateparse/router/gold in tests/, README for src/pilot, commit small public-domain data files or the download scripts.

## Paper (weeks 5-6)
- DONE-DRAFT (A8, 2026-11-23: paper/main.tex compiles, 3 pages, ACL review style, red TODOs for human annotation, Q-TIE, unread related work) LaTeX draft in paper/ (ACL style files if obtainable offline/from official repo), sections 1-3, 5-6 with current numbers, Limitations section, anonymised artifact folder. ARR format/policy check once.

## Not pursued by design
- TimelyRAG discrepancy diagnostics (raw outputs absent; fallback "Paper A" only by explicit team decision), TEMPO matrix, 144-cell factorial.
