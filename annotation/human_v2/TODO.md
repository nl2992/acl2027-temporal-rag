# Human query study: to-do list

**Status (26 Nov 2026): run with Codex models in every writer and labeller role** (`src/pilot/codex_sim.py`, results in
`EXPERIMENT_RESULTS.md`). The output is model-generated. Any write-up must call it that, never human data.
The steps below stay as the protocol if people are asked to repeat it.

## What this is

Right now every test question is a template that **copies the rule's title**, for example
"*\<full rule title\>* rule legally in effect on 2019-05-01". Real people do not ask like that, and
accuracy falls from 0.78 to 0.35 when the title is cut to four words. We also have **no human judgment**
of which document answers a question.

A **human query** is the same question written by a person in their own words. A **human label** is a
second person's choice of the document that answers it. We need both for 120 cases.

## People

| Role | People | Task | Rough time each |
|---|---|---|---|
| Owner | 1 (method author) | sends sheets, runs scripts, scores. Does **not** write or label | 3 h |
| Writers | A, B | write 60 questions each | 5 to 8 h |
| Labellers | C, D | answer 80 questions each | 8 to 12 h |

Writers and labellers must be four different people who have not worked on the method.
Times are estimates; time your first five and tell the owner if they are far off.

## Rules for everyone

- **Do not open** `annotation/GOLD_KEY*`, `annotation/judge/`, `annotation/codex_sim/`, `reports/`, `data/`, `src/` or the paper.
- **Do not push filled sheets to GitHub.** This repository is public. Send files to the owner directly.
- Do not discuss cases with each other until everything is returned.
- Use your letter (A to D), not your name, in file contents.

## Step 1. Owner: hand out (target: 27 Nov)

- [ ] Choose people for A, B, C, D.
- [ ] Send `writer_A.csv` to A and `writer_B.csv` to B, with this file.
- [ ] Ask the router developer not to change `router.py` or `dateparse.py` from now until scoring is done.

## Step 2. Writers A and B (target: 4 Dec)

For each row of your sheet:

- [ ] Read `what_your_question_must_ask`. It gives the kind of question and the date.
- [ ] Open a few of the links in `documents`. They are versions of one recurring rule.
- [ ] Write one question in `your_question`, as you would ask a colleague.
  - Keep the meaning and the exact date(s). Write the date any way you like.
  - Say enough to identify the rule: the product, species, place, bridge, agency or programme.
  - **Do not copy the title.** No more than three words in a row from it.
  - No document numbers and no links.
  - Do not use the words "valid time", "known time" or "publication time".
  - Do not reuse the wording of `what_your_question_must_ask`. Vary your phrasing between rows.
- [ ] If the case is confusing or the links are not versions of one rule, still write your best question and explain in `notes`.
- [ ] Save as CSV with the same file name and send it to the owner.

Example (made up, not a case):
*Instead of* "Drawbridge Operation Regulation; Example River, Town, ST rule legally in effect on 2019-05-01"
*write* "On May 1st 2019, which schedule governed openings of the bridge over the Example River in Town?"

## Step 3. Owner: check and build label sheets (target: 7 Dec)

- [ ] Put the two returned files in `annotation/human_v2/returned/`.
- [ ] Skim for copied titles, document numbers or wrong dates. Send those rows back.
- [ ] Run `python3 -B src/pilot/make_human_sheets.py labeller`
- [ ] Send `labeller_C.csv` to C and `labeller_D.csv` to D, with this file. 40 cases appear on both sheets so we can measure agreement.

## Step 4. Labellers C and D (target: 14 Dec)

For each row:

- [ ] Read `question`.
- [ ] Open the links and read each rule's **DATES** section and its publication date.
- [ ] In `best_document_number_or_NONE`, put the one document number that answers the question (the last part of its link), or `NONE` if none does.
  - "Published by" means the publication date is on or before that day.
  - "In force" means it has taken effect and has not ended, been withdrawn or been postponed.
  - If several qualify, choose the most recent one.
- [ ] Fill `confidence_high_medium_low`.
- [ ] Use `notes` for ties, ambiguity, a question you cannot match to the documents, or a question that could mean two things.
- [ ] Save as CSV and send it to the owner. Do not compare with the other labeller.

## Step 5. Owner: score once (target: 18 Dec)

- [ ] Put the labeller files in `returned/`.
- [ ] Write the scoring script **before** looking at any system output on the new questions.
- [ ] Report agreement and Cohen's kappa on the 40 double-labelled cases.
- [ ] Report how often labellers agree with the metadata-derived key.
- [ ] Resolve disagreements by reading the rule text. Record each one; do not silently edit.
- [ ] Run every system once on the human questions with settings frozen: gated baselines, router over the two baselines, routed v2, LLM re-ranker.
- [ ] Update the paper with whatever comes out, including if the method loses.

## Other open items (owner)

- [ ] Run the LLM re-ranker **in a normal terminal** (it will not start inside a Claude Code session). It uses your Claude plan, about 30 calls.
  - `python3 -B src/pilot/llm_rerank.py smoke`
  - `python3 -B src/pilot/llm_rerank.py run`
  - `python3 -B src/pilot/llm_rerank.py score`
- [ ] Add the router-over-baselines control to the paper.
- [ ] Check every citation exists and says what the draft says.

## Caveats to state in the paper

The 120 cases come from the `test5` families, which have already been evaluated with template queries.
The new element is the wording and the human labels. The older sheets in `annotation/` (42 cases, title
kept) are replaced by this study.

The target dates assume a start on 26 November and the ARR deadline of 4 January 2027 recorded in
`RESEARCH_DIRECTION.md`; check that deadline before relying on it.
