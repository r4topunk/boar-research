# LITEDECLINE: the 1.7B's compact-only declines, ON vs OFF

Criterion: `LITEDECLINE-criterion.md`, sha256 `bbed081d070bb01e…`. I checked it with shasum before any generation and did not edit it. Machine: the Mac mini (M4), llama-server b11010 CPU `-t 4`, run on a free OS-assigned port. The :8094 detector was used but never started or stopped. Qwen3-1.7B Q4_K_M, `--reasoning off`, seed 42. Judge: Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, uncapped. That came to 678 calls with 0 missing: ON 474, OFF 16, OFF5 188. No paid API. No reads of blind/, rnd/veil or bench v0.4.

## TL;DR

**Verdict by the frozen rule: PARTIAL.** Pooled U0 rises +0.014 (+0.005…+0.024): above 0 but under the +0.03 adopt bar. Confident errors do not move (+0.000). The criterion's OFF arm is close to a no-op for two reasons:
1. A fourth compact-only rule that the criterion does not name, `uncited-with-sources-declined-compact`, makes most of the declines: 67 of 94.
2. It also re-declines every item that rule 3 would have released.

The report-only arm OFF5 turns all five compact declines off, so the 1.7B is treated like the 4B. It would meet the same rule's ADOPT bar: U0 +0.170 (+0.141…+0.199) and confident-error rate +2.5 points (−1.3…+6.3). The number of confident errors doubles, though (17 → 34 of 237).

| Arm | Set | n | Q | U0 | Decline rate | CE rate (count / answered) |
|---|---|---|---|---|---|---|
| ON (engine as is, 1.7B compact) | v0.1 | 57 | 0.416 | 0.328 | 0.386 | 0.114 (4 / 35) |
| | self-tests | 180 | 0.393 | 0.298 | 0.400 | 0.120 (13 / 108) |
| | **pooled** | 237 | 0.399 | 0.306 | 0.397 | 0.119 (17 / 143) |
| OFF (criterion: the 3 named rules off) | v0.1 | 57 | 0.438 | 0.383 | 0.246 | 0.116 (5 / 43) |
| | self-tests | 180 | 0.393 | 0.298 | 0.400 | 0.120 (13 / 108) |
| | **pooled** | 237 | 0.405 | 0.319 | 0.363 | 0.119 (18 / 151) |
| OFF5 (report only: all 5 compact declines off) | v0.1 | 57 | 0.465 | 0.465 | 0.000 | 0.175 (10 / 57) |
| | self-tests | 180 | 0.479 | 0.479 | 0.000 | 0.133 (24 / 180) |
| | **pooled** | 237 | 0.475 | 0.475 | 0.000 | 0.143 (34 / 237) |

Paired deltas (item bootstrap B 2000, seed 11, 95 % CI):

| Contrast | Set | Answers changed | ΔQ | ΔU0 | ΔDecline rate | ΔCE rate |
|---|---|---|---|---|---|---|
| **OFF − ON** | v0.1 | 8 | +0.022 (+0.005…+0.042) | +0.055 (+0.021…+0.094) | −0.140 (−0.228…−0.053) | +0.002 (−0.040…+0.058) |
| | self-tests | 0 | 0 | 0 | 0 | 0 |
| | **pooled** | 8 | **+0.005 (+0.001…+0.011)** | **+0.014 (+0.005…+0.024)** | −0.034 (−0.059…−0.013) | **+0.000 (−0.009…+0.016)** |
| OFF5 − ON (report only) | v0.1 | 22 | +0.049 (+0.024…+0.078) | +0.137 (+0.090…+0.187) | −0.386 (−0.509…−0.263) | +0.061 (−0.018…+0.150) |
| | self-tests | 72 | +0.085 (+0.065…+0.106) | +0.180 (+0.144…+0.216) | −0.400 (−0.472…−0.322) | +0.013 (−0.029…+0.055) |
| | pooled | 94 | +0.076 (+0.060…+0.093) | +0.170 (+0.141…+0.199) | −0.397 (−0.460…−0.333) | +0.025 (−0.013…+0.063) |

