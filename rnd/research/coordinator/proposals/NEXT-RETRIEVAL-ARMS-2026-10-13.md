# NEXT-RETRIEVAL-ARMS — turning ORACLE-ST's +0.095 headroom into a measured gain (2026-10-13 23:5x; opus/high design agent, 0 LLM / 0 judge / 0 paid, public replay outputs only; coordinator saved the text; for the loop's BACKLOG re-rank — criterion draft at the end, NOT frozen)

**TL;DR:** most of the 137 unreached items are not a vocabulary problem. On 56 the fact's ARTICLE is already in the pack's BM25 top-80 but the wrong chunk wins; on 95 the fact chunk fails the text relevance gate (coverage ≥ 0.5, wikiPack.ts:857) even if ranked first; on 20 it is reached and then dropped by the keep step. Doc2query only changes the index, so it hits both walls, is inflated on this set (items were written from chunks by an LLM — the same generative process), and costs ≈ 264–273 mini-hours of 4B generation for the 9 packs (travel 40 h, ethereum 30, bitcoin 22, simplewiki 150; the five small packs ≈ 22.5 h). **Rank 1 = HEADPASS-ST:** append, without displacing anything and outside the keep step (the ORACLE-ADD append path), the chunks at positions 1–2 of the top retrieved pack article (A2); declared variant X2 adds ST2's dense extra-2 the same way. Projected fact-present 35 → 75 (A2, cut 7) / 43 → 117 (D + A2, ST2 tree); projected Δ +0.024…+0.038 (A2) / **+0.045…+0.070** (X2); 0 LLM build. Scripts: arms/h8st/tools/diag/ (diag137.py → diag137.json sha 8feeb0f1…, simcap.py, pos.py, arthead.py, arthead_cut7.py, union_st2.py, peek.py).

## 1. Why the 137 are unreached (all 137 classified automatically; 14 read by eye)
Method: lists from the cut-7 replay (h8st/runs/st-<pack>.ref.jsonl: raw, pool = extra retrieve(q, 8), kept, diag sub/comp/ground); fact chunks from oracle-facts.json; the 137 = ORACLE-ST's "S did not keep a fact chunk" split; ranks from a Python replica of bm25Candidates + queryTerms + the coverage gate run read-only on the published packs (FTS5 stems, idf from df / fts5vocab; df ≤ 2 % with keepMin 3, wikiPack.ts:483-488; `bm25(fts, 2, 1, 1)` LIMIT 80 + 0.5·log10(1 + views), :421, :663-681; per-article cap 2, :663; gate coverage(title + text) ≥ 0.5, :337-341, :857-858; limit = max(k, …), :835). Caveat: the lead-cosine ≥ 0.7 gate pass (wikiPack.ts:226, :857-858; needs the query embedding, retrieve.ts:167) is not modelled → "in top-80 but not raw" is one merged group.

| class (137) | n | SE | topic | what fails |
|---|---|---|---|---|
| in raw, dropped by grounding (onSubject/onTopic) | 16 | 11 | 5 | keep step: termCoverage ≥ 0.75 on long paraphrased questions (context.ts:320, :702-746; answer.ts:1038) |
| in raw, dropped by compression / health filter | 1 / 3 | 1 / 2 | 0 / 1 | keep step (answer.ts:1027) |
| in the pack's capped top-80 but not in raw | 33 | 17 | 16 | gate cov < 0.5: 21; passes the gate but cut in fusion / by kit or peer passages: 10; own-pack rank: 2 |
| **in top-80 but cut by the per-article cap 2** (article found) | **37** | 21 | 16 | 2 sibling chunks of the same article outrank it (median raw bm25 rank 19) |
| **article found (top-80 or raw) via other chunks; fact chunk rank > 80** | **19** | 15 | 4 | wrong section of the right article; 5 contain no query term |
| lexical: matched but rank > 80 (median 480) | 12 | 10 | 2 | weak term overlap |
| lexical: no query term in the chunk | 15 | 13 | 2 | vocabulary gap ("high blood sugar" vs Hyperglycemia; "free bitcoin sites" vs faucets) |
| kept on the cut-7 tree (tree difference vs ST2 OFF) | 1 | 0 | 1 | — |

