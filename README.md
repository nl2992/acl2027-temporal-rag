# ACL 2027 — Retrospective-Aware Temporal RAG

Research workspace for baseline reproduction and a preregistered 144-cell reranking study.

## Start here

- [Original protocol](docs/guides/ACL2027_Temporal_RAG_Replication_Protocol.md)
- [Original factorial registry](docs/guides/ACL2027_Temporal_RAG_Factorial_144.jsonl)
- [Progress and next actions](reports/progress.md)
- [Research tools](docs/research_tools.md)
- [TEMPO retriever coverage](reports/tempo_retriever_coverage.md)

The supplied documents are research guides, not proof that sources, deadlines, experiments, or results have been verified. Original files are preserved unchanged with SHA256 hashes in `manifests/input_documents.json`. The working experiment registry is `configs/factorial_144.jsonl`.

Run `python scripts/validate_project.py` to verify document integrity and the factorial registry. Native reproduction requires a separately audited Linux/CUDA environment; the Windows setup does not satisfy that gate.

Measured repaired-baseline results are in [the parity audit](reports/baseline_parity.md) and [baseline registry](reports/baseline_registry.md). Several automatic TimelyRAG cells do not reproduce the published targets; no new-method or SOTA success is claimed.

Do not commit raw datasets, model weights, credentials, caches, or lockbox labels. Audit source and data licenses before redistribution.
