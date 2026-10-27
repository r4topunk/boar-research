# PK-3 OVERLAP-ARTEFACT + PK-4 PACK-PRUNE: frozen criterion (2026-10-21)

Frozen before any overlap number or A-union replay output was computed. 0 LLM, 0 generation, 0 judge, 0 paid. MacBook only (stub llama-server; detector :8094 already up). No blind/, no rnd/veil, no bench v0.4.

## Hypothesis rules (verbatim from ruler/hypotheses-round2-2026-10-21.json)

PK-3 statement: "The self-test pack gain (+0.056 1.7B, +0.069 K3, +0.076/+0.102 Gemma) is a lexical artefact of pack-written questions. Self-test questions share far more surface tokens with their gold chunk than real questions do. Prediction: when the 180 self-tests are stratified by question-to-gold-chunk overlap (BM25 rank of the gold chunk for the raw question, plus token Jaccard), the K3-K0 gain in the lowest tertile is at most +0.02 with a CI that includes 0. Reweighting the self-tests to the real v0.1 overlap distribution brings the gain under +0.03."

PK-3 kill_criterion: "Kill the artefact explanation (the self-test gain stays quotable as 'single-fact retrieval-matched questions') if the lowest-overlap tertile still shows K3-K0 of at least +0.04 with a CI above 0, OR the real-distribution-reweighted gain is at least +0.04 with a CI above 0. Otherwise the page drops the self-test gain from the headline and reports it only as an upper bound with the overlap caveat."

PK-4 statement: "Under A-union, at least 2 of the 6 text packs (prime suspect medlineplus, never retrieved; then visa or firstaid) contribute 0 kept chunks on every dev item: v0.1 57 + MAIN 97 + phone 73 + the 180 self-tests minus their own pack's items. Dropping them from the default persona set leaves the kept context byte-identical on at least 98 pct of dev items. It also saves at least 0.3 s of Pixel 8a retrieval p50, about 0.15 s per pack per question measured in AUNION-PIXEL."

PK-4 kill_criterion: "Kill if every one of the 6 packs contributes kept chunks on at least 3 dev items, OR if removing any candidate pack changes the kept context on more than 2 pct of items. The default set then stays at 6, and the cost question moves entirely to PK-5."

## PK-3 operationalisation
- Self-test set (primary) = cand80 (arms/gemma4-e2b/packs/cand80.ids: firstaid, medlineplus, factbook, simplewiki x 20). Sensitivity = the 180 public self-tests (9 packs x 20). Gold chunk = oracle_chunk in arms/oracle-st/tools/oracle-facts.json, text read from the published pack file (build_oracle.py pub(); UTF-16 slice + trim; sha checked against chunk_text_sha256).
- Real set = arms/oracle-real/gold-labels.tsv rows labelled Y or P (one gold per item: first Y row, else first P row); expected 37 v0.1 items. Gold text from the K3 kit files (ragfunnel.py PF map; same chunk ids across builds). Real items without a Y/P gold chunk have no question-to-gold overlap and are not used for the overlap distribution (the FACTPRESENT key facts are terms, not chunks).
- Overlap measures (question vs gold title + text):
  - J = token Jaccard on sets of content tokens (factpresent.py toks(): NFKC lower, len >= 3, stopword list).
  - RANK = 1-based position of the gold chunk in FTS5 bm25 order for OR(question content tokens) in the gold's own pack file, limit 1000 (absent = 1001).
  - RARE = share of the question's rare tokens (idf >= T90) found in the gold (plural-stemmed), idf = log((N+1)/(df+1)) on the simplewiki v3proto FTS; T90 = 90th percentile of idf over the pooled distinct question tokens of all real + 180 self-test items. Items with no rare token get RARE = none (excluded from that measure).
  - LCS = longest common contiguous run of content tokens (toks() sequence) between question and gold.
