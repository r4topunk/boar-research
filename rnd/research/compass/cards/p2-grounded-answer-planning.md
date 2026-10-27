# P-2 Grounded answer planning: one direct sentence, then one cited sentence per needed fact (bounded, no free length)
TL;DR: the in-kit taxonomy shows the Android 4B loses most points on correct-but-incomplete answers (33 %) and wrong claims (27 %). P-2 changes only the answer persona (config-only arm): a direct answer sentence, then up to 4 sentences, one per fact the question type needs, **each ending with its source number**, ≤ 110 words, plus an explicit "Not in the offline sources: …" line instead of filling gaps from memory. Without sources it stays 2–3 sentences.
Lane: Compass · Status: **tested: NOT ADOPTED** (QUEUE, report `boar-eval/reports/night-2026-10-01/p2-grounded-planning.md`): Δ −0.053 (CI −0.085…−0.021), in-kit-key −0.108, completeness 2.80→2.36, unsafe 4/4 vs 3/3, gate FAIL · Priority: C
Axes moved:
- quality ↑ via completeness on in-kit items;
- truthfulness = or ↑ (every added sentence must carry a source; the omission line replaces memory filler);
- latency: ~1.3–1.5× desktop total time (answer ≤ 110 words vs ~49 today);
- safety = (frozen safety stack untouched).
Fits BOAR? Yes. Prompt text only (a persona), the same mechanism as the shipped personas in `src/constants/personalities.ts`. In the product it would be a new persona or the default's text. No model, no engine logic change.
Evidence:
- **Error taxonomy** ([in-kit-error-taxonomy](in-kit-error-taxonomy.md)): on 11 in-kit-key items × 2 seeds, 33 % of lost rubric points are correct-but-incomplete (Singapore, Kyoto, Appomattox) and 27 % are wrong claims or synthesis (India self-contradiction, Montenegro "kuna").
- **Why the persona arm (#12) failed, and how P-2 differs:**

  | | #12 P2 persona | **P-2 grounded planning** |
  |---|---|---|
  | Instruction | "1 paragraph, 4–6 sentences" (a length target) | one direct sentence + **one sentence per needed fact**, facet list by question type |
  | Grounding | none added | every added sentence must end with a source number; uncited facts are left out |
  | Gaps | filled from memory (cw 10 → 20) | explicit "Not in the offline sources: …" line |
  | Length | ~143 words p50 | **≤ 110 words**, 1 + ≤ 4 sentences |
  | No-source questions | same long format | 2–3 sentences, close to today's |

- **Method background:**
  - plan-then-write / outline prompting improves coverage in long-form QA (Skeleton-of-Thought, Ning et al., arXiv 2307.15337, 2023: "skeleton first, then expand each point");
  - attribution-constrained generation (cite per sentence) reduces unsupported claims (ALCE, Gao et al., arXiv 2305.14627, 2023, "Enabling LLMs to generate text with citations").
  - Neither paper measured a 4B on a phone. Expected effect is my estimate.
- **Engine compatibility:**
  - the persona's system prompt becomes the system message's leading `instruction`, followed by the engine's own "cite a source you used by its number, like [1]" context instruction (`src/rag/pure.ts` ~L332, L386–390);
  - the style reminder is appended to the question (`personalities.ts` comment: small models follow what's closest to the question);
  - CT-1's citation check runs unchanged, so unsupported [n] still get removed.
Test in boar-eval:
- **Arm `main~persona-p2g`:** config-only on the shared engine via the desktop adapter's `settings.personaSystemPrompt` + `settings.personaStyleReminder` (the persona arm's mechanism). Texts are in `exp/p2-planning/persona-p2g.json`:
  - systemPrompt sha256 `519a786e36228387f0c7e10f7453beb1b83e9d1e5ad63813efc19ed9b954a54c`;
  - styleReminder sha256 `5fe8283146580eb59f1f511f85183386b0afbc1262f151563b5d9297f4189683`;
  - the adapter's `runtime.versions["persona.sha256"]` is computed in JS, so compare the two strings, not that field.
- Profile: Android 12 GB, qwen3-4b-instruct-2507-q4km, kit A, questions72, seeds 42/43. Base = `and-qwen-s42/s43` (already judged). Judge judge.v1, both orders. v0.1 only: never v0.2.
- **FROZEN criterion (coordinator's terms, stated before any run):**
  1. whole-bench paired Δ quality ratio (two-level bootstrap, 2 seeds × judged items, vs `and-qwen-s42/s43`) **≥ +0.03**;
  2. confident-wrong per seed **≤ base + 1**;
  3. unsafe on danger items per seed **≤ base**, with safety rules **v0.5** (both arms re-scored with v0.5);
  4. `harness/gate.py` **PASS** (v0.5);
  5. **completeness sub-score up on in-kit-key items:** mean judge completeness over the 11 kit-A in-kit-key items (`exp/error-taxonomy/rows.json` class list), pooled over both seeds, arm > base.
  - Fail on any one = not adopted.
  - **Reported, not gating:** words p50; total time p50 (expected 1.3–1.5×); correctness Δ; per-class Δ (in-kit-key / in-kit-no-key / not-in-kit); `harness/lengthctl.py` length-controlled Δ (if Δ survives length control, it's not a length artifact); count of answers with a "Not in the offline sources" line.
- **Expected (stated now):**
  - (2)–(4) pass;
  - (5) likely passes;
  - (1) is uncertain: Δ +0.01 to +0.04. In-kit items gain, but not-in-kit items (33 of 52 keyed) may lose a little if the model now leaves out memory facts it used to state correctly.
Cost to try: config only. 2 runs × 72 items on the mini (~20 min each) + judge (~228 calls). No downloads.

## Post-mortem (Compass, 2026-10-02; from the report and the s42 traces, no new runs)
**Result vs my stated expectation:** I expected Δ +0.01…+0.04 with in-kit completeness up; the result was Δ −0.053 with in-kit completeness *down* (2.80 → 2.36) and the in-kit class hit hardest (−0.108). It's a clear miss of my prediction, not noise.

**Why "one cited sentence per facet" made the 4B drop kit facts:**
1. **Facets were chosen by what the passages in context say, not by what the question needs.** Forced to cite every sentence, the 4B filled its slots with whatever citable sentences the retrieved passages held:
   - Civil War: Pea Ridge, "23,000 soldiers", instead of Appomattox;
   - Singapore: Chinese dialects, instead of the 1963 merger;
   - Kyoto: "14 UNESCO sites".
   The class name "in-kit-key" means the key is in the *installed article*. Sonar's check is an article-level upper bound, and the passage actually in the prompt often isn't the section with the key. So the plan bound the answer to the wrong section.
2. **The citation constraint suppressed correct memory facts.** The base answer for Singapore had "9 August 1965" from memory; P-2 wrote only "1965". In-kit items are exactly where the 4B already knew the key facts, so forbidding uncited facts cost most there.
3. **The mandatory gap line was always wrong in effect.** "Not in the offline sources: …" appeared in 59/59 answers, usually naming an invented, irrelevant gap ("economic or military impact of Kyoto"). The judge reads it as admitted incompleteness.
4. **Longer answers cost points with this judge.** Words p50 went 49 → 82, and the length-controlled Δ is −0.002 (β −0.55 per log-word), so the whole drop is what the added (tangential) length cost. The persona arm showed the same: this judge doesn't reward padding and penalizes it.
5. **Structure didn't fix reasoning errors.** The India self-contradiction survived verbatim. More sentences also meant more surface for unsafe text (vit-hlt-001 "flush with fresh water").

**Lessons for the pipeline track:**
- With 0/2 prompt-shaping arms on the 4B, answer *format* is not the lever. Completeness on in-kit items is bounded by **which passage is in the prompt** (P-1 keep-the-key, context assembly), not by how the answer is laid out.
- Never make a gap or uncertainty line mandatory. Emit it only when a check shows the key is missing.
- My taxonomy's "correct but incomplete" category was partly a context problem in disguise: the article had the fact, but the prompt's passage didn't.
- Any future answer-shaping idea should first be replayed offline on the 11 in-kit items (answer text vs the passages actually sent) before a seeded arm.
- The P-2 texts stay frozen as a negative result; no follow-up prompt arm (coordinator).

## Body
- **Latency estimate:** today's Android 4B answer is ~49 words p50 (desktop total 8.2 s); P2 at ~143 words took 14.0 s (1.7×). P-2 is capped at 110 words, so expect ~1.3–1.5× desktop. On the phone, decode time scales the same way; the device run is in progress, so the number is UNKNOWN.
- **What would make it fail:**
  - the 4B ignores the facet structure and writes prose anyway;
  - it cites sources for facts they don't contain (CT-1 removes the [n], and the sentence stays as an uncited claim);
  - not-in-kit items lose memory facts. That's the (1) risk; watch the per-class Δ.
- **If it passes:** the iPhone 1.5B is the second target, using the same text with the compact model's citation decline left unchanged. Only after the Android result.
- **If (1) fails but (5) passes:** P-2 fixes completeness where knowledge is present but costs elsewhere. Report per class and don't adopt.
