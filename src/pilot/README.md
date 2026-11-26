# src/pilot: two-clock temporal retrieval pilot (exploratory)
Run `bash src/pilot/run_all.sh` (stdlib only; needs network for the Federal Register API). Outputs go to `data/pilot/` (gitignored; public-domain, regenerable). Note the family miner is time-dependent (new rules appear): rerunning later gives a superset, so pin by committing `annotation/split_v1.json` and the case list when freezing. fr_families.py must run before fr_families_v2.py; draft_queries.py rewrites `annotation/queries_to_rewrite.csv`, so do NOT rerun it after annotators have the sheets.
Files: common.py (corpus, BM25, gold, baselines B0-B3), method_v1.py (B4v1/B4v2, B6, splits, bootstrap), router.py, dateparse.py, qtie_style.py, eval_natural.py, build_pilot.py, verify_dates.py, draft_queries.py.
Paper tables and figures (run after the corpus exists): `controls_test5.py` (add `--dense` using .venv) writes `reports/pilot_controls_test5_*`; `make_figures.py` (needs matplotlib) reads those JSON files and writes `paper/figures/`. `run_all.sh` does not cover these.
`router_switch.py` (router over gated B2/B3), `llm_rerank.py` (run outside Claude Code), `make_human_sheets.py` (sheets for annotation/human_v2/TODO.md).

`annotation/codex_sim/writer_*.csv` are model-written stand-in questions, not human data. Model labels and raw replies are not published until the human study is scored.
