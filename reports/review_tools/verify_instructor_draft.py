"""Exercise pinned TEMPO functions with a fake encoder and synthetic vectors on CPU."""
import ast
import contextlib
import difflib
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace

import numpy as np
import sklearn
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = "8731487254e0988eaf2ca4ae3e93ff587fec64d0"
BASE = ROOT / "scripts/tempo_isolated.py"
DRAFT = ROOT / "scripts/drafts/tempo_instructor_isolated.py"
STAGED = json.loads((ROOT / "manifests/tempo_instructor_checkpoint.json").read_bytes())
SNAPSHOT = STAGED["snapshot"]
QUERY_PROMPT = "Represent this query for retrieving relevant documents: "


def digest(value):
    return hashlib.sha256(value).hexdigest()


def definition(tree, name):
    matches = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(matches) == 1, name
    return matches[0]


def execute(nodes, env):
    module = ast.Module(body=nodes, type_ignores=[])
    exec(compile(module, "<extracted source>", "exec"), env)


def named_assignment(tree, name):
    matches = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)
               and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name]
    assert len(matches) == 1, name
    return matches[0]


def source_check():
    native = subprocess.check_output(["git", "-C", str(ROOT / "vendor/Tempo"),
                                      "show", UPSTREAM + ":retrievers.py"])
    assert digest(native) == "90169e77aec737c238df9d682833379404d2e4381b074d43495c22bebaae27e4"
    base = BASE.read_bytes()
    draft = DRAFT.read_bytes()
    assert digest(base) == "9f0e5555495972ea6cb076d46fe11b2b4052cf1295cb066e2093b53bf601c3ee"
    patch = difflib.diff_bytes(difflib.unified_diff,
                               base.splitlines(True), draft.splitlines(True),
                               b"frozen-tempo-isolated-9f0e5555.py", b"draft-tempo-instructor-isolated.py")
    assert b"".join(patch) == (ROOT / "reports/instructor_worker_draft.patch").read_bytes()
    assert ast.dump(definition(ast.parse(base), "evaluate")) == ast.dump(definition(ast.parse(draft), "evaluate"))
    with tempfile.TemporaryDirectory() as tmp:
        replica = Path(tmp)
        (replica / "scripts").mkdir()
        (replica / "reports").mkdir()
        builder = Path("scripts/build_instructor_worker_draft.py")
        shutil.copyfile(ROOT / builder, replica / builder)
        shutil.copyfile(BASE, replica / "scripts/tempo_isolated.py")
        subprocess.run([sys.executable, "-IB", str(replica / builder)], capture_output=True, check=True)
        for name in ["scripts/drafts/tempo_instructor_isolated.py", "reports/instructor_worker_draft.patch"]:
            assert (ROOT / name).read_bytes() == (replica / name).read_bytes()
    return ast.parse(native), definition(ast.parse(draft), "worker")


def cache_key(worker, data):
    # Use the draft's descriptor expressions with a fixed synthetic version environment.
    env = {"data": data, "a": SimpleNamespace(model="inst-l"),
           "model_manifest": STAGED, "VENDOR": Path("synthetic"), "sha": lambda _: "review-source",
           "importlib": SimpleNamespace(metadata=SimpleNamespace(version=lambda p: p + "-review")),
           "json": json, "hashlib": hashlib}
    names = ["instructions", "ordered_docs_sha256", "descriptor", "key"]
    execute([named_assignment(worker, n) for n in names], env)
    descriptor = env["descriptor"]
    assert (descriptor["batch_size"], descriptor["max_length"]) == (4, 2048)
    assert descriptor["input_serialization"] == {"query": QUERY_PROMPT, "document": ""}
    assert descriptor["model_revision"] == descriptor["tokenizer_revision"] == STAGED["revision"]
    return env["key"]


class Encoder:
    vectors = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]], dtype=np.float32)

    def __init__(self, name, dtype):
        self.name = name
        self.dtype = dtype
        self.max_seq_length = 512
        self.pool = SimpleNamespace(include_prompt=True)
        self.calls = []

    def parameters(self):
        yield SimpleNamespace(dtype=self.dtype)

    def modules(self):
        return [self, self.pool]

    def set_pooling_include_prompt(self, flag):
        self.pool.include_prompt = flag

    def encode(self, texts, **kwargs):
        self.calls.append((list(texts), kwargs.copy(), self.max_seq_length, self.pool.include_prompt))
        rows = self.vectors[[int(text[-1]) for text in texts]]
        return rows.astype(np.float16) if self.dtype == "torch.float16" else rows


def run_once(native, worker, cache, observed, inputs, dtype="torch.float32"):
    models = []

    def constructor(name):
        model = Encoder(name, dtype)
        models.append(model)
        return model

    profile = {}
    env = {"np": np, "json": json, "Path": Path, "cosine_similarity": cosine_similarity,
           "torch": SimpleNamespace(no_grad=lambda: (lambda f: f)), "original_st": constructor,
           "mapped": {STAGED["repo"]: SNAPSHOT}, "profile": profile}
    execute([definition(worker, "local"), definition(worker, "sentence_transformer"),
             definition(native, "get_scores"), definition(native, "retrieval_instructor")], env)
    env["SentenceTransformer"] = env["sentence_transformer"] if observed else constructor
    with contextlib.redirect_stdout(io.StringIO()):
        scores = env["retrieval_instructor"](**inputs, cache_dir=str(cache))
    assert len(models) == 1 and models[0].name == (SNAPSHOT if observed else STAGED["repo"])
    return {q: list(row.items()) for q, row in scores.items()}, models[0].calls, profile


