"""CPU audit of saved P0 predictions. Run from the Windows workspace in WSL.

Reads local protected research inputs for offline verification. Prints aggregate
evidence and hashes only. No model, network, first-stage retrieval or output writes.
"""

from collections import defaultdict
from datetime import datetime
from hashlib import sha256
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import zipfile

import numpy as np


PROJECT = Path(__file__).resolve().parents[2]
LINUX = Path("/home/nigel/acl2027")
INFER = Path("/home/acl-infer")
PRISTINE = LINUX / "vendor/TimelyRAG"
REPAIRED = LINUX / "vendor/TimelyRAG-repaired"
UPSTREAM = "5213a0c1743f23fd52a258005c3887aaf7e8cd0f"
METHODS = ("baseline", "auto", "oracle_best")
FIELDS = ("hit", "recall", "precision", "ndcg", "map", "standard_ndcg", "standard_map")
DOMAINS = {"company": "company_policies", "law": "law", "terms": "terms_of_service", "university": "university"}
GRID = [i / 10 for i in range(11)]
WEIGHTS = [1 / math.log2(i + 2) for i in range(10)]


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    with path.open("rb") as f:
        h = sha256()
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
        return h.hexdigest()


def git(repo, *args):
    return subprocess.check_output(["git", "-c", f"safe.directory={repo}", "-C", str(repo), *args])


def close(a, b):
    assert math.isclose(a, b, abs_tol=1e-12, rel_tol=0), (a, b)


def vector(top, gold):
    hits = [i for i, gid in enumerate(top) if gid in gold]
    dcg = sum(WEIGHTS[i] for i in hits)
    numerator = sum(rank / (i + 1) for rank, i in enumerate(hits, start=1))
    n = len(hits)
    ideal_count = min(10, len(gold))
    return (int(bool(n)), n / len(gold), n / 10, dcg / sum(WEIGHTS[:n]) if n else 0,
            numerator / max(1, n), dcg / sum(WEIGHTS[:ideal_count]), numerator / ideal_count)


def check_public(source, data, labels, domain):
    # Source record ordinals and explicit released fields, never inferred from rankings.
    from TimelyQABench_datasets import prepare_dataset_collections
    assert set(data) == {"domain", "smoke", "ids", "docs", "dit", "det", "queries"}
    assert data["domain"] == domain
    if data["smoke"]:
        source = source[:2]
    gold = {f"{domain}:{i}": {"gold": sorted(set(item["gold_docs_final_global"])),
                              "category": item["category"]} for i, item in enumerate(source)}
    assert gold == labels
    docs = [d for item in source for d in item["docs_ko"]]
    ids = [d["global_doc_id"] for d in docs]
    assert ids == data["ids"] and len(set(ids)) == len(ids)
    id_set = set(ids)
    assert "__NO_TRUE_GOLD__" not in id_set
    assert all(rec["gold"] and set(rec["gold"]) <= id_set for rec in gold.values())
    assert [d["text"] for d in docs] == data["docs"]
    _, _, _, _, qet, qit, det, dit = prepare_dataset_collections(source)
    def stamp(t):
        return t.isoformat() if t is not None else None
    assert [stamp(t) for t in det] == data["det"] and [stamp(t) for t in dit] == data["dit"]
    assert data["queries"] == [{"query_id": f"{domain}:{i}", "query": item["query_ko"],
                                "qit": stamp(qit[i]), "qet": stamp(qet[i])} for i, item in enumerate(source)]


