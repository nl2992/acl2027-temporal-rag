"""CPU replay of upstream reranking on sampled saved candidates, without labels.

For each selected row, the first-stage candidate order is an observed input.
Preserve that order, including ties, rather than assume excluded scores.
All temporal scores, auto/grid rankings, and synthetic-label oracle decisions
are computed by the pristine upstream source. No embeddings/models are loaded.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import runpy
import sys
from types import ModuleType

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = Path("/home/nigel/acl2027")
INFER = Path("/home/acl-infer")


def forbidden_encoder(*args, **kwargs):
    raise AssertionError("Encoder construction outside fixture scope")


def parse(value):
    return datetime.fromisoformat(value) if value else None


def main():
    assert __debug__ and os.environ.get("CUDA_VISIBLE_DEVICES") == ""
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / "vendor/TimelyRAG"))
    encoder_guard = ModuleType("FlagEmbedding")
    encoder_guard.BGEM3FlagModel = forbidden_encoder
    sys.modules["FlagEmbedding"] = encoder_guard
    import metrics
    import retrieval
    from config import ALPHA_GRID

    # Existing 20-document smoke retains every first-stage score and checks
    # genuine full-array sort, 42 synthetic cases and subsequently offline labels.
    runpy.run_path(str(HERE / "replay_dense_smoke.py"), run_name="__main__")

    class SavedCandidateOrder:
        def __init__(self, scores):
            self.scores = scores

        def __getattr__(self, name):
            return getattr(np, name)

        def argsort(self, values, *args, **kwargs):
            if values is self.scores:
                return np.arange(len(values) - 1, -1, -1)
            return np.argsort(values, *args, **kwargs)

    counts = {}
    for pred in sorted((INFER / "runs").glob("baseline-*/predictions.jsonl")):
        run = pred.parent.name
        data = json.loads((INFER / "inputs" / run / "input.json").read_bytes())
        doc_index = {doc_id: i for i, doc_id in enumerate(data["ids"])}
        counts[run] = 0
        with pred.open("rb") as f:
            for i, line in enumerate(f):
                if i not in {0, 1, 23, 127, 499, 1023, 1999, 2999}:
                    continue
                row = json.loads(line)
                ids = row["candidate_ids"]
                scores = np.array(row["candidate_scores"])
                dates = [np.array([parse(data[k][doc_index[d]]) for d in ids], dtype=object) for k in ("det", "dit")]
                q = data["queries"][i]
                assert row["query_id"] == q["query_id"]
                retrieval.np = SavedCandidateOrder(scores)
                for synthetic_gold in ([ids[1], ids[7]], ["__ABSENT_SYNTHETIC__"]):
                    observed = []

                    def observe(top, gold, k):
                        observed.append(list(top))
                        return metrics.evaluate_ranking_ids(top, gold, k)

                    retrieval.evaluate_ranking_ids = observe
                    native = dict(query=q["query"], qit=parse(q["qit"]), qet=parse(q["qet"]), positive_ids=synthetic_gold)
                    _, _, auto_hist, best_hist = retrieval.evaluate_2stage("audit", lambda _: scores, [native], ids, *dates)
                    assert observed[0] == row["auto"] and auto_hist[row["auto_alpha"]] == 1
                    assert observed[1:-1] == [e["top_ids"] for e in row["grid"]]
                    winner = max(range(len(ALPHA_GRID)), key=lambda j: metrics.evaluate_ranking_ids(observed[1+j], synthetic_gold, 10)[3])
                    assert observed[-1] == observed[winner+1] and best_hist[ALPHA_GRID[winner]] == 1
                    counts[run] += 1
    assert len(counts) == 8 and set(counts.values()) == {16}
    print(json.dumps({"status": "pass", "basis": "recorded full-run candidate order and scores", "full_run_synthetic_cases": counts}))


if __name__ == "__main__":
    main()