def rejected_dtype_published_cache(native, worker, cache, inputs):
    # Replay the worker's final dtype assertion too, so an error after publication is visible.
    post_checks = [s for n in worker.body if isinstance(n, ast.If) for s in n.body
                   if isinstance(s, ast.Assert) and "parameter_dtype" in ast.unparse(s.test)]
    assert len(post_checks) == 1
    try:
        _, _, profile = run_once(native, worker, cache, True, inputs, dtype="torch.float16")
        execute(post_checks, {"profile": profile})
    except AssertionError as rejection:
        assert "torch.float16" in str(rejection), "unexpected fixture failure"
    else:
        raise AssertionError("draft accepted fake FP16 model")
    published = list(cache.rglob("embeddings.npy"))
    if published:
        assert len(published) == 1 and np.load(published[0]).dtype == np.float16
    return bool(published)


def main():
    native, worker = source_check()
    assert STAGED["repo"] == "hkunlp/instructor-large"
    assert STAGED["revision"] == "54e5ffb8d484de506e59443b07dc819fb15c7233"
    docs = [{"id": f"d{i:04}", "content": f"synthetic-{i % 4}"} for i in range(1004)]
    public = {"domain": "fixture", "documents": docs, "queries": []}
    initial_key = cache_key(worker, public)
    assert initial_key == cache_key(worker, {**public, "queries": ["different"]})
    assert initial_key != cache_key(worker, {**public, "documents": docs[::-1]})
    revised = [{**docs[0], "content": "revised"}, *docs[1:]]
    assert initial_key != cache_key(worker, {**public, "documents": revised})
    inputs = {"model_id": "inst-l", "long_context": False, "task": "fixture",
              "queries": ["query-0", "query-1"], "query_ids": ["q0", "q1"],
              "documents": [d["content"] for d in docs], "doc_ids": [d["id"] for d in docs],
              "instructions": {"query": QUERY_PROMPT, "document": ""},
              "excluded_ids": {"q0": ["d0000", "d0004", "N/A"], "q1": ["d0001", "d0005"]}}
    # Independent ranked oracle for the two orthogonal queries and four unit-vector types.
    expected = {}
    for q, allowed in enumerate(([1, 0, -1, 0], [0, 1, 0, -1])):
        qid = f"q{q}"
        pairs = [(d["id"], float(allowed[i % 4])) for i, d in enumerate(docs)
                 if d["id"] not in inputs["excluded_ids"][qid]]
        expected[qid] = sorted(pairs, key=lambda pair: -pair[1])[:1000]
    summaries = {}
    with tempfile.TemporaryDirectory() as tmp:
        for phase in ("cold", "warm"):
            plain = run_once(native, worker, Path(tmp) / "plain", False, inputs)
            wrapped = run_once(native, worker, Path(tmp) / "wrapped", True, inputs)
            assert plain[0] == wrapped[0] == expected
            assert plain[1] == wrapped[1]
            texts_by_call = [inputs["documents"], inputs["queries"]] if phase == "cold" else [inputs["queries"]]
            prompts = ["", QUERY_PROMPT] if phase == "cold" else [QUERY_PROMPT]
            assert len(wrapped[1]) == len(texts_by_call)
            expected_calls = []
            for (texts, kwargs, length, include), expected_texts, prompt in zip(wrapped[1], texts_by_call, prompts):
                assert texts == expected_texts and length == 2048 and include is False
                assert kwargs == {"show_progress_bar": True, "batch_size": 4,
                                  "normalize_embeddings": True, "prompt": prompt}
                expected_calls.append({"texts": len(texts), "batch_size": 4,
                                       "normalize_embeddings": True, "prompt": prompt})
            assert wrapped[2] == {"parameter_dtype": "torch.float32", "constructor_max_seq_length": 512,
                                  "max_seq_length": 2048, "pooling_include_prompt": [False],
                                  "encode_calls": expected_calls}
            summaries[phase] = [len(texts) for texts, *_ in wrapped[1]]
            for name in ["embeddings.npy", "doc_id_mapping.json"]:
                artifact = Path("doc_emb/inst-l/fixture/long_False") / name
                assert (Path(tmp) / "plain" / artifact).read_bytes() == (Path(tmp) / "wrapped" / artifact).read_bytes()
        assert not rejected_dtype_published_cache(native, worker, Path(tmp) / "rejected", inputs)
        # Replay the exact previous candidate in memory to preserve the failure as a reproducible witness.
        import subprocess
        current = subprocess.check_output(['git', 'show', '6d28b06:scripts/drafts/tempo_instructor_isolated.py'])
        assert digest(current) == '88e1a336534abd8abdf91cf06eace91d4fc25661a9911d86de3c7fb1976b16cd'
        guard = b"            assert profile['parameter_dtype']=='torch.float32', profile\n"
        assert current.count(guard) == 1
        previous = current.replace(guard, b"")
        assert digest(previous) == "974207548ab0d7fd1675f41594db0f64267c6a1077e8c0f3afa0aedb7db4ddfc"
        old_worker = definition(ast.parse(previous), "worker")
        assert rejected_dtype_published_cache(native, old_worker, Path(tmp) / "old", inputs)
    assert not ({"torch", "transformers", "sentence_transformers"} & sys.modules.keys())
    print(json.dumps({"status": "PASS", "scope": "synthetic CPU only", "draft_sha256": digest(DRAFT.read_bytes()),
                      "python": sys.version.split()[0], "numpy": np.__version__, "sklearn": sklearn.__version__,
                      "queries": 2, "documents": len(docs), "returned_per_query": 1000,
                      "observed_encode_sizes": summaries, "wrong_dtype_rejected_before_cache": True,
                      "previous_wrong_dtype_cache_bug_reproduced": True}, indent=2))


if __name__ == "__main__":
    main()
