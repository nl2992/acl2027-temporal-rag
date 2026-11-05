"""Check the completed-run evidence against release digests and the frozen parity reports.

Execute on Windows. Read-only access to WSL; the only network calls fetch two
small Hugging Face directory listings at the pinned dataset commit.
"""
import hashlib
import json
import re
import subprocess
import urllib.request
from collections import Counter
from decimal import Decimal

from verify_tempo_results import DATA, PROJECT, ROOT, SOURCE, digest, local, read, wsl


def installed_metric_provider():
    code = """
from importlib import metadata, util
import base64, hashlib, json, pathlib
out = {}
for module in ('pytrec_eval', 'pytrec_eval_ext'):
    path = pathlib.Path(util.find_spec(module).origin).resolve()
    content_hash = hashlib.sha256(path.read_bytes())
    token = base64.urlsafe_b64encode(content_hash.digest()).decode().rstrip('=')
    owners = []
    for name in ('pytrec-eval', 'pytrec-eval-terrier'):
        dist = metadata.distribution(name)
        if any(f.hash and f.hash.mode == 'sha256' and f.hash.value == token
               and dist.locate_file(f).resolve() == path for f in dist.files or []):
            owners.append(f'{name}=={dist.version}')
    out[module] = {'sha256': content_hash.hexdigest(), 'matching_records': owners}
print(json.dumps(out))
"""
    return json.loads(wsl("/home/nigel/miniforge3/envs/tempo-native/bin/python", "-IB", "-c", code))


def author_rows(blob):
    rows = [line.split("|")[1:-1] for line in blob.decode().splitlines() if line.startswith("|")]
    header_index = next(i for i, row in enumerate(rows) if row[0].strip() == "Domain")
    header = [name.strip() for name in rows[header_index][1:]]
    records = {}
    for row in rows[header_index + 2:]:
        if len(row) != len(header) + 1:
            break
        name, *values = [re.sub(r"<[^>]+>|\*", "", item).strip() for item in row]
        domain = {"Political": "politics"}.get(name, name.lower())
        assert domain not in records
        records[domain] = dict(zip(header, map(float, values), strict=True))
    return records


