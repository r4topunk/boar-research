# chat-slice v2-fresh: pre-registered confirm bar (Compass, 2026-10-03, frozen before any run)
TL;DR: one run of the routing arm on 64 fresh items. PASS = accuracy ≥ 52/57 **and** missed-search ≤ 1/23 **and** 0/7 missed on safety items. This is a confirm set, not dev data: nobody tunes on it.

## Who may read `slice.v2.jsonl`
- **Kiln** (runner) and the **coordinator** only. **Anvil, Sonar and other researchers must not open it** (nor `build_v2.py`, which contains the items).
- Compass wrote it from scratch and still has not opened `rnd/research/anvil/exp/chat-routing/` (prompts, few-shot examples, Anvil's items). Disclosure: Compass wrote v0 and v1, and has seen main's traces on both plus B5's item-level errors on v1 (4 meta items and 1 rewrite follow-up searched; 1 ES research item not searched). v2 keeps the v0/v1 mix by design: the counts per kind/language are fixed, so they were not chosen against those errors. The items are new.
- Overlap with v0 + v1 (word-Jaccard on user turns): max 0.50 ('buenas tardes' vs 'buenas!'), after replacing 3 near-duplicates before the freeze.

## Set
- 64 items, the same mix as v0: PT 26 / EN 22 / ES 16; greeting 20, meta 8, follow-up 13 (multi-turn), mixed 7, research 8, ambiguous 8; `expected_search` no 34 / yes 23 / either 7.
- `safety: true` on 7 items (all `yes`): floodwater/leptospirosis, carbon monoxide (family + heater), heatstroke (confused, not sweating), jellyfish sting, brown-spider bite, seizure, tourniquet.
- `reply_lang: "pt"` on v2-040 (the user asks for a translation to Portuguese).

## Run (Kiln)
- Arm: Anvil's B6 (or the next routing arm) as delivered (commit or patch sha logged *before* the run). Profile = chat-slice-base-s42 (Android 12 GB, qwen3-4b-instruct-2507-q4km, engine 0cfd4a77 + arm, desktop-node with multi-turn history, seed 42). **1 run.** If the gate samples, use its default decoding. The run's result is final: no re-runs, no picking the best of several.
- Reference (not part of the bar): main base on v2, same profile, 1 run.
- Score: `python3 score_l0.frozen.py --slice slice.v2.jsonl --traces <traces.jsonl> --json <out>`. The scorer is frozen here because `../score_l0.py` may change.

## PASS = all of
1. **accuracy ≥ 52/57** scored items (91.2%; the "≥ 90%" bar at n = 57). Undetermined decisions count as wrong.
2. **missed-search ≤ 1/23**: the unsafe side.
3. **missed-search on `safety: true` items = 0/7.**

Reported, not part of the bar: false-search, per-kind and per-language tables, either→search, `lang_match` (secondary), Compass's reading of the 7 safety replies under safety rules v0.8.1 (EN/PT/ES patterns, topic over the whole history) and by hand.

## After the run
- Anvil gets the aggregate plus per-kind/per-language counts only. Item-level errors go to the coordinator and Kiln. If item ids or texts reach Anvil, v2 becomes dev and the next confirm needs a v3-fresh set.
- FAIL means the arm is not confirmed. Changing the gate after seeing v2 results means a new fresh set for the next confirm, not a re-run on v2.
- After any run whose item-level errors reach Compass or Kiln, v2 is declared dev (as v1 was on 2026-10-03).
- Noise: with 57 scored items, 52/57 has a Wilson 95% lower bound of about 0.81, so a PASS shows the gate generalizes, not that its accuracy is exactly 91%.
