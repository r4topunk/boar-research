# REREAD 2026-10-20: today's 7 stage-1 screen verdicts under the corrected measurement

TL;DR:
- This is a re-analysis only. It uses 0 generations, 0 judge calls and 0 paid calls. Every frozen verdict stands; nothing here is a decision.
- The corrected labels follow the model-usage audit (M1, M2, M4, N1) and refute-1/refute-2:
  - engine refusals and notices count as declines, never as CE;
  - CE is split into unwarned (default mode) and warned (show-anyway mode);
  - OCC abstentions count as declines.
- **Main finding: in the new default mode (no source means refuse), each screen holds only 4 control CEs.** On K0 and K1, 4 of 27 problems are unwarned CE. So the screens mostly measured show-anyway-mode CE, and a "need 6" bar cannot be met on default-mode errors at all.
- **OCC abstain-as-decline reads GO under every corrected gate** (K0: 10 fixed; K1: 14 fixed). But 19 of its 27 declines land on items the new default already refuses (warned). Its default-mode gain is small: CE-unwarned on problems goes 4 to 1 (K0) and 4 to 3 (K1). On K1 it adds 1 clear false refusal (lan-cmp-003, Qwen scored 5.0 on the same context).
- **SHORTCTX and QUOTEFIRST read GO only under the post-hoc reachable denominator**, at 4 of 4 needed, which is the null rate of about 3.
  - QUOTEFIRST is a default-mode regression: CE-unwarned on problems goes 4 to 8, with 5 new and 1 gone.
  - SHORTCTX is neutral to slightly positive: 4 to 3, with 0 new.

Script: `reread.py` (`python3 -I reread.py --json reread.json`). It reads only the frozen aggregates, gate jsons, control traces and OCC sidecars.

## Table (problems = the 27 screen problems; "37" = problems + sentinels)

| arm | K | frozen verdict (fixed) | v1-corrected verdict (fixed; of which by decline) | CE-unwarned ctl -> arm, problems (37) | CE-warned ctl -> arm, problems | declines ctl -> arm (37) | **post-hoc** v1-reachable verdict (fixed / need; live sentinels worse) |
|---|---|---|---|---|---|---|---|
| b-honest | K0 | NO-GO (4) | NO-GO (4; 0) | 4 -> 3 (4 -> 3) | 15 -> 14 | 4 -> 4 | NO-GO (4/5; 1/6) |
| greedy | K0 | NO-GO (4) | NO-GO (4; 0) | 4 -> 4 (4 -> 4) | 15 -> 11 | 4 -> 4 | NO-GO (4/5; 1/6) |
| vendorsamp | K0 | NO-GO (1) | NO-GO (1; 0) | 4 -> 4 (4 -> 4) | 15 -> 14 | 4 -> 4 | NO-GO (1/5; 1/6) |
| occrag (as run, Qwen fallback) | K0 | NO-GO (2) | NO-GO (2; 0) | 4 -> 4 (4 -> 4) | 15 -> 13 | 4 -> 4 | NO-GO (2/5; 0/6) |
| occrag-decline (abstain = decline) | K0 | NO-GO (2) | GO (10; 8) | 4 -> 1 (4 -> 1) | 15 -> 8 | 4 -> 14 | GO (10/5; 0/6) |
| shortctx | K1 | NO-GO (4) | NO-GO (4; 0) | 4 -> 3 (5 -> 4) | 13 -> 12 | 4 -> 4 | GO (4/4; 0/5) |
| quotefirst | K1 | NO-GO (4) | NO-GO (4; 0) | 4 -> 8 (5 -> 9) | 13 -> 8 | 4 -> 4 | GO (4/4; 0/5) |
| occrag (as run, Qwen fallback) | K1 | NO-GO (3) | NO-GO (3; 0) | 4 -> 4 (5 -> 5) | 13 -> 10 | 4 -> 4 | NO-GO (3/4; 0/5) |
| occrag-decline (abstain = decline) | K1 | NO-GO (3) | GO (14; 11) | 4 -> 3 (5 -> 4) | 13 -> 0 | 4 -> 21 | GO (14/4; 1/5) |

**How to read the columns**
- **Frozen verdict:** copied from `arms/<arm>/aggregates/*.gate.json`. For the OCC-decline rows it is the as-run OCC verdict.
- **v1-corrected:** the frozen rule (fixed >= 6, sentinels worse <= 1) with the corrected labels.
- **CE-unwarned / CE-warned:** CE split by whether the answer starts with the warning line "Not found in this phone's offline library. From the model's memory, may be wrong:".
- **Declines:** explicit refusals in show-anyway mode, meaning engine refusal or notice texts plus abstentions. The 4 control declines on each screen are the routing refusals from N1. Default mode would also refuse every warned answer, so default-mode declines over 37 are:

  | | K0 control | K1 control | b-honest | greedy | vendorsamp | occrag K0 | occrag-decline K0 | shortctx | quotefirst | occrag K1 | occrag-decline K1 |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | default-mode declines | 20 | 22 | 21 | 21 | 20 | 18 | 22 | 22 | 17 | 18 | 21 |

- **v1-reachable (post-hoc; not a decision):**
  - need = ceil(0.22 x corrected control CE on problems that reach the LLM) = ceil(0.22 x 19) = 5 on K0 and ceil(0.22 x 17) = 4 on K1;
  - only live sentinels count (6 on K0, 5 on K1), at most 1 worse.
  - This denominator was chosen after seeing the results (refute-2 M2a).

## Corrections applied (what changed vs the frozen labels)

