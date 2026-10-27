# RD1 READ-SEQ: SE question-body demotion and score order of SE answers in the sources block (2026-10-22, Haiku 64 of 100, Opus 0, paid 0, phone 0)
Criterion READER-criterion.md (sha f361f738, not edited). Fix: BOAR_READ_SEQ=1 (unset or any other value = F1b bytes). Patch: arms/retrieve-sweep/patches/RD1-READ-SEQ-SE-question-body-demotion-and-score-order-of-SE-answers-in-the-sources-block.patch (sha 7281afb8, H4-relative: src/rag/pure.ts reorderSeSources + src/rag/readSeq.test.ts + src/routing/answer.ts hook; adapter.ts run-metadata line engine.read_seq in boar-eval, uncommitted). Tree kiln-local/rs-RD1 (cp -c -R of rs-H4). Nothing committed or pushed.
## Checks (0 LLM)
- (a) tsc: clean for the changed files (the tree has no expo base; typechecked a copy of rs-H4 and rs-RD1 src against boar-app's node_modules: 4 identical missing-JSON-asset errors in both, 0 new). Unit tests: readSeq.test.ts 7/7 (lan-hlt-003 shape, money-010 shape, wiki-only list unchanged, pinned question kept, tie order, no mutation).
- (b) Byte identity, switch unset: replay MAIN 97 (rs-RD1, RS_MERGE=gidf, 13-pack kit with v3 cooking/money, packHeadPass a2 + packDense2 extra) vs sefix/replays/main.v3-extra.jsonl: keptFull, sources, reasonCodes identical 97/97 (rd1/replay-off.json). Switch-off live identity 20/20 vs the F1b traces: text, reasonCodes, cited, kept, weakSources (rd1/ident20.json; 20 items generated on the mini, readseq codes 0).
- (c) Switch on, replay: 34 of 97 changed contexts (expected 15-30), all 34 with a qa-pack chunk kept (rd1/replay-on.json). Of these, 32 changed the live answer text; the other 2 (lan-hlt-003, vit-hlt-003) are instant-path items whose answer is the snippet, unchanged. The readseq codes fired on 34: dropq on the question-echo items, reorder, qlabel.
## Generation (mini, one job, seed 42, F1b configuration + switch)
Sanity 97/97, 0 empty, 0 loops, 0 errors; the 26 deterministic items byte-identical to F1b; mean output tokens 33.4 vs 32.3; mean totalMs 4656 vs 3748 (mini load varies, not a speed claim). Answers that differ from F1b: 32 (v0.1 5, cooking 12, money 15), all judged (cap 100 calls not reached, left 0).
## Answer screen (Haiku 5.5-low judge.v1 N 4 both orders, 64 calls; F1b and control rows reused)
| | n | U | corr | CE | CE unwarned | warned |
|---|---|---|---|---|---|---|
| K3 control, all 97 | 97 | 0.4102 | 2.536 | 29 | 12 | 46 |
| F1b, all 97 | 97 | 0.4009 | 2.443 | 32 | 18 | 36 |
| **RD1, all 97** | 97 | 0.4080 | 2.464 | 30 | **14** | 43 |
| F1b, 32 changed | 32 | 0.3744 | 2.203 | 10 | 4 | 15 |
| RD1, 32 changed | 32 | 0.3963 | 2.266 | 8 | 0 | 22 |
- dU vs F1b on the 32 changed: **+0.0219 [-0.0121, +0.0560]** (item bootstrap B 2000 seed 11); dcorr +0.063 [-0.203, +0.344]. All 97: +0.0071 [-0.0037, +0.0196].
- vs the K3 control over all 97: **-0.0022 [-0.0265, +0.0205]**.
- CE-unwarned (all 97): 18 -> 14 (not up; K3 control 12). New CE: cooking-014, money-001, money-013 (all warned); fixed CE: trv-004, cooking-003, cooking-010, money-006, money-012. corr up >= 1: lan-rsn-001, trv-004, cooking-019, money-012; down >= 1: lan-hlt-001, vit-trv-003, cooking-014, money-001, money-013.
- By source (changed): v0.1 n 5 +0.086 [-0.017, +0.198]; cooking n 12 +0.028 [-0.028, +0.075]; money n 15 -0.005 [-0.053, +0.042].
- Targets (8): mean correctness 1.875 -> 2.062 (+0.187; rule needs +0.5). Changed 4/8: lan-rsn-001 2.5 -> 4.0, money-010 1.0 -> 1.0, cooking-008 2.0 -> 2.0, cooking-012 1.5 -> 1.5. Unchanged 4/8: lan-hlt-003 and vit-hlt-003 (instant path, answer is the snippet), cooking-001 and money-018 (no readseq code fired: nothing to drop, reorder or label). CE-unwarned on the targets 3 -> 2.
## Verdict by the frozen rule: **no**
dU >= +0.02: yes (+0.022) but CI low -0.012 is not > -0.01: fail; CE-unwarned not up: pass (18 -> 14); targets +0.5: fail (+0.19). Not READS, so not LEVER-CANDIDATE (vs K3 -0.002).
## Mechanism read (from the traces)
- The CE-unwarned drop is a labelling effect, not a correctness effect: warned answers 36 -> 43 (7 newly warned: lan-hlt-001, cooking-004, cooking-008, money-006, money-010, money-012, money-013, none un-warned). In money-010 F1b cited [1], the premise-echo question chunk, so the wrong memory answer ("Yes, you can ... before the April deadline") passed the grounding gate; with the question chunk dropped the same wrong answer is uncited and gets the memory warning line. Correctness stays 1.0. Dropping the echo removes false support; it does not make the 1.7B read the answer chunk.
- Improved by >= 1 (lan-rsn-001 +1.5, trv-004, cooking-019, money-012) and fell by >= 1 (lan-hlt-001, vit-trv-003, cooking-014, money-001, money-013): per-item causes not autopsied here (cap on scope); net correctness on the changed items +0.06, inside noise.
- The two health-shaped targets of the prediction (lan-hlt-003, vit-hlt-003) are instant-path items: the readseq codes fire on them in the replay, but the answer is the snippet, so the reorder cannot change it.
## Prediction vs result
Predicted +0.5..+1.5 correctness on 3-5 of 8 targets, dU +0.02..+0.05 on changed, CE-unwarned down, most likely READS. Result: dU +0.022 (low end, CI crosses), CE-unwarned down (as predicted, but through warnings), targets +0.19 with 1 of 8 clearly up, changed contexts 34 (above 15-30). Prediction missed on the targets; it hit on CE-unwarned direction and on the replay size.
## Items (32 changed, all judged)
| item | corr F1b | corr RD1 | warned F1b>RD1 | CE F1b>RD1 |
|---|---|---|---|---|
| lan-hlt-001 | 3.0 | 2.0 | n>Y | n>n |
| lan-rsn-001 | 2.5 | 4.0 | n>n | n>n |
| st-qa-cooking-se-003 | 1.5 | 2.0 | Y>Y | Y>n |
| st-qa-cooking-se-004 | 4.0 | 4.0 | n>Y | n>n |
| st-qa-cooking-se-006 | 2.5 | 3.0 | Y>Y | n>n |
| st-qa-cooking-se-007 | 1.5 | 1.5 | Y>Y | Y>Y |
| st-qa-cooking-se-008 | 2.0 | 2.0 | n>Y | n>n |
| st-qa-cooking-se-009 | 4.0 | 4.0 | n>n | n>n |
| st-qa-cooking-se-010 | 1.5 | 2.0 | Y>Y | Y>n |
| st-qa-cooking-se-011 | 3.0 | 3.0 | n>n | n>n |
| st-qa-cooking-se-012 | 1.5 | 1.5 | Y>Y | Y>Y |
| st-qa-cooking-se-014 | 2.5 | 1.0 | Y>Y | n>Y |
| st-qa-cooking-se-019 | 2.0 | 3.0 | Y>Y | n>n |
| st-qa-cooking-se-020 | 2.0 | 2.0 | Y>Y | n>n |
| st-qa-money-se-001 | 2.0 | 1.0 | Y>Y | n>Y |
| st-qa-money-se-003 | 3.0 | 3.0 | Y>Y | n>n |
| st-qa-money-se-006 | 1.5 | 2.0 | n>Y | Y>n |
| st-qa-money-se-007 | 1.0 | 1.0 | Y>Y | Y>Y |
| st-qa-money-se-008 | 2.5 | 2.0 | n>n | n>n |
| st-qa-money-se-009 | 3.0 | 2.5 | n>n | n>n |
| st-qa-money-se-010 | 1.0 | 1.0 | n>Y | Y>Y |
| st-qa-money-se-011 | 2.0 | 2.0 | n>n | n>n |
| st-qa-money-se-012 | 1.0 | 2.5 | n>Y | Y>n |
| st-qa-money-se-013 | 3.0 | 1.5 | n>Y | n>Y |
| st-qa-money-se-014 | 2.0 | 2.0 | Y>Y | n>n |
| st-qa-money-se-016 | 2.0 | 2.0 | Y>Y | n>n |
| st-qa-money-se-017 | 3.0 | 3.5 | n>n | n>n |
| st-qa-money-se-019 | 3.0 | 3.0 | Y>Y | n>n |
| st-qa-money-se-020 | 1.0 | 1.0 | Y>Y | Y>Y |
| trv-004 | 1.0 | 3.5 | n>n | Y>n |
| vit-cry-006 | 2.0 | 2.0 | n>n | n>n |
| vit-trv-003 | 3.0 | 2.0 | n>n | n>n |
## Reproduce
tools: rd1/tools/{run_rd1_gen.sh, select_rd1_ids.py, judge_rd1.sh, agg_rd1.py, run_rd1_replay.sh, ident_rd1.py, ident_replay_rd1.py}; traces rd1/traces/; judgments rd1/judge/; data RD1.json. Call ledger: rd1/judge/calls.log (v01 10, cooking 24, money 30 = 64; an interrupted first judge run may have billed up to 1 extra in-flight call that left no row). UNKNOWN: whether the question-chunk drop helps when the model is also told which source is an answer (RD3/RD2 lines run separately).
