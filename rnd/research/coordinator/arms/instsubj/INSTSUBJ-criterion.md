# INSTANT-SUBJ (instant extractive answer only when the snippet's subject is the question's entity) on cut 4 — frozen 2026-10-05 by the coordinator before any code

Evidence: on kit A only 2/30 blind lookups finish instant and one is wrong ('capital of the usa' → "Baton Rouge is the capital of Louisiana"); the France/Lyon warm-up (fixed by INSTANT-FRAG) was the same class. instantFinalBlock has no answers-the-question check.
Mechanism: an instant extractive snippet may be FINAL only if the question's main entity (country/place/person/thing named in the question, incl. common aliases: USA/US/United States, UK/Britain…) is the grammatical subject or the possessor of the answered slot in that sentence; otherwise fall through to the normal path. No other change; cards/calculators/places unaffected.
## L0 (stub-LLM replay, no judge)
- New blind lookup set #2 (≥ 40 lookups + 15 controls, written blind; builder never opens it; coordinator scores once): 0 wrong instant-final answers (vs cut 4 baseline on the same set); correct instant-final answers lost ≤ 1.
- v0.1 EN + V-exact: 0 correct instant answers lost; dev messages: report tier changes.
## L1 (only if v0.1 answers change): v0.1 EN s44+s45, same-day control, changed items only, judge.v1-med; no changed item down ≥ 1.0, unsafe 0, cw not up, Δ ≥ 0. If no v0.1 answer changes, adoption rests on L0.
Stop rule: one revision after an L0 FAIL (new blind set needed); none after L1.
