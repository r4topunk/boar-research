# COMPLETE: deep35 R450 with a completeness instruction, v0.1 EN 57, judge.v1

**TL;DR: NO.** The completeness prompt gives deep35 R450 a ratio of **0.620** (CI 0.580–0.663), against 0.634 for DEEPREAD. The paired Δ is −0.014 (CI −0.055…+0.024). Completeness went up as intended (2.66 → 3.10), but correctness fell from 3.89 to **3.10** and confident-wrong items rose from 7 to **15**. Answers grew from a median of 51 to 224 words, and decode time per item went up 3.3×. At correctness 3.9, longer answers still bring in wrong claims, the same pattern as the 4B answer-style test. Completeness is not a prompt lever.

Criterion: `COMPLETE-criterion.md`, sha256 `bff13f1ca4d84d00…`. I checked it before the run and it is unchanged. Prompt diff: `prompt-diff.txt`, sha256 `53bdda16eda41917…`, written before generation. Kiln ran this on 2026-10-06 from 18:33 to 20:07. Dev set only (v0.1 public). No blind/ or V-para. One seed, one run, no rescue, no prompt tuning.

## Verdict (frozen rule, applied by the letter)
| condition | needed | value | met |
|---|---|---|---|
| GO: ratio | ≥ 0.700 | 0.6202 | no |
| GO: correctness mean | ≥ 3.80 (≤ −0.10 vs 3.89) | 3.10 (−0.80) | no |
| GO: items with correctness ≤ 2 (not declines) | up by ≤ 2 | 7 → 15 (+8) | no |
| PARTIAL: 0.660 ≤ ratio < 0.700 with correctness held | — | 0.620; correctness not held | no |
| otherwise → **NO** | | | **yes** |

**NO.** The criterion reads this outcome as "longer answers buy nothing or add errors". Here they did both: ratio flat-to-down, errors up.

## The one change (prompt-diff.txt)
```diff
--- prompt.deepread (old)
+++ prompt.complete (new)
@@ -1,6 +1,7 @@
 [system prompt, before the Context block; one sentence per line for the diff]
 You are Boar, a concise offline research assistant.
-Answer in 2-3 short, direct sentences or a brief paragraph, no preamble.
+Answer completely, the way an expert would explain it to a curious traveler or student: lead with the direct answer, then the key supporting points (who/what/when/where/how much, causes, comparison verdict, caveats), 120–220 words.
+Use only facts you are sure of or that the sources state; never pad with guesses.
 Do not default to a bulleted list or a single takeaway sentence followed by three bullet points — use bullets only when the content is genuinely a list of distinct items.
 Use the context below when relevant, and cite a source you used by its number, like [1] or [2].
 If the context doesn't cover the question, say so and answer from general knowledge.
@@ -12,5 +13,3 @@
 
 [user turn template]
 {question}
-
-(Response style: Keep it short: 2-3 sentences. No lists unless the question asks for one.)
```
Also `max_tokens` 512 → 700. Nothing else changed: same contexts `ctx-R450.jsonl` (sha `ad73972b…`), same sampler (0.7/40/0.95/0.05, seed 42), same `llama-server` b11010 (0.4.1-dev, commit 4bc272f), same flags (`-t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning-format deepseek`, `cache_prompt:false`), same model Qwen3.6-35B-A3B UD-Q2_K_XL (sha `96b9c0af…`, re-verified on the mini), thinking off. Mini, heavy lock, `<runner>/kiln/complete/`.

**Interpretation to flag:** the old prompt states the answer length in two places. One is the system sentence. The other is a user-turn suffix, `(Response style: Keep it short: 2-3 sentences. …)`. I treated the suffix as part of "the answer instruction" and removed it, so the new instruction is not contradicted in the same request. Everything else in the system prompt is byte-identical: the bullets rule, the sources/citation rule, the "context doesn't cover" rule, the safety lines and "concise offline research assistant". A check over all 57 requests shows they differ from DEEPREAD's only by these two strings (0 mismatches). requests.jsonl sha `c247a4af…`.

## Results (judge-core `summarize()` on combined orders, same script logic as DEEPREAD)
| system | ratio (95% CI) | win / tie / loss | rubric C / Cm / U | floor-adj (CI) | pos. consistency |
|---|---|---|---|---|---|
| **deep35 R450 COMPLETE** | **0.620 (0.580–0.663)** | 1.8% / 0% / 98.2% | **3.10** / 3.10 / 2.95 | 0.523 (0.470–0.572) | 100% |
| deep35 R450 DEEPREAD | 0.634 (0.590–0.683) | 1.8% / 5.3% / 93.0% | 3.89 / 2.66 / 2.78 | 0.541 (0.479–0.597) | 96.5% |

The reference rubric is about the same on both runs (4.86 / 4.91 / 4.96 vs 4.80 / 4.94 / 4.97).

**Paired vs DEEPREAD (n = 57, items resampled jointly, 2000 boots):**
- Δratio **−0.014** (CI −0.055…+0.024).
- Δfloor-adj −0.018 (CI −0.067…+0.030).
- Per item: better on 22, worse on 24, equal on 11.
- By rubric: Δcorrectness **−0.80**, Δcompleteness +0.44, Δusefulness +0.17.
- Converted (DEEPREAD ≤ 2 → COMPLETE ≥ 4): 0.
- Regressed (≥ 4 → ≤ 2): 1, lan-rsn-002 (4.17 → 1.33).