Coordinator buckets: lexical miss 27 · in raw, dropped by keep 20 · crowded out by kit/peers ≤ 12 · **article found, wrong section 56** · the other 21 fail the relevance gate. Side facts: the fact chunk's text coverage is ≥ 0.5 on only 42/137 (a ranking/index lever alone brings up chunks the gate then onTopic drop; the gate sees displayed text, not index columns, wikiPack.ts:578-585). Position: SE fact chunks at article position 1 (first chunk after the question = top answer's start) on 59/90, ≤ 2 on 83/90; topic at the lead on 19/47, ≤ 1 on 35/47. Gate/cap relaxation alone (simcap.py): fact in the first 8 gate-passing candidates 49 → 87 with cap ∞ and gate 0.35, but those chunks still land behind k = 4 raw slots and the keep step.

## 2. Candidate levers
Per-item conversion: each item that newly has the fact chunk in the prompt ≈ **0.11–0.17 raw** (ORACLE ADD +0.095 × 180/152; ST2 +0.017 × 180/18) → **+0.03 on the 180 needs ≈ +32…+49 fact-present items**; the H8 "kept ≥ OFF + 15" bar bought only ≈ +0.009…+0.014 (< MDE).

| lever | tree | fact present (OFF →) | reach raw ∪ appended | added chunks/item | projected Δ raw |
|---|---|---|---|---|---|
| A1 = top pack article's chunk at pos 1, appended | cut 7 | 35 → 64 | — | 0.65 (≈ 447 chars) | +0.018…+0.027 |
| **A2 = pos 1–2, appended** | cut 7 | **35 → 75** | 55 → 80 | 1.22 (≈ 817 chars) | +0.024…+0.038 |
| A2 | ST2 tree (wt/packs) | 43 → 86 | 67 → 92 | 1.36 | +0.026…+0.041 |
| D = ST2 dense extra-2, appended (no keep drop) | ST2 tree | 43 → 90 | 67 → 108 | 1.71 | +0.029…+0.044 |
| **D + A2** | ST2 tree | **43 → 117** | 67 → **121** | 2.88 | **+0.045…+0.070** |
| residual after D + A2 | — | 63 missing: lexical 24, article found / not head 25, gate 7, fusion 4, keep 3 (SE 43) | | | doc2query's remaining target |