def check_rows(rows, records, data, labels, summary, subgroup):
    totals = defaultdict(list)
    grouped = defaultdict(list)
    common, ceilings = [], []
    n = len(labels)
    seen = set()
    times = defaultdict(list)
    allowed_ids = set(data["ids"])
    for row_line, q in zip(rows, data["queries"], strict=True):
        row = json.loads(row_line)
        qid = q["query_id"]
        assert row["query_id"] == qid and qid not in seen
        seen.add(qid)
        gold = set(labels[qid]["gold"])
        ids = row["candidate_ids"]
        scores = row["candidate_scores"]
        assert len(ids) == len(scores) == len(set(ids)) == min(100, len(allowed_ids))
        assert set(ids) <= allowed_ids and all(math.isfinite(s) for s in scores)
        assert scores == sorted(scores, reverse=True) and row["baseline"] == ids[:10]
        grid = row["grid"]
        assert [e["alpha"] for e in grid] == GRID
        assert row["auto"] == grid[GRID.index(row["auto_alpha"])]["top_ids"]
        for top in [row["baseline"], row["auto"], *(e["top_ids"] for e in grid)]:
            assert len(top) == len(set(top)) == 10 and set(top) <= set(ids)
        best = max(grid, key=lambda e: vector(e["top_ids"], gold)[3])
        top_by_method = (row["baseline"], row["auto"], best["top_ids"])
        for method, top in zip(METHODS, top_by_method):
            r = json.loads(next(records))
            assert (r["query_id"], r["method"]) == (qid, method)
            assert r["category"] == labels[qid]["category"] and r["oracle"] == (method == "oracle_best")
            values = vector(top, gold)
            for x, y in zip(values, [r["author"][k] for k in FIELDS[:5]] + [r["standard"]["ndcg"], r["standard"]["map"]]):
                close(x, y)
            totals[method].append(values)
            grouped[method, r["category"]].append(values)
        ng = len(set(ids) & gold)
        common.append(ng / len(gold))
        ceilings.append(min(10, ng) / len(gold))
        for key in ("score_seconds", "instrumented_rerank_with_all_grid_seconds"):
            times[key].append(row[key])
    assert seen == labels.keys() and next(records, None) is None
    for method, values in totals.items():
        for i, key in enumerate(FIELDS):
            close(statistics.mean(v[i] for v in values), summary[method][key])
    close(statistics.mean(common), summary["candidate_recall100"])
    close(statistics.mean(ceilings), summary["oracle_recall10_ceiling"])
    if subgroup is not None:
        assert len(grouped) == len(subgroup) == len({(r["method"], r["raw_category"]) for r in subgroup})
        for r in subgroup:
            group = grouped[r["method"], r["raw_category"]]
            assert len(group) == r["queries"]
            close(statistics.mean(v[3] for v in group), r["author_ndcg"])
            close(statistics.mean(v[5] for v in group), r["standard_ndcg"])
    return times


def check_timing(query_times, m, timing):
    for source, key in [("score_seconds", "base_scoring"), ("instrumented_rerank_with_all_grid_seconds", "native_rerank_plus_all_11_grid_trials")]:
        times = sorted(query_times[source])
        assert all(math.isfinite(t) and t >= 0 for t in times)
        assert len(times) == timing[key]["queries"]
        for metric, value in [("mean_seconds", statistics.mean(times)), ("median_seconds", statistics.median(times)), ("p95_seconds", times[int(len(times) * 0.95)])]:
            close(value, timing[key][metric])
    assert timing["worker_elapsed_seconds"] == m["worker"]["elapsed_seconds"]
    assert timing["peak_torch_allocated_bytes"] == m["worker"]["peak_torch_vram_bytes"]


