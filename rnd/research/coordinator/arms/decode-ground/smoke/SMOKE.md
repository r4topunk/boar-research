# DECODE-GROUND stage 1 smoke (2026-10-21 21:0x, Mac mini, 0 judge calls, 0 paid, 0 phone)

Patch `tools/dg.patch` (sha256 c81ba53106c16d49…; patches `src/routing/answer.ts` + `be/adapter-litedecline.ts` of the K1 tree be-0cfd4a77-cut7-litepacks, answer.ts base 0d1ac07dd1d664be). Entry: `tools/run_dg.sh ARM REQUESTS RUN` (ARM = B | S | C1 | SC | SB). Server: the adapter's own llama-server b11010 per job (OS-assigned port, stopped at job end; -np 1 for B/S/SB, `-np 2 -c 8192` for C1/SC). **No server left running** (stage-0 server on :8096 stopped; :8094 detector untouched).

Items (`smoke/smoke5.ids`): smoke-main.ids has only 3 ids (lan-cmp-004, st-qa-money-se-001, vit-sci-003 = calculator) → + vit-hum-001, vit-hum-004 (first model-answer items of main-97 with raw candidates).

## Parity
B (patched tree, DG_ARM unset) vs MINI-BASELINE lp-K1-{cm,v01}-s42.mini: **5/5 answers byte-identical**, reasonCodes, kept titles, promptTokens and outputTokens identical (`tools/parity_dg.py`). The calculator item (vit-sci-003) is byte-identical in every arm. NO_EVIDENCE item (vit-hum-001): S, SB (-np 1) and SC, SCp01 (-np 2, ctx 8192) all give the same closed-book text (slot count does not perturb the plain path).

## Table (totalMs / B uses the regenerated B on the same idle mini, sequential jobs)
| run | non-empty | loops | NO_EVIDENCE | selected in dropped | selected in kept | CJK answers | diff vs B | diff vs S | mean out tok | mean totalMs | totalMs / B |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dg-B-smoke5-s42 | 5/5 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 37.4 | 3595 | 1.00 |
| dg-S-smoke5-s42 | 5/5 | 0 | 1 | 0 | 3 | 0 | 4 | 0 | 40.4 | 4863 | 1.35 |
| dg-C1-smoke5-s42 | 5/5 | 0 | 0 | 0 | 0 | 2 | 4 | 4 | 30.6 | 3855 | 1.07 |
| dg-C1p01-smoke5-s42 | 5/5 | 0 | 0 | 0 | 0 | 0 | 4 | 4 | 33.0 | 3966 | 1.10 |
| dg-SC-smoke5-s42 | 5/5 | 0 | 1 | 0 | 3 | 1 | 4 | 3 | 41.4 | 5753 | 1.60 |
| dg-SCp01-smoke5-s42 | 5/5 | 0 | 1 | 0 | 3 | 0 | 4 | 3 | 39.2 | 5706 | 1.59 |
| dg-SB-smoke5-s42 | 5/5 | 0 | 1 | 0 | 3 | 0 | 4 | 1 | 41.2 | 4985 | 1.39 |

CAD: C1 (spec, missing −30): 41 of 153 steps flip vs the ctx argmax, ms/step 37.8 (two slots batched), 0 reprocessed tokens; **garbage tail tokens** in 4/4 CAD answers ("还款记录", "aChinese", "Wormtongsue", "(creckshields)"). C1p01 (`DG_PLAUS=0.1`: only tokens with p_ctx ≥ 0.1·max p_ctx): 15/165 flips, clean text. SC 39/151 flips (CJK "贷款", "Wormtongs", "ofthe"), SCp01 10/140 clean. SELECT: 4/5 items have candidates (raw ∪ kept, 5–7 chunks, 13–20 sentences); select call 2.2–4.5 s (prompt 427–683 tok, out 5–100 tok); 0/4 unmapped; the selected chunk was in B's kept on 3/3 picks (0 in dropped), 1 NO_EVIDENCE. SB: 45–95 biased token ids per item; changes the S answer on 1/3 evidence items at b 2.0.

