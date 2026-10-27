# P-5: recognise "get from X to Y" as a travel question, so the destination guide is retrieved
TL;DR: For vit-trv-003 ("How do I get from Chiang Mai to Pai, and what should I know about the road?"), `isTravelQuestion` is false: `TRIP_INTENT` matches "get to / there / around" but not "get **from** X to Y". So the engine's destination logic never runs. "Pai" resolves, but its share of the question (0.237) is under `namedMinShare` (0.5), and the slots go to Chiang Mai's groceries and intro. One narrow pattern makes the Pai guide's "Get in > By bus" section (hourly minivans from Chiang Mai's Arcade terminal) the first source. It fires on 1 of 89 public questions. This is the genuine recall fix for this confident-wrong target; P-1b was not.
Lane: Sonar (same-model pipeline, retrieval) · Status: ready-to-test, **criterion frozen 2026-10-02 (evening), before any run** · Priority: A
Axes moved:
- truthfulness ↑ on vit-trv-003 (a Compass CW target: memory claims about the road beside a groceries passage);
- quality: tiny on the bench (1 item; by the exchange rate ≈ +0.003);
- the class it fixes ("how do I get from A to B" in a travel app) is common in real use. the post author-style travel questions on the phone are the product's core.
- Latency ≈ 0: the destination logic runs only on matched questions and uses the same lookups.
- Safety: neutral.
Fits BOAR? One regex added to `isTravelQuestion` in `src/rag/wikiPack.ts` (`upstream/main` 0cfd4a77):
```ts
// point-to-point trips ("get from Chiang Mai to Pai"): capitalized origin and destination
const FROM_TO_TRIP = /\b(get|go|travel|getting|going) from \p{Lu}[\p{L}.' -]*? to \p{Lu}/u;
export function isTravelQuestion(query: string): boolean {
  return TRIP_INTENT.test(query) || TRAVEL_PRACTICAL.test(query) || FROM_TO_TRIP.test(query);
}
```
The existing `destinationOf` then picks the first place after a `PLACE_CUE` that isn't after an `ORIGIN_CUE` ("from Chiang Mai" is the origin, "to Pai" the destination).

Evidence (`exp/20-travel-from-to/`, engine code @0cfd4a77 replayed on `boar-wikivoyage-en`):
- Before (engine as is, `exp/18-keep-the-key/pai.mts`):
  - `isTravelQuestion` false;
  - named Chiang Mai (share 0.547) and Pai (share 0.237 < 0.5, dropped);
  - hits Chiang Mai §Buy > Groceries / § intro / §Go next, plus Mae Hong Son Loop §Understand as a keyword 4th, cut at k = 3.
  - This matches the trace's raw (Chiang Mai ×3).
- After (patched copy, `check.mts`):
  - `isTravelQuestion` true;
  - hits at k = 3: **Pai §Get in > By bus** (via title), Pai § intro, then Chiang Mai.
  - The Pai passage carries the answer ("Minivans (150 baht) that leave hourly from Chiang Mai (Arcade terminal)…").
- False-fire scan: the pattern matches **1 of 60** public v0.1 questions (vit-trv-003) and **0 of 29** vitalik58 extras. v0.2 is blind, so it is unscanned by design; the held-out run will tell.
- Correction recorded: P-1b's apparent vit-trv-003 gain was a key-term false positive (the groceries passage gained a sentence containing "route"/"bus"), not the Mae Hong Son Loop passage. P-1b is withdrawn.

Frozen criterion (arm `p5-fromto` vs `and-qwen`, Android 4B, kit A, 0cfd4a77; `-kic` traces; replay-first: the pre-answer check below decides before any judged run):
1. **Exact key-in-context at `pre`** (`tools/key_in_context.py` 84182b67): vit-trv-003 gains the key **from a Wikivoyage: Pai passage**. Checked by title in the pre-answer sources, not only by key terms.
2. **0 keys lost** on the other keyed items; **0 items emptied**.
3. **No other item's pre-answer sources change**, except items the pattern matches (expected: none on v0.1).
4. Retrieval p50 ≤ 1.2× base.
5. Then judged (2 seeds): whole-bench paired Δratio ≥ −MDE; gate PASS v0.5; 0 new safety hits. Reported: confident-wrong on vit-trv-003 (expected down).
- Fail on 1–4 → stop before judging.

**Stacking with P-1:** yes, independent and additive.
- P-5 changes which articles the retriever names (`isTravelQuestion` → `destinationOf`, before `retrieveOne`'s merge). P-1 changes `answer.ts`'s `onSubject` (after compression).
- The Pai passages pass `onTopic` on their own ("Pai" is a question word; the title rule fires), so P-1's rescue isn't involved.
- Expected combined effect on v0.1 kit A: +3 genuine keys: lan-exp-003 and vit-cry-010 (P-1), vit-trv-003 (P-5).
- Suggest one arm with both patches, after each is checked separately at `pre` (cheap, no judging).

Cost to try: ~1 h (one regex + one `-kic` pair). Risk: low; the pattern needs a capitalized origin and destination.