def main():
    assert __debug__, "Checks must run without python -O"
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(PRISTINE))
    archive = PRISTINE / "datasets.zip"
    up = read(PROJECT / "manifests/upstream_audit.json")
    assert git(PRISTINE, "rev-parse", "HEAD").decode().strip() == up["sha"] == UPSTREAM
    assert git(PRISTINE, "diff", "--name-only", UPSTREAM) == b""
    assert set(git(REPAIRED, "diff", "--name-only", UPSTREAM).decode().splitlines()) == {"config.py", "pipeline.py", "requirements.txt"}
    assert git(REPAIRED, "diff", UPSTREAM, "HEAD") == (PROJECT / "reports/setup/repair.patch").read_bytes()
    assert digest(archive) == up["files"]["datasets.zip"] == digest(REPAIRED / "datasets.zip")
    assert digest(PRISTINE / "TimelyRAG_paper.pdf") == up["files"]["TimelyRAG_paper.pdf"]
    for f in read(PROJECT / "manifests/input_documents.json"):
        assert digest(PROJECT / f["path"]) == f["sha256"]
    scripts = {}
    for filename in ("baseline_isolated.py", "isolated_worker.sh"):
        scripts[filename] = {sha256(git(PROJECT, "show", f"{rev}:scripts/{filename}")).hexdigest() for rev in ("4cf61d3", "b1cafe1", "05d48e3")}
    stage = read(PROJECT / "manifests/bge_checkpoint.json")
    model_hashes = {name: digest(Path(stage["snapshot"]) / name) for name in stage["files"]}
    assert model_hashes == {k: v["sha256"] for k, v in stage["files"].items()}
    cells = read(PROJECT / "reports/baseline_parity.json")
    assert cells["status"] == "REPRO_PARTIAL" and len(cells["cells"]) == 16
    table = {(r["run"], r["method"]): r for r in cells["cells"]}
    targets = read(PROJECT / "configs/published_timelyrag_table4.json")
    assert len(table) == 16 and targets["ndcg_absolute_tolerance"] == 0.005
    runtime = {r["run_id"]: r for r in read(PROJECT / "reports/baseline_runtime.json")}
    assert len(runtime) == 8
    declarations = {r["domain"]: r for r in read(PROJECT / "manifests/temporal_metadata_audit.json")}
    folders = sorted((PROJECT / "reports/baselines").glob("*/manifest.json"))
    full = set()
    report = []
    for mf in folders:
        folder = mf.parent
        run = folder.name
        if not run.startswith(("baseline-", "smoke-")):
            continue
        m = read(mf)
        domain, backbone, smoke = m["domain"], m["backbone"], m["smoke"]
        n = 2 if smoke else 3000
        assert m["run_id"] == run and m["status"] == "complete"
        assert (m["queries"], m["documents"], m["metric_k"], m["candidate_pool"]) == (n, n * 10, 10, 100)
        pred = INFER / "runs" / run
        priv = LINUX / "eval-private" / run
        out = LINUX / "results" / run
        public = INFER / "inputs" / run / "input.json"
        w = read(pred / "worker.json")
        assert w == m["worker"] and m == read(out / mf.name)
        assert w["queries"] == n and w["documents"] == 10 * n and w["uid"] != 0 and w["label_access_probes"] == "passed"
        assert w["status"] == "complete" and w["backbone"] == backbone
        mp = read(priv / "manifest.json")
        assert all(m[k] == v for k, v in mp.items())
        assert digest(mf) == digest(out / mf.name)
        assert m["upstream_sha"] == UPSTREAM and m["repaired_sha"] == git(REPAIRED, "rev-parse", "HEAD").decode().strip()
        assert m["script_sha256"] in scripts["baseline_isolated.py"]
        if "evaluator_script_sha256" in m:
            assert m["evaluator_script_sha256"] in scripts["baseline_isolated.py"]
        assert len(w["scoring_source_sha256"]) == 5
        for name, h in w["scoring_source_sha256"].items():
            assert h == digest(PRISTINE / name) == digest(REPAIRED / name) == sha256(git(PRISTINE, "show", f"{UPSTREAM}:{name}")).hexdigest()
        hashes = { "source": m["source_sha256"], "input": digest(public), "gold": digest(priv / "labels.json"),
                   "predictions": digest(pred / "predictions.jsonl"), "per_query": digest(out / "per_query_metrics.jsonl"),
                   "summary": digest(out / "summary.json"), "manifest": digest(mf)}
        assert hashes["input"] == w["input_sha256"] == m["input_sha256"] and hashes["gold"] == m["gold_sha256"]
        assert hashes["predictions"] == w["predictions_sha256"] and hashes["per_query"] == m["per_query_metrics_sha256"]
        assert hashes["summary"] == m["summary_sha256"] == digest(folder / "summary.json")
        summary = read(out / "summary.json")
        if (folder / "launch.json").exists():
            launch = read(folder / "launch.json")
            assert launch["status"] == "complete" and launch["run_id"] == run
            assert launch["launcher_sha256"] in scripts["isolated_worker.sh"] and launch["worker_script_sha256"] == m["script_sha256"]
            assert datetime.fromisoformat(launch["utc_start"]) <= datetime.fromisoformat(w["utc_start"]) <= datetime.fromisoformat(w["utc_finish"]) <= datetime.fromisoformat(launch["utc_finish"])
            assert read(folder / "prepare.log") == mp and read(folder / "evaluation.log") == summary
            log = (folder / "inference.log").read_bytes()
            start = log.rindex(b"\n{") + 1
            end = log.index(b"\n}", start) + 2
            assert json.loads(log[start:end]) == w
        else:
            assert run == "smoke-company-bm25-002"
        member = f"timelyrag_{DOMAINS[domain]}_dataset_v2.jsonl"
        with zipfile.ZipFile(archive) as z:
            content = z.read(member)
        assert sha256(content).hexdigest() == digest(REPAIRED / "datasets" / member) == m["source_sha256"]
        public_data = read(public)
        labels = read(priv / "labels.json")
        check_public([json.loads(line) for line in content.splitlines()], public_data, labels, domain)
        if not smoke:
            counts = declarations[domain]
            for key, recorded in [("dit", "parsed_document_insert_time"), ("det", "parsed_document_event_time")]:
                assert sum(x is not None for x in public_data[key]) == counts[recorded]
            for key, recorded in [("qit", "parsed_query_insert_time"), ("qet", "parsed_or_query_extracted_event_time")]:
                assert sum(q[key] is not None for q in public_data["queries"]) == counts[recorded]
        group = read(folder / "subgroups_raw.json") if not smoke else None
        with (pred / "predictions.jsonl").open("rb") as predictions, (out / "per_query_metrics.jsonl").open("rb") as metrics:
            times = check_rows(predictions, metrics, public_data, labels, summary, group)
        if backbone == "dense":
            assert m["model_revision"] == w["model_revision"] == stage["revision"] and w["model_file_sha256"] == model_hashes
            emb_path = pred / "document_embeddings.npy"
            emb = np.load(emb_path, mmap_mode="r", allow_pickle=False)
            assert emb.shape == (n * 10, 1024) and np.isfinite(emb).all()
            hashes["embedding_observed_at_review"] = digest(emb_path)
        if not smoke:
            assert (domain, backbone) not in full
            full.add((domain, backbone))
            check_timing(times, m, runtime[run])
            for method in ("baseline", "auto"):
                r = table[run, method]
                expected = targets["domains"][domain][backbone][method]
                assert r["queries"] == n and r["domain"] == domain and r["backbone"] == backbone and r["published"] == expected
                for key, v in expected.items():
                    close(r["measured"][key], summary[method][key])
                    close(r["delta"][key], summary[method][key] - v)
                assert (r["ndcg_gate"] == "within_tolerance") == (abs(r["delta"]["ndcg"]) <= 0.005)
                close(r["candidate_recall100"], summary["candidate_recall100"])
        report.append({"run": run, "queries": n, "metric_rows": n * 3, "hashes": hashes})
    assert full == {(d, b) for d in DOMAINS for b in ("bm25", "dense")}
    assert len(report) == 10 and sum(r["queries"] for r in report if r["run"].startswith("baseline-")) == 24000
    print(json.dumps({"status": "pass", "checkpoint_files": len(model_hashes), "runs": report}, indent=2))


if __name__ == "__main__":
    main()