## Examples (first 200 chars)
- **B** `vit-hum-004`: "Gríma Wormtongue kills Saruman in Isegard during the War of the Ring, as Saruman's army attacks Helm's Deep. Gríma is later killed by hobbit archers [2]."
- **B** `lan-cmp-004`: "Not found in this phone's offline library. From the model's memory, may be wrong: / An adult male moose weighs on average about 1,400 kg, while an adult male American bison weighs about 1200 kg on avera"
- **S** `vit-hum-004`: "Not found in this phone's offline library. From the model's memory, may be wrong: / Gríma Wormtongue kills Saruman in the Battle of the Hornburg, as part of Saruman's army attacking Helm's Deep. This ac"
- **S** `lan-cmp-004`: "Not found in this phone's offline library. From the model's memory, may be wrong: / An adult male moose weighs more on average than an adult male American bison. The average weight of a male moose is ar"
- **C1** `vit-hum-004`: "Not found in this phone's offline library. From the model's memory, may be wrong: / Gríma Wormtongsue kills Saruman in Isegard during the conflict. Gríma joins Sarumann's军队 to spy, but is shot by hobbit"
- **C1** `lan-cmp-004`: "Not found in this phone's offline library. From the model's memory, may be wrong: / An adult male moose weighs on average 500 kg, while an adult male American bison (creckshields) weighs about 1,000 kg "
- **C1p01** `vit-hum-004`: "Gríma Wormtongue kills Saruman in Isegard during the Battle of Isegard, as Saruman's army is defeated. Gríma is later shot by hobbit archers during the return journey [2]."
- **C1p01** `lan-cmp-004`: "Not found in this phone's offline library. From the model's memory, may be wrong: / An adult male moose weighs on average 500 kg, while an adult male American bison weighs about 1,200 kg, so the America"
- **SC** `vit-hum-004`: "Gríma Wormtongs kills Saruman during the Battle ofthe Hornburg [1]. Saruman sends his army to Helm's Deep, and after the Rohirems defeated his army, Gríma participates in the kill [1]."
- **SC** `lan-cmp-004`: "Not found in this phone's offline library. From the model's memory, may be wrong: / The average wild male moose weighs approximately 550 kg (1210 lb), while an adult male American bison weighs about 900"
- **SCp01** `vit-hum-004`: "Gríma Wormtongue kills Saruman during the Battle of the Hornburg, helping to defeat Saruman's army [1]. Saruman is killed by Gríma, who is later captured by Aragorn's army [1]."
- **SCp01** `lan-cmp-004`: "Not found in this phone's offline library. From the model's memory, may be wrong: / An adult male moose weighs more on average than an adult male American bison. The average weight of a wild male moose "
- **SB** `vit-hum-004`: "Not found in this phone's offline library. From the model's memory, may be wrong: / Gríma Wormtongue kills Saruman in the Battle of the Hornburg, as part of Saruman's army attacking Helm's Deep. This ac"
- **SB** `lan-cmp-004`: "Not found in this phone's offline library. From the model's memory, may be wrong: / An adult male moose weighs more on average than an adult male American bison. The average weight of a male moose is ar"

## Reading for the freeze (no judge used)
- Recommend freezing CAD arms with `DG_PLAUS=0.1` (C1p01/SCp01) instead of the spec's pure −30 imputation: at α 1.0 the spec variant emits non-words/CJK on most CAD answers (it rewards any ctx top-40 tail token absent from the no-ctx top-40). Both variants are runnable (env DG_PLAUS).
- SB at b 2.0 is near-inert on this smoke (diff vs S 1/3); consider b 4–5 before the freeze, or accept SB ≈ S.
- Cost: S/SB +≈1.3 s per item (select call), SC/SCp01 ≈ 1.6× B; C1 ≈ 1.1× B. All under the 4× kill.
- Smoke selected-in-dropped = 0: the S3 mechanism is not exercised on these 5; it can only be read on the 97.

## Full MAIN 97 run (not started; coordinator freezes the criterion first)
```
cd <workspace>/rnd/research/coordinator/arms/decode-ground
python3 -I ../lp-screens/tools/mkreq.py K1 ../lp-screens/main-97.ids dg-S-K1-main-s42 cut7-headpass-x2+litepacks+dg-S runs/req/dg-S-K1-main-s42.requests.jsonl
NOWAIT=1 bash tools/run_dg.sh S runs/req/dg-S-K1-main-s42.requests.jsonl dg-S-K1-main-s42      # or without NOWAIT: polls, copies runs/traces/<run>.traces.jsonl
DG_PLAUS=0.1 bash tools/run_dg.sh SC runs/req/dg-SC-K1-main-s42.requests.jsonl dg-SCp01-K1-main-s42
```
Mini STATUS: `<runner>/kiln/lp-screens/jobs/<RUN>/STATUS` (queued/slot/start/end + DONE|FAIL, from lp-screens mini_gen.sh). Disk on the mini is at the 25 GiB guard (df -g 25): a job FAILs at start if it dips below.