How to read it:
- The 1.7B as the product ships it declines **40 % of dev questions**: 94 / 237.
- On the 94 items it declines, the answers it would have given average correctness 2.4–2.9 / 5. 17 of the 94 are confident errors (18 %), against 12 % on the questions it answers today. Unlocking all 94 buys +0.076 Q and +0.170 U0. In exchange, 17 more confidently wrong answers reach the user.
- The phone's Grima case reproduces on the desktop (vit-hum-004):
  - ON declines it through rule 3 (all citations removed).
  - The criterion's OFF still declines it, because rule 4 catches it.
  - OFF5 answers "Gríma kills Saruman in the Battle of the Five Armies…", a confident error with correctness 1.0. the post author's over-refusal complaint and the 4B's confident-wrong answer are the same trade.

## Per rule (fires counted on ON, pooled 237)

| Rule (reason code) | Fires (v0.1 / st) | OFF: what happens there | OFF5: correctness on the released items | OFF5 confident errors | Mean item score s, ON → OFF5 |
|---|---|---|---|---|---|
| 1 `declined-compact` (no source, from memory) | 8 (8 / 0) | All 8 answer, with the "not from an offline source" preface; mean correctness 2.88; 1 CE; histogram 1:1, 2:2, 3:2, 4:3 | 2.75 (same items) | 1 / 8 | 1.10 → 1.88 |
| 2 `false-claim-declined-compact` | 0 | never fires | n/a | n/a | n/a |
| 3 `all-citations-removed-declined-compact` | 19 (6 / 13) | **0 / 19 change.** All 19 are declined again by `uncited-with-sources-declined-compact`, with the same message text | 2.37 | **6 / 19** | 1.07 → 1.75 |
| 4 `uncited-with-sources-declined-compact` (not in the criterion) | 67 (8 / 59) | unchanged (still on) | 2.93; histogram 1:7, 2:16, 3:14, 4:28, 5:2 | 10 / 67 | 1.07 → 2.11 |
| 5 `uncited-declined-compact` (not in the criterion) | 0 | never fires | n/a | n/a | n/a |

What each rule decides:
- **Rule 1:** a small, clean gain. +0.055 U0 on v0.1 with CE flat. These are no-source questions such as Mozi or "astronauts before 1970". The 1.7B answers them from memory behind the preface, at about the same error rate as its other answers. A per-rule decision to switch rule 1 off is supported on its own: that is the OFF arm.
- **Rule 2:** inert on these sets. It needs a false quantum-resistance sentence. Keep it; it costs nothing.
- **Rule 3:** cannot be judged alone. Rule 4 implies it: the same conditions, without "had citations". Releasing rule 3 alone is a no-op. Released together with rule 4 (OFF5), it is the worst rule to release: 32 % of its answers are confident errors (6 / 19), and that is where Grima sits.
- **Rule 4:** the biggest lever and the biggest decliner. 59 of the 72 self-test declines come from it. Released, its answers are mostly usable (30 of 67 score correctness ≥ 4), with 15 % confident errors (10 / 67).

## Examples (what OFF / OFF5 answered instead of declining; judge correctness = mean of both orders)

Rule 1, `declined-compact`. Criterion OFF arm:
- lan-hlt-001 "Can a raw vegan diet be healthy long term?" → "[preface] A raw vegan diet can be healthy long term if it includes a variety of nutrient-dense foods, but it requires careful planning…" Correctness **3.0**.
- lan-ref-003 "Did astronauts walk on the Moon before 1970?" → "[preface] Yes, astronauts did walk on the Moon before 1970. The first Moon landing occurred in 1969." Correctness **3.5**.
- vit-hum-002 "How did Mozi's idea of universal love differ from the Confucian view, and how did Mencius attack it?" → "[preface] Mozi's idea of universal love emphasized equality… Mencius criticized Mozi's universal love as impractical…" Correctness **2.5**.

