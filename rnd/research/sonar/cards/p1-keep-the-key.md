# P-1 "keep the key": the topic filter stops overriding the pack's own relevance rule (leadSim ≥ SEMANTIC_KEEP)
TL;DR: On `and-qwen` (Android 4B, kit A), retrieved-then-dropped answer keys are lost almost entirely at `onSubject` (the generic topic filter). The fix: a large-pack passage that the pack itself judged relevant (question ↔ article lead cosine ≥ `SEMANTIC_KEEP` 0.70) is not dropped by `onSubject`. In a faithful replay this rescues 2 key-bearing passages and 0 noise passages. It needs ~0 latency: the value is already computed by `searchDetailed`.
Lane: Sonar (same-model pipeline, context assembly) · Status: **PASS on all frozen criteria → ADOPTABLE** (Kiln, QUEUE 2026-10-02: +2 exact keys lan-exp-003/vit-cry-010, 0 lost, 0 emptied, paired Δ −0.003 [−0.019, +0.015], gate PASS v0.5, unsafe 3/3 = base, retrieval 1.19×); criterion frozen before the run · Priority: A
Axes moved: quality on in-kit items, small (+2 keys in context on v0.1; by the exchange rate ≈ +0.006 on the whole bench, below the MDE, hence the frozen "not worse" quality bar). Latency ~0: no new retrieval or embedding; the prompt grows only on rescued items (+1 passage on 2 of 57). Safety: neutral by construction. The health path never runs `onSubject` (`answer.ts`: `guarded && !health`), and the one health-adjacent key passage (Wikivoyage: Langkawi for a jellyfish sting, lead cos 0.470) stays out.
Fits BOAR? Pure TS on `upstream/main` 0cfd4a77. Two small edits: carry `leadSim` from `WikiPack.searchDetailed` (computed at `wikiPack.ts:841` whenever a `queryVec` is passed) onto the hit/chunk (`RetrievedChunk.leadSimilarity`, new optional field), and in `answer.ts` `onSubject`: `onTopic(...) || (c.leadSimilarity ?? -1) >= SEMANTIC_KEEP`. Same code delta as G1+'s verification signal, without its reordering.

**Per-item stage table** (the trace's retrieved-then-dropped items, `and-qwen` s42 = s43, retrieval is deterministic).
- Replay of the engine's own code (`wikiPack.searchDetailed` → `compressContext` → `onTopic`) on exactly reconstructed raw chunks; `exp/18-keep-the-key/stage.txt`, `full*.txt`, `rescue.txt`.
- Fidelity: 61/68 items reproduce the trace's `context:X->Y` exactly; 57 usable non-health items.

| Item | Key-bearing passage (passage level) | Stage that drops it | Fixed by P-1? |
|---|---|---|---|
| lan-exp-003 Kenya essentials | Wikivoyage: Nairobi §Understand > History | **onSubject** (lexical coverage; lead cos 0.710) | **yes** |
| vit-cry-010 2016 DAO hack | Decentralized autonomous organization | **onSubject** (lead cos 0.785) | **yes** |
| vit-trv-003 Chiang Mai → Pai | Wikivoyage: Mae Hong Son Loop | onSubject (lead cos 0.591) | no (below 0.70) |
| vit-hlt-001 jellyfish sting | Wikivoyage: Langkawi / Darwin §Stay healthy/safe | onSubject (lead cos 0.470) | no, intentionally (travel guide as health advice) |
| lan-ref-003 Moon before 1970 | Wikivoyage: Webster (Texas) §Cope (Apollo 11) | compression sentence selection (only "no compression limit" recovers it) | no |
| lan-hlt-001, vit-hlt-002, lan-ref-004 | none at passage level (article-level match only) | n/a. vit-hlt-002's Altitude sickness passages are cut by compression, but they lack the key terms | n/a |

**Levers tested and rejected** (same replay, 51 keyed items):
- compression `RELATIVE_RELEVANCE_FLOOR` 0.5 → 0.3 / 0.0: +0 keys;
- `FAST_CONTEXT_TOKENS` ×1.5 / ×2: +0 keys, Δ 0 tokens (the budget isn't binding);
- `onSubject` off entirely: +4 keys, 0 lost, 0 emptied, but +92 prompt tokens per item of mostly noise. That is the upper bound; P-1 takes the precise half of it.
- Rescue threshold: at 0.65, +2 key and +2 noise (Atlas Mountains 0.673, Extreme points 0.671); at 0.70, +2 key and 0 noise.

**Frozen criterion** (arm `p1-keepkey` vs `and-qwen`, Android 4B profile, kit A, shared engine 0cfd4a77; Kiln-4 after E3):
1. **Exact key-in-context at `pre`** (`tools/key_in_context.py` 84182b67, traces with `--event-source-text`), on v0.1 public keyed items: lan-exp-003 and vit-cry-010 gain the key, i.e. **+2 on the dropped items**, and **≤ 1 key lost elsewhere**.
2. **0 items emptied** (any item with ≥ 1 pre-answer source in base keeps ≥ 1).
3. **Whole-bench paired Δratio ≥ −MDE** (not worse beyond the MDE at the run count used; 2 seeds × 57 judged items, MDE ≈ 0.030–0.036).
4. **Gate PASS with safety rules v0.5**; 0 new safety hits; 0 new danger memory answers.
5. **Retrieval p50 ≤ 1.2× base** (Android desktop profile). Expected ≈ 1.0×.
6. Reported, not pass/fail: mean prompt tokens Δ (expected ≈ +2 tokens per item averaged over the bench), confident-wrong per run.
- Fail on 1, 2, 4 or 5 → not adopted. Fail on 3 alone → report as "not shown safe for quality".

Cost to try: ~1–2 h (two edits + one `-kic` pair + 2 judged seeds). Risk: low (it only adds passages the pack already scored as relevant, and only on the generic path).

## Details
- Why this is consistent with the engine: `searchDetailed` keeps a keyword candidate when `coverage ≥ 0.5 || leadSim ≥ SEMANTIC_KEEP`. `onSubject` then re-judges with stricter lexical rules and drops some of the same passages the pack just called relevant. P-1 makes the second stage respect the first stage's semantic verdict.
- What it won't fix: compression's sentence selection (lan-ref-003), and keyword passages below 0.70 (vit-trv-003). Nor anything on the iPhone 1.5B path in a measurable way; this card targets the Android 4B, per the new direction.
- Development on v0.1 only (v0.2 is held out); a v0.2 confirmation follows the coordinator's plan.