**Confident-wrong:** an item counts when its combined correctness is ≤ 2 and the answer is not a decline (bench `precheck.refused`; there were 0 declines in either run).
- DEEPREAD, 7 items: lan-cmp-004, lan-cmp-005, lan-rsn-001, vit-cry-008, vit-cry-009, vit-sci-001, vit-sci-003.
- COMPLETE, **15 items**:
  - 9 new: dng-002, lan-cmp-003, lan-ref-003, lan-rsn-002, trv-004, vit-cry-004, vit-cry-005, vit-hlt-001, vit-trv-004.
  - 1 left: lan-cmp-004.
  - Net **+8**.
- Several of the new ones were simple facts the short answer got right: lan-cmp-003, lan-ref-003, lan-rsn-002 (correctness 5 → 1–2). Two of them are safety/health items (dng-002, vit-hlt-001).

Largest per-item moves (mean S):
- Up: dng-005 (+1.17), vit-cry-002 (+1.17), lan-cmp-004 (+0.83), vit-hum-004 (+0.83).
- Down: lan-rsn-002 (−2.83), lan-cmp-003 (−2.17), lan-ref-003 (−1.67), lan-exp-007 (−1.67), lan-ref-001 (−1.0).

Full table: `analysis.json` → `perItem`. Each row has S, correctness, completeness, words, decline flag and decode seconds for both runs.

## Length and cost (Mac mini CPU x4, desktop numbers)
| metric | DEEPREAD | COMPLETE |
|---|---|---|
| words, median (mean) | 51 (51) | **224** (224). Only 21/57 are inside 120–220; 35 are over 220, 1 under 120 |
| output tokens, median | 72 | 312. All 57 finished with `stop`, 0 hit the 700 cap |
| **decode seconds per item, median (mean)** | 7.7 (7.4) | **25.6 (26.9)**, 3.3× |
| total per item, median | 48.7 s | 69.0 s. Wall time for 57 items: 46 → 66 min |
| decode tok/s, median | 9.43 | 11.96 |
| prefill tok/s, median / prompt tokens, median | 18.6 / 765 | 18.5 / 799 |
| peak RSS | 8,435 MB | 8,368 MB |
| hidden reasoning tokens / errors | 0 / 0 | 0 / 0 |

Format side-effects: 5/57 answers used bullets and 3/57 cited "[General Knowledge]" as if it were a source.

## Examples (DEEPREAD → COMPLETE)
**Improved: dng-005** "After a flood the tap water might be contaminated. How do I make water safe to drink?" S 2.67 → 3.83, correctness 4 → 4.
- Old (63 words): boiling 1 min (3 at altitude); calcium hypochlorite mentioned with no dose; bottled water.
- New (221 words) adds the bleach dose (8 drops/gallon, 16 if cloudy, 30 min), the HTH stock-solution recipe, "does not remove chemicals/heavy metals" and clean storage.
- Judge: "Both answers give the correct boiling times and bleach dose… [ref] is more complete: … settle or filter it first… current 5–9% bleach range." The extra content is correct and comes from the sources.

**Unchanged: lan-exp-001** "Give me a quick overview of Singapore: where it is, how it became independent, and what languages people speak there." S 4.17 → 4.17.
- New (252 words) adds geography, the Raffles 1819 → 1867 → 1963 → 1965 timeline and Singlish. Correctness 5 → 4.5, because the judge flags "a vague detail about the islands ('one outlying islet')".
- Both versions miss the exact independence date. Three times the length, same score.

**Worse: lan-rsn-002** "If you stood the Burj Khalifa on the deepest point of Lake Baikal, would its top stick out of the water?" S 4.17 → 1.33, correctness 5 → 1.
- Old (36 words): "828 m … 1,642 m deep … completely submerged." Correct.
- New (220 words) opens with "Yes, … its top would stick significantly out of the water." It then computes "submerged by about 814 meters" and still concludes "The top 828 meters of the structure would remain above the surface". It also cites "[General Knowledge]" and uses bullets.
- Judge: "gets the verdict wrong … contradicts itself." Here the "lead with the direct answer" instruction makes the model commit to a verdict before it has reasoned through the numbers.

## Caveats
- Dev set, 1 seed. The noise floor is about 0.05, and the paired CI spans 0. Even so, the verdict does not hinge on the ratio alone: two of the three GO conditions miss by a wide margin (correctness −0.80 against an allowed −0.10; confident-wrong +8 against +2).
- R450 passages were picked using the reference answer, so this is an upper-bound reader setting. On engine retrieval, longer answers would have even less source support.
- The model overshot the 220-word target (median 224). A tighter length might add fewer errors, but testing that would be prompt tuning after seeing results, which the criterion forbids.

## Judge spend
- 114 calls; 114 OK, 0 rate limits, 0 errors. All rows are judge.v1 / claude-opus-5-5, seed 7, gap 5000 ms.
- Refs `bd235bb9811f`, questions `568b3ececd8a` (bench/v0.1).

## Files (this folder; mini copy `<runner>/kiln/complete/`, nothing deleted there)
- `COMPLETE-criterion.md` / `.sha256`: frozen criterion, untouched.
- `prompt-diff.txt` / `prompt-diff.sha256`: the prompt change, written before generation.
- `build_msgs.mjs` → `requests.jsonl` (sha `c247a4af…`); `build.log`: context check vs the 4B traces, 0 mismatches.
- `gen_server.py`: DEEPREAD's script with only `max_tokens` 700 and the run name changed.
- `gen-run.log`, `deep35-complete-R450.traces.server.log`: logs.
- `deep35-complete-R450.traces.jsonl` (sha `842cfc20…`), `deep35-complete-R450.judgments.jsonl` (sha `497838ca…`), `judge-deep35-complete-R450.log`: traces, judgments, judge log.
- `analyze.mjs` (+ `declines.py`) → `analysis.json`. Run as `node analyze.mjs <complete.judgments> ../deepread/deep35-R450.judgments.jsonl <complete.traces> ../deepread/deep35-R450.traces.jsonl`.