Rule 3, `all-citations-removed-declined-compact`. OFF still declines these, so the text is from OFF5:
- lan-rsn-001 "How long is the Great Wall of China, and can you really see it from the Moon?" → "…spans over 21,000 kilometers… while it is visible from space, it is not visible from the Moon due to the Earth's atmosphere…" Correctness **2.5**.
- st-qa-bitcoin-se-010 "What usually explains those days when Bitcoin transactions paid absurdly large fees?" → "High transaction fees… occur when there is significant demand… congestion and higher fees due to limited block space." Correctness **2.0**.
- st-qa-outdoors-se-015 "Give me ways to spot boggy, dangerous ground while hiking after heavy rain." → "…Look for signs like deep puddles, soft ground that sinks underfoot, and vegetation that appears wet or discolored…" Correctness **4.0**.
- Also vit-hum-004 (Grima) → "Gríma kills Saruman in the Battle of the Five Armies…" Correctness **1.0** (confident error).

Rule 4, `uncited-with-sources-declined-compact`. Not a criterion rule; from OFF5:
- lan-cmp-003 "Which countries are bigger than India by area?" → "China, Russia, Canada, and the United States are all larger…" Correctness **4.0**. Brazil and Australia are missing.
- st-boar-simplewiki-en-020 "Compare Hyundai Motor Company and the Mercedes-Benz S-Class…" → "Hyundai Motor Company began in 1967, while the Mercedes-Benz S-Class started in 1972…" Correctness **4.0**.
- st-qa-health-se-011 "What criteria do doctors use to be sure a patient is really dead…" → "…absence of cardiac electrical activity, no breathing, and no neurological activity…" Correctness **3.5**.

The full rows are in `aggregates/examples.jsonl`. The 17 OFF5 confident errors include Curaçao's capital "named after Willem de Kooning", d/acc as "a diagnostic and accident reporting system", and Chiang Mai to Pai "50 km east".

## Patch and identity proof

`tools/litedecline.patch` (sha256 `1455beca…`, generated by `tools/mk_patch.py`) touches 2 files:
- **`src/routing/answer.ts`** (`2cd3d656…`, from `289607fd…` = the cut 7 + X2b kiln tree):
  - New optional `AnswerDeps.compactDeclinesOff?: "three" | "all"`.
  - Any value adds `&& !deps.compactDeclinesOff` to the three named rules (lines 1293, 1542, 1580).
  - `"all"` also adds `&& deps.compactDeclinesOff !== "all"` to rules 4 and 5 (1598, 1618).
  - Unset, the behaviour is byte-identical. The engine reads no env.
- **`be/adapter-litedecline.ts`** (`d53c1487…`, from `adapter-lite5.ts` `5785ffc4…`). Two changes:
  1. The 1.7B catalog entry drops `answerTier: "default"`. It becomes untiered, as in the product: 1.11 GB ≤ the 1.6e9-byte cap, so `isCompactModel` is true.
  2. `LITEDECLINE_OFF=3` passes `"three"` and `LITEDECLINE_OFF=5` passes `"all"`.

Identity proof, over the full runs rather than a 3-item replay:
- **OFF:** every item where none of the three named rules fired in ON (210 / 210) has a byte-identical answer and reason-code list.
- **OFF5:** every item where none of the five fired (143 / 143) is byte-identical too.
- The only items that change are the ones whose rule the arm turns off. Generation is deterministic run to run on the mini (seed 42, one slot).

## Deviations

