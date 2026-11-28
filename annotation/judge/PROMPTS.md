# How the machine judges were run

Recovered from the session logs after the fact (2026-11-27). These are language-model judges, not human annotators.

- Model: `claude-sonnet-5-5` (agent alias `sonnet`), recorded in all 18 judge agent logs.
- Six agents per sample, one packet of 20 cases each: `packet_N` (first sample), `d_packet_N` (development sample), `p5_packet_N` (`test5`).
- The restriction to one file was an instruction, not a technical sandbox.
- Below is the instruction for packet 1 of each sample, with the local directory replaced by `<dir>`. Other packets differ in file number, the example case id, and in the first sample a short closing phrase.

## First sample

```text
You are an independent annotator judging which US Federal Register rule answers a question about a particular date. Read ONLY this one file: <dir>/packet_1.json. Do not open, list or search any other file or directory (not the repository, not other packets, not any answers or key files); work only from the information in the packet.

The packet is a JSON list of 20 cases. Each case has a plain-language question, a rule title, and a list of candidate rules. Each candidate has an id, the date it was published, and the rule's own statement of when it takes effect (its DATES statement). All candidates are versions or updates of the same recurring rule. For each case choose the single candidate that best answers the question as a careful reader would understand it, using the question wording and the dates given. Use your own reading of phrases such as "in force", "governed", "had been published by", and "today (date)". If several candidates seem to qualify, choose the one a careful reader would consider the controlling one and note the ambiguity. If no candidate fits, answer "NONE". Do not guess hidden metadata; use only what the packet shows.

Write your answers as a JSON object to <dir>/answers_1.json in exactly this shape: {"J001": {"choice": "<candidate id or NONE>", "confidence": "high|medium|low", "note": "<one short sentence, especially if ambiguous>"}, ...} covering every case in the packet. Then reply with just the number of cases answered.
```

## Development sample

```text
You are an independent annotator judging which US Federal Register rule answers a question about a particular date. Read ONLY this one file: <dir>/d_packet_1.json. Do not open, list or search any other file or directory (not the repository, not other packets, not any answers or key files); work only from the information in the packet.

The packet is a JSON list of 20 cases. Each case has a plain-language question, a rule title, and a list of candidate rules. Each candidate has an id, the date it was published, and the rule's own statement of when it takes effect and, where stated, until when (its DATES statement). All candidates are versions or updates of the same recurring rule. For each case choose the single candidate that best answers the question as a careful reader would understand it, using the question wording and the dates given. Use your own reading of phrases such as "in force", "governed", "had been published by", and "today (date)". If several candidates seem to qualify, choose the one a careful reader would consider the controlling one and note the ambiguity. If no candidate fits (for example nothing was in force on that date, or nothing had been published yet), answer "NONE". Do not guess hidden metadata; use only what the packet shows.

Write your answers as a JSON object to <dir>/d_answers_1.json in exactly this shape: {"J001": {"choice": "<candidate id or NONE>", "confidence": "high|medium|low", "note": "<one short sentence, especially if ambiguous>"}, ...} covering every case in the packet (use the case ids exactly as they appear). Then reply with just the number of cases answered.
```

## `test5` sample

```text
You are an independent annotator judging which US Federal Register rule answers a question about a particular date. Read ONLY this one file: <dir>/p5_packet_1.json. Do not open, list or search any other file or directory (not the repository, not other packets, not any answers or key files); work only from the information in the packet.

The packet is a JSON list of 20 cases. Each case has a plain-language question, a rule title, and a list of candidate rules. Each candidate has an id, the date it was published, and the rule's own statement of when it takes effect and, where stated, until when (its DATES statement). All candidates are versions or updates of the same recurring rule. For each case choose the single candidate that best answers the question as a careful reader would understand it, using the question wording and the dates given. Use your own reading of phrases such as "in force", "governed", "had been published by", and "today (date)". If several candidates seem to qualify, choose the one a careful reader would consider the controlling one and note the ambiguity. If no candidate fits (for example nothing was in force on that date, or nothing had been published yet), answer "NONE". Do not guess hidden metadata; use only what the packet shows.

Write your answers as a JSON object to <dir>/p5_answers_1.json in exactly this shape: {"J001": {"choice": "<candidate id or NONE>", "confidence": "high|medium|low", "note": "<one short sentence, especially if ambiguous>"}, ...} covering every case in the packet (use the case ids exactly as they appear). Then reply with just the number of cases answered.
```
