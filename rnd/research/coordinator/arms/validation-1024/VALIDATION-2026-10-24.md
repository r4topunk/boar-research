# VALIDATION 2026-10-24 — ENGINE-RC closing tests (night 10-23 18:00 → 10-24)

TL;DR: ENGINE-RC (SEFIX-124 search + W78 reading cost + shaped boar-factbook v2 + bannerkept, Succinct, Deep hidden) is identical to its parts and passes every 0-LLM suite. The one letter-FAIL (V1 clause 3) is pre-existing in SEFIX-124. Retrieval cost is 21 MB per question instead of 125. All LLM suites are generated (2,855 answers, 25 jobs, 0 failures) and judge-ready. **0 judge calls were made; r4to picks what to judge** (menu in §4). The follow-up gap stays (1/21). Subject carry (app-like) recovers 16/20 referents, and the carried follow-up answers cite a source more often (0.57 vs 0.41, 0-LLM).

Criterion VALIDATION-criterion.md sha aa08650f (frozen 18:2x) + ADDENDUM-1 (r4to: all suites, judging deferred), -2 (V1 reading, mini extension), -3 (carry job, two-paragraph variant), -4 (overnight jobs). Reports: V0-V1-V3L1.md, S3-ROUTES.md, V3-CARRY-GATE.md, night/aggregates/NIGHT0.md, night/judge-ready/JUDGE-READY.md.

## 1. Pass/fail matrix
| suite | reference | ENGINE-RC | verdict |
|---|---|---|---|
| V0 identity (a) switches off | retbench base kept ids | MAIN 97/97, ST 180/180 | PASS |
| V0 (b) W78 PF32 | W78-PACKFMT kept lists, 42 facts | 97/97, 42 | PASS |
| V0 (c) shaped factbook | PACKSHAPE 20 kept lists, MAIN 42 | 20/20, 42 | PASS |
| V0 (d) bannerkept | answer.test.ts green | 157/157 | PASS |
| V1 safety: 65 probes | ≤ 5 changed, 0 dose/number | 0/65 | pass |
| V1 MAIN health-family facts | 0 lost | 0 lost | pass |
| V1 cooking/money chunk on a health-strict turn | 0 | 2 (st-qa-cooking-se-002, h26), identical in SEFIX-124 | FAIL by the letter, pre-existing, 0 regressions |
| S1 delivery | MAIN 42, ST fact 77, own art. 100, TOPICS 24, F8 1, LS 4, factbook ≥ 15/20 | 42, 84, 108, 24, 1, 4, 15/20 | PASS |
| S3 routes (wt/engfix 3c38b6a0, other lineage) | 103/110, 5/5, 6/6, vitest green | 103/110, 5/5, 6/6, 1,645/1,645 | PASS |
| S8 cost | ≤ 25 MB/q, ctx ≤ 1.15x | 21.26 MB/q (SEFIX-124 125.09), ctx 0.978x, kit on disk 1.06x | PASS |
| V3 L1 multi-turn (0 LLM) | F8 1/19, LS 4/13 | 1/21, 4/13 | PASS (no regression; gap untouched) |
| V3 carry gate (RS_STICKY=2, measurement) | U5: recovers 15/18 at 1.22x | recovers 16/20 at 1.20x; LS 8/9 | PASS (gate), not adopted |
| RETBENCH B-k4comp40 candidate | probes ≤ 5, 0 dose/number | 3 changed, 2 dose/number (h19, n05) | NO (closed) |
| X2B-BUDGET (step 0) | gate | +5 MAIN, ctx 1.17x, 9 dose/number probes | NO |
| V2 UXMATRIX S (page numbers) | CWS ON ≥ 0.28, wrong-unwarned OFF ≤ 0.10 | generated | PENDING-JUDGE |
| V2 S+ ADOPT | rule in criterion | generated (seeds 42/43/44) | PENDING-JUDGE |
| S4 MAIN answers s42/s43 | paired U ≥ −0.01, CE ≤ +2 | generated; text differs 43/97, 36/97 | PENDING-JUDGE |
| S5 PACKPROOF ON/OFF | pooled ≥ 0.48, factbook ≥ 0.45 | generated (s42 + s43) | PENDING-JUDGE |
| S7 seed 44 | report | generated | PENDING-JUDGE |
| V3 L2 follow-up answers | report | generated (S, S+, s43, carry) | PENDING-JUDGE |
| S10 27 topics | KEEP ≥ 19/27 | generated (S, S+) | PENDING-JUDGE |

