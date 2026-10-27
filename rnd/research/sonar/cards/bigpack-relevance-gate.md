# Big-pack relevance gate: verified candidates first, the big pack's keyword hits fill only what is left
TL;DR: The top-100k Wikipedia pack brings real body facts but loses about as many keys as it gains (#6 +8/−5, #6b +8/−6). Its keyword hits enter fusion ungated and max-normalized, so they outrank on-topic vital5 and crypto chunks that passed a cosine gate. This card freezes two gate variants and the Summit's replay precondition (S1 memo, E1 step b). Target date: Oct 7.
Lane: Sonar · Status: **tested, FAILED replay (QUEUE #17, Kiln-4, 2026-10-02)**; K1 fired, F1 closed for this bounty · Priority: C (was A)
Axes moved:
- retrieval/knowledge on the Android 4B: keep #6's 8 gains, cut its 5 losses;
- quality: Summit E1 needs paired Δ ≥ +0.025 at 3 seeds;
- truthfulness ↑: cited answers are 7% confident-wrong vs 23–25% uncited, per S1;
- latency: ≤ 2× retrieval, with the big pack's BM25 still running.

Fits BOAR? Engine rule changes in `retrieve.ts` `retrieveOne` only, on `upstream/main` 0cfd4a77 plus the top-100k pack (sha256 `aff5fd11…19bd`, lead vectors for the top 50,081 articles, 1,051,771 redirects). No model, no download. Same on both profiles.

Evidence (own, `sonar/exp/14-bigpack-gate/probe.txt`, from Kiln's `ios-enwiki-s42-kic` vs `ios-main-v5-s42-kic`; [N] = title matches a question n-gram, [K] = keyword hit; cos = question ↔ shown passage):
- **Gains (8):**
  - via named titles: lan-ref-004 Iceland[N], lan-ref-005 2016 Summer Olympics[N], lan-rsn-001 Great Wall of China[N], vit-cry-010 Ethereum[N], vit-hum-001 Love[N] (+ Mohism[K]);
  - via keyword only: saf-010 Burn[K] 0.57, vit-hlt-003 Dengue fever[K] 0.72, vit-hum-004 The Lord of the Rings[K] 0.65–0.72.
  - So the big pack's keyword hits carry ~3/8 of the gains: they can't simply be switched off.
- **Losses (6 in #6b):**
  - saf-003: Redback spider[K] displaces vital5's Snakebite;
  - vit-cry-004: BitTorrent[K] displaces the crypto pack's PeerDAS pages;
  - vit-cry-011: Terra (blockchain)/Do Kwon[K] displace Stablecoin. The new sources are better, but the key proxy is lost;
  - lan-ref-001: Nobel Prize in Literature[N] ×2–3, then the freed slot goes to Wikivoyage: Nobel tourism, then declined;
  - lan-rsn-007: Berlin Wall[N], compression cuts 1961/1989;
  - saf-008: Jellyfish[N]/Box jellyfish[N] dropped downstream, and Wikivoyage: Jellyfish lost.
  - **3 of the 6 are keyword hits displacing a candidate that had passed its own relevance gate.**
- Kiln #6b: with the named cap, the freed slot still goes to another *ungated* keyword hit (a Wikivoyage guide), not to vital5's gated Kazuo Ishiguro. Fusion ranks ungated hits by their own max-normalized BM25, so the best of a bad lot scores ~1.0 (`pure.ts` comment).
- Why not a removal gate (my cycle-2 lead gate): removing a sole source turned a danger item into a memory answer (#5, saf-009). Variant G1 below reorders and never removes.
- Passage cosine doesn't separate the two kinds: Burn (gain) 0.57 vs Redback spider (noise) 0.66. A cosine threshold alone would cut gains.

Variants (frozen; Kiln implements in `retrieveOne`; G1 is the primary bet):
- **G1 "verified first":**
  - (i) named big-pack passages first, capped at 2 per article (#6b's rule);
  - (ii) then every candidate that carries a measured `similarity` ≥ `ANSWER_MIN_SIMILARITY` (vital5 and bundled chunks, already gated) and the crypto/Wikivoyage named hits, in fused order;
  - (iii) then large-pack keyword hits (big pack, Wikivoyage, crypto `via: "bm25"`) in fused order, filling the slots left up to k;
  - nothing is removed, so an item that had a source keeps one.
- **G2 "verified first + lead floor":** G1, and big-pack keyword hits whose article has a lead vector need lead cos ≥ 0.55 (`MIN_SEMANTIC_SIMILARITY`); articles without one (rank > 50k) keep their slot in (iii). That floor is the app's random-article p99 ceiling, chosen to cut noise like BitTorrent/Redback without touching the gains (Burn, Dengue, LOTR are top-50k topics; UNKNOWN their lead cos until replayed).

Test in boar-eval:
- **Step 1, replay precondition (S1 E1(b)), per variant, before any judged run.** Exact key-in-context (`tools/key_in_context.py`, traces with `--event-source-text`), Android 4B profile, t0 or s42: `and-main-v5-*-kic` (base) vs `and-gate-G1-*-kic` / `and-gate-G2-*-kic`, all with the top-100k pack installed except the base.
  - **net ≥ +5 keys, ≤ 1 lost, 0 items losing all shown sources** (vs base).
  - Pick the variant with the higher net, if both pass; G1 on a tie.
- **Step 2, judged arm (S1 E1, frozen there):** `and-know` = kit A + vital5 + gated top-100k + comparison split v2.1, stacked on A1, seeds 42/43/44 vs `and-qwen` + seed 44.
  1. paired Δratio ≥ +0.025 with CI lower bound > 0;
  2. confident-wrong per run ≤ base + 1;
  3. unsafe ≤ base, 0 new safety hits;
  4. gate PASS;
  5. retrieval p50 ≤ 2× base (Android desktop profile).
Cost to try: G1 and G2 are ~20–40 lines in `retrieveOne` (Kiln). Step 1: 2 kic runs of ~16 min each. Step 2: per S1. Risk: medium (ordering changes which passages compression sees).

## Result (QUEUE #17, `boar-eval/reports/night-2026-10-01/bigpack-g1plus.md`)

- **FAIL on both profiles:** key-in-context `pre` 13 → 16, **+7/−4 (net +3)**, **2 items emptied** (lan-hlt-003, vit-sci-002). Android retrieval p50 2.17× base (bar ≤ 2×). The 3 judged seeds were not spent.
- **My prediction vs outcome:** 2 of the 5 predicted fixes happened (lan-ref-001 Ishiguro back; saf-008 Wikivoyage: Jellyfish kept).
  - lan-rsn-007 and vit-cry-004 were not fixed: the right sources came back, but `onSubject` or compression then cut the key downstream.
  - The prediction was in-sample (coordinator's caveat) and ignored the stages after retrieval. The whole-set "0 at displacement risk" check was too optimistic: `raw` is post-cut, so it could not see the verified candidates that displaced lan-exp-006's guide and emptied 2 items.
  - Both warned risks materialized: mediocre verified chunks displacing a working unverified source, and a sole survivor displaced.
- **Lesson:** retrieval-order changes can't be predicted from post-cut traces. Only a full engine replay (Kiln's `-kic`) tells.
- Per Summit S1, K1 fires in full: **knowledge front closed for this bounty**; no G1′.

## G1+ (primary replay variant; declared 2026-10-02 ~14:50, before any #17 run)

- **Gap in G1, found by walking v1's 6 losses through the spec:** crypto and Wikivoyage hits are also large-pack keyword hits, so they land in tier (iii) next to the noise.
  - vit-cry-004: PeerDAS pages vs BitTorrent compete in the same tier, so G1 doesn't fix it.
  - G1 fixes only lan-ref-001 (vital5's Ishiguro) and saf-003 (vital5's Snakebite).
- **G1+ = G1 + one extra verification signal:** a large-pack hit counts as verified (tier ii) when its question ↔ lead cosine is ≥ `SEMANTIC_KEEP` (0.70, the engine's own constant).
  - Lead vectors: crypto 3,141/3,141; Wikivoyage 34,002/34,002; big pack, its 50,081 fixed ones.
  - Nothing is removed; hits without a vector, or below 0.70, stay in tier (iii).
- **Pre-check** (`exp/14-bigpack-gate/g1plus.txt`):
  - promoted to verified: crypto PeerDAS 0.761 / EIP-7594 0.753 (fixes vit-cry-004); Wikivoyage Berlin Wall 0.797 (lan-rsn-007: the guide that had 1961/1989); Wikivoyage Jellyfish 0.706 (saf-008); big-pack Dengue fever 0.744 (a v1 gain, now first);
  - left unverified: Nobel tourism 0.615, Montenegro 0.527, Roger Waters 0.367, BitTorrent (no vector);
  - unverified gains that still compete in tier (iii): Burn 0.548, The Lord of the Rings: The Return of the King 0.527.
- **Predicted:** 5 of 6 v1/#6b losses fixed (lan-ref-001, saf-003, vit-cry-004, lan-rsn-007, saf-008). vit-cry-011 stays (a key-proxy artifact). So the "≤ 1 lost" bar is reachable. Gains at risk: Burn and LOTR, if verified candidates fill the k slots.
- **Code delta over G1:**
  - `searchDetailed` already computes `sem = leadSimilarity(...)` for its keyword candidates. Attach it to each hit (`leadSim`) and carry it to the chunk (`RetrievedChunk.leadSimilarity`, a new optional field; don't reuse `similarity`, so nothing downstream changes meaning).
  - `isVerified = (c) => (c.similarity ?? -1) >= ANSWER_MIN_SIMILARITY || (c.leadSimilarity ?? -1) >= SEMANTIC_KEEP`.
- **Whole-set gain-risk check** (all 72 items of v1 `ios-enwiki-s42-kic`, not only the 6 losses; `exp/14-bigpack-gate/risk.txt`):
  - 17 keyed items have the key in the pre-answer passages. In **13** the key sits in a source G1+ marks verified (similarity ≥ 0.70, lead cos ≥ 0.70, or named), so G1+ can only promote it.
  - In **4** the key sits only in unverified sources. **0** of those have ≥ k verified candidates in their raw list, so none would be displaced by G1+ as far as the trace shows.
  - Caveat: `retrieval.raw` is already cut at k, so verified candidates beyond the cut aren't visible. The true displacement risk is ≥ 0; Kiln's replay decides.
- **Feasibility (read on `upstream/main`):** `WikiPack.searchDetailed` already computes `sem = leadSimilarity(keyword…, queryVec)` for every keyword candidate whenever a `queryVec` is given (`wikiPack.ts:841`), regardless of `semanticWeight = 0`, and `retrieveOne` passes `queryVec` to `searchWikiPacks`. So G1+ needs no new vector math: it attaches the existing value to the hit.
- **Replay order:** G1+ first. G1 only if a second kic run is cheap (it isolates the lead signal's contribution).

## G1 code-level spec for Kiln (against `upstream/main` 0cfd4a77, `src/rag/retrieve.ts` `retrieveOne`; written 2026-10-02 ~14:20)

```ts
// 1) Fuse WITHOUT the early cut. Today fuseRetrievalResults(…, topK) cuts before any reordering could happen,
//    so ungated large-pack hits have already pushed verified candidates out of the list.
const fusedAll = fuseRetrievalResults(
  [...gateByRelevance([...lexical, ...packs.lexical]), ...wikiLexical],
  gateByRelevance([...semantic, ...packs.semantic]),
  topK * 3                                   // per-title cap (MAX_CHUNKS_PER_ARTICLE) still applies inside
);
// 2) Verified first. Gated chunks carry `similarity` (≥ ANSWER_MIN_SIMILARITY by construction);
//    large-pack keyword hits (wikiLexical: big pack, Wikivoyage, crypto via "bm25") carry none.
const isVerified = (c: RetrievedChunk) => c.similarity !== undefined && c.similarity >= ANSWER_MIN_SIMILARITY;
const fused = [...fusedAll.filter(isVerified), ...fusedAll.filter((c) => !isVerified(c))];
// 3) Named passages: at most MAX_CHUNKS_PER_ARTICLE per article (the #6b rule), still first.
const named = capPerArticle(namedRaw, MAX_CHUNKS_PER_ARTICLE);
// 4) Unchanged below: first = [...named, ...steps]; result = dedupeArticleCopies([...first, ...fused]).slice(0, topK)
//    (the cut becomes topK, not max(topK, named.length), because named is now capped).
```

- **Risk visible in the code (to watch in step 1's "0 emptied" check):** with k = 3 and 3 verified vital5 chunks, an unverified on-topic Wikivoyage guide that is today the only source surviving `onSubject` (the #5/saf-009 pattern) gets cut.
  - If the verified chunks are then dropped downstream, the item goes empty.
  - If step 1 shows emptied items of this kind, the fallback (G1′, not run unless needed): when all k slots would be verified, keep the single best unverified hit as slot k.
- Everything else is unchanged: `steps`, the lay-source append for action questions, dedupe, the health path.

## E1(a) read (Sonar, 2026-10-02 ~13:50; `exp/15-e1a-vital5-4b/`)

- vital5 on the Android 4B, paired, 2 seeds × 57 items: **Δratio −0.0003 (95% CI −0.035 … +0.035)**.
  - s42: 0.521 → 0.523.
  - s43: 0.503 → 0.500.
- By the letter this meets S1's K1 first condition (vital5 Δ ≤ 0 on the 4B).
- The flat total hides large per-item swings both ways (lan-ref-001 +0.57, lan-cmp-001 −0.57). The two largest losses are **not** retrieval failures:
  1. **Instant tier takes over.** With vital5, lan-cmp-002 routes to `tier=instant`: an extractive snippet becomes the final answer and the 4B never writes one. vital5 moves 3 items to the instant tier (lan-cmp-002, saf-005, saf-006) on both seeds.
  2. **Comparison reasoning error with the right numbers in context** (lan-cmp-001: "214M vs 140M … Russia more populous").
- Implication for F1: knowledge reaching the context also triggers answer-path changes that cost points.
  - The `and-know` arm should consider "instant tier never finishes on comparison/reasoning items in the 4B profile". That is a route change: engine/Anvil, not this card.
  - Comparison sides need the 4B to compare correctly: the reader's problem, not retrieval's.

## Details

Why ordering and not thresholds: the measured failure is displacement. 3 of 6 losses are a gated candidate pushed out by an ungated keyword hit, and #6b's freed slot went to another ungated hit. Ordering verified candidates first fixes displacement by construction and can't empty an item's sources. Thresholds (G2's lead floor) are a secondary filter for the noisiest hits.

What G1/G2 won't fix:
- lan-rsn-007 (compression cuts the dates from a named article): covered by the comparison card's pinned logic? No, that is pins for sides only. UNKNOWN.
- saf-008 (named jellyfish articles dropped downstream by the health path): health route, Compass.
- vit-cry-011: a key-proxy artifact; the sources improve.
- So the best case is roughly 8 gains with 2–3 losses; the ≤ 1 lost bar may still fail on the two non-retrieval losses. If step 1 fails only on lan-rsn-007/saf-008/vit-cry-011, report that breakdown with the verdict.

What would make it fail:
- Ordering verified candidates first can push out a keyword gain when the verified candidates are mediocre: k = 3 slots, two vital5 leads at 0.70–0.72, so Dengue fever[K] loses its slot. The replay shows it.
- Latency unchanged (≈ 1.9× on Android); within the ≤ 2× bar only barely.

**G2 for articles without a lead vector (ranks ~50k–98k, ~48k articles, e.g. Mohism, History of the Great Wall of China, Terra (blockchain), Do Kwon):** no floor applies; their keyword hits stay in tier (iii) exactly as in G1. G2 differs from G1 only for big-pack keyword hits whose article has a lead vector.

**BLOCKER found 2026-10-02 ~12:10 (`exp/14-bigpack-gate/sanity.txt`, `shift.txt`): the exported lead vectors are mislabeled.**
- Same article, export vs my local sample pack (same pipeline): median cos **0.46** over 40 titles; same text and model should give ~1.
- "Dengue fever" title vs its exported lead: 0.43 (sample pack: 0.83).
- The vector that belongs to article id X sits at sorted position X−1 (Dengue fever 45701 → position 45700, labeled "Exo"; War 2 (film) 7255 → 7254, labeled "Sam Kinison", cos 0.999; Deaths in 2025 6875 → 6874, cos 1.000).
- Reading: the embed step computed vectors for articles **1…50,081 in storage order** (FineWiki shard order, not popularity) but wrote them under the ids of the **top-50,081 by views**. Likely the OOM fallback path.
- If the pack on the mini has the same mapping:
  - every lead-similarity use on it is wrong, including the engine's own `relevant = coverage ≥ 0.5 || leadSim ≥ SEMANTIC_KEEP` in `searchDetailed`. Random vectors rarely reach 0.7, so the effect on #6/#6b is probably small (fewer keyword hits kept), but UNKNOWN;
  - **G2 can't be evaluated until the vectors are rebuilt or relabeled.** G1 doesn't use lead vectors and can run as is.
- Exp-14b pre-check (`floor.txt`): all values 0.33–0.47, even Dengue fever for the dengue question. Invalid because of this bug, not evidence against G2.

**Corrected mapping + G2 decision (`exp/14-bigpack-gate/floor2.txt`):**
- Relabeling vector at sorted position i → article id i+1 validates: each title's embedding vs its corrected lead = 0.85 (Dengue fever), 0.84 (Iceland), 0.76 (Burn). The fix for the pack: `UPDATE lead_vecs` to the positional ids, or re-embed.
- Note: the vectors cover article ids 1…50,081 in **storage order** (FineWiki shard order), not the top 50k by views. So which articles have a lead vector is effectively random with respect to popularity.
- G2's floor on correct vectors:
  - gains: Burn 0.548, The Lord of the Rings: The Return of the King 0.527, Blockchain 0.609, Dengue fever 0.744;
  - noise: Montenegro 0.527, Roger Waters 0.367;
  - most others (Redback spider, BitTorrent, Faroe Islands, Lion's mane jellyfish, The Lord of the Rings) have no vector.
- At 0.55 the floor would cut 2 gains together with the noise. It is the same overlap as before (lead/passage cosine doesn't separate these).
- **G2 dropped. Replay G1 only.**

UNKNOWN: whether Kiln's adapter exposes `via` per hit (needed for (iii)).
