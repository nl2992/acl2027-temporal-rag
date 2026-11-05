# TEMPO INSTRUCTOR-L preparation

Status: **checkpoint staged; inference not executed**. This is preparation for another listed original retriever, not a completed reproduction.

The released TEMPO `retrieval_instructor` selects `hkunlp/instructor-large` for `inst-l`. Its defaults are batch 4, maximum sequence length 2,048, normalized embeddings, excluded prompt tokens in pooling, and the released top-1,000/exclusion logic. No smaller checkpoint, precision change, truncation repair or alternate instruction has been selected.

The official [snapshot](https://huggingface.co/hkunlp/instructor-large/tree/54e5ffb8d484de506e59443b07dc819fb15c7233) was frozen at `54e5ffb8d484de506e59443b07dc819fb15c7233`. Official metadata identifies Apache-2.0 licensing. Twelve selected model/config/tokenizer files total 1,346,191,645 bytes. Downloaded file sizes and all advertised LFS SHA256 values matched. See `manifests/tempo_instructor_source.json` and `manifests/tempo_instructor_checkpoint.json`.

The model's module configuration uses standard SentenceTransformers Transformer, Pooling, Dense and Normalize modules. It describes a T5 encoder and a 1,024-to-768 dense projection. Its saved sequence configuration says 512; the released TEMPO function explicitly overrides this to 2,048. These are source observations, not proof of loader compatibility or local GPU feasibility. The author code does not pin a historical checkpoint revision, so this candidate freeze alone cannot establish the checkpoint used for the published result.

Weights were downloaded into a separate `instructor-only` cache without constructing an encoder. The active BGE registry remains at its previously recorded Linux SHA256 `49fd9c91d3c921c1194ca23f3dac2754f199d34e6fe2a1f3a9aa7460ddf91951`. Its archived Windows export has CRLF and SHA256 `c06df5e5900dcf8f6efec6823ca70a705d5ee7d9cb735de74b40ffd73e1d8410`; JSON values are identical. No active registry repair or replacement was needed.

Remaining gates: integrate a separately reviewed gold-free worker, verify the original loader/settings in a native smoke after the active GPU queue, measure memory, then execute full original domains and compare ordinary metrics. Keep the current BGE worker/version frozen while its queue runs. The staging step overlapped Law's run only as checkpoint download/hashing; Law timing must not be described as an isolated speed measurement.