def verify_snapshot():
    reports = ROOT / "reports"
    evidence = [json.loads(line) for line in
                (reports / "review_tools/tempo_evidence.jsonl").read_text().splitlines()]
    assert len(evidence) == len({row["run_id"] for row in evidence}) == 16
    full = [row for row in evidence if not row["smoke"]]
    assert Counter(row["model"] for row in full) == {"bm25": 13, "bge": 1}
    assert len({(r["model"], r["domain"]) for r in full}) == 14
    parity = read(reports / "tempo_parity.json")
    coverage = read(reports / "tempo_retriever_coverage.json")
    targets = read(ROOT / "configs/published_tempo_retrievers.json")
    bm_targets = read(ROOT / "configs/published_tempo_bm25.json")
    readme = subprocess.check_output(["git", "-C", str(ROOT / "vendor/Tempo"), "show", f"{SOURCE}:README.md"])
    readme_hash = hashlib.sha256(readme).hexdigest()
    assert readme_hash == targets["readme_blob_sha256"]
    author = author_rows(readme)
    assert len(author) == 14 and len(targets["models"]) == 12
    for model, target in targets["models"].items():
        assert target["domains"] == {k: vals[model] for k, vals in author.items() if k != "avg."}
        assert target["macro_average_percentage"] == author["avg."][model]
    assert bm_targets["domains"] == targets["models"]["BM25"]["domains"]
    assert bm_targets["macro_average"] == author["avg."]["BM25"]
    hashes = {}
    for kind in ("examples", "documents"):
        url = f"https://huggingface.co/api/datasets/tempo26/Tempo/tree/{DATA}/{kind}"
        with urllib.request.urlopen(url, timeout=20) as response:
            files = json.load(response)
        hashes[kind] = {r["path"]: r["lfs"]["oid"] for r in files}
        assert len(hashes[kind]) == 13
    for r in evidence:
        for kind, files in hashes.items():
            assert files[f"{kind}/{r['domain']}.parquet"] == r["digests"][kind]

    parity_rows = {r["run_id"]: r for r in parity["runs"]}
    assert len(parity_rows) == len(parity["runs"]) == 13
    values = []
    for r in full:
        domain, run_id = r["domain"], r["run_id"]
        model = {"bge": "BGE", "bm25": "BM25"}[r["model"]]
        summary = reports / "tempo" / run_id / "summary.json"
        assert digest(summary) == r["digests"]["summary"]
        value = read(summary)["NDCG@10"]
        coverage_row = coverage["models"][model]["runs"][domain]
        assert coverage_row["run_id"] == run_id and coverage_row["ndcg10"] == value
        assert all(coverage_row[key] == r[key] for key in ("queries", "documents"))
        # Strict inequality rules out the ambiguous half-unit boundary in the
        # production report's inclusive rounding-interval test.
        assert abs(Decimal(str(value))*100 - Decimal(str(author[domain][model]))) < Decimal(".05")
        assert coverage_row["author_target_percentage"] == author[domain][model]
        if model == "BM25":
            p = parity_rows[run_id]
            assert all(p[key] == r[key] for key in ("queries", "documents", "domain"))
            assert p["ndcg10"] == value and p["published_percentage"] == author[domain][model]
            values.append(value)
    assert abs(sum(values)/13 - parity["full_macro_ndcg10"]) < 1e-12
    assert abs(sum(values)/13 - coverage["models"]["BM25"]["full_macro_ndcg10"]) < 1e-12
    assert abs(sum(values)/13*100 - author["avg."]["BM25"]) < .05
    assert set(coverage["models"]) == set(targets["models"])
    for model, entry in coverage["models"].items():
        count = {"BM25": 13, "BGE": 1}.get(model, 0)
        assert len(entry["runs"]) == entry["completed_domains"] == entry["matching_domain_rounding"] == count
        assert entry["expected_domains"] == 13
        if count < 13:
            assert entry["full_macro_ndcg10"] is None

    staged = read(local("/home/acl-infer/models/tempo_models.json"))["bge"]
    assert staged == read(ROOT / "manifests/tempo_models.json")["bge"]
    for r in evidence:
        if r["model"] == "bge":
            manifest = read(local(f"{PROJECT}/results/{r['run_id']}/manifest.json"))
            assert manifest["worker"]["model_snapshot"] == staged
    model_paths = [f'{staged["snapshot"]}/{name}' for name in staged["files"]]
    model_hashes = wsl("ionice", "-c", "3", "nice", "-n", "19", "sha256sum", *model_paths).splitlines()
    assert [line.split()[0] for line in model_hashes] == [f["sha256"] for f in staged["files"].values()]
    return {"pinned_author_readme_sha256": readme_hash, "verified_target_cells": 156,
            "verified_target_macros": 12, "hf_lfs_oids_verified": 26,
            "verified_full_rounded_cells": len(full), "verified_full_macro_count": 1,
            "verified_bge_snapshot_files": len(staged["files"]),
            "current_metric_provider": installed_metric_provider(),
            "full_bm25_total_queries": sum(r["queries"] for r in full if r["model"] == "bm25"),
            "full_bm25_domain_document_entries": sum(r["documents"] for r in full if r["model"] == "bm25"),
            "total_ranking_entries_all_checked_runs": sum(r["saved_rank_entries"] for r in evidence),
            "full_runs_without_runtime_worker_sha256": sum(not r["worker_script_sha256_if_recorded"] for r in full),
            "checked_run_count": len(evidence), "sum_ordinary_keys": sum(r["ordinary_keys_verified"] for r in evidence),
            "sum_oracle_keys": sum(r["diagnostic_keys_verified"] for r in evidence),
            "hashes": {str(path.relative_to(ROOT)).replace(chr(92), "/"): digest(path) for path in (
                reports/"tempo_parity.json", reports/"tempo_retriever_coverage.json",
                reports/"review_tools/tempo_evidence.jsonl", reports/"review_tools/verify_tempo_results.py",
                reports/"review_tools/verify_tempo_snapshot.py")}}


if __name__ == "__main__":
    print(json.dumps(verify_snapshot(), indent=2))
