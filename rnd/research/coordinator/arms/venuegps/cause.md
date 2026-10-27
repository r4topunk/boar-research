# VENUEGPS step 1: cause of V-para P5 0/7 (cut 6, config (b)) — tools/cause.mjs, counts only
Inputs: blind/V-para/runs-cut6/cut6-vpara-s4{2,3}.traces.jsonl; venue ids from items.jsonl grading.type = venue-list.
Rule: task ≠ places → other; location:{unavailable,denied,timeout,stale,prompt,stopped} or places:no-pack → no-location;
0 POIs in the places event or places:{coverage-*,no-match,search-failed} → no-places-hit; else places-hit-but-answer-ignores.

| id | s42 | s43 | route codes (both seeds) |
|---|---|---|---|
| vpara-016 | no-location | no-location | task:places, near:device, location:unavailable |
| vpara-017 | no-location | no-location | same |
| vpara-018 | no-location | no-location | same |
| vpara-019 | no-location | no-location | same |
| vpara-020 | no-location | no-location | same |
| vpara-049 | no-location | no-location | same |
| vpara-050 | no-location | no-location | same |

Counts: s42 no-location 7/7; s43 no-location 7/7; no-places-hit 0, places-hit-but-answer-ignores 0, other 0.
All 14 answers are the instant-tier needs_place template (0 output tokens, 0 POIs, tier instant). The engine reads the
questions as "near me" (near:device), asks the device for a fix, and the desktop runner has none (EvalItem.context absent).
