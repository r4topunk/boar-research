# RETFLOOR: 0-LLM retrieval replay of the X2b append gates (2026-10-20)

TL;DR
- **Recommendation: V1orC.** It keeps an X1 or dense append only if it passes the grounding check (onSubject) **or** has cosine >= 0.70.
  - K1 MAIN 97: removes all 82 off-topic appends (50 % of the 163) and 0 on-topic appends.
  - PM 180: fact reach is 98 vs base 97 (lost 1, gained 2). The 32 PM appends it removes are all off-topic.
- **Coverage today includes off-topic padding.** On K1 MAIN, ruler retrieval coverage is 63/97 (64.9 %).
  - Only 44/97 (45.4 %) have a grounded source.
  - 19 are covered by appends alone, and 8 of those (8.2 pts) by off-topic appends only.
  - Under V1orC coverage is 58/97 (59.8 %). PM: 157/180 → 156/180.
- **V1 (onSubject only) is too strict.** PM fact reach drops 97 → 73: the check rejects 134 on-topic appends, most of them fact chunks from SE packs.
- **V2 (DENSE2_FLOOR 0.70 on dense only) leaves padding in.** 39 off-topic appends remain on MAIN, because X1 is ungated.
- **V3 (margin 0.05 under the item's top append cosine) gives the best fact reach**, 102/180 (+5). But it keeps 51 off-topic appends on MAIN.
- **V4 (cosine-ordered fill, RET-F3)** gives +2 fact reach and removes only 22 off-topic appends.
- **A Haiku screen is worth running for V1orC.** It changes the context on 43/97 MAIN items, 21 of them in screen-K1 (37). Fact reach holds, so the screen tests the CTX-F1 claim directly.

Cost: 0 generations, 0 judge calls, 0 paid. Mini slot gen2, 21:24–21:4x, 81 replays.

## Method
- **Tree.** A copy of `kiln-local/be-0cfd4a77-cut7-litepacks`, patched by `tools/apply_retfloor.py` (diff: `tools/retfloor.vs-litepacks.diff`). The original tree was not touched. On the mini: `<runner>/kiln/retfloor/be-0cfd4a77-cut7-litepacks-retfloor`.
  - The variant is selected with env `RETFLOOR_VARIANT`.
  - The variant gates the X2b pending appends (X1 neighbours + dense picks) **before** the 600-work budget.
  - Every run logs `retfloor:cand:<x1|dense>:<chunkId>:<cos>:<onSubject>` and `retfloor:kept:<grounded n>:<final chunk ids>`.
  - X1 cosine = the question vector (the item's first retrieve embed) against the pack's `chunk_vecs` row. This is the same scorer the dense path uses.
- **Harness.** The real LITEPACKS adapter (`be/adapter-litedecline.ts`, LITEDECLINE_OFF=5, detector :8094) runs against the stub llama-server from `model-usage/context-tools`, as in the context audit. Driver: `tools/mini_rf.sh`, with an atomic slot lock.
- **Parity of base.** Kept titles and context/headpass/grounding codes match LITEPACKS K1 v01+cm on 100/100 items. Kept titles match the LITE5-180 1.7B X2b traces on 180/180.
- **Sets.**
  - MAIN 97 = `lp-screens/main-97.ids`, from the K1 requests (kit + simplewiki).
  - PM 180 = the 180 self-tests, each with its own pack (the LITE5-180 / X2b-gate setting).
  - Fact chunks come from `arms/oracle-st/tools/oracle-facts.json`. The X2b gate's 102/180 was measured on the 4B; this run's 1.7B base is 97.
- **Definitions.**
  - **Off-topic append** = fails onSubject **and** cosine < 0.70, i.e. both checks fail. V1orC removes all of these by construction, so the item lists in `tools/inspect.py` output are the independent sanity check.
  - **Coverage** = >= 1 source received by the answer step (RULER-SPEC-v1 §3.3).
- **Variants.**
  - V1: onSubject on appends. Health questions keep the existing onHealthTopic rule.
  - V2: dense appends need cosine >= 0.70 (equivalent to DENSE2_FLOOR 0.70).
  - V2b: 0.70 on X1 and dense.
  - V3: cosine >= item top-1 of pending X1 ∪ dense − 0.05.
  - V4: X1 ∪ dense ordered by cosine for the budget.
  - V1orC: onSubject OR cosine >= 0.70.
  - V1V4: V1, then cosine order.

## K1 MAIN 97

| variant | kept chunks | appended (x1/dense) | off-topic appends left | appends removed vs base (off/on) | coverage | covered by appends only | of which off-topic only | items emptied |
|---|---|---|---|---|---|---|---|---|
| base | 270 | 163 (62/101) | 82 | – | 63 (64.9 %) | 19 | 8 | – |
| V1 | 179 | 72 (20/52) | 0 | 98 (82/16) | 54 | 10 | 0 | 9 |
| V2 | 216 | 109 (62/47) | 39 | 54 (43/11) | 60 | 16 | 9 | 3 |
| V2b | 176 | 69 (11/58) | 0 | 105 (82/23) | 53 | 9 | 0 | 10 |
| V3 | 235 | 128 (16/112) | 51 | 54 (37/17) | 63 | 19 | 5 | 0 |
| V4 | 267 | 160 (37/123) | 66 | 25 (22/3) | 63 | 19 | 5 | 0 |
| **V1orC** | 202 | 95 (23/72) | **0** | 82 (**82/0**) | 58 (59.8 %) | 14 | 0 | 5 |
| V1V4 | 179 | 72 (18/54) | 0 | 100 (82/18) | 54 | 10 | 0 | 9 |

Grounded coverage (>= 1 source after onSubject, before any append) is 44/97 in every variant.

## PM 180 (each item with its own pack)

| variant | kept chunks | appended (x1/dense) | off-topic appends left | removed vs base (off/on) | coverage | emptied | **fact reach** | lost / gained vs base |
|---|---|---|---|---|---|---|---|---|
| base | 663 | 390 (187/203) | 32 | – | 157 | – | **97** | – |
| V1 | 519 | 246 (91/155) | 0 | 166 (32/134) | 142 | 15 | 73 | 25 / 1 |
| V2 | 650 | 377 (187/190) | 29 | 13 (3/10) | 157 | 0 | 95 | 2 / 0 |
| V2b | 624 | 351 (135/216) | 0 | 65 (32/33) | 156 | 1 | 97 | 4 / 4 |
| V3 | 591 | 318 (79/239) | 3 | 129 (31/98) | 157 | 0 | **102** | 3 / 8 |
| V4 | 664 | 391 (106/285) | 16 | 81 (19/62) | 157 | 0 | 99 | 7 / 9 |
| **V1orC** | 646 | 373 (158/215) | 0 | 32 (**32/0**) | 156 | 1 | **98** | 1 / 2 |
| V1V4 | 519 | 246 (70/176) | 0 | 187 (32/155) | 142 | 15 | 74 | 27 / 4 |

- Grounded coverage is 129/180. Fact chunks appear in the kept set or the candidates on 106/180, which is the ceiling for any append gate here.
- Removing an append frees budget, so later candidates can enter. That explains the "gained" column and why V1orC's appended count falls by less than the 82 off-topic appends on MAIN.

## Sanity read (V1orC, MAIN; `python3 -I tools/inspect.py V1orC`)
- **Items emptied (5):**

  | item | base kept titles | read |
  |---|---|---|
  | Mozi | Camera obscura ×2 | off-topic |
  | French vs Dutch oven | Cookware, Hollandaise, Eggs Benedict | off-topic |
  | credit card | Captain Jack Harkness ×2, Credit card, Advance-fee scam | "Credit card" is borderline |
  | HSA | Social Security, Form W-9 | off-topic |
  | basket ETF | Stock market, Volatility | borderline |

- **Still covered by appends only (14):** mostly on-topic. Examples: Mosquito/Vector, Moose/American bison, Simmering, Pineapple, Skimmed milk, Garlic/Onion, Checking account/Clearing bank, Tax advantage.
- **One survivor is off-topic:** "What is d/acc?" still gets Digital-to-analog/Analog-to-digital converter. Fixing that needs a lexical or term check, not a cosine floor.

## Recommendation
1. **Adopt V1orC as the candidate gate** (env-gated in the copy; not yet a setting). Among the variants run, it is the only one that removes the off-topic padding without touching on-topic appends or PM fact reach.
2. **Report the ruler's coverage two ways until it lands:** "kept >= 1" (63/97) and "grounded or on-topic append" (55/97 = base minus the 8 padding-only items). Today about 8 pts of K1 MAIN coverage is off-topic padding. On PM it is 1/180.
3. **Haiku screen: worth one K1 stage-1 screen (37 items, mini, gen slot)** on V1orC vs the lpctl-K1 control. The context changes on 21/37 items. Read CE-unwarned and CE-warned, as refute-2 M4 asks. V3/V4 and V2 are not worth a screen: they leave 37–66 off-topic appends on MAIN.
4. **Next 0-LLM step (not run):** V1orC followed by cosine-order fill (V1orC+V4). V4 and V3 show the order and margin recover +2 to +5 fact chunks on PM, so the combination may reach ~100 or more with no padding.

UNKNOWN:
- Whether removing padding moves U or CE (needs the screen).
- The off-topic label is mechanical (both checks fail). It was eyeballed only on MAIN's 5 emptied and 14 append-only items.
- PM fact reach is for the 1.7B config; the 4B gate figure (102) was not re-run.

## Files
- `tools/apply_retfloor.py` (patch), `tools/retfloor.vs-litepacks.diff`, `tools/mini_rf.sh` (mini driver), `tools/analyze.py` → `aggregates/retfloor.json`, `tools/inspect.py` (parity + item lists).
- `req/` (MAIN + 9 PM request files), `out/` (81 trace files + `STATUS.mini`). Prompt dumps were left on the mini (`<runner>/kiln/retfloor/out/*.prompts.jsonl`).