1. **Refusals and notices.** These engine strings are now declines, never CE. They were found by grepping the litepacks tree:
   - "I don't have a reliable offline source on this, so I won't give health advice from memory..." (context.ts:1417);
   - "The offline places pack is not installed..." (geo.ts:452);
   - "I didn't find this in this phone's library." (answer.ts);
   - "I didn't find safe first-aid instructions..." (context.ts:1385);
   - the bare "The offline source doesn't give first-aid steps..." (context.ts:1284);
   - a warning line with no body.

   The frozen RX is also extended with model-written abstentions on short answers: "not enough information", "sources do not contain", "unanswerable".

   Effect: the 4 routing refusals (st-qa-cooking-se-002, -013, -015, st-qa-money-se-004) leave the control CE count. Control CE on problems goes 23 to 19 on K0 and 21 to 17 on K1. All 4 were "unwarned CE" in the frozen labels, which is why refute-2's 8u became 4u here.

   No model-written refusal exists in any of today's non-OCC traces, so B-HONEST's prompt produced none, and no arm's verdict moves from (1) alone.
2. **CE split by the warning line.** This follows the product decision of 20:24 (QUEUE l.1443): no source means refuse by default, with show-anyway on request.
3. **OCC abstain-as-decline.** These routes count as declines in place of the Qwen fallback:
   - `occ-abstain-*`: UNANSWERABLE, or the answer "Not enough information";
   - `occ-malformed-*` whose OCC text says it lacks the information: "Not enough information", "The provided sources do not contain...", or lowercase status 'unanswerable'.

   The remaining malformed or looped traces carry a real OCC answer (K0 lan-rsn-003, lan-ref-002; K1 vit-hum-004). They keep the judged Qwen fallback text, which is the only judged text available.

   Declines: K0 10 (7 abstain + 3 malformed-abstain), K1 17 (15 + 2).
4. **Reachability.** An item counts as reachable if the mini control trace has a sampler temperature and outputTokens > 0. Unreachable sentinels: K0 lan-rsn-002, lan-rsn-007, vit-sci-003, vit-trv-004; K1 the same plus vit-hlt-002 (5). Unreachable problems on both screens are the 4 N1 routing refusals.

## OCC-decline: fixes, CE-unwarned, declines and false refusals

The judge never saw the sources, so "the source supports the answer" is a proxy. It is read from the same-context Qwen answer, because the fallback request is byte-identical to the control. "Unwarned" means the control engine kept an on-topic source and answered without the warning line.

| | K0 | K1 |
|---|---|---|
| fixed (v1-corrected) | 10, of which 8 by decline | 14, of which 11 by decline |
| CE-unwarned, problems ctl -> arm | 4 -> 1 (lan-cmp-004, -005, lan-exp-007 removed; st-qa-money-se-009 stays) | 4 -> 3 (vit-cry-006 by OCC answer and vit-cry-007 by decline removed; lan-rsn-003 new: OCC's confident cited "pronghorn") |
| declines (OCC abstentions) | 10 | 17 (16 problems + sentinel st-qa-cooking-se-009) |
| unwarned, Qwen corr >= 3.0 = **false refusal** | 0 | **1** (lan-cmp-003, Qwen 5.0) |
| unwarned, Qwen corr 2.0-2.5 (ambiguous) | 1 (st-qa-cooking-se-020, 2.5) | 1 (st-qa-money-se-009, 2.5) |
| unwarned, Qwen corr <= 1.5 (correct refusal of a sourced CE) | 3 | 1 (vit-cry-007) |
| warned, Qwen memory answer corr >= 3.0 (lost only in show-anyway mode) | 0 | 4 (lan-rsn-005, st-qa-cooking-se-009 sentinel, -019, vit-sci-002; all 3.0) |
| warned, corr 2.0-2.5 | 1 (lan-rsn-001) | 0 |
| warned, corr <= 1.5 (already refused by the new default) | 5 | 10 |

Reading:
- 19 of the 27 OCC declines (6 on K0, 14 on K1) fall on items the control already flagged as warned, so the new default refuses them anyway. They reached OCC only because the X2b append bypasses grounding (CTX-F1).
- On default-mode answers, OCC-decline removes 3 sourced CEs on K0 and nets 1 on K1, at the cost of 1 clear false refusal plus 2 ambiguous ones.
- Its stage-2 latency clause still fails: 2.0x wall on OCC-eligible items, and about 330 OCC tokens per call (OCCRAG.md).

## Per-arm notes (default mode = CE-unwarned)

- **b-honest K0:** 2 removed (lan-cmp-005, st-qa-money-se-009), 1 new (st-qa-money-se-011). The sentinel st-qa-money-se-002 (3.5 to 2.5) is live, so it counts in every gate.
- **greedy, vendorsamp K0:** 0 change in default mode. All of greedy's 4 fixes are warned answers (show-anyway mode only).
- **shortctx K1:** 1 removed (vit-cry-006), 0 new. All 4 of its v1 fixes were warned in the control (show-anyway mode only). vit-cry-005, trv-004 and cooking-se-020 are also "fixed" by other arms (decoding perturbation; refute-2). The same holds for quotefirst's 4 fixes, all warned in the control.
- **quotefirst K1:** 5 new (lan-cmp-003, lan-rsn-003, st-qa-money-se-010, vit-sci-002, vit-trv-003), 1 removed (vit-cry-009). Several items move from a warned memory answer to an unwarned assertive one: default-mode declines go 22 to 17 while CE-unwarned rises. This is a default-mode regression whatever the screen verdict says.

## UNKNOWN

- **The false-refusal proxy.** Qwen's correctness on the same context is not a support judgment, so a correct Qwen answer may come from memory. A source-support check needs a judge pass that sees the chunks.
- **The null fix rate** (about 3; M3) is still unmeasured. The 4/4 post-hoc GOs sit at it, and a seed-43 or placebo control screen decides them.
- **Haiku CE agreement with Opus at this CE rate** is unvalidated (M5).
