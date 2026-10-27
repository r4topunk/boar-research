# HUMANSFT criterion (frozen 2026-10-07 15:4x, coordinator call under the autonomous mandate). Arm A1 of WEB-SWEEP-2026-10-07.md. Data screen only; no training authorised by this file.
Question: do human-verified grounded-QA targets (CLAPnq, HAGRID, Dolly closed_qa) pass the strict faithfulness bar that the Opus teacher set failed (REVIEW-20: 16/20), and are they numerically faithful, so that they can be LoRA targets (alone or mixed with FTDATA-REJ's kept rows)?
Sources (read-only downloads from the HF Hub, no account actions, no uploads; files land in an untrusted dir under the scratchpad or <workspace>/shared-data/humansft-raw/, scripts live elsewhere, python -I):
 - PrimeQA/clapnq, train split: answerable + unanswerable rows, gold passage included (Apache-2.0);
 - miracl/hagrid, train: answers labelled informative AND all sentences attributable (Apache-2.0);
 - databricks/databricks-dolly-15k, category closed_qa (CC-BY-SA-3.0, share-alike: flagged; kept in the screen, excluded from any shipped artifact unless r4to OKs).
 Record sha256 and row counts of every downloaded file. Never bench items: drop any row whose passage title/question matches a v0.1 question title (same exclusion list as FTDATA, 65 titles); never read blind/.
Normalisation: one JSONL (humansft-pool.jsonl) with {id, source, question, passages[], answer, answerable, words}. Keep rows with answer words 20–220 (answerable) or ≤ 40 (unanswerable abstentions). Report counts per source before/after.
Deterministic measures (bars):
 (b) numeric fidelity: every number token (same regex as tools/fidelity_filter_1k.py, with the dot-prefix bug fixed and noted) in an answerable answer appears verbatim (folded or raw) in its passages; share of answers with 0 foreign numbers ≥ 0.98 per source (report each source; Dolly may fail: report).
 (d) extractiveness: share of answer tokens present in the passages (median per source; report only).
 (e) length: median/p25/p75 words per source (report only).
Strict review: 20 rows sampled with seed 51 from the pooled ANSWERABLE rows of CLAPnq + HAGRID (Dolly excluded from the review pool), written to review-sample-20h.md (id, passages, question, answer only) → a SEPARATE Opus reviewer (coordinator launches), same rubric as REVIEW-20.md → REVIEW-20h.md. Bar: ≤ 2/20 examples with ≥ 1 unsupported-or-contradicted claim.
Verdict (read once, no rescue): (b) ≥ 0.98 for CLAPnq and HAGRID AND review ≤ 2/20 → PASS: CLAPnq+HAGRID are approved LoRA targets; the LoRA criterion is then frozen for a MIXED set (REJ-kept rows if FTDATA-REJ passed + CLAPnq/HAGRID) with completeness measured explicitly, because these targets are short (median 48 / 23 words) and could lower completeness. Review 3–5/20 → PARTIAL: report. Else FAIL: close.
