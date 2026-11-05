# Native automatic-placement candidates

Only official metadata and small config files were inspected. No weights, encoders, placement pilot or scores were produced by this step. The native placement policy is documented separately in `tempo_placement_source_audit.json` and the compute-limits report.

| Author backend | Frozen repository revision | License metadata | Config access in tested client |
|---|---|---|---|
| E5 | `d62cc4417be0e3289c03dd459d1ef2d137e2554e` | MIT | Downloaded and hashed |
| SFR | `33a60fe7b5e00b9414981280c571e8a4f9f42f1b` | CC-BY-NC-4.0 | Downloaded and hashed |
| Qwen (paper's Qwen1.5 checkpoint) | `e2f771ba1aba0666210c7fa446fdcf467fb49108` | Apache-2.0; access-gated | HTTP401; config unavailable |
| RaDeR | `f3f15af7632da5d5e52f6089debf12c54160b147` | MIT | Downloaded and hashed |

Repository names, available root weight-file inventories, official advertised LFS digests and config digests are saved in `manifests/tempo_auto_model_candidates.json`. File inventories are not measurements of runtime memory or proof that a native full-domain run fits. E5/SFR config types are Mistral; RaDeR is Qwen2. Qwen's config could not be inspected, so loader/remote-code assumptions remain unverified.

The first collection attempt stopped on Qwen's HTTP401. The metadata collector was repaired to retain per-model results and record access failures without substituting another checkpoint or accepting model-gate terms. A subsequent collection completed and retained the same denial. No auth token value was printed or copied; standard Windows credential-presence checks and the Linux SDK reported no configured token. An optional access-status question is pending while other baselines continue.

Remaining gates: authorized access where required, checkpoint/remote-code audit and storage budget, gold-free worker review, original-settings smoke on an idle GPU, actual device-map and resource/throughput measurements, then all original domains and parity checks. The active BGE pipeline is unchanged. Larger-model local feasibility remains unresolved, and none of these preparation records counts as reproduction.
