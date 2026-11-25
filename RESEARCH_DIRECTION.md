# Research direction (2026-11-23, v0)

**Deadline:** ACL 2027 ARR submission 4 Jan 2027 (confirmed on 2027.aclweb.org / LINGUIST List, one check). ~6 weeks.

**Working title:** Two Clocks for Temporal Evidence Retrieval: Valid Time vs. Known Time in Versioned Official Documents

**Problem.** Temporal retrievers use one time signal (recency, an interval, or one timestamp). Historical queries can ask for what *applied* at t (valid time), what was *announced/knowable* by h (known time), or what applied at t *as known then*. In versioned official sources the two clocks routinely disagree (Federal Register final rules: publication precedes effective date, sometimes by months; a few take effect retroactively; some are later corrected).

**Novelty hypothesis (to test, not assumed).** Single-clock rankers (recency, publication cutoff, validity filter) each fail systematically on the intents they do not model; an intent-conditioned (t, h) eligibility rule fixes this, and the gain survives held-out families and a real semantic ranker. Nearest prior work: TimelyRAG, Q-TIE, Re3, IA-RAG, TEMPS, FRESCO (see LITERATURE_POSITIONING.md, still to write: one focused pass). Bitemporal DB theory (Jensen/Snodgrass, Clifford/Isakowitz) is the background, not the claim. Main collision risk: IA-RAG/Q-TIE interval handling and Re3 recency/conflict; the discriminating angle is the explicit horizon h.

**Method v1.** Parse intent in {current, valid_at, known_at, valid_known, retrospective}, derive (t, h); hard/soft eligibility from pub_time<=h and valid_from<=t<valid_to; rank eligible candidates by semantic score then temporal closeness; fall back to semantic rank when timestamps are missing.

**Data.** Federal Register API (public domain): publication_date, effective_on, corrections, CFR references. Recurring rule families (Reg Z thresholds, Medicare PPS rate updates, FMVSS, etc.). Existing TimelyRAG caches are NOT on this machine (data/, results/, cache/ are empty), so BM25 pools are built fresh.

**First experiment:** `src/pilot/*` (done, see PILOT_RESULTS.md).

**Success:** B4 beats every single-clock baseline on its own intents, no worse on current queries, on held-out families with text-verified timestamps. **Failure/pivot:** a single clock plus a trivial rule matches B4 on real (not metadata-constructed) judgments, or timestamps cannot be verified from source text.
