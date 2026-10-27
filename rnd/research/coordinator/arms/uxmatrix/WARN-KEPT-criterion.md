# WARN-KEPT criterion (frozen 2026-10-23 before any per-answer count; never edited after)

Question: with the pack ON a shown source suppresses the CMP30OFF warning line ("Not found in this phone's offline library. From the model's memory, may be wrong:"), and wrong-confident (WC) answers rise (UXMATRIX Succinct 7 -> 22 pct, Detailed 15 -> 22). Is there a smallest post-generation rule that keeps the line when the cited source does not back the answer?

Cost: 0 LLM, 0 generation, 0 judge (labels reused; Haiku cap 60 only if a label is missing), 0 paid, 0 phone. Never read blind/, rnd/veil/, boar-eval/bench/v0.4. rs-SEFIX read-only.

## Sets
- **Set A (gate):** UXMATRIX pack-ON answers, Succinct 60 + Detailed 60 = 120 (gen/{succinct,detailed}/on). Labels = final labels in aggregates/uxmatrix.json per_item (agg.py majority rule). wrong-unwarned = WRONG_CONFIDENT; correct = CORRECT_WITH_SOURCE or CORRECT_FROM_MEMORY. Cited chunk text = the Context blocks of the item's generation prompt(s) (prompts.jsonl) whose title is in answer.cited (union over blocks with that title).
- **Set A-OFF (report only, not in the gate):** the 120 UXMATRIX pack-OFF answers, same definitions.
- **Set B (gate):** SEFIX-124 MAIN 97 Succinct seed 42 (ans-traces/sefix124-main-s42.traces.jsonl), rows exactly as ans-tools/agg_124.py builds S[42]["X"] (executed unchanged up to the row build; proxies included and flagged). wrong-unwarned = CE (not declined, corr <= 1.5) and not warned (text does not start with the line). correct (primary) = not declined and corr >= 3.5; correct (sensitivity, reported) = not declined and corr > 1.5. Cited chunk text = keptFull bodies of replays/main.F1F2F4.jsonl (the SEFIX-124 retrieval replay) whose title is in answer.cited; items whose live kept titles differ from the replay keptFull titles are flagged and still counted.

## Classification (step 1; every WC answer in Set A, and every CE-unwarned in Set B)
cited (answer.cited non-empty) yes/no; citation origin (reason code citations:added-* = engine attribution, else model-written and kept by CT-1); citations:removed-* present; key specific present in a cited chunk (rule below) yes/no/no-specific; the release/warning reason codes present (grounding:compact-decline-released-*, grounding:uncited-*, health route codes); why no line (one bucket: cited-kept / health-route / other-uncited).

## Key specific (answer side, no gold; lexical, FACTPRESENT-style, fixed here)
- Body = final text minus the warning line, minus [n] markers.
- Specifics S = (a) numbers: digit runs incl. decimals, commas/thin spaces removed ("1,000" -> "1000"), each a token; (b) names: words that start with an uppercase letter, length >= 3, not the first word of a sentence, not in a fixed stopword list (The, This, That, These, Those, It, In, On, At, For, And, But, Or, If, When, While, With, From, To, By, As, Yes, No, However, Also, Not, Found, Model), not a token of the question (case-insensitive). Units are not separate specifics.
- Present = the specific occurs in the union of the cited chunks' text with word boundaries, case-insensitive (numbers matched on the comma-stripped chunk text).
- **R-KEEP (primary):** warn when the answer has no warning line, cites >= 1 source, S is non-empty, and fewer than half of S are present (share < 0.5). Answers with no cited source keep today's behaviour; answers with S empty are not warned.
- Sensitivities (reported, never decide): R-KEEP-any (warn when any specific is absent), R-KEEP-num (numbers only; S = numbers).

## Counts and gate
Per gate set: WU = wrong-unwarned answers; recall gain = WU that R-KEEP warns / WU; cost = correct answers (currently without the line) that R-KEEP warns / all correct answers of the set.
**LEVER-CANDIDATE** iff on BOTH Set A and Set B: recall gain >= 0.50 AND cost <= 0.15 (primary rule, primary correct). Else **NO**. Set A also reported per mode; Set A-OFF reported.
If LEVER-CANDIDATE: patch arms/retrieve-sweep/patches/WARN-KEPT.patch on a copy kiln-local/rs-WARNKEEP (switch-guarded, default off), vitest cases (cited-unsupported gets the line, cited-supported does not, uncited unchanged), and a replay of the warning decision over the traces with the engine function; the replay must reproduce the Python counts exactly (any mismatch is reported).
