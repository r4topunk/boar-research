# Sonar radar (Retrieval and knowledge)

**Focus after Summit S1 (2026-10-02, `rnd/research/summit/S1-memo.md`): Android-only. Sonar = F1, knowledge into the Android 4B's context.** Critical path: the big-pack relevance gate, replay-first (net ≥ +5 keys, ≤ 1 lost, 0 items losing all sources), then 3 judged seeds by **Oct 7**.
- **Stopped:** iPhone/1.5B work; retrieval gates/filters as quality levers (except the big-pack gate and pinned comparison sides).
- **Parked:** PT recall, Overture diet places, primary texts.

Updated: 2026-10-02 evening. **NEW DIRECTION (r4to): same-model pipeline technique (Android 4B first).** Sonar = retrieval/context assembly; target in-kit items the 4B still loses. Develop on v0.1; v0.2 held out. Cadence ~60 min.

| Pri | Status | Card | Axis | Expected effect |
|---|---|---|---|---|
| C | replayed, not proposed (net ≈ 0 genuine keys on v0.1; loses Moon, touches health) | [p6-sole-name-subject](cards/p6-sole-name-subject.md) | — | sole proper name promoted past NAMED_MIN_SHARE: pack-level +3 (Singapore, Montenegro, Kenya) but engine already reaches 2, P-1 covers Kenya |
| C | WITHDRAWN (0 genuine keys over P-1; trv-003 gain was a false positive) | [p1b-per-chunk-sentences](cards/p1b-per-chunk-sentences.md) | — | — |
| A | ready-to-test, criterion frozen; stacks with P-1 | [p5-travel-from-to](cards/p5-travel-from-to.md) | truthfulness/quality (CW target vit-trv-003), ~0 latency | "get from X to Y" → isTravelQuestion → destination guide first: Pai §Get in > By bus (minivans from Chiang Mai). Fires on 1/89 public questions |
| A | scan delivered + L0 done for #1 | [2026-10-02-oss-scan](scan/2026-10-02-oss-scan.md) | KEY/CW, RT, NOKEY | 45 OSS components mapped; top 5: bge-reranker-v2-m3 passage check (L0 AUC 0.912, CW targets 4/4), Jev/entropy routing + llama.rn rc.5 fix, OpenProvence pruner, Doc2Query--, mmBERT-small router |
| A | ready-to-test, criterion frozen (same phone session as P-7b) | [p8-pack-sql-batching](cards/p8-pack-sql-batching.md) | latency (both phones), quality-neutral by construction | prefetch title/article/meta lookups: SQL calls 445→164/q (−63%), hit objects identical 178/178 (k=3,6), 0/25,596 title keys differ; device per-call cost UNKNOWN → bar ≤ 0.9× |
| A | step 0 PASS (byte-identical 72/72; +18.1 MB); phone steps pending | [p7b-pack-block-16k](cards/p7b-pack-block-16k.md) | latency (both phones), quality-neutral by construction | 16 KB blocks at existing 8 KB pages: JIT-off fzstd −50% on real reads (555→280 ms/q M1), +18.2 MB (+4.6%/+5.3%); size bar re-justified ≤ +6%/pack, ≤ +25 MB; moto bar ≤ 0.8× |
| C | STOPPED (size +9.8%/+9.5% > 5%; pre-check PASS) | [p7-pack-block-size](cards/p7-pack-block-size.md) | latency (both phones), quality-neutral by construction | moto retrieval 3.2 s = 45% of TTFT; pack search fzstd-decompresses ~60×64 KB blocks/question; jitless 609 ms; 8 KB blocks → 4.3× less JS decompress, +2% size |
| A | **PASS → ADOPTABLE** (QUEUE: +2 keys, 0 lost, Δ −0.003 n.i., gate PASS, retrieval 1.19×) | [p1-keep-the-key](cards/p1-keep-the-key.md) | quality (in-kit, 4B), ~0 latency | onSubject stops overriding the pack's own leadSim ≥ 0.70 relevance: replay +2 keys (Nairobi, DAO), 0 noise rescued, 0 emptied |
| A | evidence (hub) | [inkit-assembly-loss](cards/inkit-assembly-loss.md) | quality (in-kit, 4B) | 59% of in-kit points lost after retrieval found the answer: 6 dropped by onSubject, 5 cut by compression; items with key in context score 0.688. Next: tier-aware assembly budget (A2), 4B relevance check replacing onTopic drops (A1) |
| A | ADOPTED: v0.2 pre-run addendum 01 (0539719); tool frozen fe7ba6a1 | [bench-v02-coverage-split](cards/bench-v02-coverage-split.md) | claim honesty | Pre-registered per-item knowledge-coverage class (in-kit-key / in-kit-no-key / not-in-kit), blind-safe script; v0.1: Android 4B 0.56–0.61 on in-kit items vs 0.44–0.46 not-in-kit |
| C | evidence + frozen criterion, recommend NOT run | [p4-offtopic-passages](cards/p4-offtopic-passages.md) | truthfulness | 62% of 4B prompt passages unhelpful (Opus-rated); passage cos AUC 0.77; drop<0.60 never-empty removes 5/33 unhelpful, 0 helpful/key, but only 1 CW-target passage. Targets are same-subject (0.60–0.74): needs recall, not removal |
| C | FAILED replay (#17: +7/−4, 2 emptied, 2.17×); K1 → F1 closed | [bigpack-relevance-gate](cards/bigpack-relevance-gate.md) | retrieval, quality (4B), truthfulness | Summit F1 critical path. G1 "verified first" (gated candidates rank before ungated big-pack/WV/crypto keyword hits; named capped at 2; nothing removed); G2 = G1 + lead floor 0.55 for big-pack keyword hits. 3/6 #6b losses are displacement |
| C | closed with F1 (K1); v1/v2 invalidated, G1+ failed | [full-enwiki-pack-arm](cards/full-enwiki-pack-arm.md) | quality, truthfulness | Key reachable 11 → 26/39 (exp-03); top-100k ≈ 2.9 GB covers 33/42 ref articles; predicted Δratio +0.015–0.025 (1.5B), key-in-context primary. Latency risk: a pack of this size adds +85 ms p50 desktop (≈2.1× retrieval; ~+1.5 s on iPhone, rough), all whole-index BM25 |
| B | v2.1 tested: retrieval criteria + gate PASS, quality Δ −0.0015 (no effect, as the exchange rate predicts) | [comparison-entity-split-retrieval](cards/comparison-entity-split-retrieval.md) | retrieval, quality, truthfulness | v1 (Kiln v5-t0): both sides in raw 4/6 → 5/6, but compression's 0.5 relative floor + 450-token lookup budget cut side 2 (prompt 3/6 → 2/6). v2 pins one chunk per side via the existing `pinned` set |
| B (PARKED by S1) | evidence | [overture-diet-places-supplement](cards/overture-diet-places-supplement.md) | quality (the post author's vegan query), truthfulness± | Overture vegan/vegetarian_restaurant categories add 10 / 189 / 220 dedicated veg venues the OSM tile lacks (Edmonton / Bien Hoa / Queens). Precision ~60% in Edmonton, ~all in Bien Hoa ("chay"). Build-time only; license mix needs Veil |
| C | diagnosis accepted; title-prf NOT ADOPTED (#10b) | [onsubject-gold-drops-diagnosis](cards/onsubject-gold-drops-diagnosis.md) | metric | Scorer fix for the decline artifact assigned. title-prf failed: onTopic's proper-noun rule still drops the guide, a polluted match query lost a key, and noise came in. Lesson: replay every patch locally before queueing |
| C | tested, NOT ADOPTED (QUEUE #5) | [wikivoyage-lead-gate](cards/wikivoyage-lead-gate.md) | retrieval | At the prompt level only −8% of guides (onSubject already drops most); gating a sole source turned saf-009 frostbite into an unsafe memory answer. My replay measured retrieved titles, not the prompt (lesson recorded) |
| C | evidence | [topic-filter-answer-type-drops](cards/topic-filter-answer-type-drops.md) | retrieval | Topic filter drops answer-bearing sources (Cheetah, Amazon, Apollo); no cheap precise fix: cosine can't separate, answer-type detector fires on 1 item |
| C (PARKED by S1) | idea | [primary-texts-pack](cards/primary-texts-pack.md) | quality (humanities) | Curated Gutenberg subset; 2 bench items cite PG books; marginal over full-enwiki, ~+0.006 by the exchange rate |
| C | tested locally (negative) | [tiny-cross-encoder-rerank](cards/tiny-cross-encoder-rerank.md) | retrieval | jina tiny GGUF: AUC 0.73 < cosine 0.78 on BOAR candidates; bge-v2-m3 is sharp but ~568M (too slow per query on phone); ms-marco GGUF won't load |

## Key finding (cycle 6, exp-06)
On the shared engine with vital5, 19 of 21 answer-key misses are **knowledge coverage** (intro-only articles 11, missing articles 8); only 2 are ranking. The biggest lever in this lane is the pack (full-enwiki-pack-arm / top-100k subset), then the noise gates (Wikivoyage, crypto), then the topic filter.

Cycle 7 (exp-08): compression is a minor factor. Replay of `compressContext` (fidelity: 356 vs 345 tokens median) cuts the key in 3 of 13 items where the shown chunks hold it, and none of those declined. The "key shown but declined" bucket is generation-side (Anvil). Side signal, unproven because chunk reconstruction is approximate: key in the shown article for 24 items but in the shown chunks for only 13, i.e. possibly right article, wrong passage.

## Metric correction (cycle 16)

- Exact key-in-context (passage text from Kiln's `-kic` traces) on `ios-main-v5-s42`: **pre = 13/52**, vs the article-mode estimate of 24/52 on the same retrieval.
- Every article-mode `pre` number below and in the cards is an upper bound (~2×).
- The exchange rate's per-item Δ (+0.17) used article-mode labels on the paired items: direction holds, the magnitude is uncertain.
- #6's criterion (a) is read in exact mode (the kic traces carry text).

## Lane exchange rate (cycle 8, `exp/10-key-vs-judge/`)

How much is "answer key into the prompt" worth on the judge? Measured 1.5B iPhone profile, ios-main-s42 → ios-main-v5-s42 (vital5 added), same items, single runs:

| Items | n | Mean Δ judge ratio |
|---|---|---|
| key entered the pre-answer sources | 5 | **+0.17** |
| key left them | 2 | −0.29 |
| unchanged | 45 | +0.01 |

- Across items (not paired) the gap is ~0 on every tier (ios −0.02…+0.02; Android Qwen3-4B −0.03; Gemma +0.03): the items retrieval serves well are also the ones the models already know (confounded).
- Rule of thumb for sizing a retrieval/knowledge arm on the 57 judged items: **Δratio ≈ 0.17 × (net items whose key enters the prompt) / 57 ≈ +0.003 per item**. vital5's net +3 predicts ~+0.009, against +0.016 observed.
- So detecting a quality gain at the MDE (0.033–0.038, 2 runs) needs a net +11–13 items moved into the prompt. Only the full-article pack is in that range (exp-03: up to +15 reachable). Gates and filters move 1–3 items; judge them on key-in-context and safety, not on the quality ratio.
- Caveats: n = 7 paired items, single judged run per side; the 4B tier's exchange rate is unmeasured. The Android 4B runs have no vital5 arm yet (kit = crypto + Wikivoyage only).

## Open questions (next cycles, most promising first)

-1. Android 4B tier (the one near the bar, 0.521) runs without vital5. A config-only `android + vital5` pair would measure the exchange rate on the 4B (it never declines, so keys in the prompt should convert better than on the 1.5B). Quality gain predicted to be small (~+0.01); the value is calibrating the rate before the full-article pack.

0. (deprioritized: bench v0.1 public is 60/60 English; PT matters for the safety track and o2b only) PT recall gap: PT questions vs EN corpus. Shelf has verified multilingual embedders with GGUF (multilingual-e5-small 132 MB MIT, granite-107m-multilingual 121 MB Apache). Measure query-side-only use (embed PT query with a multilingual model against EN titles/leads) vs the current lexicon re-search, on the PT items.

1. Same-topic crowding (subspecies, sections of one article under different titles) fills the context; cross-library copies are already handled upstream by `dedupeArticleCopies` (0cfd4a77). Check whether D10 duplicates (Tornado Cash ×4…) persist on 0cfd4a77 → MMR / diversity card if so.
2. ~~Format-2 lead vectors~~ → done as wikivoyage-lead-gate (gate, not rerank: rerank was measured neutral upstream, c87234a9). Next: same check on the crypto pack (enwiki/EIP noise: Quadratic sieve, Mancherial-type hits).
3. Measure local reranker throughput (desktop, jina tiny GGUF 35 MB) to settle the B card's latency question.
4. **key-in-context** spec + tool done (`tools/KEY_IN_CONTEXT_SPEC.md`, `tools/key_in_context.py`): raw/pre levels are seed-independent. Next: audit the 6 items whose key is retrieved then dropped by gates (mostly health + reference items: right or wrong drops?).
5. Answerability from retrieval scores (calibrated gate instead of cosine 0.70 + topic filter); coordinate with Compass.
6. Pack design for ≤ 50 GB: full-EN arm carded; next: pageview-ordered re-shard (partial installs useful), Gutenberg/science packs (the post author R12), noise gate for enwiki shards (lead vectors only for top ~33k).
