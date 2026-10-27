# FACTPRESENT (2026-10-21): on the self-tests the whole pack gain sits on items whose key fact the pack adds to the kept context (+0.14 to +0.17). On real dev items, the same cell gives about 0 (1.7B K3-K0 -0.010 [-0.077, +0.050], n 10).

TL;DR (post-hoc, 0 LLM, 0 generation, 0 judge calls, 0 paid; existing Haiku 5.5-low judgments only)
- **Hypothesis:** "packs lift an answer only when the item's key fact is actually present in the kept context".
- **Self-tests: the hypothesis holds.** On the topical 60, the K3-K0 gain is all in cell (a), the items where K3 adds the fact.
  - 1.7B, oracle chunk rule: (a) +0.139 [+0.075, +0.201], n 27. (c) -0.012 [-0.050, +0.020], n 33.
  - 1.7B, lexical rule: (a) +0.166 [+0.110, +0.236], n 20. (c) +0.001.
  - Gemma: (a) +0.168 (oracle) / +0.213 (lexical). (c) about 0.
  - So fact presence is a necessary condition there. The +0.056 average is (a)'s share times about +0.15.
- **Real items (v0.1, MAIN): the self-test gain is NOT reproduced in cell (a).**
  - 1.7B K3-K0: (a) -0.010 [-0.077, +0.050], n 10; strict rule +0.005 [-0.054, +0.072], n 7.
  - 1.7B K1-K0: (a) -0.015 [-0.084, +0.052], n 9.
  - Gemma K1-K0: (a) -0.034 [-0.111, +0.044], n 9.
  - Every (a) CI excludes the self-test cell-(a) effect (+0.14 to +0.17). Under the primary rule they also exclude the +0.056 average; the strict CI does not.
- **Real items rarely get the fact from a pack.** Kept-context fact presence on MAIN keyed 92: K0 14 %, K1 24 %, K3 25 %.
  - In-pack items: K0 13 %, K3 21 %. With the covering pack loaded: K3 14/27 = 52 %. Cooking/money (pack never loaded): 0/40.
  - On the 17 "matching pack added" items (14 keyed): K0 3, K1 6, K3 7. Most of the added facts come from simplewiki (K1 already has them), not from the topical pack.
- **The only positive cell on real items is (b): fact already in K0, K3 adds more context.** K3-K0 +0.059 [+0.022, +0.093], n 13 (strict +0.063, n 8).
  - Items: crypto 6, country 3, place 2.
  - The K1-K0 (b) is weaker: +0.021, CI straddles 0.
  - (b) is not pre-specified, has small n, and is one of about 20 cells. Treat it as a lead, not a finding.
- **Cross-section (within K0): items whose kept context holds the fact score lower, not higher.** All CIs straddle 0.
  - 1.7B: 0.359 vs 0.405 (gap -0.046 [-0.122, +0.036]). Gemma: -0.041. 4B: -0.027.
  - These are the crypto/country items, the hard slices.
  - In the K3 context the sign flips: +0.051 [-0.024, +0.126].
