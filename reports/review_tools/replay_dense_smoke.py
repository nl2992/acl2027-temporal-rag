"""Replay captured two-query Company BGE smoke scores in a CPU-only evaluator.

This witness uses synthetic relevance labels in the author reranker and opens
true smoke labels only after every reranking call has completed. It never
initializes a retriever or model.
"""

import os, sys, math, json, hashlib
from datetime import datetime
from pathlib import Path
import numpy as np

root = Path("/home/nigel/acl2027")
vendor = root / "vendor/TimelyRAG"
run = "smoke-company-dense-20261105T013539Z"
public = Path("/home/acl-infer/inputs") / run / "input.json"
pred_dir = Path("/home/acl-infer/runs") / run
result = root / "results" / run
priv = root / "eval-private" / run


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rows(p):
    return [json.loads(line) for line in p.read_text().splitlines()]


sys.path.insert(0, str(vendor))
import metrics, retrieval
from config import ALPHA_GRID

assert not os.environ.get("CUDA_VISIBLE_DEVICES")
retrieval.tqdm = lambda seq, *a, **kw: seq
manifest = read(result / "manifest.json")
worker = read(pred_dir / "worker.json")
assert manifest["worker"] == worker
assert sha(public) == manifest["input_sha256"] == worker["input_sha256"]
assert sha(pred_dir / "predictions.jsonl") == worker["predictions_sha256"]
assert sha(result / "summary.json") == manifest["summary_sha256"]
assert sha(result / "per_query_metrics.jsonl") == manifest["per_query_metrics_sha256"]
assert all(
    sha(vendor / n) == expected
    for n, expected in worker["scoring_source_sha256"].items()
)
stage = read(root / "reports/bge_checkpoint.json")
assert stage["revision"] == worker["model_revision"]
assert {n: rec["sha256"] for n, rec in stage["files"].items()} == worker[
    "model_file_sha256"
]
fixture = read(public)
captured = rows(pred_dir / "predictions.jsonl")
assert len(fixture["queries"]) == len(captured) == 2 and len(fixture["ids"]) == 20
parse = lambda x: datetime.fromisoformat(x) if x else None
det = np.array([parse(x) for x in fixture["det"]], dtype=object)
dit = np.array([parse(x) for x in fixture["dit"]], dtype=object)
fields = ["hit", "recall", "precision", "ndcg", "map"]


def vector(ids, gold):
    hits = [i + 1 for i, x in enumerate(ids[:10]) if x in set(gold)]
    dcg = sum(1 / math.log2(rank + 1) for rank in hits)

    def ideal(count):
        return sum(1 / math.log2(rank + 1) for rank in range(1, min(count, 10) + 1))

    ap_sum = sum(num / rank for num, rank in enumerate(hits, start=1))
    return [
        int(bool(hits)),
        len(hits) / len(set(gold)),
        len(hits) / 10,
        dcg / ideal(len(hits)) if hits else 0,
        ap_sum / len(hits) if hits else 0,
        dcg / ideal(len(set(gold))),
        ap_sum / min(len(set(gold)), 10),
    ]


def eq(a, b):
    np.testing.assert_allclose(a, b, rtol=0, atol=1e-12)


synthetic_count = 0
tie_count = 0
mid_winners = 0
all_zero_ties = 0
for q, row in zip(fixture["queries"], captured):
    assert q["query_id"] == row["query_id"] and set(row["candidate_ids"]) == set(
        fixture["ids"]
    )
    as_native = dict(zip(row["candidate_ids"], row["candidate_scores"]))
    scores = np.array([as_native[d] for d in fixture["ids"]])
    rank = [fixture["ids"][i] for i in np.argsort(scores)[::-1]]
    assert rank == row["candidate_ids"] and rank[:10] == row["baseline"]
    assert [e["alpha"] for e in row["grid"]] == ALPHA_GRID
    for fake_id in fixture["ids"] + ["absent-synthetic"]:
        synthetic_gold = [fake_id]
        query = dict(
            query=q["query"],
            qet=parse(q["qet"]),
            qit=parse(q["qit"]),
            positive_ids=synthetic_gold,
        )
        observed = []

        def capture(ids, gold, k):
            observed.append(list(ids))
            return metrics.evaluate_ranking_ids(ids, gold, k)

        retrieval.evaluate_ranking_ids = capture
        m_auto, m_best, ha, hb = retrieval.evaluate_2stage(
            "review", lambda _: scores, [query], fixture["ids"], det, dit
        )
        values = [vector(e["top_ids"], synthetic_gold)[3] for e in row["grid"]]
        winner = values.index(max(values))
        if max(values) == 0:
            all_zero_ties += 1
        if values.count(max(values)) > 1:
            tie_count += 1
        if winner > 0:
            mid_winners += 1
        assert observed[0] == row["auto"]
        assert observed[1:-1] == [e["top_ids"] for e in row["grid"]]
        assert observed[-1] == row["grid"][winner]["top_ids"]
        assert ha[row["auto_alpha"]] == hb[ALPHA_GRID[winner]] == 1
        eq([m_auto[k][0] for k in fields], vector(row["auto"], synthetic_gold)[:5])
        eq(
            [m_best[k][0] for k in fields],
            vector(row["grid"][winner]["top_ids"], synthetic_gold)[:5],
        )
        synthetic_count += 1
# Only after synthetic reranking is over, open the two smoke evaluation labels.
assert sha(priv / "labels.json") == manifest["gold_sha256"]
labels = read(priv / "labels.json")
per_query = rows(result / "per_query_metrics.jsonl")
summary = read(result / "summary.json")
assert len(per_query) == 6
means = {name: [] for name in ["baseline", "auto", "oracle_best"]}
candidate_recall = []
ceiling = []
for row in captured:
    qid = row["query_id"]
    gold = labels[qid]["gold"]
    scores = [vector(e["top_ids"], gold)[3] for e in row["grid"]]
    oracle = row["grid"][scores.index(max(scores))]["top_ids"]
    for name, ranking in [
        ("baseline", row["baseline"]),
        ("auto", row["auto"]),
        ("oracle_best", oracle),
    ]:
        matching = [
            x for x in per_query if x["query_id"] == qid and x["method"] == name
        ]
        assert len(matching) == 1
        record = matching[0]
        assert record["category"] == labels[qid]["category"] and record["oracle"] == (
            name == "oracle_best"
        )
        result_values = vector(ranking, gold)
        eq(
            result_values,
            [record["author"][k] for k in fields]
            + [record["standard"]["ndcg"], record["standard"]["map"]],
        )
        means[name].append(result_values)
    common = len(set(gold) & set(row["candidate_ids"]))
    candidate_recall.append(common / len(set(gold)))
    ceiling.append(min(10, common) / len(set(gold)))
for method, vals in means.items():
    eq(
        np.mean(vals, axis=0),
        [summary[method][k] for k in fields + ["standard_ndcg", "standard_map"]],
    )
eq(
    [np.mean(candidate_recall), np.mean(ceiling)],
    [summary["candidate_recall100"], summary["oracle_recall10_ceiling"]],
)
print(
    json.dumps(
        {
            "synthetic_query_label_cases": synthetic_count,
            "tied_maxima": tie_count,
            "zero_maximum_ties": all_zero_ties,
            "winner_after_initial_alpha": mid_winners,
            "real_smoke_per_query_rows": len(per_query),
            "metric_values_checked_per_row": 7,
            "three_method_means_and_two_candidate_scalars_verified": True,
            "pinned_model_files_verified": len(stage["files"]),
            "prediction_sha256": sha(pred_dir / "predictions.jsonl"),
            "status": "passed",
        }
    )
)
