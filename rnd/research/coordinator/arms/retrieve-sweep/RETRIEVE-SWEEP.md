# RETRIEVE-SWEEP (2026-10-21 23:2x): make the right chunk reach the context — engine-side arms measured 0-LLM on the QFORM 432 + the real-item funnel

Asked by r4to 23:2x ("shouldn't we research how to guarantee the chunk is found?"). QFORM showed: with the gold chunk kept the 1.7B is at reference level (U 0.88 vs 0.19), the base question keeps the gold only 50 %, 25/432 golds are retrieved then dropped by the keep step, keywords beat questions (+12), one long document crowds a pack (firstaid), and the fact often sits in a sibling chunk of the right article (factbook). Each fix below is an engine change on the K1 bench tree (MacBook copy kiln-local/be-0cfd4a77-cut7-litepacks; llama.cpp untouched; the LLM is stubbed in the replay), measured by replay in ~2 min per arm.

## Arms (each one a small patch with an env/setting switch, default off = byte-identical baseline)
| arm | change | QFORM evidence it targets |
|---|---|---|
| A GROUND-DENSE | the keep step (`onSubject` in answer.ts) also keeps a chunk whose dense similarity to the query ≥ τ_A (0.78 first; 0.74 second) even with no lexical subject overlap | 25 golds retrieved then dropped; F1 contexts empty 23/48 |
| B KEYQ | retrieve twice, question + its keyword form (stop/wh/aux words stripped, ≤ 6 content terms), merge by max fused score, same k | F2 62 % vs F0 50 % |
| C SIBLING | after fusion, for the top-2 kept articles add the article's best other chunk by dense similarity (one per article) within the work budget, on top of the K1 settings (packHeadPass a2 + dense append) | factbook: right article 6/8, right chunk 1/8 |
| D DIVERSITY | before fusion, cap candidates to 2 per article and 4 per source family (title prefix) so one long document cannot fill the list | firstaid 0/8, ATP manual dominates |
| E MINSIM | ANSWER_MIN_SIMILARITY 0.7 → 0.62 for dense hits only | the 0.7 cutoff is shared with the app maintainer's RagPure.kt; untested by form |
| F COMBO | the arms that pass, together | |
Baselines: B0 stock (= QFORM replay), B1 K1 settings (head pass + dense append; QFORM: F1 10 → 21).

## Measurement (0 LLM; frozen in RETRIEVE-SWEEP-criterion.md before any replay)
- Sets: (1) QFORM 432 (arms/qform/items/qform.questions.jsonl; gold = quote in kept); (2) real items: MAIN 97 keyed through RAG-FUNNEL K1 — the 25 S2/S3 ids (fact in a pack, not kept; arms/qform/funnel-S2S3.ids) as the recovery set and the 22 S4/S5 ids as the must-not-lose set; fact-present check = the FACTPRESENT lexical rule used by the funnel (ruler/FACTPRESENT-2026-10-21.json keys).
- Per arm: hit@kept per form and pooled with paired bootstrap CI vs B0 (B 2000, seed 11); funnel recovery x/25 and losses y/22; **junk-kept** = mean kept chunks on QFORM items whose gold is not in wide-12 (crowding proxy; must not rise > 25 % relative); prompt tokens after compression (mean); wall per query.
- Rule: an arm is a CANDIDATE iff pooled QFORM hit@kept ≥ +8 points with CI low > 0 AND funnel recovery ≥ 5/25 AND losses ≤ 2/22 AND junk-kept ≤ 1.25 × B0. Candidates and F go to a Haiku answer screen (divergence-first: 1.7B generation on the mini for the changed-context items only, judge.v1 N 4 both orders vs QFORM gold/rubric and MAIN 97 refs; cap 400). Nothing is a lever until that screen passes (ΔU ≥ +0.02, CI low > −0.01 on the changed items) — QFORM's 0.88 vs 0.19 says it should, but crowding can eat it.
- Prediction (before any run): A +10…+18 pooled (F1/F3 largest), junk up; B +5…+10; C +3…+6 on factbook only; D +0…+4 pooled, firstaid +2…+4/8; E +2…+6 with junk up; F +15…+25. Funnel recovery: A 6–10/25, others ≤ 4.
Caps: 0 judge in stage 1; Haiku ≤ 400 in stage 2; Opus 0; paid 0; phone 0. Items dev only.