- Primary stratifier = J. Tertile cut points c1, c2 = the 33.33 / 66.67 percentiles (linear interpolation) of J over the REAL set. Bands: low J <= c1, mid c1 < J <= c2, high J > c2. Secondary stratifier (reported, not the verdict) = RANK with the same real-set tertile construction (low overlap = worst ranks).
- Gain = U(K3) - U(K0), ratio of sums of the item U (as factpresent.py: Haiku 5.5-low judge.v1-low, both orders, s = 0 when declined, K3 reuses K0 rows for byte-identical answers), paired item bootstrap B 2000, seed 11, 2.5 / 97.5 pct. Systems: 1.7B LITEPACKS K0/K3 (MacBook) = PRIMARY; Gemma E2B K0/K3 cand80 = secondary (same rule, reported verdict); 1.7B on the 180 = sensitivity.
- Reweighted gain = sum over bands of w_b x gain_b, w_b = share of real items in band b; gain_b = the band's ratio-of-sums gain on the self-tests; bootstrap resamples within each band. A band with < 5 self-test items is merged into its neighbour (low into mid, high into mid) for both the weight and the gain.
- Verdict per system:
  - KILL (artefact explanation killed; gain quotable as 'single-fact retrieval-matched questions') if low-band gain >= +0.04 with CI low > 0, OR reweighted gain >= +0.04 with CI low > 0.
  - ARTEFACT SUPPORTED if low-band gain <= +0.02 with a CI that includes 0, AND reweighted gain < +0.03.
  - Otherwise NOT KILLED (page action per the kill criterion: self-test gain off the headline, upper bound with the overlap caveat), labelled PARTIAL.
  - If the low band holds < 10 self-test items, the low-band clause is not estimable: KILL only via the reweighted clause; SUPPORTED needs reweighted < +0.03 with CI including 0.
- Descriptive (no verdict): overlap medians/IQR self-test vs real; share of self-tests above the real 90th percentile of J; Spearman of per-item gain (U3 - U0 per item, s/sref) vs J on self-tests and on the real items (1.7B K3-K0).

## PK-4 operationalisation
- Replay: the RAG-FUNNEL tree (FACTPRESENT tree + apply_funnel.py, logging only) cloned + arms/coverage-matrix/kadirs.patch (wave4 appended last, so boar-visa-en resolves); stub llama-server; requests = arms/coverage-matrix/req/lp-KA-{v01,cm,st}-s42 (KA = A-union: crypto, wikivoyage, visa, factbook, medlineplus, firstaid). Same env as ragfunnel_replay.sh. Parity: kept titles vs the judged KA traces where they exist (MAIN 97, cand80), reported.
- Per item x pack: raw hits (fun:raw), dense candidates (fun:dense), kept chunks (retfloor:kept). Fact-chunk contribution = a kept chunk id that is the item's gold (self-tests: oracle-facts fact_chunks; real: gold-labels Y/P chunk).
- Dev items for "contributes": v0.1 57 + MAIN cm 40 (= MAIN 97) + the 180 self-tests minus the items of the pack in question. Phone 73: the AUNION-PIXEL retrievedTitles counts (already measured; medlineplus 0, visa 0) are quoted, not re-run.
- Candidate = a pack with <= 2 dev items carrying a kept chunk from it. For each candidate, and for all candidates jointly, replay KA minus that pack and compare per item the kept titles (title + section, in order) and the dumped Context block bytes vs full KA on all 280 replayed items.
- Verdict:
  - KILL if every one of the 6 packs has kept chunks on >= 3 dev items, OR removing any candidate changes the kept context (Context bytes) on > 2 % of items.
  - SUPPORTED if >= 2 packs have 0 kept chunks on every dev item AND dropping them jointly leaves the Context bytes identical on >= 98 % of items AND the latency saving (pack's SQL seconds over the aunion73-a run / 73, summed) >= 0.3 s.
  - Otherwise PARTIAL (e.g. one pack prunable): the app maintainer note names only the packs that meet the 0-kept + <= 2 % rule.
- medlineplus probe: on v0.1 health items and the 20 medlineplus self-tests, its FTS bm25 rank (own list) of the gold chunk, presence in the fused raw / dense lists, and kept; separates 'no content' from 'outranked'. The phone-vs-desktop gap (PackSource code 10) is reported, not resolved.
