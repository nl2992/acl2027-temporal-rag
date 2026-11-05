# Source availability recheck — 2026-11-05

Read-only recheck while the local TEMPO queue remained active. These observations establish access limits, not numerical replication or exhaustive absence of releases elsewhere.

- `gh api repos/facebookresearch/fresco/releases --jq length` returned0; `gh api repos/facebookresearch/fresco/tags --jq length` returned0. No tagged-release assets are available through these endpoints. The [official README](https://github.com/facebookresearch/fresco) documents data generation, not a frozen benchmark download. This does not prove that no fixed data exists outside the checked channels.
- `gh api repos/cjwyv/Re3 --jq .html_url` returnedHTTP404. The [Re³ paper](https://aclanthology.org/2026.acl-long.1180.pdf) still identifies that repository. No verified alternative release emerged from the focused search.
- `gh api repos/ssoy0701/Q-TIE --jq .html_url` returnedHTTP404. The [official arXiv abstract](https://arxiv.org/abs/2609.23880) names that same repository. No alternative official code/checkpoint link was found in this recheck.

Searches: site:github.com/facebookresearch/fresco dataset download evaluation; site:huggingface.co/datasets FRESCO temporal retrieval; exact Re3/cjwyv and Q-TIE/ssoy0701 author/project terms. Search absence is not proof of universal unavailability. No author messages, paid resources, model calls or dataset-generation commands were sent. Larger hardware alone cannot resolve missing source/checkpoints or frozen benchmark provenance.