- **Reading.** On real questions the bottleneck is not reach alone. When a pack does put the fact in the kept context, the 1.7B/Gemma answer does not measurably improve. Possible causes:
  - the fact sits in a 4-6-chunk context with distractors;
  - the questions are multi-fact (the rubric's other points are not covered);
  - lexical matching overstates presence (see caveats).
  - The self-test effect needs pack-written single-fact questions whose fact chunk is retrieved.

Files: script `tools/factpresent.py` (sha256 7cd11c65...); output `FACTPRESENT-2026-10-21.json` (sha256 **4a5cb4fcd6eb993a024f920cc9ed7cdcb479ebe2caccb1330d00ac7afd602890**). The JSON holds per item x arm: share, present, strict, oracle, n_blocks, pack_loaded; per cell: ids, n, U0, U1, d, CI. It also holds sha256 of the 18 replay files. Replay driver `tools/factpresent_replay.sh` (sha256 62fa3eb8...).
Rerun:
```
bash tools/factpresent_replay.sh <job>                       # MacBook, about 7 min, 0 generation
python3 -I tools/factpresent.py <job>/out FACTPRESENT-2026-10-21.json
```
The replay prompts/traces (pack text) stay out of git and are reproducible.

## 1. Method
- **Kept context.** LITEPACKS traces log kept titles, not chunk text. So the K0/K1/K3 requests (v0.1 60, cooking+money 40, self-tests 180; LITEPACKS runs/req, unchanged) were replayed against a stub llama-server.
  - The replay used the real LITEPACKS adapter (`be/adapter-litedecline.ts`, LITEDECLINE_OFF=5, ship profile, mmbert v3b detector on the MacBook's :8094).
  - The tree was a clone of `kiln-local/be-0cfd4a77-cut7-litepacks`, patched by `arms/retfloor/tools/apply_retfloor.py` (sha 7c26f177..., identical to RETFLOOR's) at `RETFLOOR_VARIANT=base`. That variant is the LITEPACKS behaviour plus a `retfloor:kept:<chunk ids>` log line.
  - `--dump-prompts` captured the exact Context block of every generation call. An item's kept context = the union of the numbered blocks over its calls.
- **Parity.** Kept titles (title + section, per item, in order) match the judged LITEPACKS runs on **280/280 items for each of K0, K1 and K3**.
  - Gemma (K0 s42, K1 s42, K0/K3 cand80) and 4B (K0 s42) kept titles also equal the 1.7B's on every item. Their contexts are therefore taken from the 1.7B replay; parity is at title level.
  - First try on the mini was cancelled: both slots were held by another session's lp-screens jobs. The run moved to the MacBook (8 min).
- **Key-fact rule (lexical; stated before computing; never tuned).** The match runs on the kept context only, never on the answer.
  - **v0.1:** the item's grading contract, i.e. must_any groups and must_k.
    - Matching uses the vendored precheck term semantics (`boar-eval/scorers/vendor/lantern/precheck.py`: word-boundary terms, `re:` regexes, echo filter).
    - share = groups hit / groups. must_k counts as one group, hit at >= k distinct terms.
    - 5 items have no lexical key (trv-002, trv-004 judge-only; dng-001/002/005 firstaid scorer) and are excluded, leaving 52 v0.1 keyed.
  - **Self-tests (incl. MAIN cooking/money):** the item's `in_pack_facts`. A fact is hit when any of these holds:
    - the pack quote is a substring of the normalised context;
    - >= 80 % of the quote's content tokens (>= 4) sit in one kept block;
    - >= 80 % of the fact statement's content tokens (>= 3) sit in one kept block.
  - **PRESENT** (primary) = share >= 0.5. **STRICT** (sensitivity) = share = 1.
  - **ORACLE** (self-tests only) = an `arms/oracle-st/tools/oracle-facts.json` fact chunk id is among the kept chunk ids.
- **Lexical vs oracle, 180 self-tests, K3:** both 30, lexical only 2, oracle only 13, neither 135. So the lexical rule has precision about 94 % and recall about 70 % against the chunk-id truth. K1: 10 / 3 / 6. K0: 0 / 1 / 0.
- **U and deltas.**
  - U per item: Haiku 5.5-low judge.v1-low, both orders, s0 = 0 when declined. K1/K3 reuse K0 rows for byte-identical answers. All of this follows `inpack_split.py`.
  - Cell delta = U(Kx) - U(K0) as a ratio of sums inside the cell. Paired item bootstrap: B 2000, seed 11, 2.5/97.5 pct.
  - Cells: (a) present in Kx only, (b) present in both, (c) absent in both, (d) present in K0 only. (d) is empty in every contrast: no pack set ever pushed out a fact K0 held.

## 2. Cells (U delta Kx - K0, 95 % CI)
MAIN keyed 92 = v0.1 52 + cooking/money 40. Cooking/money sit entirely in (c): their facts live in qa-cooking-se / qa-money-se, which no arm loads. MAIN cells (a)/(b) are therefore the v0.1 cells.

| contrast | rule | (a) present in Kx only | (b) present in both | (c) absent in both | all |
|---|---|---|---|---|---|
| 1.7B K3-K0, MAIN 92 | present | n 10: -0.010 [-0.077, +0.050] | n 13: **+0.059 [+0.022, +0.093]** | n 69: -0.022 [-0.049, +0.003] | -0.009 [-0.031, +0.014] |
| 1.7B K3-K0, MAIN 92 | strict | n 7: +0.005 [-0.054, +0.072] | n 8: +0.063 [+0.018, +0.104] | n 77: -0.018 [-0.042, +0.006] | |
| 1.7B K1-K0, MAIN 92 | present | n 9: -0.015 [-0.084, +0.052] | n 13: +0.021 [-0.013, +0.056] | n 70: -0.015 [-0.037, +0.006] | -0.010 [-0.028, +0.010] |
| 1.7B K1-K0, MAIN 92 | strict | n 8: +0.011 [-0.038, +0.070] | n 8: +0.021 [-0.018, +0.063] | n 76: -0.015 [-0.036, +0.005] | |
| 1.7B K3-K0, MAIN in-pack 67 | present | n 5: +0.003 [-0.060, +0.057] | n 9: +0.063 [+0.025, +0.094] | n 53: -0.032 [-0.064, -0.003] | -0.017 [-0.044, +0.008] |
| Gemma K1-K0 s42, MAIN 92 | present | n 9: -0.034 [-0.111, +0.044] | n 13: +0.048 [-0.004, +0.096] | n 70: -0.016 [-0.044, +0.009] | -0.009 [-0.031, +0.015] |
| Gemma K1-K0 s42, MAIN 92 | strict | n 8: +0.017 [-0.046, +0.073] | n 8: +0.055 [-0.022, +0.130] | n 76: -0.018 [-0.044, +0.006] | |
| **self-tests topical 60, 1.7B K3-K0** | oracle | n 27: **+0.139 [+0.075, +0.201]** | n 0 | n 33: -0.012 [-0.050, +0.020] | +0.056 [+0.018, +0.096] |
| self-tests topical 60, 1.7B K3-K0 | present | n 20: +0.166 [+0.110, +0.236] | n 0 | n 40: +0.001 [-0.035, +0.039] | |
| self-tests topical 60, 1.7B K3-K0 | strict | n 11: +0.168 [+0.091, +0.258] | n 0 | n 49: +0.031 [-0.009, +0.072] | |
| self-tests topical 60, Gemma K3-K0 | oracle | n 27: +0.168 [+0.086, +0.244] | n 0 | n 33: +0.001 [-0.045, +0.043] | +0.076 [+0.025, +0.123] |
| self-tests topical 60, Gemma K3-K0 | present | n 20: +0.213 [+0.149, +0.280] | n 0 | n 40: +0.007 [-0.043, +0.053] | |
| self-tests 180, 1.7B K3-K0 | oracle | n 43: +0.130 [+0.085, +0.174] | n 0 | n 137: -0.003 [-0.021, +0.014] | +0.029 [+0.011, +0.049] |
| self-tests 180, 1.7B K1-K0 | present | n 12: +0.140 [+0.077, +0.200] | n 1 | n 167: +0.003 [-0.010, +0.017] | +0.011 [-0.004, +0.025] |

**Cell (a), real items, 1.7B K3-K0, present rule, per item (U0 -> U1):**

| item | U0 -> U1 | tag |
|---|---|---|
| lan-rsn-001 | 0.28 -> 0.45 | place |
| lan-hlt-002 | 0.53 -> 0.60 | health |
| lan-exp-003 | 0.67 -> 0.72 | country |
| vit-trv-003 | 0.24 -> 0.28 | travel |
| vit-hum-004 | 0.20 -> 0.23 | humanities |
| lan-ref-002 | 0.69 -> 0.67 | history |
| lan-hlt-003 | 0.47 -> 0.43 | health |
| lan-ref-003 | 0.53 -> 0.47 | history |
| lan-hlt-001 | 0.43 -> 0.32 | health |
| lan-rsn-004 | 0.43 -> 0.20 | history |

- 8 of these 10 already have the fact in K1 (simplewiki). Only lan-hlt-002 and lan-hlt-003 depend on medlineplus.
- K0 U in cell (a) is 0.45, against 0.39 on the self-test cell (a), so there is less headroom. That cannot explain a 0.15 gap on its own.

## 3. Coverage: does the pack set surface the fact? (share of keyed items with the fact in the kept context, present rule)
| subset | K0 | K1 | K3 |
|---|---|---|---|
| MAIN keyed 92 | 13 (14 %) | 22 (24 %) | 23 (25 %) |
| MAIN in-pack 67 | 9 (13 %) | 13 (19 %) | 14 (21 %) |
| MAIN off-pack 25 | 4 (16 %) | 9 (36 %) | 9 (36 %) |
| in-pack, covering pack loaded in the arm | 6/13 (46 %) | 7/13 (54 %) | 14/27 (52 %) |
| in-pack, covering pack not loaded | 3/54 (6 %) | 6/54 (11 %) | 0/40 (0 %) |
| v0.1 in-pack 27 / off-pack 25 | 9 / 4 | 13 / 9 | 14 / 9 |
| matched 17 of INPACK-SPLIT §3 (14 keyed: health 4, firstaid 2, country 8) | 3 | 6 | 7 |
| MAIN in-pack, strict rule | 7 (10 %) | 10 (15 %) | 10 (15 %) |
| self-tests topical 60 (own pack in K3): lexical / oracle | 0 / 0 | 2 / 0 | 20 (33 %) / 27 (45 %) |
| self-tests 180 whose domain pack (tag-level) is loaded: lexical / oracle | 1/60 / 0/60 | 11/80 / 16/80 | 32/160 / 43/160 |

- K3 per tag (MAIN): crypto 6/11, country 4/8, health 3/4, firstaid 0/2, travel 1/2, history-culture 4/7, place-other 3/6, nature 1/4, humanities 1/6, science-tech 0/2, cooking 0/20, money 0/20.
- **A domain match is a weak proxy for fact presence.** Even with the covering pack loaded, about half of real in-pack items get the key fact into the kept context.
- On the SE self-tests, the tag-level "domain pack" in K0 (boar-crypto for the ethereum/bitcoin SE items, wikivoyage for travel SE) surfaces their facts 0/60 times by the oracle rule.

## 4. Cross-section within an arm (MAIN keyed 92; U present vs absent, gap CI)
| system (context) | present n / U | absent n / U | gap [CI] |
|---|---|---|---|
| 1.7B K0 | 13 / 0.359 | 79 / 0.405 | -0.046 [-0.122, +0.036] |
| Gemma K0 s42 | 13 / 0.395 | 79 / 0.436 | -0.041 [-0.098, +0.015] |
| 4B K0 s42 | 13 / 0.454 | 79 / 0.482 | -0.027 [-0.105, +0.051] |
| 1.7B K3 | 23 / 0.428 | 69 / 0.377 | +0.051 [-0.024, +0.126] |

In K0 the fact-present items are mostly crypto (6) and country (3), the hard slices in INPACK-SPLIT. So presence is confounded with difficulty, and the paired cells in §2 are the cleaner read.

## 5. Verdict on the question asked
- **Is the self-test gain (+0.056) reproduced on real items in cell (a)? No.**
  - The real-item (a) estimates are -0.010 (1.7B K3), -0.015 (1.7B K1) and -0.034 (Gemma K1).
  - Every CI upper bound (+0.044 to +0.072) sits below the self-test (a) effect (+0.139 oracle / +0.166 lexical). Under the primary rule the K3 and K1 CIs also exclude +0.056.
- "Fact present" is necessary for a pack gain on pack-written questions. On real questions it is not sufficient, at least for the 1.7B and Gemma E2B with this context.
- **Next cheap checks (not run):**
  - Read the 10 cell-(a) answers against their kept fact block, 0 LLM, to classify misread / ignored / partial-fact / lexical false positive.
  - Test whether the (b) +0.06 survives a second seed (K3 s43 on the 13 (b) items) before treating it as a lever.

## 6. Caveats
- **Post-hoc.** The question was asked after INPACK-SPLIT's numbers were known. The lexical rule and the 0.5 threshold were written before the first computation and never changed. The strict rule is the only sensitivity analysis.
- **Lexical fact matching is noisy on v0.1.** must_any terms are short and some are generic.
  - Spot check of the 10 cell-(a) items: about 6 are clear matches (Kenya facts, Apollo 1969, Great Wall not visible, 150/75 min, malaria/dengue/yellow fever, Union victory).
  - The other 4 are generic-term hits: lan-hlt-001 "risk/evidence", vit-trv-003 "route/motorbike", lan-rsn-004, vit-hum-004 at share 0.5.
  - So real-item presence is overstated, if anything. The strict-rule cell (a) (n 7) gives the same answer.
  - On the self-tests, lexical vs chunk-id truth has precision about 94 % and recall about 70 %.
- **Context parity is at title level for Gemma/4B.** Their contexts come from the 1.7B replay, and chunk-level identity is assumed. Context parity of the replay vs the judged 1.7B runs is also at title level (280/280 per arm); the chunk text is the deterministic engine output.
- **Judge and seeds.** Haiku 5.5-low judge (it compresses gaps), one seed per arm, dev sets only. Small cells: real (a) n 7-10, CI half-widths about 0.06.
- (d) is empty, so this design cannot test "losing the fact hurts".
- **Exposure.** No blind/, no rnd/veil, no v0.4. The v0.1 and self-test question text and grading terms were read by the script only. The JSON and this file hold ids, flags and numbers; the only grading terms quoted here are in §6.