1. **Rules 4–5 and the report-only OFF5 arm.** The engine has five compact-only declines; the criterion names three. Rule 4 (`uncited-with-sources-declined-compact`) has a superset condition of rule 3, so the criterion's OFF cannot release a rule-3 item.
   - The verdict uses the criterion's OFF exactly as frozen.
   - OFF5 is reported only. It matches the criterion's own wording: "treated like the 4B (answer with the uncited / weak-source warning…)". Its same-rule outcome (ADOPT) is not a verdict.
2. **ON setup.** Every earlier desktop lite run (LITE5, LITE7, LITE17's engine baselines, LITESAFETY) gave the 1.7B `answerTier: "default"`, so `isCompactModel` was false and **none of these declines ever fired there**. Those numbers correspond to OFF5, not to the product. Here ON uses the untiered entry, which is how the product classifies the 1.7B (LITEPROFILE noted "an untiered 1.7B counts as compact").
3. **Engine settings.**
   - Self-tests: the LITE5-180 requests, so the X2b settings `packHeadPass a2` / `packDense2 append-budget` (the lite line's pack configuration, as in PACKREAD/RELGATE), with each pack installed on top of the claim kit.
   - v0.1: the cut 7 claim-kit requests (crypto + Wikivoyage, X2b off, inert on the claim kit per LITESAFETY), modelId switched to the 1.7B, no places files.
   - Tree: a copy of the mini's `be-0cfd4a77-cut7-headpass-x2` (cut 7 + X2b) plus the patch.
4. **v0.1 n = 57, not 60.** The public file has 60 items, and 3 of them are venue-list items (food-001/002/006) with no rubric reference. They were generated but are not judged, following every v0.1 L1 run (`data/v01-57.ids`).
5. **Judging identical answers.** ON was judged in full. OFF and OFF5 were judged only where the answer text differs from ON (8 and 94 items); identical answers reuse ON's rows. Their delta is therefore exactly 0, not judge noise (as in LITE17 deviation 5).
6. **Preflight.** It ran without `--criterion`: the criterion says "uncapped" and has no Budget `calls_cap` line, which preflight refused. The guards and set status (dev) were still checked.
7. **Bootstrap.** The CE-rate delta is bootstrapped on the paired item resample. Its denominator (answered items) differs per arm by construction.
8. **Cross-machine check.** The mini OFF5 self-test answers are byte-identical to the MacBook LITE5-180 ON answers on 37 / 180, so there is host-level drift. Q is similar: 0.479 vs LITE5-180's 1.7B X2b 0.486 (Haiku).

## Next (options for the coordinator)

- A per-rule decision is now possible:
  - Rule 1 off: +0.055 U0 on v0.1, CE flat; the criterion's OFF.
  - Rule 4 off: the big lever, +U0 with CE 15 % on released items.
  - Rules 3 and 4 off together: releases the Grima-type cases at 32 % CE.
- A cheaper middle ground would release rule 4 but keep a decline when CT-1 removed citations, i.e. keep rule 3 effective with rule 4 off. That needs its own frozen criterion.
- UNKNOWN:
  - Phone-side numbers. These are desktop, one seed.
  - Haiku vs Opus on the released answers. The CE threshold of ≤ 1.5 sits at the judge's floor region.
  - Whether the WARN tier's banner, `uncited-warning`, changes how a user reads the released answers.

## Files

- `tools/`: mk_patch.py, litedecline.patch(+.sha256), mkreq.py, run_ld.sh (mini runner), judge.sh, changed_ids.py, agg.py, examples.py.
- `runs/req/`: 30 request files. `runs/logs/`: generation and judge logs, statuses.
- `traces/`: ld-{on,off,off5}-{v01,st-<pack>}-s42.traces.jsonl.
- `judgments/`: per run, plus shard dirs.
- `aggregates/`: litedecline.json, agg-stdout.txt, examples.jsonl. `data/v01-57.ids`.

Mini tree: `<runner>/kiln/be-0cfd4a77-cut7-litedecline`; work dir `<runner>/kiln/litedecline`. No llama-server is left running other than :8094. Mini free space is 34 GiB.