0-LLM verdicts: 6 suites PASS (V0, S1, S3, S8, V3-L1, carry gate), 1 letter-FAIL pre-existing (V1), 2 candidates NO. Judge-dependent: 7 PENDING.

## 2. What the night says without a judge (night/aggregates/NIGHT0.md; seed 42 unless noted; desktop M4 CPU times)
| arm | output tokens p50 / p90 | time p50 | "passages found don't support" line | cited ≥ 1 | false "Not found" |
|---|---|---|---|---|---|
| Succinct S (V2, 115) | 44 / 59 | 5.2 s | 0.60 | 0.22 | 0.026 |
| S+ 4-5 sentences | 89 / 108 | 6.0 s | 0.48 | 0.34 | 0.026 |
| P2 two paragraphs | 105 / 169 | 6.5 s | 0.53 | 0.30 | 0.026 |
| S seed 43 / S+ seed 43 | 44 / 88 tokens | | 0.54 / 0.46 | 0.28 / 0.36 | |
| PACKPROOF S (360) / S+ ON (180) / P2 ON (180) | 43 / 82 / 97 | 5.0 / 5.9 / 6.3 s | 0.51 / 0.36 / 0.32 | 0.33 / 0.50 / 0.54 | |
| MAIN S / S+ / P2 (97) | 40 / 85 / 98 | 5.4 / 6.1 / 6.4 s | 0.40 / 0.27 / 0.30 | 0.37 / 0.51 / 0.49 | 0.01 |
| V3 follow-ups S / S+ / S carry (96 = 48 + 48) | 37 / 77 / 37 | 4.9 / 5.9 / 5.4 s | 0.46 / 0.45 / 0.29 | 0.41 / 0.42 / **0.57** | 0 |
Readings (0 LLM, not correctness):
- bannerkept works: the false "Not found in this phone's offline library" line falls from 37/97 MAIN answers (SEFIX-124) to 1/97.
- Longer answers cite more often (more sentences, more [n]), but citing more says nothing about support. PARA135 found the unsupported share rising after paragraph 1. Only the judge can tell whether S+ / P2 are right more often.
- About half of Succinct answers go out with the "passages found don't support this answer" warning. That is the reading gap made visible (CT-1 removed every [n], or the answer cites nothing).
- Carry: 42/48 follow-ups actually carried turn-1 sources, and cited ≥ 1 rises from 0.41 to 0.57. Whether they answer the right subject is the V3-L2 judge question.

## 3. Identity and shas
Tree kiln-local/rs-RC (manifest build/tree.sha256; mini copy identical 0cb31a74…): files changed vs rs-SEFIX = wikiPack.ts 7be8cfe7, answer.ts d1104957, answer.test.ts 08cd31f7. Patches: W78-BINARY 54822a94, W78B-DENSE 07ecafa0, W78C-DENSE e7ae9780, W78-PACKFMT 10192fb0, bannerkept b3cc02eb (2 of 3 test hunks hand-applied, the target test of the third is absent from rs-SEFIX). Kit (13): w78pf boar-simplewiki-en 9c316ff2, w78pf qa-travel-se 6c7221a6, shaped boar-factbook 981f7b4b, others as SEFIX-124 (build/packs.sha256). Personas: Succinct 5e0de1c7 (= UXMATRIX), S+ splus.json 328ecb38, P2 p2.json 3936980a. rs-RC-STICKY = rs-RC + R5-STICKY 6b172fd2 + bench-only adapter carry (f28d5047).

