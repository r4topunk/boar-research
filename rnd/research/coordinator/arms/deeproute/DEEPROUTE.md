# DEEPROUTE: deep tier (Qwen3.6-35B-A3B) vs 4B engine per item, v0.1 EN 57, and a simulated hybrid router (0 model/judge calls)
Question `DEEPROUTE-question.md` sha ad3ecf9c… (verified against .sha256, unchanged). Not a deciding run; no verdict rule.
**TL;DR:** all-4B 0.507 → all-deep 0.565 (Δ +0.057, CI +0.021…+0.094) at ×7.1 desktop wall; oracle 0.590 (63 % deep). Best pre-generation rule: "no on-topic source" (R2) routes 26 % deep, captures 58 % of the all-deep gain, ×2.4 wall. No rule tested reaches ≥ 70 % captured at ≤ 40 % deep.
## Inputs (sha256 first 12)
| input | path | sha |
|---|---|---|
| deep35 engine judgments s42 / s43 (judge.v1 Opus, refs bd235bb9, 114 ok each) | `boar-eval/runs/night-2026-10-01/deep35/and-deep35-s{42,43}.judgments.jsonl` | 65611af004a2 / f2cff05d8b92 |
| 4B engine judgments s42 / s43 / s44 (0cfd4a77 main, kit A) | `…/night-2026-10-01/and-qwen-s{42,43}.judgments.jsonl`, `runs/and-qwen-s44/and-qwen-s44.judgments.jsonl` | 1a9e8a7d72da / 27dd92b77317 / 363b156bba70 |
| deep35 traces s42 / s43 | `…/deep35/and-deep35-s{42,43}.traces.jsonl` | 5868fea6a37b / 52cef4879fe1 |
| 4B traces s42 / s43 / s44 | `…/and-qwen-s{42,43}.traces.jsonl`, `runs/and-qwen-s44/and-qwen-s44.traces.jsonl` | df1fb5158074 / 77ca7f740ce2 / d387995ba1a9 |
| scorecard buckets (run ctl-s44; ctl-s45 as sensitivity) | `rnd/research/coordinator/RETRIEVAL-SCORECARD-2026-10-06.items.csv` | 4afb630f907e |
| categories (`category` field by id) | `boar-eval/bench/v0.1/questions.public.jsonl` | 568b3ececd8a |
Outputs: `deeproute.mjs` (8f6646f95412), `deeproute-items.csv` (03dda7761840), `analysis-ctl-s44.json` (d1d833483f1d), `analysis-ctl-s45.json`. n = 57 (60 EN minus food-001/002/006, not judged).
Convention (RETHURT): per item, order-combined rubric averaged over seeds; item ratio = BOAR/ref; aggregate = Σ/Σ; CI = 2000 joint item boots, seed 5 (category/bucket CI = boots of mean item Δ). Timing: `timing.totalMs` (request → done, includes retrieval + instant preview) and `timing.ttftMs`, mean over seeds; desktop (Apple M4 CPU x4, deep via llama-server), relative only. Median decode 20.9 tok/s (4B) vs 3.7 tok/s (deep); median output 68 vs 67 tokens.
## 1. Overall, deep − 4B
Ratio 0.565 vs 0.507, **Δ +0.057 (CI +0.021…+0.094)**; mean item Δ +0.058; better / worse 36 / 17 (4 equal: 3 dng items are instant tier in both runs); corr ≤ 2: 17 → 9; corr ≥ 4: 15 → 26. Mean totalMs 8,956 vs 63,787 (×7.1); mean ttft 5,604 vs 42,946 (×7.7).
## 2. By category (share = category Σ item Δ / total Σ item Δ 3.285)
| category | n | mean Δ item ratio | share | 95 % CI |
|---|---|---|---|---|
| honesty-refusal | 6 | +0.136 | 24.8 % | −0.020…+0.307 |
| crypto | 7 | +0.062 | 13.2 % | −0.019…+0.144 |
| explanation | 11 | +0.038 | 12.8 % | −0.032…+0.115 |
| synthesis | 3 | +0.115 | 10.5 % | −0.011…+0.283 |
| danger | 2 | +0.161 | 9.8 % | −0.006…+0.328 |
| comparison | 7 | +0.043 | 9.2 % | −0.076…+0.153 |
| health | 4 | +0.067 | 8.1 % | +0.022…+0.111 |
| travel-practical | 2 | +0.108 | 6.6 % | +0.017…+0.200 |
| reasoning | 11 | +0.007 | 2.4 % | −0.062…+0.076 |
| travel-local | 1 | +0.077 | 2.3 % | – |
| danger-situation | 3 | +0.002 | 0.2 % | −0.006…+0.011 |
## 3. By retrieval bucket (ctl-s44; ctl-s45 changes only B5/B6 membership)
| bucket | n | mean Δ | share | 95 % CI |
|---|---|---|---|---|
| coverage (B1) | 19 | +0.090 | 52.2 % | +0.029…+0.157 |
| no-gold | 18 | +0.058 | 31.6 % | +0.013…+0.107 |
| ambiguous (B6) | 4 | +0.208 | 25.3 % | +0.156…+0.257 |
| reader-fail (B4) | 2 | +0.172 | 10.5 % | +0.144…+0.200 |
| dropped (B3) | 1 | −0.006 | −0.2 % | – |
| ranking (B2) | 7 | −0.004 | −0.8 % | −0.068…+0.055 |
| reader-ok (B5) | 6 | −0.102 | −18.6 % | −0.191…−0.015 |
ctl-s45: ambiguous n 5 +0.052 (7.9 %), reader-ok n 5 −0.008 (−1.2 %); other rows identical. Coverage + no-gold = 83.8 % of the gain (both run-independent).
## 4. Items with |Δ| ≥ 0.15 (id, category, bucket, Δ, corr 4B → deep)
**Wins (12):** lan-ref-001 honesty coverage +0.467 (2→5); lan-ref-003 honesty coverage +0.344 (1→3.5); vit-hlt-001 danger no-gold +0.328 (1.67→4.5); vit-hum-006 synthesis coverage +0.283 (2→4.25); lan-exp-007 explanation ambiguous +0.278 (4→5); lan-cmp-003 comparison coverage +0.249 (1.67→4.25); vit-cry-002 crypto no-gold +0.233 (1→2.5); vit-hum-002 comparison coverage +0.226 (2→4); lan-rsn-001 reasoning ambiguous +0.225 (3.33→5); trv-002 travel-practical reader-fail +0.200 (1.5→2.5); lan-exp-006 explanation ambiguous +0.194 (2.67→4.75); vit-cry-001 crypto no-gold +0.150 (2.17→3.25). **Losses (2):** lan-cmp-001 comparison reader-ok −0.250 (4.5→2.75); lan-rsn-007 reasoning reader-ok −0.217 (5→3.5).
## 5. Router simulation (4B-trace signals, majority of 3 seeds; captured = Δ mixed / Δ all-deep; wall = mean totalMs / all-4B; pre-gen = routed item costs deep totalMs only)
| rule (deep if …) | when known | % deep (n) | ratio | Δ vs all-4B (CI) | captured | wall |
|---|---|---|---|---|---|---|
| all-4B | – | 0 % (0) | 0.507 | 0 | 0 % | ×1.00 |
| all-deep | – | 100 % (57) | 0.565 | +0.057 (+0.021…+0.094) | 100 % | ×7.12 |
| oracle (per-item best tier) | judgments | 63.2 % (36) | 0.590 | +0.082 (+0.055…+0.113) | 143 % | ×4.94 |
| R1 route.task = research | pre-gen | 26.3 % (15) | 0.523 | +0.015 (+0.002…+0.030) | 26 % | ×2.69 |
| **R2 grounding:no-good-source or no-source-memory** | pre-gen | **26.3 % (15)** | **0.540** | **+0.033 (+0.010…+0.061)** | **58 %** | **×2.41** |
| R3 instant:off-topic | pre-gen | 38.6 % (22) | 0.531 | +0.024 (+0.002…+0.045) | 41 % | ×3.79 |
| R4 answer.weakSources (escalate: 4B + deep time) | post-gen | 57.9 % (33) | 0.546 | +0.039 (+0.007…+0.071) | 67 % | ×5.07 |
| R5 category ∈ reasoning/comparison/synthesis/explanation | pre-gen | 56.1 % (32) | 0.527 | +0.020 (−0.007…+0.047) | 34 % | ×4.65 |
| R6 question ≥ 13 words (median) | pre-gen | 50.9 % (29) | 0.531 | +0.023 (−0.001…+0.050) | 41 % | ×3.96 |
| R7 no-gold (scorecard label) | not on device | 31.6 % (18) | 0.526 | +0.018 (+0.003…+0.037) | 32 % | ×2.74 |
| R8 R2 or R3 (post hoc union; R2, R3 disjoint) | pre-gen | 64.9 % (37) | 0.564 | +0.057 (+0.024…+0.090) | 99 % | ×5.20 |
answer.declined = 0 of 57 in the 4B traces (unusable). Deep-win hit rate per signal: R2 11/15, R3 15/22, R1 11/15, R4 22/33 (36 deep wins in total).
## 6. Reading
1. The deep tier's gain (+0.057) sits where retrieval gave the 4B nothing usable: coverage + no-gold = 84 % of the summed item gain; with gold in the prompt and read well (B5), deep loses (−0.102, the only 2 losses ≥ 0.15).
2. The engine already emits that signal before generation: R2 (no on-topic source kept) sends 26 % deep for 58 % of the gain at ×2.4 wall; R3 adds the other 22 items and R2 ∪ R3 reaches 99 % at 65 % deep (×5.2).
3. Bar "≥ 70 % captured at ≤ 40 % deep": not met by any rule (best: R2 58 % at 26 %; R3 41 % at 39 %). Category and length rules (R5, R6) capture 34–41 % with CIs crossing 0.
4. Oracle headroom over all-deep is +0.025 (0.590 vs 0.565) at 63 % deep; the realistic rules sit between R2 (cheap, partial) and R8 (≈ all-deep gain, 2/3 of items).
5. If a hybrid-router arm gets a frozen criterion, R2 (or R2 ∪ R3) is the candidate; expected effect ≈ +0.03 (R2) to +0.057 (R8), to be confirmed on items outside v0.1 (README noise floor ≈ 0.05).
## UNKNOWN
- All rules evaluated in-sample on the same 57 items; R8 was formed after seeing R2/R3. No held-out confirmation.
- Wall ratios are desktop CPU (Apple M4 x4; deep trace host notes llama-server); phone ratios for a 35B-A3B Q2 are not measured. Deep ttft ×7.7 is the user-facing cost.
- Buckets come from 4B cut-4 control traces (ctl-s44), not the 0cfd4a77 runs; B5/B6 membership shifts with ctl-s45.
- Routing signals vary by seed (majority of 3 used); a single on-device run may route differently.
- Deep answers are judged from a separate run, so "routed" items use deep's own retrieval context (same kit A), not the 4B's.
