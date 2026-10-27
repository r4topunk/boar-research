# The lexical topic filter drops answer-bearing sources on "which X is the most…" questions
TL;DR: `onSubject`/`onTopic` (answer.ts/context.ts @0cfd4a77) keeps a source only if it shares the question's words, but in answer-type questions ("Which land animal runs fastest?", "longest rivers", "astronauts on the Moon before 1970") the right article is named by the *answer* (Cheetah, Amazon River, Apollo program), so it is dropped and a lexically closer wrong one is kept.
Lane: Sonar · Status: evidence · Priority: C (was B)
Axes moved: retrieval ↑ (key-in-context at `pre`: up to +5 of 52 keyed items, the 5 wrong drops below); quality/truthfulness ↑ on reasoning and honesty-refusal items. Today these items answer from a wrong source: Common ostrich for fastest land animal, Mackenzie River for longest rivers. Or they decline: the Moon item. Safety: 0. Do not touch the health path.
Fits BOAR? A fix is pure TS. The hard part is finding a signal that separates right from wrong, see Evidence.
Evidence (own, 2026-10-02, `sonar/exp/05-topic-filter-rescue/`):
- Audit of the 7 items whose key was retrieved and then lost before the prompt (`tools/key_in_context.py`, ios-main-v5-t0): **5 are wrong drops by the topic filter**:
  - lan-rsn-003: Cheetah dropped, Common ostrich kept;
  - lan-rsn-005: Amazon River and Nile dropped, Mackenzie River kept, then declined;
  - lan-ref-003: Apollo program dropped, `no-good-source`, declined;
  - lan-cmp-005: Saltwater crocodile dropped;
  - lan-exp-003: Wikivoyage: Nairobi dropped, then a memory answer with the uncited warning.
  - 2 are health items (vit-hlt-001/002) where the dropped sources are travel guides, a Compass question.
- A cosine rescue does **not** work: dropped key-bearing sources sit at cos 0.71–0.79, the same band as dropped wrong ones (Cheetah 0.717 vs Sailfish 0.724). At ≥ 0.75 the rescue brings back 3 right and 3 wrong (`result.txt`, 101 dropped sources).
- A strong cross-encoder separates them (bge-reranker-v2-m3: Cheetah 0.99 vs Sailfish 0.23, Amazon 0.98 vs Mackenzie 0.16) but is too slow per query on a phone. The tiny one doesn't separate them (`tiny-cross-encoder-rerank`, now C).
Test in boar-eval: no arm yet. Candidate arms, cheapest first:
- (A) **Answer-type exemption.** When the question asks for an entity it doesn't name (superlative + "which/what/who" with no proper noun), the filter keeps vital5/Wikipedia chunks that already passed `ANSWER_MIN_SIMILARITY` 0.70 and drops only Wikivoyage/off-source ones. The filter then stops overriding the cosine gate for exactly the class it can't judge. Risk: lets back the 0.70-band noise (Sailfish, Sochi); the 1.5B must pick.
- (B) On Android 12 GB: one yes/no relevance call to the resident 4B for the top 3 dropped candidates.
- Success criterion for (A), to freeze before a run: key-in-context at `pre` +≥ 3 on the 52 keyed items with 0 losses, confident-wrong not up (Jev band), safety unchanged, on the t0 pair.
Cost to try: (A) ~3 h. Risk: medium (more noise reaches the 1.5B).

Demoted 2026-10-02 (`exp/05-topic-filter-rescue/answer-type.txt`):
- A simple answer-type detector (which/what/who + superlative + no proper noun) fires on only 1 bench item, lan-rsn-003.
- There the exemption would rescue Cheetah (key) together with Sailfish and Pronghorn (noise).
- The other wrong drops are not answer-type by that rule:
  - "longest rivers on Earth": "Earth" is capitalized;
  - "Did astronauts walk on the Moon": a yes/no question;
  - a comparison side;
  - a destination guide.
- Too few hits and too little precision for an arm. The root fix needs a sharper relevance signal (see `tiny-cross-encoder-rerank`).

## Details
Why it happens: answer.ts runs `onTopic(matchQuery, c)`. A source passes if:
- every year and at least one proper noun of the question are in it;
- or a title segment is made only of question words;
- or two consecutive question terms appear in the title or first sentence;
- or the title opens with a question word;
- or it reaches term coverage.

"Cheetah", "Amazon River" and "Apollo program" satisfy none of these for questions phrased around the attribute ("runs fastest", "longest rivers", "walk on the Moon"). The rule was added against real noise (s32: "United States Northern Command" for northern lights), so a fix must not reopen that.

UNKNOWN: how often answer-type questions occur in the post author-style use, beyond the bench's reasoning/honesty-refusal items.
