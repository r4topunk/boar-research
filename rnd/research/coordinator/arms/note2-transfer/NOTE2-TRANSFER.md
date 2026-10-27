# NOTE2-TRANSFER (2026-10-21): KILLED on the 1.7B A-union pair (+26 pp). The kit pairs transfer (1.7B +7 pp, Gemma +2 pp). The phone bench build has no warning line, so the literal rule hides 12 pp less on Gemma

Criterion NOTE2-TRANSFER-criterion.md (sha in .sha256, rnd b6b1f787, committed before any count). Script tools/note2_apply.py -> aggregates/note2-transfer.json. 0 Opus, 0 paid, 0 generation, 0 phone minutes. **Haiku 5.5-low: 60 calls** (30 units, both orders, N 4, cap 60, 0 failures; judge/*.judgments.jsonl). Dev ids only.
Phone rows: handoff/pixel8-2026-10-20/bench/results/{q17b73-a,aunion73-a,gemma73-a,gemmaa73-a,q4ba73-a}/rows.jsonl (tree 0ca54d87, compactDeclinesOff unset).
Desktop traces (LITEPACKS frame, s42, mini): 1.7B kit arms/lp-screens/control/traces/lpctl-K0-main-s42 (MacBook replication arms/litepacks/traces/lp-K0-v01-s42); 1.7B A-union arms/coverage-matrix/q17/traces/q17-KA-main-97-s42; Gemma arms/gemma4-e2b/stage2/traces/gemma4-e2b-eng-K0-main-s42; 4B arms/gemma4-e2b-vs4b/traces/gemma4-e2b-vs4b-K0-main-s42.
Shared ids: the 57 v0.1 dev ids. 42 of them reach the LLM on every tier and every host. The 15 deterministic ids are the same everywhere.

## Rule applied (NOTE-2 as written = RU / REVEAL-CENSUS hidden set)
A row is hidden when it is LLM-routed AND it is (a decline OR it starts with the warning line OR it has outputTokens > 0 with no kept source).
- **P1** applies this to the phone text as it is.
- **P2** also counts the engine's compact-release decisions on non-compact rows: no-source-memory, OR a kept source with no "[n]" citation, non-health.

Why P2 is needed: the phone runs have the line off.
- The 1.7B declines instead of warning (25 of its 29 hidden rows are declines with no text).
- Gemma and the 4B run as non-compact models and get the cut-7 preface or banner.

On the desktop, the P2 predicate marks exactly the warned rows (75/75, 73/73, 73/73 agreement).

## Per tier (57 shared ids; hide rate = hidden / 42 LLM-routed rows; per 100 = per 100 questions)
| tier | hide P2 phone / desktop (d pp) | hide P1 phone | hidden /100 phone | LLM s hidden /100 phone (per hidden answer; desktop host) | correct / CE hidden /100 phone (labelled / revealable) | desktop correct / CE /100 | deciding |
|---|---|---|---|---|---|---|---|
| 1.7B kit | **69.0 / 61.9 (+7.1)**; MacBook 66.7 | 69.0 | 50.9 | 301 s (8.2 s; desktop 2.4 s) | 1.8 / 0.0 (4/4); 25 declines with no text, desktop proxy 7.0 / 10.5 | 10.5 / 10.5 (Opus 26/26) | yes, holds |
| 1.7B A-union | **71.4 / 45.2 (+26.2)** | 71.4 | 52.6 | 342 s (8.9 s; 4.3 s) | 1.8 / 1.8 (4/4); 26 with no text, proxy 0 / 19.3 | 1.8 / 12.3 | **yes, KILL** |
| Gemma kit | **50.0 / 47.6 (+2.4)** | **35.7 (-11.9)** | 36.8 | 432 s (11.7 s; 3.4 s) | 10.5 / 7.0 (18/18, Haiku) | 8.8 / 7.0 (Opus) | yes, holds |
| Gemma A-union | 42.9 / 47.6 (-4.7)* | 31.0 | 31.6 | 314 s (9.9 s) | 1.8 / 8.8 (17/17, Haiku, 16 new) | 8.8 / 7.0* | no |
| 4B A-union (counterfactual: NOTE-2 shows 4B answers) | 59.5 / 61.9 (-2.4)* | 28.6 | 43.9 | 983 s (22.4 s; 6.5 s) | est. 12.1 / 8.6 (12 of 25 labelled, 9 sampled of the 22 unlabelled) | 14.0 / 7.0* | no |

\*The desktop row is K0 (kit): no desktop Gemma or 4B A-union run exists on MAIN, so these pairs are not pack-matched.
- Labels: Opus judge.v1 wherever a unit (id | sha256 text) exists, else Haiku 5.5-low.
- Correct-hidden on the phone is a lower bound for the 1.7B. Its hidden answers are compact declines, so there is no text to reveal.

## Verdict (frozen rule)
**KILLED: the 1.7B A-union pair differs by +26.2 pp.**
- The phone hides 30/42 answers; the desktop KA cell hides 19/42.
- 12 ids are hidden only on the phone. Examples: vit-cry-002/006/007/008/010, lan-exp-003/007, vit-sci-002. All of them are compact declines (uncited or all-citations-removed).
- Cause: the desktop KA cell ran LITEPACKS retrieval (pack head pass + dense append, v3proto files). The phone runs neither, so the desktop KA kept and cited sources the phone did not.
- The kit pairs transfer: 1.7B +7.1 pp (MacBook +2.3 pp), Gemma +2.4 pp. The A-union failure is a frame mismatch, not a hardware one. By the frozen rule, NOTE-2 still quotes phone numbers per tier.

**P1 config clause fires on Gemma kit (-11.9 pp).**
- The bench build's default has no warning line. Applied literally, the rule then hides about 1 Gemma answer in 3, not 1 in 2.
- On the 1.7B, the warned answers are declined outright, so there is nothing behind a show-anyway button.

Prediction check:
- Hide rates: 1.7B 69-71 % (predicted 35-50 %), Gemma 43-50 % (predicted 20-35 %). Both are above the predicted ranges. NOTE-2's "about two thirds hidden" matches the 1.7B on the phone; for Gemma it is closer to half.
- Generation hidden per answer: 1.7B 8-9 s on the Pixel (predicted 3-5 s), which is about 5.0-5.7 min per 100 questions (Gemma 5.2-7.2 min).
- Correct-hidden near 19 per 100 for the 1.7B: not testable on the phone (no text).

## Proposed NOTE-2 diff (not applied; handoff/notes-2026-10-22/NOTE-2-refuse-by-default-show-anyway.md)
```
- - Cost: refuse-by-default hides about two thirds of answers on every model and roughly halves the score users get from what is shown.
+ - Cost on a Pixel 8a (bench engine, 57 dev questions, one run): refuse-by-default hides 69-71 % of the 1.7B's model answers
+   (about 51 per 100 questions; about 8-9 s of generation each, about 5-6 min per 100 questions) and 43-50 % of Gemma's
+   (32-37 per 100; about 10-12 s each). With the six persona packs (A-union) the 1.7B hides 71 % on the phone vs 45 % in our desktop replay:
+   quote the phone figure.
+ - The rule needs the warning line in the build: the answer behind "Show the model's answer" is the one released under the line.
+   A build that still declines the 1.7B's unsupported answers (compact declines on) has no text to reveal, and on Gemma
+   without the line the rule hides about 1 in 3 instead of 1 in 2.
- - All numbers are desktop proxies of the phone path, dev sets, one seed; the phone 1.7B line was judged on 26 questions only.
+ - Hide rates were replayed on Pixel 8a bench rows (NOTE2-TRANSFER): the kit numbers transfer (1.7B +7 pp, Gemma +2 pp vs desktop);
+   reveal quality (correct vs confidently wrong) is still desktop (Opus) except Gemma's phone rows (Haiku: 10.5 correct / 7.0 CE hidden per 100).
```

## Device day 10-22 (RC rows, ready to run)
```
cd <workspace>/rnd/research/coordinator/arms/note2-transfer/tools
python3 -I note2_apply.py --rc <workspace>/handoff/pixel8-2026-10-20/bench/results/rc-speed9-17b \
  <workspace>/handoff/pixel8-2026-10-20/bench/results/rc-speed9-4b <workspace>/handoff/pixel8-2026-10-20/bench/results/rc-layer10-4b \
  <workspace>/handoff/pixel8-2026-10-20/bench/results/rc-t1a-gemma <workspace>/handoff/pixel8-2026-10-20/bench/results/rc-t1b-gemma
```
- Output: one aggregates/rc-<dir>.json per run, with line presence on the ids where the bench engine (aunion73-a / q4ba73-a / gemmaa73-a) would warn under P2, P1 hide rate, hidden generation seconds and personas.
- The premise clause (line on <= 3/10 bench-warn ids) and the "detailed" not-like-for-like flag are computed there.
- The bench reference is picked from the dir name (17b, 4b or gemma); --ref <run> overrides it. Rows are read from rows.jsonl or eval-out/**/*.jsonl.

## Limits
- One phone run per tier, unseeded.
- 42 LLM-routed rows per tier: one row is 2.4 pp, so the 10 pp kill line is about 4 rows.
- Mixed judges: Opus where it exists, else Haiku-low, which under-calls correct on warned text (HAIKU-CAL).
- Gemma A-union and 4B have no pack-matched desktop pair.
- The 4B correct/CE is a 9-of-22 sample expansion.
- The health tag is the engine's route code.
