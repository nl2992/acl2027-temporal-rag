# INSTRUCTOR-L runner independent review checkpoint

2026-11-06. Fresh Codex reviewer was requested through the regular reviewer route (gpt-6-astra, xhigh, native); actual backend identity was not independently attested. Findings below are the reviewer's interim message, not a completed review or deployment approval. Review was read-only and used synthetic checks.

- P1: The draft runner verifies four deployed script identities but does not pin the data staging script or the TEMPO retriever implementation. The worker records the retrieval source hash; recording it is not an expected-value check. The BGE suite's source gate does not automatically apply to this draft.
- P1: The standalone runner lacks a shared process/resource exclusion gate. The BGE queue's current process detection does not list the INSTRUCTOR worker. Concurrent runs could contend for GPU/memory or shared caches.
- P2: Export validation does not assert requested domain, smoke/full scope, expected counts, staging hash, source hash, or repaired revision before marking the launch complete. A synthetic reviewer check accepted wrong scope. Reporting filters are not a replacement for run-level validation.
- P2: The worker can reuse a cache while overwriting its descriptor without proving cached array bytes, dtype, mapping and completeness match that descriptor; the upstream retriever trusts pre-existing cache contents. FP32 constructor checks do not establish the dtype of a warm cache.

Actual namespace deployment and access controls, offline paths, full integration and real-model execution remain untested. The reviewer did not establish a current gold-label leak. Runner remains disabled; do not deploy until issues are repaired and re-reviewed. Bitcoin BGE remains separately running.

The reviewer subsequently completed the read-only review and confirmed all four findings, recommending the runner remain disabled. Reviewed runner SHA256: d4a159644f37ce0496d79ed14da198281dd9bb25c7e2732d06b0ca60e6d8ded7; worker SHA256: 88e1a336534abd8abdf91cf06eace91d4fc25661a9911d86de3c7fb1976b16cd. The review is same-family provisional and actual backend identity is not independently attested. The reviewer independently reran the synthetic export fixture and demonstrated acceptance of a wrong-scope manifest in memory. No source changes or experiments were made by the reviewer.
