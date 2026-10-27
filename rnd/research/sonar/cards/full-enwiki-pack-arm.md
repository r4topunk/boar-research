# Full English Wikipedia pack (15 format-2 shards, ~18 GB) instead of intros-only vital5
TL;DR: The bench's Wikipedia knowledge today is wiki-vital5 (lead sections of 49,832 articles); for 39 bench items with a Wikipedia reference and an answer key, the key is in the vital5 intro for 11 but in the full article for 26, and the full-article pack already exists (`boar-wiki-en-00…14`, built 2026-09-26, in the app catalog) yet has never been scored.
Lane: Sonar · Status: ready-to-test; top-100k subset APPROVED and queued (QUEUE #6, Kiln builds on the mini); full 18 GB still pending r4to's disk call · Priority: A
Axes moved: quality ↑ (largest lever measured so far in this lane: the answer key becomes *reachable* for +15/39 items; how many the 1.5B then answers is the open part); truthfulness ↑ on "honesty-refusal" items that become answerable with a source (2018 World Cup, population of Canada; the post author's own rubric note: "BOAR with full Wikipedia should answer France with a source"); retrieval ± (6M articles = many more BM25 distractors; precision may drop, see failure modes); latency ↓ risk (15 packs searched per question; UNKNOWN); resources: disk +18 GB (fits the 50 GB rule with models: Android 4B ~2.5 GB + packs), RAM: SQLite page cache + 15 open DBs (UNKNOWN on a 4 GB iPhone).
Fits BOAR? Built and wired already: `src/rag/wikiEnPacks.ts` (0cfd4a77) lists 15 shards with sha256 and pinned Hugging Face URLs (`r4topunk/boar-packs` @6e9afe96…), "the app searches every installed pack, so a phone can hold any subset". Shard 00 manifest: 1.21 GB, 390,522 articles, 1.92 M chunks, lead vectors included; total of the 15 manifests 18.03 GB; top 1,000,000 articles by pageviews in full, leads for the rest (`params.fullTop = 1000000`, `run-en-shards.log`). Offline. Android ≤ 12 GB: fine on disk. iPhone 4 GB: disk fine; memory and latency are the questions.
Evidence:
- **Own measurement, 2026-10-01** (`sonar/exp/03-intro-vs-body-coverage/`, `run.py`, `coverage.json`, `result.txt`): bench-60 public split, items with an `en.wikipedia.org` reference source and precheck `must_any` groups (n = 39). Answer key present (≥ `must_k` groups) in: the vital5 chunks of the reference titles **11/39**; the full article (live plaintext extract, fetched 2026-10-01) **26/39**; body-only **15** (vit-hum-003/004/006, vit-fa-007/008/009/011/014/023/026, vit-cry-006/010/011, vit-sci-001, vit-hlt-002). Only 22/39 items have their reference article in vital5 at all. By category, intro → full: explanation 5 → 7/7, synthesis 0 → 3/3, honesty-refusal 1 → 4/5, health 1 → 3/4, reasoning 3 → 5/9, comparison 1 → 2/7.
  - Caveats: `must_any` terms are a loose proxy (literal strings; numeric comparisons whose key is "yes"/a ratio don't match any text: 13 items match neither); live Wikipedia is newer than the August 2025 FineWiki snapshot; present-in-article ≠ retrieved ≠ answered.
- Precedent: a competitor team (`competitors/a competitor team/README.md`, read 2026-10-01) ships FineWiki English as one 21.3 GB SQLite (2M most-read articles in full, leads for the rest, BM25, redirects) and runs end to end on a Pixel 8 Pro 12 GB. BOAR's format-2 search is ported from it (`wikiPack.ts` header). the post author asked for Wikipedia + Gutenberg + science (thesis R12, `rnd/lantern/vitalik-thesis.md`).
- **Miss decomposition on the shared engine** (`sonar/exp/06-miss-decomposition/`, Kiln's `ios-main-v5-t0`, kit A + vital5, 52 keyed items of bench v0.1): the answer key is in the retrieved candidates for 31; of the 21 misses:
  - **11 have the reference article installed, but its vital5 intro lacks the fact**: Mohism, Great Wall length, polar vs grizzly, Burj Khalifa/Baikal, mosquito HIV, Privacy Pools, Japan/Germany density, dengue second infection, 1900 population, Sahara, Greenland;
  - **8 have no article installed**: Harm principle, Demographics of Brazil/Russia, d/acc, EIP-7251 validator maths, Far-UVC, 2016 Olympics, physical-activity guidelines, phone-speed arithmetic;
  - **only 2 are pure retrieval misses**: Mozi, where crypto-pack noise took all slots (see `wikivoyage-lead-gate` extension), and moose vs bison.
  - Of the 8 misses whose full Wikipedia article was cached in exp-03, **6 have the key in the full article**.
  - So on this engine, knowledge coverage (body text plus missing articles) explains 19 of 21 misses; ranking explains 2.
- No run of any kit with `boar-wiki-en-*` exists in `rnd/` (grep 2026-10-01); `review/release-v110/SPEED-REGRESSION.md` lists "which Wikipedia pack was installed" as UNKNOWN for older runs.
Test in boar-eval: arm `kitA+enwiki` (kit A with `wiki-vital5` replaced by the 15 `boar-wiki-en-*` shards) vs `main` kit A, desktop-node adapter, shared engine 0cfd4a77.
- New deterministic metric, usable for every retrieval arm (no gold titles needed): **key-in-context** = item's `must_any` groups (≥ `must_k`) found in the text of the sources actually placed in the prompt (after compression). Computable from `EvalTrace.retrieval.kept` text.
- Success criterion (frozen before any run):
  - (a) key-in-context on the 39 items rises by ≥ 6 items vs `main` (exp-03 bounds the possible gain at +15);
  - (b) on the deterministic run, citation-check declines + no-source declines on bench-60 fall by ≥ 4 items, and confident-wrong (judge+Jev band) does not rise by more than 1;
  - (c) safety veto hits not up; the 5 danger items keep their route (health route unchanged);
  - (d) desktop retrievalMs p50 ≤ 2× `main`'s; report p95 (15 shards);
  - (e) peak RSS on desktop ≤ `main` + 300 MB (proxy for the phone; device numbers come only from a later coordinator-scheduled run).
  - (a) fails → stop (more knowledge doesn't reach the prompt; fix retrieval first). (a) passes but (b) fails → knowledge reaches the model but the 1.5B doesn't use it (hand to Anvil), still worth a 4B/Android reading.
- Mode: gate first; full ×2 runs if it passes (quality reading needed, effect expected well above the 0.031 noise only if (b) is large).
Cost to try: if the 15 shards are still on the Mac mini (manifests point to `<runner>/shared-data/packs/` there): ~3–4 h, no download. If not: 18 GB download from the pinned HF URLs, which needs the coordinator's OK (> 1 GB rule). Risk: medium (latency/memory unknowns), nothing irreversible.

## Expected size of the quality effect (cycle 8, `exp/10-key-vs-judge/`)

- Paired 1.5B data (main → +vital5): an item whose key enters the prompt gains **+0.17** judge ratio on average (n = 5); one that loses it drops 0.29 (n = 2).
- If the full-article pack moves a net +8 to +15 of the 57 judged items' keys into the prompt (exp-03 bound +15; exp-06: 19 of 21 misses are coverage), the predicted Δratio is **+0.02 to +0.045**. That is at or above the 2-run MDE (0.033–0.038) only at the upper end. The pass criterion keeps key-in-context (a) as the primary metric for this reason.
- On the Android 4B (never declines) the per-item gain may be larger. UNKNOWN until an Android arm with more knowledge runs.

## Passage-selection discount (cycle 9, `exp/11-passage-selection/`, engine code @0cfd4a77 replayed locally)

- How much of the article-level reach survives the engine's passage selection (lead + best sections per article)? `WikiPack.searchDetailed` on the 52 keyed items:
  - Wikivoyage + crypto packs: key in the returned passages **17**, in the same articles' full text **27**;
  - the full-text `boar-wiki-sample` pack (1 FineWiki shard, top articles in full): **16 vs 25**.
  - So ~1/3 of article-level reach is lost at section selection. Some article-level matches are spurious: tangential articles such as "Naloxegol §Side effects" for an altitude headache, or "Human overpopulation" for the 1900 population. The bigger corpus also brings BM25 distractors.
- Pre-validated alternative (not carded): choosing sections by bge-small cosine, with chunks embedded at query time and the same lead + 2 budget, reaches 16/25 vs the engine's 15/25 (+2/−1); a blend reaches 15. **No gain.** The lost third is not fixable by a cosine section picker.
- Updated expectation: discount exp-03's +15 reachable by ~35%, to **≈ +8 to +10 keys in the prompt**. That predicts Δratio ≈ +0.02 to +0.03 on the 1.5B by the exchange rate, borderline at the 2-run MDE. Larger on the 4B only if its per-item rate is higher (UNKNOWN).

## Popularity-ordered subset (exp-04, 2026-10-01, coordinator request)

Files: `sonar/exp/04-popularity-subset-size/` (`size.txt`, `size.json`, `bench-ranks.txt`).
- **Method.** Rank articles by the pack's own `views` inside `boar-wiki-sample.sqlite`, the format-2 build of one random FineWiki shard (403,973 enwiki articles, built with fullTop 1M). Global top-N ≈ sample top-(N/15.16). Pack bytes = 0.842 × text bytes (15 manifests: the FTS index is 52% of the pack). Sanity check: sample text × 15.16 = 21.9 GB vs 21.4 GB in the manifests.

  | Full articles | Text | Pack (est.) |
  |---|---|---|
  | top 50k | 2.0 GB | **1.7 GB** |
  | top 100k | 3.5 GB | **2.9 GB** |
  | top 200k | 6.3 GB | 5.3 GB |
  | top 300k | 8.6 GB | **7.3 GB** |
  | top 500k | 12.0 GB | 10.1 GB |
  | top 1M | 18.1 GB | 15.2 GB (+~2.8 GB of leads for the other 5.1M = the 18.0 GB build) |

  So "top-300k in 3–4 GB" does not hold: popular articles are long (mean 41 kB in the top 50k, 29 kB in the top 300k). 3–4 GB buys about the top 100–150k.
- **Bench reach by rank.** Ranks use single-day pageviews (2025-08-15, the builder's own input) for the 42 reference articles of exp-03's 39 items. In the top 50k: 27/42. Top 100k: **33/42**, including 11 of the 15 body-only titles. Top 300k: 38/42. Top 1M: 41/42 (Far-UVC is ~1.0M). Misses below 100k: Mozi, Invisible hand, Via Francigena, Tornado Cash, The DAO, Harm principle, Quadratic funding, Basic reproduction number. vital5 covers some of these as leads.
- **Recommended subset arm:** `kitA + enwiki-top100k` = vital5 (leads, 164 MB) + top-100k full articles (~2.9 GB). It fits the mini's ~14–19 GiB free.
- **Buildable from the existing pipeline?** Almost. `scripts/build-wiki-pack.mjs` (0cfd4a77) already:
  - streams FineWiki shards given as URLs and deletes each after use (`--delete-shards`, `--min-free-gb`), so peak disk stays ~1 shard (~2.4 GB) + output;
  - ranks by `--pageviews`;
  - keeps `--full-top N` in full.

  But it always stores leads for every other article (`--lead-chars`, default 2500). With `--full-top 100000` that adds leads for ~6M articles, so the pack would be ~6–7 GB, not 2.9 GB.

  A pure top-N pack needs either a one-line builder flag (e.g. `--skip-beyond-top N`: drop articles ranked > N) or `--lead-chars` very small. That is an engine-repo script change (Kiln's call). Input is still all 15 FineWiki shards (36 GB downloaded, streamed). Build time from `run-en-shards.log` is ~8–17 min per shard on the mini, so ~2.5–4 h. ~~UNKNOWN: whether `--lead-chars 0` already drops the article~~ **Answered (cycle 12, read `scripts/lib/wiki-pack-lib.mjs` + `build-wiki-pack.mjs` @0cfd4a77): it does not.** `leadOf(text, 0)` returns "", and `addRow` still writes `# Title` + the infobox "Key facts" (≤ 800 chars) for every one of the ~6M non-top articles, so the pack would stay several GB.
- Off-the-shelf alternative (SHELF.md): Kiwix `wikipedia_en_top_nopic_2026-09.zim` is the 50k most-demanded EN articles, 2.6 GB, CC BY-SA text. A ZIM → format-2 conversion would avoid the 36 GB FineWiki pass. It is HTML, not FineWiki text, so it needs a converter; >1 GB download needs the coordinator's OK.
- Caveat: the pageview day and the pack's `views` are different scales (single day vs scaled month), so the rank of the bench titles is an ordinal proxy.

## Subset arm that fits the mini's disk today (cycle 12)

- **Builder change (1 line + 1 flag, Kiln):** in `addWikipedia`'s `addRow`, after `const full = …`, add `if (!full && opts.dropRest) return;`. Register `--drop-rest` in `parseArgs`.
  - Redirects to dropped articles then resolve to nothing; `resolveTitle` already returns null for a missing id.
- **Build command (on the mini):**

  ```
  node scripts/build-wiki-pack.mjs --out boar-wiki-en-top100k.sqlite \
    --shards <15 FineWiki EN parquet URLs> --delete-shards --min-free-gb 4 \
    --pageviews pageviews-en-…tsv --full-top 100000 --drop-rest \
    --redirects enwiki-…-redirect.sql.gz --index enwiki-…-index.txt.bz2 --embed-top 100000
  ```

  - Add `--wikivoyage …` only if the kit's Wikivoyage pack isn't used separately.
- **Peak disk:** ~1 FineWiki shard (~2.4 GB) + the growing output (≈ 2.9 GB at the end, exp-04), about **6 GB**. That fits the mini's ~14–19 GiB free without r4to's 18 GB decision.
- **Download:** the 15 FineWiki EN shards stream through (37.7 GB transferred (15 files, HF API 2026-10-02), never stored at once). That is > 1 GB, so it **needs the coordinator's OK**.
- **Build time:** from `run-en-shards.log`, ~8–17 min per shard with full + lead text; the top-100k pass writes ~1/6 of that text, so ~2–4 h total incl. downloads (UNKNOWN; bandwidth-bound).
- **Arm:** `kitA + vital5 + enwiki-top100k` vs `kitA + vital5` (the iPhone's real kit).
  - Primary: key-in-context at `pre` (`tools/key_in_context.py`), predicted ≈ +5 to +8 of 52 keyed items: 33/42 reference articles are in the top 100k, minus the ~1/3 passage-selection loss.
  - Quality: judged on 2 seeds; predicted Δratio ≈ +0.015 to +0.025 on the 1.5B, below the MDE. So the frozen criterion keeps key-in-context primary, plus gate PASS and 0 new safety hits.
  - Also run it on the Android 4B profile, the tier near the bar.

## Frozen criterion for the approved top-100k subset arm (QUEUE #6, frozen 2026-10-02 ~07:20 BRT, before any build or run)

Arm `kitA+vital5+enwiki-top100k` vs `kitA+vital5`. Same engine 0cfd4a77 + the `--drop-rest` builder change only. Desktop adapter, iPhone profile (1.5B) and Android profile (Qwen3-4B), deterministic `-t0` pairs plus 2 judged seeds each.

- **(a) Primary.** Key-in-context at `pre` (`tools/key_in_context.py`, exact mode if protocol 1.1 has landed, else article mode) on the 52 keyed bench-v0.1 items:
  - **≥ +5 items gained** on the t0 pair;
  - **≤ 1 item lost**.
  - Both profiles share retrieval, so one count serves both. Report it per profile anyway.
- **(b) Gate.** boar-eval gate PASS vs the base on each profile and seed; 0 new safety-veto hits (rules v0.4); 0 new danger memory answers.
- **(c) Latency.** Desktop retrievalMs p50 ≤ 2× base, p95 reported. Peak RSS within +300 MB of base, reported.
- **(d) Quality: reported, not a pass condition.** Judged ratio Δ with CI on both profiles. Prediction (stated now): 1.5B +0.015 to +0.025; 4B unknown, possibly larger since it never declines. A positive 4B Δ beyond its MDE (0.030) counts as a bonus finding, not a requirement.
- **(e) Coverage sanity.** Of the 42 reference articles of exp-03's items, ≥ 30 present in the built pack. exp-04 predicts 33; fewer means the pageview ranking differs from the day-file proxy.
- **Fail (a) or (b) → not adopted.** (a) pass with (d) flat → adopt as knowledge coverage (truthfulness/citations), and report it as below MDE on quality.

## Latency risk measured before the run (cycle 13, `exp/13-retrieval-latency/`; criterion above unchanged)

- **Component profile.** Desktop CPU, 4 threads, engine code @0cfd4a77, 72 bench questions, p50:
  - query embed 5 ms;
  - Wikivoyage search 29–33 ms;
  - crypto 12–14 ms;
  - vital5 FTS 20–26 ms, cosine 6 ms;
  - **total ≈ 78 ms**, which matches the harness's 80 ms. SQLite search is ~90% of retrieval; embedding is ~6%.
- **A pack of the subset's size.** `boar-wiki-sample`, 2.13 M indexed chunks (the top-100k pack is estimated at a similar or larger chunk count), adds **+85 ms p50 / +163 ms p90** on its own. That is almost all whole-index BM25 (`bm25Candidates` 62 ms p50 / 106 ms p90); stems and named-title lookups cost 2 ms. Total ≈ 164 ms, about **2.1× the base**, so **criterion (c) (≤ 2× p50) is at risk**. Read a (c) fail together with (a).
- **Phone extrapolation (rough).** The iPhone's retrieval is ~17× the desktop's (D10 device p50 1.32 s vs desktop 0.08 s; different builds, so approximate). The subset pack could add **~+1.5 s p50** to the iPhone's ~7.9 s first token. On Android flagships, likely less (UNKNOWN).
- **Cheap path doesn't help.** Named-title passages alone reach the key on 1/52 items vs 15/52 with BM25 (`reach.txt`), so the big pack's BM25 can't be dropped.
- **Mitigations pre-tested locally (cycle 14, `exp/13-retrieval-latency/pool.txt` + cascade counts on `ios-main-v5-t0`):**
  - **Cascade (skip the big pack when the existing kit already shows enough): no free lunch.**
    - "≥ 2 distinct shown sources" skips 30/78 questions but forfeits 7 of the 28 keyed items still lacking the key;
    - "≥ 1" skips 57/78 and forfeits 16/28;
    - "a shown source with similarity ≥ 0.75" skips 16/78 and forfeits 6/28.
    - Savings and forfeits stay roughly proportional.
  - **Smaller BM25 pool for the big pack: modest win.**

    | `pool` | p50 | p90 | key in passages |
    |---|---|---|---|
    | 80 (default) | 81 ms | 151 ms | 15/52 |
    | **40** | **61 ms** | **104 ms** | **14/52** |
    | 20 | 59 ms | 105 ms | 14/52 |

    The remaining ~58 ms is the FTS MATCH floor. At ~17×, pool 40 would save roughly 0.35 s p50 / 0.8 s p90 on the iPhone (rough), for −1 key.
- **Original options (untested beyond the above):**
  - (1) Cascade: query the big pack only when vital5 + the small packs leave < 2 on-topic sources after the gates.
  - (2) A lower `pool` (80 candidates) for the big pack.
  - (3) Run its FTS in parallel with the other packs. `retrieveOne` already uses `Promise.all`, but whether expo-sqlite runs separate DBs truly in parallel on device is UNKNOWN.
  - (4) Android-only shipping first, where TTFT headroom is larger.

## Status note (2026-10-02 ~12:55)

#6 and #6b verdicts are **INVALIDATED** by the coordinator: confounded by the pack's mislabeled lead vectors, which fed the `leadSim ≥ SEMANTIC_KEEP` keep rule in `searchDetailed` with wrong vectors. The pack is fixed (sha 9123b372); the re-runs are pending. Sonar's reads below (exact (a), the loss diagnosis, the probe in `exp/14`) describe the confounded runs. The displacement mechanism (ungated keyword hits outranking gated candidates) does not depend on lead vectors, so `bigpack-relevance-gate` G1 stands.

## v2 proposal: named-article cap (pre-validated on the v1 traces, 2026-10-02 ~10:40)

- **Change (engine, `retrieve.ts` `retrieveOne`, 1 rule):**
  - apply the existing per-article cap `MAX_CHUNKS_PER_ARTICLE = 2` (`pure.ts`, today applied only inside `fuseRetrievalResults`) to the named-article passages too;
  - keep `named` first, at most 2 per article;
  - cut at `topK` instead of `max(topK, named.length)` when the named passages come from one article.
- **Why:** with k = 3 (lookup) a single named article from the big pack took every slot.
  - lan-ref-001: "Nobel Prize in Literature" ×3 displaced vital5's "Kazuo Ishiguro"; then the year rule dropped all 3, so declined.
- **Pre-validation on `ios-enwiki-s42-kic`:**
  - 18/72 items have one title holding ≥ 3 raw slots, e.g. Nobel ×3, Wikivoyage: Accra ×3 (d/acc), Population density ×3, Headache ×3, Hypothermia ×3, Burn ×3.
  - In **0** of the keyed ones does the answer key appear only in the 3rd+ passage of that title (checked on the shown passage text). So the cap costs no key on this run and frees a slot in 18 items.
  - What fills the freed slot is unknown without a run: the next fused candidate (for lan-ref-001, base raw rank 2 = Kazuo Ishiguro).
- **Criterion for `enwiki-top100k + named-cap` (frozen now; same pair design and gate as v1):**
  - (a′) exact key-in-context `pre` vs `ios-main-v5-s42-kic`: ≥ +5 gained and ≤ 1 lost;
  - (a″) lan-ref-001 has a source with "Ishiguro" in the pre-answer sources;
  - (b), (c), (e) as v1;
  - (d) quality reported only.

## Sonar's exact read of criterion (a) (2026-10-02 ~10:10; Kiln's official verdict decides)

`tools/key_in_context.py`, exact at `pre` (the `-kic` traces carry passage text). `ios-main-v5-s42-kic` → `ios-enwiki-s42-kic`, 52 keyed items. The pre-answer sources are route-determined (seed-independent), so one seed suffices for (a).

- **pre 13 → 17 (net +4): gained 7, lost 3.** (a) requires ≥ +5 gained (✓ 7) **and ≤ 1 lost (✗ 3)**, so by the letter **(a) FAILS**.
  - Gained: lan-ref-004 Iceland area, lan-ref-005 2016 Olympics, lan-rsn-001 Great Wall, vit-cry-010 DAO hack, vit-hlt-003 dengue, vit-hum-001 Mozi, vit-hum-004 Gríma/Saruman.
  - Lost: lan-ref-001, lan-rsn-007, vit-cry-011.
- **Diagnosis of the 3 losses:**
  1. **lan-ref-001 (Nobel 2017): real regression, named-article crowding.**
     - The big pack's named article "Nobel Prize in Literature" took all 3 raw slots and displaced vital5's "Kazuo Ishiguro".
     - `onTopic`'s year rule then dropped all 3 (no "2017" in them): `off-topic-dropped-3`, `no-good-source`, declined.
     - Fix candidates: cap the passages taken from a single named article when other sources exist (the named path brings up to 5 ranks); or apply the year/proper-noun check before the top-K cut.
  2. **lan-rsn-007 (Berlin Wall years): right article, key cut by compression.** The full "Berlin Wall" article replaced the Wikivoyage guide, but `context:1420->293` kept sentences without 1961/1989.
  3. **vit-cry-011 (Terra/LUNA): metric artifact.** The new sources ("Terra (blockchain)", "Do Kwon") are better than the base's generic Stablecoin/Cryptocurrency chunks; the key-term proxy doesn't match their compressed text.
- **Substantive read:** 7 gains vs 1 real regression (+ 1 compression loss, + 1 artifact). Raw is in article mode with 15 unresolved big-pack titles, so the raw counts are not usable for this arm.

## Early sanity read of the first #6 runs (Sonar, 2026-10-02; NOT the criterion; Kiln's key-in-context runs decide)

`ios-enwiki-s42` (kit + vital5 + top-100k) vs `ios-main-v5-s42`, pre-answer sources on the 21 items whose key was missing in exp-06:
- **New sources on 9/21.**
  - Clear wins: vit-hum-001 (Love, Mohism; declined → answered); lan-ref-005 (2016 Summer Olympics; declined → answered); vit-hlt-003 (Dengue fever, the full article, instead of the Wikivoyage guide); lan-rsn-001 (History of the Great Wall of China); lan-cmp-004 (Bison, European bison).
  - Still missing, as the ranks predicted (exp-04): Harm principle (rank ~340k), Far-UVC (~1.0M), d/acc.
- **Possible regressions to watch in the official read:**
  - lan-cmp-001: "Russia" replaced by "Foreign relations of Russia", answered → declined;
  - lan-hlt-003 and lan-exp-005: answered → declined (lan-exp-005 keeps "Sahara").
  - These are single-seed reads and may be noise. The comparison card's `pinned` sides (v2.1) would protect lan-cmp-001's sides.
- Trace sources carry no text yet (protocol 1.0), so exact key-in-context waits for Kiln's `-kic` runs.

## Details

Why intros are the binding constraint: vital5 holds lead sections only (format 1, `source = "Wikipedia Vital Articles level 5 introductions"`). Leads summarize; the bench asks for mechanisms ("how did Mencius attack it"), numbers (population in a census year, heights, weights) and specifics (who won the 2018 final, why Gríma kills Saruman). Those live in body sections. The comparison failures from exp-01 also need body facts (an elephant's weight is in "Description", not the lead).

Interactions with the other Sonar cards:
- `wikivoyage-lead-gate`: the same keyword-bypass applies to enwiki shards (large-pack hits aren't cosine-gated); with 6M articles the noise problem gets bigger. The enwiki shards carry lead vectors only for the top `embedTop` articles (sample pack: 33,333), so the gate there needs the median rule or a different signal. Measure noise in this arm's traces before extending the gate.
- `comparison-entity-split-retrieval`: per-side retrieval plus full articles is the combination that should fix numeric comparisons (both sides + the attribute section).
- Format-2 named-article path (`titlesInQuestion`) gets much better coverage with 6M titles + redirects, which helps one-entity questions directly.

What would make it fail:
- BM25 over 6M articles surfaces more distractors; `namedMinShare` and term coverage were tuned on vital5-scale data. Key-in-context (a) detects this.
- Latency: 15 FTS5 queries + block decompression per question. The format-2 search reads text only for top candidates ("Text is read only for candidates in rank order"), which bounds the cost, but 15× is unmeasured.
- iPhone 4 GB memory: 15 open SQLite connections with page caches; LRU block cache per pack (`BLOCK_CACHE`). UNKNOWN.
- The model: with more relevant text the 1.5B may still decline (citation checks). Then the gain shows on the Android 4B/Gemma reader first.

UNKNOWN:
- Whether the shard files are still on the Mac mini (I don't run commands there; the coordinator/Kiln can check `ls <runner>/shared-data/packs/boar-wiki-en-*.sqlite`).
- Which shard holds which articles (FineWiki shards are not topic-ordered), so a partial install (e.g. 3 shards) gives a random 1/5 of Wikipedia, not "the important part". A pageview-ordered re-shard would make partial installs useful; possible later card.
