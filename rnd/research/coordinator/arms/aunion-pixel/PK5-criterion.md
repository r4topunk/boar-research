# PK-5 MERGED-PACK criterion (frozen 2026-10-21, before the build, the replay and the phone run)

Hypothesis: ruler/hypotheses-round2-2026-10-21.json id "PK-5 MERGED-PACK". 0 LLM in the build and replay, 0 judge, 0 paid.

## Build
tools/merge-packs.mjs (sha256 ce5dbf6b8bd2fc81610a48eeae2f56bcb5b063a451305afc132e1f02e8949fa3), node, on the mini: one format-2 sqlite boar-aunion-merged.sqlite from the 6 A-union packs in kit order (wikivoyage, crypto, visa, medlineplus, firstaid, factbook): blocks/articles/chunks/redirects/article_meta/lead_vecs copied with id offsets (source codes, zstd blocks, offsets, int8 lead vectors unchanged); contentless FTS5 re-indexed from the article text the way build-wiki-pack.mjs does (title, heading path, chunk text; only the chunk ids each source pack indexed); df rebuilt (doc >= 2000); meta format 2 + same embedding sha. Re-index fidelity checked before freezing: a one-pack merge of factbook, crypto and visa gives an fts5vocab 'instance' table identical to the source pack (sha of term/doc/col/offset rows equal). What changes by design: one index (global BM25 idf, nIndexed = sum), one k-limited candidate list instead of k per pack, one topicSources set.

## Step 1: identity (MacBook, boar-eval replay-retrieval.sh, engine tree bench-app/engine = 0ca54d87, the phone's engine; --gate rules; engine k; MacBook CPU embeddings)
Items: union of MAIN 97 (lp-screens/main-97.ids, questions from the LITEPACKS request rows) and the v0.1 57 (device-x6/v01.jids, bench v0.1 questions). Arm S = --packs the 6 A-union files; arm M = --packs the merged file. Per item compare the engine's pre-answer sources (kept titles, ordered) and the raw retrieve list as ordered (title, section) pairs; items that do not retrieve in both arms count as identical.
- Identity = items with identical kept sources / items. GATE: identity >= 95 pct (the coordinator's rule; stricter than the hypothesis's 90 pct kept-title parity). Below 95 pct: STOP before the phone and report the differing items with both lists.
- Reported, not gating: raw-list identity, per-item differences listed, retrieve ms p50 S vs M on the MacBook.

## Step 2: Pixel 8a (only if step 1 passes)
Phone state change: files/corpus/<6 packs> moved with run-as mv to files/corpus-off/, boar-aunion-merged.sqlite pushed into files/corpus/ (sha-checked); gazetteer unchanged; ls -l recorded before and after. Request merged10-a = aunion10-a with requestId changed (gemma-10 set, qwen3-1.7b-q4km). Thermal gate before: status 0 and battery <= 31.0 C (hypothesis), waiting up to 30 min; if not reached, run anyway and label the speed numbers "hot start" with the temperature. Afterwards: mv the 6 packs back, rm the merged file, sha-check the 6 files against SHA256SUMS, ls -l.
Compared with aunion10-a (same phone, APK, set, model; 6 separate packs): retrieval p50 (timeline retrieve ms), TTFT p50, answer p50, PSS peak.
- PASS: retrieval p50 saving >= 1.0 s vs aunion10-a (3.90 s) AND PSS peak <= 4.0 GB. The hypothesis target (merged retrieval p50 <= 2.4 s) is reported as met or not.
- KILL: saving < 1.0 s OR PSS > 4.0 GB.
Caveat recorded with the result: n = 10 questions (7 retrieve), one run each; the 73 is not run here.
