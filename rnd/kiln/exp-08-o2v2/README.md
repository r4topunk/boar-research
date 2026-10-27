# exp-08: O2 v2, measured as a deterministic paired counterfactual

Date: 2026-10-01 · Author: Kiln (R&D) · Request: coordinator (after Veil's NÃO VALIDADA, `rnd/veil/o2-ab-labels/README.md`) · Rule 0: local branch only, no PR.

## TL;DR

- **v2c passes every criterion in exp-03 §5 on this set. v2a, the literal proposal, fails it.**
  - **But v2c's fresh-item gate is in-sample.** v2 was designed from the two false refusals on these same 30 fresh items. **Before promoting it, it needs ≥ 20 new fresh in-scope items** (task below).
- **The measurement is now noise-free.**
  - Greedy decoding on the mini's real `createAnswerer` gives **82/82 identical answers** across two OFF runs.
  - In every O2 arm, **0 questions where O2 did not fire differ from OFF**. Each arm's effect is therefore exactly its refusals, with no sampling noise. The iPhone A/B had 22/47 label changes from noise (Veil).
- **v1 reproduces the device verdict.** Same 2 false refusals on the fresh items (`vit-o2b-002` Brazil/Indonesia, `vit-o2b-006` PoS/Ethereum), so the fresh gate fails at 2/6.
  - On the desktop, v1's attributable Δcw is −7.7 pp vs −1.9 pp on the device. The greedy 1.5B answers four of these cw, where the device's sampled runs had mostly declined.

| Arm | Test-set A1 / A2 / A3 (≥6/7, 7/7, 4/4) | Hits device 52 / fresh 30 | A4 Δpass device 52 (≥ −5 pp) | A5 Δcw device 52 (≤ −5 pp) | Fresh: new false refusals / hits (≤ 1/10) | §5 |
|---|---|---|---|---|---|---|
| v1 (A/B build) | 7/7 · 7/7 · 4/4 ✅ | 9 / 6 | −1.9 pp ✅ | −7.7 pp ✅ | **2/6** ❌ | FAIL |
| v2a = concept title + **every** one-sided comparative kept | **5/7** ❌ · 7/7 · 4/4 | 6 / 1 | −1.9 pp ✅ | **−3.8 pp** ❌ | 0/1 ✅ | FAIL |
| **v2c** = concept title + one-sided comparative kept **only with no third-entity passage** | 6/7 ✅ (at the limit) · 7/7 · 4/4 | 8 / 3 | −1.9 pp ✅ | **−7.7 pp** ✅ | 0/3 ✅ (in-sample) | **PASS** |

## 0. FROZEN: v2c (coordinator, 2026-10-01, before any new item existed)

- **Manifest:** `FROZEN-v2c.sha256`, itself sha256 `3e5f04d334f63b5fa8577a5c5f0dcb067cf4bc59eb9874736967bf075278b1ea`.

| Piece | sha256 |
|---|---|
| Rule: `o2v2c.patch` (byte-identical to `o2v2.patch`; v2c = `--o2 c`) | `2b79bbaa3be811dad695320e88bdf365cc002dbf6ca56c5672f952643c8db407` |
| Patched `src/routing/o2WeakSupport.ts` (mini tree = local apply) | `225bb411bfc90b123b3be01b961888475d877574c5f83a106a6ca3011b02ed0e` |
| Execution config `run-v2c-fresh.sh` (off, off repeat, v2c) | `c539d0660b0e2a8c5a95d79341b989fa778b253bfaa32030a3cd3f60aa1a6ef4` |
| Runner `answerer.ts` | `4f740aac5f51d9e0a2b534878e6ab225403fdf6b5f8f00f84fc5c721804652ae` |
| Analysis `analyze_fresh.py` (§5 fresh gate, as is) | `90d972b1a84fb551b6abef8c482dc082df581f028e447e6bda3039ee838622ed` |
| App base | boar-app `611a4b92295047cf2ca3a1f1dab3d9f65c4e5756` |
| Model | Qwen2.5-1.5B-Instruct-Q4_K_M `1adf0b11…` |
| Kit A | crypto `ae9fbd2c…`, wikivoyage `ff8595e3…`, wiki-vital5 `d3b87d56…` |

- **Fixed settings:** iPhone 13 profile (4 GB, ios), quick mode, greedy `--temp 0`, seed 42.
- **Labels:** hand labels in `hand-labels-fresh-<tag>.json`, written before `analyze_fresh.py` runs; Jev v2 as second rater.
- **Verdict:** §5 fresh gate as is (≤ 1 new false refusal per 10 hits).
- **No change to the rule** after this point. If v2c fails on the new items, the verdict is FAIL; no v2d this round.

## 1. What changed (`o2v2.patch`, against boar-app `611a4b92` = `feat/o2-compact-offsubject` + eval arm)

`src/routing/o2WeakSupport.ts` only (+40 lines). The variant is selected by `EXPO_PUBLIC_O2_V2` (`""` = v1 unchanged, `a`, `c`).

| Rule | What it does | Fixes |
|---|---|---|
| **concept title** (v2a, v2c) | Single-subject mode ("any"). A passage title segment (split at `vs`/`and`/punctuation) with ≥ 2 content words, which the question names as written (normalized, plural-stemmed, contiguous), counts as coverage | `vit-o2b-006`: "When did Ethereum switch … to proof of stake?" + *Proof-of-stake vs proof-of-work* |
| **one-side** (v2a) | Comparative with ≥ 1 side covered → keep | `vit-o2b-002` (Brazil passages). But it also keeps the distractor cases O2 exists for: Fukuoka for "Japan vs Nigeria", *Germany + Pacific War* for "Japan vs Germany density" |
| **one-side-clean** (v2c) | Same, only when **every** passage is about a covered side. A passage about a third entity (Fukuoka, *Altitude sickness*, *Pacific War*) is the distractor that makes the 1.5B conflate | `vit-o2b-002` (Brazil + *Northeast (Brazil)*, all about Brazil) |

Why v2a fails the gates, measured on Lantern's 32 fixtures (`testset_gates.mts` → `testset-gates.json`):
- **v2a** keeps the must-refuse cases P2-fa-004 (*Wikivoyage: Japan* only) and P3-fa-004 (Fukuoka + Nigeria) → A1 5/7.
- **v2c** loses only P2-fa-004 (all passages about Japan) → A1 6/7.
- A2 and A3 are unchanged for both (a v2 rule can only turn refusals into keeps).

## 2. Method

- **Harness:** exp-06's real `createAnswerer` on the Mac mini.
  - Tree `<runner>/kiln/app-611a4b92` = `611a4b92` + `o2v2.patch`.
  - Profile: iPhone 13 simulated (`--ram-gb 4 --platform ios`), Qwen2.5-1.5B Q4_K_M.
  - **Kit A**, as in Plumb's D10 A/B: `boar-crypto` + `boar-wikivoyage-en` + `wiki-vital5` (pinned `d3b87d56…`, read in place).
  - Quick mode. **Greedy** (`--temp 0`, new runner flag), seed 42, CPU 4 threads.
- **Questions:** the 82 of the A/B (`questions.o2-ab82.jsonl`, copied from `wt/eval-vitalik/eval/dataset/questions.o2-ab.jsonl`), i.e. Veil's 30 fresh + 52 device.
  - Lantern's 32 test-set cases are fixtures (question + prompt titles), so they run as unit gates on the pure function, as in the spec.
- **Arms:** `off`, `off` again, `v1`, `v2a`, `v2c` (`run-arms.sh`; `--o2 off|v1|a|c` sets `deps.o2Compact` and the variant). 5 × 82 answers in 22 min.
- **Labels:** only the OFF answers of the questions some arm fires on matter (13 questions), because each arm changes nothing else.
  - **Hand labels** (`hand-labels.json`, with reasons) against Veil's references (`rnd/veil/o2-ab-labels/work/refs.all.jsonl`), using Veil's 4 classes.
  - **Jev v2** as a second rater: it agrees on 7/8 of the hand labels it saw, the exception being `vit-fa-004`, where Jev says pass on an answer that states "Japan's population is larger" (false).
  - Spend: one call of 13 items, budget capped at [usage detail removed].
  - Already-declined OFF answers count as `refused`.

## 3. Per question (OFF answer of every fired question)

Full table: `results.md`. 🛑 = O2 fires in that arm.

| id | Set | OFF label | v1 | v2a | v2c | OFF passages |
|---|---|---|---|---|---|---|
| vit-fa-004 Japan vs Nigeria | device | cw | 🛑 | · | 🛑 | Fukuoka; Nigeria; NC Nigeria |
| vit-fa-006 blue whale vs dinosaur | device | cw | 🛑 | 🛑 | 🛑 | Blue whale; Baja Whale Trail; Baleen whale |
| vit-fa-013 tallest animal | device | cw | 🛑 | 🛑 | 🛑 | Moose; Developmental records |
| vit-sci-002 density Japan vs Germany | device | cw | 🛑 | · | 🛑 | Germany; Pacific War |
| vit-fa-014 countries above Japan | device | fail | 🛑 | 🛑 | 🛑 | Japan; Economy of Japan |
| vit-fa-022 elephant vs white rhino | device | **pass** (slip) | 🛑 | 🛑 | 🛑 | Garamba NP; Geraille NP |
| vit-o2b-002 Indonesia vs Brazil | fresh | **pass** (slip: "most populous in the world") | 🛑 | · | · | Brazil; Northeast (Brazil) |
| vit-o2b-006 Ethereum PoS | fresh | **pass** | 🛑 | · | · | Proof-of-stake vs proof-of-work; Ethash; FAQ |
| fa-021, fa-023, trv-004, o2b-007, o2b-015, o2b-026, o2b-028 | | refused already | mixed | | | |

- `vit-fa-022` is the one pass answer every variant refuses (−1.9 pp). Its passages are two national parks, and Lantern's test set files it as `neutral_right_unsupported` (expected refuse).
- **Strict-panel sensitivity:** if the "slips" count as cw, as Veil's panel did, `vit-fa-022` becomes cw. Then v2c is Δpass 0.0, Δcw −9.6 pp, still PASS.

**Time saved:** an O2 decline takes 0.1–0.16 s instead of generating. On the desktop that saves 3.4 s per fired question (median), ~4× more on the iPhone.

## Decisions / Options / Tasks

**Decisions (Kiln):**
- **v2a is out.** It fails A1 (5/7) and A5 (−3.8 pp): exempting every one-sided comparative also removes the distractor refusals O2 is for.
- **v2c is the candidate.** It passes §5 on this set, but **it is not validated** until it passes on items it wasn't designed on.

**Options:**
- O-1 (recommended): validate v2c on **≥ 20 new fresh in-scope items** (Veil or Lantern). Run them in this same deterministic desktop harness: 2 arms, about 10 min, labels only on the fired rows. Use the iPhone only for a final smoke check, since the device's sampling noise can't resolve a ~2 pp effect (Veil, Plumb Q4: 13/60 decline flips test-retest).
- O-2: A1 sits at the limit (6/7). Any further keep rule needs a new must-refuse fixture to stay honest.
- O-3: v1's desktop Δcw (−7.7 pp) vs the device's (−1.9 pp) says the greedy 1.5B is more often confidently wrong on these questions than the device's sampled runs. Desktop greedy is a stricter test of O2's benefit, not a device estimate.

**Tasks:**
- [ ] Coordinator: request ≥ 20 new fresh in-scope items (numeric / superlative / comparative / list, including comparatives with one-sided passages and concept titles). Veil wrote the first 30.
- [ ] Kiln: run v2c off/on on them (deterministic) and report §5 out of sample.

## UNKNOWN

- Out-of-sample behaviour of both v2 rules (the main gap; see the task).
- The concept-title rule fired on 1 question in this set. Its false-keep rate (a concept title that names the question's predicate but not its subject) is unmeasured.
- Device behaviour: the iPhone runs llama.rn with sampling, so its OFF answers differ (cw vs refused). The rule itself is a pure function of (question, prompt passages), and those match the device 52/52 (exp-06).
- The labels are mine, with Jev as a second rater (agreement 7/8), not a blind panel. Only 13 rows matter, and all are listed with reasons.

**Metric:** v2c: A1 6/7, A4 −1.9 pp, A5 −7.7 pp, fresh false refusals 0/3 (in-sample). v1 on the same deterministic setup: 2/6 false refusals (fails, as on the iPhone).
**Next step:** ≥ 20 new fresh items → v2c out-of-sample run (about 10 min on the mini).

## 6. Out-of-sample run: reading declared BEFORE the results (2026-10-01 05:24 -03)

- **Items:** `rnd/veil/o2v2c-fresh.jsonl` (sha256 `4990244e…`), 22 items: (a) 8 one-sided comparatives, (b) 7 concept titles, (c) 7 look-alike controls with `refuse_ok=true`.
- **Frozen manifest:** re-checked OK on both machines before the run.
- **Headline:** `analyze_fresh.py` as frozen. A false refusal is a fired item whose OFF answer is labelled `pass`, whatever its type.
- **Second reading (reported alongside, does not replace the headline):** on a (c) item, a refusal where the passages come from the look-alike is not a false refusal, per Veil's item definition (`refuse_ok`). If the two readings disagree on the verdict, I report both, and the coordinator decides. On (a)/(b), any refusal of a `pass` answer is a false refusal.

### 6.1 Result (frozen procedure, then diagnostics)

**Frozen output** (`results-fresh-o2c.md`, `analyze_fresh.py` unchanged):
- **Validity:** off vs off-rep 22/22 identical, 0 counterfactual breaks, so the run is VALID.
- **Hits:** v2c fired on **1** item, `vit-o2c-007` (Christ the Redeemer vs Statue of Liberty). Its OFF answer was already a decline (`refused`), so there are no hand labels to write.
- **Fresh gate: 0/1 → formally PASS.** Δpass 0.0 pp, Δcw 0.0 pp. The second reading (§6) gives the same result: no (c) item fired.

**Why this is not a validation (diagnostics, run after the frozen output, rule untouched):**
1. **Scope:** `o2Kind` puts **16/22** items in scope (`scope-fresh-o2c.jsonl`). §5 asks for ≥ 20 fresh in-scope items, so the gate's precondition is not met. Out of scope:
   - `vit-o2c-003` "Is Mont Blanc higher than…": "higher" is not in the comparative list;
   - `006`, `008`, `014`, `020`, `022`.
2. **No discriminating item:** a v1 arm on the same items (`runs/fresh-o2c-v1-diag.jsonl`) fires on the same single item. **v1 and v2c decide identically on 22/22.** Neither v2 rule (concept title, one-side-clean) was exercised.
   - Veil's coverage guesses (`o2_hypothesis`) were mostly wrong: the kit has **both** sides for Victoria/Malawi, Thames/Severn, Manaus/Curitiba and Mariana/Puerto Rico.
   - The concept-title items either have the subject's own article or are out of scope.
3. **A gap outside the rule, seen on the controls:** the **instant (extractive) tier answers before O2's hook**, with look-alike or off-topic passages:
   - `vit-o2c-015` "population of the Netherlands" → *South Holland* "…with a population of over 3." (`instant:final`);
   - `vit-o2c-005` Tietê×Paraná → *Paraná (state)* "The state is home to 5.";
   - `vit-o2c-013` sunlight travel time → *Earthlight*.

   These are exactly the failures O2 targets, but O2 never sees them, by design: the hook comes after the extractive return.

**Verdict as I read it: INCONCLUSIVE, not validated and not failed.** The frozen gate says 0/1 PASS, but with 16 in-scope items and 0 items where v2c differs from v1, it cannot test v2c. The coordinator decides; the rule is unchanged.

## 7. Out-of-sample round 2: reading declared BEFORE the results (2026-10-01 05:37 -03)

- **Items:** `rnd/veil/o2v2c-fresh2.jsonl` (sha256 `9c6f9276…`), 23 items, chosen by Veil with `rnd/kiln/tools/kit_coverage.py`: (a) 8 one-sided comparatives, (b) 8 concept titles, (c) 7 look-alike controls with `refuse_ok`.
- **Frozen manifest:** re-checked on both machines.
- **Headline:** `run-v2c-fresh.sh` + `analyze_fresh.py` as frozen. A false refusal is a fired item whose OFF answer is `pass`. The second reading for (c) is the one declared in §6.
- **Applicability, declared now (it was a post-hoc diagnostic in round 1):**
  - The gate counts as a test of v2c only if ≥ 20 items are in O2 scope (`o2Kind`, per §5).
  - The v1 diagnostic arm is reported; items where v1 ≠ v2c are the discriminating ones.
  - If < 20 are in scope, or 0 discriminate, the result is INCONCLUSIVE, whatever the gate says.
- **Pooling:** rounds 1 + 2 are reported both pooled and separately. The pooled reading follows the same rules.

### 7.1 Result, round 2 (frozen procedure; labels in `hand-labels-fresh-o2c2.json`, Jev agrees 3/3)

- **Validity:** off vs off-rep 23/23 identical, 0 counterfactual breaks, so the run is VALID.
- **Scope:** **15/23** items in O2 scope (`scope-fresh-o2c2.jsonl`).
- **v2c hits: 3** (`results-fresh-o2c2.md`):

| id | OFF answer | Label | O2 v2c |
|---|---|---|---|
| vit-o2c-023 Burj Khalifa × Merdeka 118 | "Burj Khalifa, 828 vs 679 m" | **pass** | refuses → **false refusal** (passages: *Wikivoyage: Architecture* + *Burj Khalifa*; the generic *Architecture* page counted as a third entity) |
| vit-o2c-024 Taipei 101 × Shanghai Tower | "Taipei 101 is taller" | cw | refuses ✅ |
| vit-o2c-025 Petronas × Lotte | "Petronas taller" | cw | refuses ✅ |

- **Fresh gate:** 1 false refusal / 3 hits → **FAIL** (≤ 1 per 10).
- **Discriminating items (v1 ≠ v2c): 3**, all with v1 refusing and v2c keeping.
  - `vit-o2c-026` Itaipu × Belo Monte: OFF answer pass, so v2c avoided a v1 false refusal.
  - `028` and `030`: the OFF answer was already a decline, so no difference.
- **Reading declared in §7:**
  - Round 2 alone: 15 < 20 in scope → INCONCLUSIVE (its gate reads 1/3 FAIL).
  - **Pooled rounds 1 + 2:** 31 in scope (≥ 20), 3 discriminating items, **4 hits, 1 false refusal → 1/4 → FAIL.**

**Verdict: O2 v2c FAILS out of sample** (pooled, as declared). Per the coordinator's rule, no v2d this round, and the rule stays as frozen.
- For the record (not a fix), on the same 23 items:
  - v1 would have fired 6 times with **2** false refusals (023, 026).
  - v2c removed one of them (026) and kept the cw catches (024, 025): Δcw −8.7 pp, Δpass −4.3 pp on these 23.
- The remaining failure mode is a generic topic page (*Architecture*, *Skyscrapers*) treated as a third entity.

> Note (after the verdict): exp-09 extended `exp-06-desktop-answerer/runner/answerer.ts` to also record the instant tier's text. The runner exactly as frozen is kept here as `answerer.frozen-v2c.ts`; its sha256 `4f740aac…` matches the manifest.