- **HEADPASS (rank 1):** first raw passage from a user-installed (non-kit) format-2 pack → append its article's chunks at positions 1–2 (minus those kept) after grounding, as ORACLE-ADD appends (oracle.vs-cut7.patch answer.ts hunk): nothing displaced, appended chunks skip onSubject/compression. Literature: parent-document / small-to-big retrieval; ONLY − S +0.115 says the rest of the context is harmless once the fact is present. Cost: build 0 h, index +0 B, one cached article read per query, prompt +≈ 200 tokens p50. Reopens R47 (new mechanism) and SECTIONHIT (LEDGER-FIXES row 70, provisional; on v0.2 the misses were article-level, on the 180 the article is found on 56/137).
- **Dense sidecar extra slots + keep pass-through (R46 + R47 as one arm):** ST2's two-stage dense path (lead top-50 → chunk cosine ≥ 0.55, D = 2) with appended chunks passed through (ST2's keep step lost 47 of 108 reached). Sidecars ≈ 400 B/chunk: travel 62 MB, ethereum 47, bitcoin 34, outdoors 13, firstaid 9, health 8, factbook 4, medlineplus 1, simplewiki 249 → ≈ 427 MB (+47 % over 900 MB); query p50 ×1.44 (simplewiki scan p50 108 ms, ST2-GATE G3); build minutes from the int8 caches if they still exist (UNKNOWN — shared-data/packs/work was deleted on the MacBook 10-13; the mini copy status unknown), else a bge-small re-embed. Best as HEADPASS variant X2.
- **doc2query-- (rank 3):** ≈ 5 questions per chunk from the 4B, drop the lowest 30 % by bge-small cosine, keep ≤ 3, index as a 4th FTS column (reuses h8st's fts_h8 tooling); only helps if the relevance gate (wikiPack.ts:857) and onTopic also count the questions (else ≤ 42/137 survive); prior +3–16 % BM25 recall (Doc2Query--), plausible +5…+15 of the 63 residual, inflated by generator-style overlap; index +5–17 %; build 4B at 0.92 s/chunk (BACKLOG estimate, unmeasured): 9 packs ≈ 1.03 M chunks ≈ 264–273 h (kit crypto 14 h, wikivoyage 140 h); step 0 on the five small packs ≈ 22.5 h. Reopens R6 NOTES35's new-mechanism clause and the H8 (b) row. Prompt + 20-chunk dry-run spec: `Passage from "{pack name}", article "{title}", section "{section}":\n<<<{chunk text}>>>\nWrite 5 different questions a person might type that THIS passage answers. Use everyday words a non-expert would use, including plain synonyms of any technical term. Each question must be answerable from the passage alone. One question per line, no numbering, at most 20 words each.` (Qwen3-4B-Instruct-2507 Q4_K_M, temp 0.7, top_p 0.9, max 160 tokens, seed 42, -np 4); dry run = 10 fact chunks (5 SE, 5 topic) + 10 random, report s/chunk (stop if > 1.5), parse rate (stop if < 90 % yield 3–5 questions), duplicate rate, filter keep rate, max token-Jaccard between each fact chunk's questions and its self-test item (inflation flag).
- **BM25DEPTH (rank 4):** per-article cap and gate relaxation; 0 B; needs extra slots + pass-through to matter; overlaps HEADPASS on the 37 cap items; reopens R44's "filter relaxations".
- **SE duplicate-question titles as 0-LLM human doc2query (rank 5):** PostLinks not on the MacBook (mini UNKNOWN); article-level only.

## 3. Ranked recommendation
1. **HEADPASS-ST** (A2; X2 = D + A2): the cheapest mechanism that targets the 56 article-found items and the 20 keep drops together; the only one whose projection clears the MDE (X2) at 0 LLM build.
2. doc2query-- on the residual, only after HEADPASS, scoped to SE packs, with the gate seeing the expansions; validate on items not written from chunks (v0.3 pack-matched) before any claim.
3. BM25DEPTH and the stand-alone dense sidecar (subsumed by 1).

## 4. Criterion draft for HEADPASS-ST (template format; to be frozen by the coordinator that launches it)
```
# HEADPASS-ST: does appending the top pack article's neighbour chunks (and dense extra slots) without displacement and outside the keep step convert ORACLE-ST's headroom on the 180? (frozen <date time>, coordinator)

## Tags
Tags: none

## Question
On the 180 public self-test items (one pack installed, claim kit, cut 7) the fact chunk is in the prompt on 35 (cut-7 replay) / 43 (ST2 OFF); ORACLE-ADD shows +0.095 when it is. Diagnosis (h8st/tools/diag/diag137.json): 56/137 misses have the fact article in the pack's BM25 top-80 but the wrong chunk wins; SE fact chunks sit at article position 1 on 59/90, <= 2 on 83/90. Arm X1 = settings.packHeadPass "a2": after grounding, append the chunks at positions 1-2 (by start) of the article of the first raw passage from a non-kit format-2 pack, skipping chunks already kept (ORACLE-ADD append path; no displacement; not subject to onSubject/compressContext; health-strict items: appended chunks must pass onHealthTopic; never multipass; never for boar-crypto / boar-wikivoyage-en). X2 = "a2+dense": X1 plus ST2's dense extra-2 (packdense2-only.cut7.patch two-stage path, non-kit sidecars only), appended the same way (<= 4 appended). Control C = S (cut 7, settings absent). Use: rank-1 retrieval-conversion lever; product setting default off.

## Fixed inputs
- Tree kiln-local/be-0cfd4a77-cut7-headpass = cut 7 + headpass.vs-cut7.patch (sha <..>) [+ packdense2-only.cut7.patch sha <..> for X2]; settings absent = byte-identical (raw, kept, prompt sha) on 180/180, v0.1 60/60, v0.2 110/110.
- Control rows: arms/packs/selftest-runs/st-<pack>-cut7-s42.{traces,judgments,judgments.opus}.jsonl (S; Haiku + Opus exist).
- Replays: copy of arms/h8st/tools/replay-h8.ts with --modes off,x1,x2,off; v0.1 public kit-only and v0.1 + boar-simplewiki-en installed; v0.2 kit-only script-only (identity counts only; EXPOSURES row).
- Generation: 4B cut 7 on the MacBook (run_oracle.sh pattern), deterministic (SEEDGEN), prompt dump on.

## Power
expected_delta: +0.03 raw (X1) / +0.05 raw (X2) (source: per-item conversion 0.11-0.17 per newly-present fact chunk from ORACLE-ST ADD (+0.095 x 180/152) and DENSECHUNK-ST2 (+0.017 x 180/18); projected fact-present X1 35 -> 75 (cut 7), X2 43 -> 117 (ST2 tree), h8st/tools/diag/{arthead_cut7,union_st2}.py)
n: 180
seeds: 1 (deterministic generation, SEEDGEN)
mde: ~0.03 raw paired at n 180 (Opus); X1 alone sits at the MDE and cannot be decided unless its step-0 present-gain is >= +40; X2 clears it
slice: n/a (no Haiku cap; all 180 judged)
l1_futility: n/a (any Haiku delta > 0 -> Opus N=4 both orders on all 180 ON rows)
reopen: R46 (dense extra parked at +0.017: here the appended chunks bypass the keep step that dropped 47/108 reached), R47 (keep relaxations: here nothing is relaxed; neighbours are appended), SECTIONHIT (LEDGER-FIXES row 70, provisional: v0.2 misses were article-level; on the 180 the article is found on 56/137)
split: paired delta by "fact chunk newly present under ON (absent in S)" vs "ON appended only non-fact chunks" vs "unchanged prompt"; expected: gain on the first (~0.11-0.17 per item), ~0 or slightly negative on the second (distractor cost), 0 on the third

## Stages and rules
0. Step 0 (0 judge calls, MacBook replays).
   - G1 reach/present (180): fact chunk in raw ∪ appended >= 90 AND fact chunk present in the final context (kept ∪ appended) >= OFF + 15. Power line: present >= OFF + 40, else the arm runs as a component estimate only (Haiku, no Opus, verdict capped at "not decidable at MDE 0.03").
   - G2 no-harm: kit-only v0.1/v0.2 byte-identical to OFF (required); v0.1 + simplewiki: lost-context 0 (append-only by construction), fire share and added tokens reported; health-strict items: 0 appended chunks failing onHealthTopic.
   - G3 cost: retrieval + keep p50 <= 1.1 x OFF (X1), <= 1.5 x OFF (X2); prompt tokens p50 <= OFF + 450 (ORACLE-ADD: +168).
   - Variant entering stage 1: X1 if it passes G1 incl. the power line and G2/G3; else X2; both fail -> FAIL at step 0 (D0 classes recorded).
1. Generation: chosen variant on the 180; v0.1 + simplewiki OFF and ON (57 judged each).
2. Haiku 5.5-low N=4 both orders vs S Haiku rows; precheck >= 20 % changed prompts (else do not judge); same_answer.py field (RULE 27).
3. Verdict on Opus (N=4 both orders, 360 ON calls; S Opus rows exist): LEVER = CI low > 0 and delta >= +0.03; SMALL = CI low > 0 and delta < 0.03; NO otherwise; |delta| < MDE with CI through 0 = "not decided at MDE 0.03". Any adoption statement also needs v0.1 + simplewiki Haiku ON - OFF CI high >= -0.03.
- One generation per stage; no rerun except an infrastructure error before the first token.

## Stop rules and budget
0 paid API. MacBook: generation + replays, disk >= 8 GiB, never two 4B jobs at once. Mini: X2 only, sidecar rebuild <= 3 h (int8 caches if present, else bge-small re-embed), disk >= 25 GiB, never restart Docker. Judge caps: Haiku 360 + 228; Opus <= 360. Stop if step 0 fails or the precheck fails.

## Outputs and exposure
arms/headpass-st/{HEADPASS-ST.md (cites this sha), GATE.md, tools/, runs/, aggregates/, headpass.vs-cut7.patch + .sha256}; v0.2 identity counts under blind/bench-v02/runs-packs/ (script-only) + one EXPOSURES row; QUEUE rows per stage.
```

## 5. UNKNOWN
Lead-cosine gate (≥ 0.7) not modelled (the merged "in top-80, not raw" 33 and the gate/cap counts could shift by a few items). X2 numbers come from the ST2 tree (OFF 43), not cut 7 (OFF 35); dense reach on cut 7 unmeasured. Whether the int8 dense caches still exist on the mini (deleted on the MacBook). Cost of appended non-fact neighbours (A2 fires on ≈ 96 of 136 items; distractor harm unmeasured — ADD added only fact chunks). Phone prefill cost of +200 (X1) / +450 (X2) prompt tokens. The 0.11–0.17 conversion is fitted on two runs with dev gold written from pack text. The 0.92 s/chunk doc2query rate is the BACKLOG estimate; a smaller generator is unmeasured. Multi-pack installs: "first non-kit article" can come from the wrong pack (R48); the arm is single-pack only.
