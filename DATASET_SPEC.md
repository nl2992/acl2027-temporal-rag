# Dataset spec (pilot v2)

**Source.** Federal Register API (federalregister.gov, US government works; check reuse terms before release). Final rules (type RULE) 2010-2026 from ~85 CFR parts. Fields: `publication_date` = known-time proxy (publication is not exactly when an observer knew it), `effective_on` = valid-from. valid-to is not recorded; the next version's effective date is NOT used (would need family oracle).

**Families.** Documents with the same normalized title (digits/years masked), >=4 versions across >=3 years and at least two with effective-publication lag >=14 days, or one retroactive rule (effective >=3 days before publication). 790 documents, 105 families after v2 mining. 790/790 `effective_on` values appear verbatim in the rule's own DATES text; one conflicting document (2015-13717) was excluded.

**Intents (gold = single best version).** current: latest with eff<=today & pub<=today. valid_at: latest with eff<=t (later publication allowed; h=today). known_at: latest with pub<=h. valid_known: latest with eff<=t and pub<=h. Cases are probes placed halfway between publication and effective date (so clocks disagree) or, for retroactive rules, between effective and publication date. 1291 cases.

**Splits.** Family-level. v1 frozen before expansion (annotation/split_v1.json: 9 dev, 5 test). Added families: md5 hash -> 35 test2, 56 dev2. lambda/delta chosen on dev+dev2 only. test1 + test2 are never used for selection.

**Known limits.** Labels derive from the same timestamps eligibility uses (violation rate 0 is by construction); queries are templated except the 42 hand-drafted ones; relevance is single-gold; only Federal Register; correction/supersession chains barely exercised. Human annotation (annotation/) is the planned fix.