## 4. Judge menu (Haiku 5.5-low; exact first-pass calls; nothing run)
Recommended minimum to close the UI (≈ 410 calls):
1. **Answer length: V2 S vs S+ vs P2, seed 42.** 207 A calls for S + S+ (cap 520), plus ≈ 104 for the P2 units (S units reuse their labels). Gives the page numbers (S: correct-with-source ON, wrong-unwarned OFF) and the S+ ADOPT verdict.
2. **Follow-up: V3-L2, S and S carry.** 48 + 48 A calls. Shows whether carry makes follow-ups answer the right subject, i.e. whether the app's FollowUp rule matters.
Optional, by value:
3. S5 PACKPROOF ON/OFF on ENGINE-RC, seed 42: 323 A (≤ 969). Confirms the 48 % / 26 % thesis numbers with the shaped factbook in the kit.
4. V2 seed 43 S vs S+: 208 A. Stability of the length verdict (seed noise is large on 60 items).
5. S4 MAIN s42 + s43 no-regression: 86 + 72 calls (judge.v1 N 4 both orders on changed answers only).
6. PACKPROOF ON with S+ (180) / P2: only if item 1 favours a longer persona.
7. S10 topics (≤ 88 sentences, S+ ≤ 125); S7 seed 44 (60); V3 seed 43 (48); B-k4comp40 (38, candidate already closed by probes: skip).
Commands: night/judge-ready/JUDGE-READY.md.

## 5. Costs
Haiku 0, Opus 0, paid 0, phone 0. Mini: 25 jobs, 2,855 generations, 18:43 → 23:48 (≈ 5.1 h). MacBook: ≈ 1.5 h of replays (RETBENCH B/C, X2B scoring, V0/V1/V3-L1/S1/S8, carry gate, S3). Agents: 2 (build/0-LLM suites; mini queue prep).

## 6. Not run / limits
- Job 22 (carry with S+) and job 23 (LONGSESSION conversations) of ADDENDUM-4: not built. The prep agent stopped responding after 19:1x, and the coordinator built only the jobs derivable with the existing tooling.
- The engfix route fixes are validated on wt/engfix only, not merged into rs-RC (different lineage): the app engine and the bench engine still differ there.
- rs-RC has no vitest of its own (V0 (d) ran answer.test.ts on a scratch clone).
- Desktop CPU timings only; phone untouched. Dev / public items only (no blind, no v0.4).
- The 0-LLM numbers in §2 are behaviour, not correctness.

## 7. Judge results (2026-10-24 14:0x-14:2x, Addendum 5; Haiku 5.5-low, 596 calls: V2 324, P2 154 new, V3 S 58, V3 carry 60; Opus 0)
V2 UXMATRIX seed 42, 60 items, labels per the UXMATRIX protocol (CWS = correct with source; WU = wrong unwarned; WW = wrong warned):
| persona | ON CWS | ON correct-any | ON WU | ON WW | OFF correct-any | OFF WU | tokens p50 |
|---|---|---|---|---|---|---|---|
| S Succinct | 0.30 | 0.43 | **0.12** | 0.33 | 0.22 | **0.10** | 44 |
| S+ 4-5 sentences | 0.30 | 0.42 | **0.23** | 0.23 | 0.27 | 0.13 | 93 |
| P2 two paragraphs | 0.32 | 0.42 | **0.25** | 0.22 | 0.22 | 0.08 | 118 |
- **S PASS** (CWS ON 0.30 >= 0.28, WU OFF 0.10 <= 0.10): these are the page's numbers.
- **S+ ADOPT rule: S STAYS** (correct-any better 3 / worse 4; WU ON +7 items; WU OFF +2; health item lan-hlt-001 worse). P2 (rule not applied) shows the same shape: same correctness, WU ON doubles.
- Reading: longer answers are not right more often; they carry the warning line less (the "passages found don't support" line 0.60 -> 0.48) while being wrong as often, so twice as many wrong answers reach the user without a warning. Succinct stays the default.
V3 layer 2 (48 F8 follow-ups, persona S, history as the app sends it):
| arm | correct-any | on-referent | WU | WW | honest unknown | turn-1 source kept | warning line |
|---|---|---|---|---|---|---|---|
| ENGINE-RC (no follow-up rule) | 0.458 | 1.00 | 0.042 | 0.354 | 0.146 | 0.083 | 0.75 |
| + subject carry (RS_STICKY=2) | 0.458 | 1.00 | 0.083 | 0.312 | 0.146 | 0.708 | 0.42 |
- The model stays on the subject in both (history in the prompt does that); carry does not make follow-ups more correct (22/48 both), it brings the turn-1 source back (0.08 -> 0.71) and shows fewer warnings, with WU 2 -> 4. Health follow-ups 0.19 correct in both. Reading: follow-up reliability is a reading problem, not a referent problem; carry is a UX gain (sources shown), not an accuracy gain.
