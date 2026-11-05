"""Read completed local TEMPO artifacts. Emit aggregate checks only, one domain at a time.

Run on Windows against the Ubuntu-24.04 store. No author model or evaluator is imported.
No dataset, private label or individual prediction is written by this program.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess

import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
DISTRO = "Ubuntu-24.04"
LINUX = Path(r"\\wsl.localhost\Ubuntu-24.04")
PROJECT = "/home/nigel/acl2027"
DATA = "1dba7027d0afa628993c6dd794e9b68c657a6fac"
SOURCE = "8731487254e0988eaf2ca4ae3e93ff587fec64d0"
KS = (1, 5, 10, 25, 50, 100)


def wsl(*args):
    return subprocess.check_output(["wsl", "-d", DISTRO, "-u", "nigel", "--", *args],
                                   encoding="utf-8").strip()


def local(path):
    return LINUX / path.lstrip("/")


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def encode(obj):
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def score_rows(path):
    """Read an outer JSON map incrementally. Each value contains one top-1000."""
    decoder = json.JSONDecoder(object_pairs_hook=unique)
    with path.open(encoding="utf-8") as stream:
        data = ""

        def refill():
            nonlocal data
            chunk = stream.read(128 * 1024)
            if not chunk:
                raise ValueError("unexpected end of ranking JSON")
            data += chunk

        def leading():
            nonlocal data
            data = data.lstrip()
            if not data:
                refill()
                data = data.lstrip()
            return data[0]

        def expect(char):
            nonlocal data
            assert leading() == char
            data = data[1:]

        def item():
            nonlocal data
            leading()
            while True:
                try:
                    value, end = decoder.raw_decode(data)
                except json.JSONDecodeError:
                    refill()
                else:
                    data = data[end:]
                    return value

        expect("{")
        while leading() != "}":
            qid = item()
            expect(":")
            yield qid, item()
            if leading() == "}":
                break
            expect(",")
        expect("}")
        assert not data.strip() and not stream.read(1)


def metric_values(scores, positives):
    """Binary trec cut metrics. Score ties rank by descending document ID."""
    ranked = sorted(scores, key=lambda did: (scores[did], did), reverse=True)
    hits = [i for i, did in enumerate(ranked, start=1) if did in positives]
    # The author oracle first picks its 100 by stable input order. pytrec_eval
    # subsequently sorts all 1000 by oracle score, including zero-score ties.
    eligible = set(sorted(scores, key=scores.get, reverse=True)[:100]) & positives
    oracle = sorted(scores, key=lambda did: (did in eligible, did), reverse=True)
    oracle_hits = [i for i, did in enumerate(oracle[:100], start=1) if did in positives]
    values = {"MRR": 1 / hits[0] if hits else 0}
    for k in KS:
        best = sum(1 / math.log2(i + 1) for i in range(1, min(k, len(positives)) + 1))
        positions = [i for i in hits if i <= k]
        values[f"NDCG@{k}"] = sum(1 / math.log2(i + 1) for i in positions) / best
        values[f"MAP@{k}"] = sum(n / i for n, i in enumerate(positions, 1)) / len(positives)
        values[f"Recall@{k}"] = len(positions) / len(positives)
        values[f"P@{k}"] = len(positions) / k
        values[f"Oracle NDCG@{k}"] = sum(1 / math.log2(i + 1) for i in oracle_hits if i <= k) / best
    return values


def verify(run_id):
    folder = ROOT / "reports/tempo" / run_id
    linux_result = local(f"{PROJECT}/results/{run_id}")
    exported = (folder / "manifest.json").is_file()
    result_folder = folder if exported else linux_result
    m = read(result_folder / "manifest.json")
    worker = m["worker"]
    domain = m["domain"]
    assert m["run_id"] == run_id and m["benchmark"] == worker["benchmark"] == "TEMPO"
    assert m["status"] == worker["status"] == "complete" and worker["uid"] == 1001
    assert m["source_sha"] == SOURCE and m["dataset_revision"] == DATA
    assert m.get("model", worker["model"]) == worker["model"]
    private = f"{PROJECT}/eval-private/{run_id}"
    runs = f"/home/acl-infer/runs/{run_id}"
    assert read(local(runs + "/worker.json")) == worker
    prep = read(local(private + "/manifest.json"))
    assert all(m.get(k) == v for k, v in prep.items())
    raw = f"{PROJECT}/tempo-private/hf_cache/datasets--tempo26--Tempo/snapshots/{DATA}"
    resolved = {key: wsl("realpath", f"{raw}/{key}/{domain}.parquet") for key in ("examples", "documents")}
    sources = dict(resolved, input=f"/home/acl-infer/inputs/{run_id}/input.json",
                   scores=runs + "/scores.json", labels=private + "/labels.json")
    # Large-file hashing stays inside Linux with a small read buffer at idle I/O priority.
    lines = wsl("ionice", "-c", "3", "nice", "-n", "19", "sha256sum", *sources.values()).splitlines()
    hashes = {k: line.split()[0] for k, line in zip(sources, lines, strict=True)}
    assert {k: hashes[k] for k in resolved} == m["raw_file_sha256"]
    assert hashes["input"] == m["input_sha256"] == worker["input_sha256"]
    assert hashes["scores"] == worker["scores_sha256"] and hashes["labels"] == m["gold_sha256"]
    newline_only_export_digests = {}
    for name in ("manifest.json", "summary.json"):
        if exported:
            export_bytes = (folder / name).read_bytes()
            original_bytes = (linux_result / name).read_bytes()
            if export_bytes != original_bytes:
                assert run_id == "tempo-iota-bge-smoke-001"
                assert export_bytes == original_bytes.replace(b"\n", b"\r\n")
                newline_only_export_digests[name] = hashlib.sha256(export_bytes).hexdigest()
    assert digest(linux_result / "summary.json") == m["summary_sha256"]
    assert wsl("sha256sum", f"{PROJECT}/vendor/Tempo-repaired/retrievers.py").split()[0] == worker["source_sha256"]

    examples = pq.ParquetFile(local(resolved["examples"]))
    documents = pq.ParquetFile(local(resolved["documents"]))
    assert examples.metadata.num_rows == m["original_queries"]
    assert documents.metadata.num_rows == m["original_documents"] == m["documents"] == worker["documents"]
    query_count = 2 if m["smoke"] else examples.metadata.num_rows
    assert query_count == m["queries"] == worker["queries"]
    data = {}
    for batch in examples.iter_batches(columns=["id", "query", "negative_ids", "gold_ids"],
                                       batch_size=16, use_threads=False):
        for row in batch.to_pylist():
            if len(data) >= query_count:
                break
            assert row["id"] not in data and row["gold_ids"]
            data[row["id"]] = row
    labels = read(local(sources["labels"]))
    assert labels == {qid: {"gold_ids": row["gold_ids"]} for qid, row in data.items()}

    # Check the public header and exact query suffix against the source. The
    # corpus text stays compressed. Its full files are covered by the hashes
    # above; this deliberately does not rederive each document's content.
    header = encode({"domain": domain, "smoke": m["smoke"], "documents": []})[:-2]
    queries = [{"id": r["id"], "query": r["query"], "excluded_ids": r["negative_ids"]}
               for r in data.values()]
    suffix = b'], "queries": ' + encode(queries) + b"}"
    with local(sources["input"]).open("rb") as stream:
        assert stream.read(len(header)) == header
        stream.seek(-len(suffix), 2)
        assert stream.read() == suffix
    docids = set()
    for batch in documents.iter_batches(columns=["id"], batch_size=2048, use_threads=False):
        docids.update(batch.column(0).to_pylist())
    assert len(docids) == m["documents"]
    sums = defaultdict(float)
    seen = set()
    rank_count = 0
    overlaps = 0
    for qid, scores in score_rows(local(sources["scores"])):
        assert qid not in seen and qid in data
        seen.add(qid)
        gold = set(data[qid]["gold_ids"])
        excluded = set(data[qid]["negative_ids"]) - {"N/A"}
        assert gold <= docids and excluded <= docids
        overlaps += len(gold & excluded)
        assert len(scores) == min(1000, len(docids) - len(excluded))
        assert all(did in docids and did not in excluded and math.isfinite(value) for did, value in scores.items())
        assert list(scores.values()) == sorted(scores.values(), reverse=True)
        rank_count += len(scores)
        for key, value in metric_values(scores, gold).items():
            sums[key] += value
    assert seen == set(data) and len(seen) == query_count
    summary = read(result_folder / "summary.json")
    assert len(sums) == 31 and set(sums) == set(summary)
    for key, total in sums.items():
        assert abs(total / query_count - summary[key]) <= 0.000005000001, (run_id, key, total / query_count, summary[key])
    log_presence = {}
    for file, expected in (("prepare.log", prep), ("inference.log", worker), ("evaluation.log", summary)):
        log = folder / file
        log_presence[file] = log.exists()
        if log.exists():
            text = log.read_text(encoding="utf-8", errors="replace")
            pretty = json.dumps(expected, indent=2, ensure_ascii=True)
            assert pretty in text, (run_id, file)
    launch = folder / "launch.json"
    if launch.exists():
        assert read(launch)["status"] == "complete"
    return {"run_id": run_id, "domain": domain, "model": worker["model"], "smoke": m["smoke"],
            "queries": query_count, "documents": len(docids), "saved_rank_entries": rank_count,
            "ranked_exclusion_violations": 0, "gold_exclusion_overlaps": overlaps,
            "ordinary_keys_verified": 25, "diagnostic_keys_verified": 6,
            "digests": dict(hashes, summary=m["summary_sha256"], manifest=digest(linux_result / "manifest.json")),
            "crlf_only_export_digests": newline_only_export_digests,
            "windows_export_present": exported,
            "worker_script_sha256_if_recorded": worker.get("worker_script_sha256"),
            "launch_json_present": launch.exists(), "logs_in_run_folder": log_presence}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    result = verify(parser.parse_args().run_id)
    print(json.dumps(dict(result, checked_at_utc=datetime.now(timezone.utc).isoformat())))
