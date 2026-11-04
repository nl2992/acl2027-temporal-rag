# Research tool setup

Installed on 2026-11-04:

- ARIS / Auto-Research-In-Sleep: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep — Codex-specific skill suite installed into the user's Codex skills directory, with shared references. Full helper checkout retained at `C:/Users/nigel/.codex/research-tools/aris`; the global `~/.aris/repo` pointer resolves helpers.
- HKUSTDial Supervisor-Skills: https://github.com/HKUSTDial/Supervisor-Skills — all 12 skills installed into the user's Codex skills directory.
- Graphify: https://github.com/Graphify-Labs/graphify — CLI pinned to `graphifyy==0.9.102` in the project `.venv`, with Codex skill registration.

Exact inspected repository revisions: `manifests/research_tool_sources.json`. Installed Python package versions: `manifests/graphify_environment.txt`. Skills are local user tools and are not redistributed in this repository.

Skills become available on the next chat turn. Begin with research planning and source audits; use experiment planning/ablation skills after the reproduction gate, and evidence audit/review skills before paper claims. Graphify is a navigation aid; graph-derived inferences do not establish research evidence.

For the project-local Graphify CLI on Windows, use `.venv/Scripts/graphify.exe --help`. Optional provider APIs, independent reviewer backends, cloud compute credentials, and Linux/CUDA reproduction dependencies are not configured by installing Markdown skills. Check their requirements when first used and report unavailable capabilities.

No recurring overnight automation is scheduled. ARIS is installed as the requested toolkit; an overnight schedule and execution window have not been specified. No cloud account or paid resource was started.
