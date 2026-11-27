All 12 works exist at the cited identifiers or venue. The main substantive problem is the novelty claim: **TimelyRAG explicitly models document availability relative to query time**, and the memory-store paper exposes separate valid-time and transaction-time filters. Code availability remains partly unverifiable.

For each entry below, “metadata matches” means the supplied title, author names and order, year, and identifier match the opened record. Missing venue or page fields are identified separately.

1. **`qtie2026` — OK; code-availability claim CANNOT VERIFY.**

   **Bibliography:** Metadata matches arXiv:2609.23880, submitted September 20, 2026. No venue or pages are asserted in the entry. The record also reports acceptance to EMNLP 2026 Main. [arXiv record](https://arxiv.org/abs/2609.23880)

   **Draft:** “Q-TIE maps a query's temporal constraint to an interval and re-ranks against document time.”

   **Evidence:** Sections 3–3.2 define one document timestamp, extract a query interval, and score temporal proximity using a Gaussian kernel. This supports the description. The formulation does not supply independent target-time and knowledge-horizon query fields. [Full text, §§3–3.2](https://arxiv.org/html/2609.23880v1)

   **Draft:** “The Q-TIE-style point-interval scorer and the Re$^3$-style relevance and recency gate are approximations from the papers' descriptions, because the official Q-TIE code was unavailable and we found no released Re$^3$ code.”

   **Evidence:** Q-TIE advertises an official GitHub link, but opening it returned 404. **CANNOT VERIFY** repository contents or availability when the experiments were run. Suggested wording: “The paper links to an official repository, which we could not access on [actual access date].” [Advertised repository](https://github.com/ssoy0701/Q-TIE)

2. **`re32025` — OK; code-release claim CANNOT VERIFY.**

   **Bibliography:** Metadata matches the September 1, 2025 v1. The withdrawal note is correct: v2, dated January 6, 2026, is withdrawn. Cite `2509.01306v1` explicitly because the technical claims concern that version. [Record and version history](https://arxiv.org/abs/2509.01306)

   **Draft:** “Re$^3$ is the closest to our setting: it describes a document by a content (clue) time and a publication time and learns a gate over relevance, temporal alignment and freshness.”

   **Evidence:** Section 3.1 distinguishes content/clue time from publication **or update** time. Section 4 combines semantic scores with temporal features through a learned gate. The description is supported; adding “or update” improves precision. Its query definition has one temporal requirement, rather than separate target and horizon fields. [v1 full text, §§3–4](https://arxiv.org/html/2509.01306v1)

   **Draft:** The code-availability sentence quoted under Q-TIE.

   **Evidence:** The abstract advertises an online Re³/Re²Bench resource. Its landing page yielded no readable contents, and the README could not be opened. **CANNOT VERIFY** whether usable code was released. Replace the absence claim with the advertised URL and the documented access limitation. [Advertised resource](https://anonymous.4open.science/r/Re3-0C5A)

3. **`iarag2026` — OK.**

   **Bibliography:** Metadata matches arXiv:2606.06044, submitted June 4, 2026. No venue or pages are asserted. [arXiv record](https://arxiv.org/abs/2606.06044)

   **Draft:** “IA-RAG represents facts as intervals related by Allen's algebra.”

   **Evidence:** The method represents facts as Interval Event Units and assigns Allen interval relations between semantically compatible units. The sentence accurately summarizes that mechanism. [Full text, §3](https://arxiv.org/html/2606.06044v1)

4. **`demartim2026` — OK for the attributed argument; the shared novelty claim needs correction.**

   **Bibliography:** Metadata matches arXiv:2606.09724, submitted June 8, 2026. No venue or pages are asserted. [arXiv record](https://arxiv.org/abs/2606.09724)

   **Draft:** “Recent work applies them to legal retrieval as a design argument and to agent memory as a storage and filter mechanism.”

   **Evidence:** Section 5.1, commitment C3, calls for independently representable and queryable valid and transaction times. It specifically discusses advance publication, retroactivity, delayed effectiveness, and corrections. The draft’s characterization as a legal-retrieval design argument is supported. This also establishes close conceptual precedent for the motivating examples. [Full text, §5.1, C3](https://arxiv.org/html/2606.09724v1)

5. **`niksarli2026` — OK for the storage/filter description; WRONG if included in the blanket “no query formulation” claim.**

   **Bibliography:** Metadata matches arXiv:2607.26520, submitted July 29, 2026. No venue or pages are asserted. [arXiv record](https://arxiv.org/abs/2607.26520)

   **Draft:** “Recent work applies them to legal retrieval as a design argument and to agent memory as a storage and filter mechanism.”

   **Evidence:** Section III stores versioned memories with valid-time and transaction-time intervals. Historical retrieval post-filters vector candidates using independently optional `valid_at` and `tx_at` parameters. The attributed description is accurate. [Full text, §III-B–C](https://arxiv.org/html/2607.26520v1)

   **Correction:** A broad claim that prior work lacks a query formulation selecting both clocks is untenable against those two parameters. A narrower claim about natural-language intent routing, document ranking, or your particular benchmark requires separate justification.

6. **`fresco2026` — OK.**

   **Bibliography:** Metadata matches arXiv:2604.14227, submitted April 14, 2026, including all seven authors. No venue or pages are asserted. [arXiv record](https://arxiv.org/abs/2604.14227)

   **Draft:** “FRESCO and HoH study evolving or outdated documents in the retrieval pool, and TimelyRAG reranks over overlapping, evolving documents.”

   **Evidence:** FRESCO constructs recency-seeking queries and candidate pools from historical Wikipedia revisions, including passages supporting older conflicting facts. This supports the FRESCO portion of the sentence. [Full text, §3](https://arxiv.org/html/2604.14227v1)

7. **`timelyrag2026` — WRONG in its treatment of prior work; bibliography is correct.**

   **Bibliography:** Title, all six authors, Findings of EMNLP 2026, Budapest, publisher, and pages **8414–8430** match both the Anthology record and published PDF. [ACL record](https://aclanthology.org/2026.findings-emnlp.398/)

   **Draft:** “FRESCO and HoH study evolving or outdated documents in the retrieval pool, and TimelyRAG reranks over overlapping, evolving documents.”

   **Evidence:** That description is supported, but omits material overlap: §3.3.1 distinguishes query/document insertion times from event times and imposes \(D_{IT}\le Q_{IT}\) when insertion times are used. Section 3.3.2 scores against clause-validity intervals. [Published paper, §§3.3.1–3.3.2, p. 8417](https://aclanthology.org/2026.findings-emnlp.398.pdf)

   **Draft:** “In the papers we read, none states the latest time at which evidence may be known as a constraint on the query, or measures how often returned evidence violates such a constraint.”

   **Correction:** The first clause is contradicted by TimelyRAG’s availability constraint. Its query insertion time supplies an availability bound distinct from query event time. Whether it reports your specific violation-rate metric is a separate question.

   **Draft:** “B6 is a soft temporal distance on publication date, a TimelyRAG-style approximation and not a reproduction.”

   **Correction:** Call B6 a **publication-date distance baseline inspired by temporal reranking**. TimelyRAG additionally models insertion/event times, validity intervals, and an availability constraint; B6 omits those features.

8. **`jensen1996` — OK; complete the missing bibliography fields.**

   **Bibliography:** Title, authors, year, journal, volume **21**, and issue **4** are correct. Add:

   ```bibtex
   pages = {311--352},
   doi = {10.1016/0306-4379(96)00017-8},
   ```

   These details appear in Snodgrass’s publication list. The publisher page returned 403, but the author-hosted paper opened successfully. [Author’s publication record](https://www2.cs.arizona.edu/~rts/publications.html)

   **Draft:** “Valid and transaction time are standard in temporal databases.”

   **Evidence:** The paper systematically distinguishes valid and transaction times and develops a bitemporal conceptual model. The citation supports this statement. Transaction time concerns database recording history; publication time as a proxy is your modeling choice. [Author-hosted full text](https://www2.cs.arizona.edu/~rts/pubs/ISJune96.pdf)

9. **`mrag2025` — OK, with version clarification.**

   **Bibliography:** Title and authors match. The first arXiv submission was **December 20, 2024**; v2 is dated **May 21, 2025**, so 2025 is defensible if you explicitly cite v2. Alternatively, cite the published Findings of EMNLP 2025 paper, pages **3080–3118**, Suzhou, China. [arXiv history](https://arxiv.org/abs/2412.15540), [published record](https://aclanthology.org/2025.findings-emnlp.167/)

   **Draft:** “MRAG decomposes time-sensitive questions with constraints such as ‘as of’ and judges evidence by temporal reasoning, and TEMPS adds an anchor-date temporal score to dense retrievers.”

   **Evidence:** MRAG separates main content from temporal constraints, retrieves and summarizes evidence, then combines semantic and temporal scores. It explicitly discusses “as of” constraints. The MRAG portion is supported. [Full text, §4](https://arxiv.org/html/2412.15540v2)

10. **`temps2026` — OK; the venue can now be filled in.**

    **Bibliography:** The arXiv identifier, title, four authors, and 2026 year match. The published venue is **Proceedings of EMNLP 2026**, Budapest, pages **60482–60505**, Anthology ID `2026.emnlp-main.2657`. Those unusual page numbers are printed in the PDF. The Anthology metadata omits Christian Jacquelinet’s given name; the PDF confirms your full author name. [Published PDF](https://aclanthology.org/2026.emnlp-main.2657.pdf)

    **Draft:** The MRAG/TEMPS sentence quoted above.

    **Evidence:** TEMPS trains an anchor-date-conditioned temporal encoder and fuses its temporal score with a frozen semantic retriever’s score. The TEMPS portion is supported. [Full text, §5](https://arxiv.org/html/2609.28048v1)

11. **`hoh2025` — OK.**

    **Bibliography:** Metadata matches arXiv:2503.04800. The “ACL 2025” note is correct. A complete published citation would use **Proceedings of ACL 2025, Volume 1: Long Papers**, pages **6036–6063**, Vienna, Austria. [ACL record](https://aclanthology.org/2025.acl-long.301/)

    **Draft:** “FRESCO and HoH study evolving or outdated documents in the retrieval pool, and TimelyRAG reranks over overlapping, evolving documents.”

    **Evidence:** HoH constructs current and outdated evidence from Wikipedia changes and tests how their coexistence affects retrieval and generation. This supports the HoH portion. [Full text, §§3–5](https://arxiv.org/html/2503.04800v3)

12. **`tempo2026` — OK for the cited preprint; resolve the venue note.**

    **Bibliography:** The supplied title, authors, year, and identifier match the arXiv preprint. The published EMNLP 2026 title drops the article “A”: **“TEMPO: Realistic Multi-Domain Benchmark for Temporal Reasoning-Intensive Retrieval.”** Published pages are **6657–6709**, Budapest, Anthology ID `2026.emnlp-main.291`. Retain the supplied title when citing the preprint; use the published title if converting the entry. [arXiv record](https://arxiv.org/abs/2601.09523), [published paper](https://aclanthology.org/2026.emnlp-main.291.pdf)

    **Draft:** “TEMPO evaluates whether retrieved evidence covers the time periods a query needs.”

    **Evidence:** Its Temporal Coverage metric measures coverage of required periods, including baseline and comparison periods for cross-period queries. The sentence is supported. [Full text, §4 and Appendix C](https://arxiv.org/html/2601.09523v1)

Two broader sentences need revision:

> “We found no measurement of how single-clock rankers fail on versioned authoritative documents, and no query formulation that makes the choice of clock explicit.”

**WRONG as broadly phrased.** TimelyRAG studies evolving regulation-focused document families and separates query event and insertion times; Niksarli and Baheti provide separate query filters for valid and transaction time. A supportable replacement is:

> “Prior work distinguishes event or valid time from insertion or transaction time. We evaluate four explicit temporal intents on Federal Register rule clusters and measure accuracy and constraint violations.”

[TimelyRAG](https://aclanthology.org/2026.findings-emnlp.398.pdf), [memory-store paper](https://arxiv.org/html/2607.26520v1)

> “In the papers we read, none states the latest time at which evidence may be known as a constraint on the query, or measures how often returned evidence violates such a constraint.”

Remove the first clause. **CANNOT VERIFY the universal absence claimed by the second clause**; the evidence above establishes mechanisms, but does not establish that no cited work reports an equivalent violation analysis.

The two Federal Register document citations also check out:

- **2019-16300 — OK:** “The rule published on 1 August 2019 … takes effect on 1 January 2020, 153 days later.” The publication date and DATES statement agree; the interval is 153 days. [Official published rule](https://www.govinfo.gov/content/pkg/FR-2019-08-01/pdf/2019-16300.pdf)
- **2018-18209 — OK:** “The rule it replaces … was published on 27 August 2018 and took effect on 1 January 2019.” The official record confirms those dates and the preceding annual threshold adjustments. [Official published rule](https://www.govinfo.gov/content/pkg/FR-2018-08-27/pdf/2018-18209.pdf)

These citation checks do not independently verify the draft’s experimental results or the fidelity of its implemented approximations.