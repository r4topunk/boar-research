# CV5-RECOMPUTE + CV5-EXPOSURE-AUDIT criterion (frozen 2026-10-21 before the final script runs; 0 LLM, 0 judge)

Source hypotheses: hypotheses-round3-2026-10-21.json ids CV5-RECOMPUTE and CV5-EXPOSURE-AUDIT (kill criteria copied, scope narrowed by the coordinator brief).

## A. RECOMPUTE (tools/recompute_page_numbers.py)
Scope: every quoted measured number in RESEARCH-PAGE-OUTLINE-2026-10-21.md §0-§2 (incl. the 05:xx update blocks) and PLAN-2026-10-21-TO-25.md §1 (table + 05:xx update). Excluded: bounty constants (12 GB, 50 GB, 15 min), dates, shas, QUEUE line numbers, spec version numbers, decision thresholds that are rules rather than results.
Rule per number: recompute from the cited machine-readable source (aggregate JSON, judgment rows or phone rows.jsonl), round to the document's precision; MATCH if |rounded - doc| <= 0.001, else MISMATCH. A number whose only source is prose (.md, QUEUE, external paper) or a file under blind/ is UNSOURCED.
Kill (from the hypothesis): more than 5 % of checked numbers MISMATCH, or any headline number (tag H) off by more than 0.005 U / 1 per-100 point / a CI bound by more than 0.01. A killed sentence is barred from v5 until re-sourced. If more than 10 % of numbers are UNSOURCED the page ships only sourced numbers.

## B. EXPOSURE-AUDIT (tools/exposure_audit.py)
Walk every judgment/trace/phone-rows file modified since 2026-10-06 outside blind/, rnd/veil and node_modules; extract item ids by regex only (never parse or print question/answer text); hash the sorted id set; classify the set by id prefix (vpara-, v02-, cw-/cx- = v0.4, st-*, v0.1 public ids, longsession ls*, rivalset exp-*). Diff against EXPOSURES.md rows by (set, arm name).
Kill (from the hypothesis): any v0.4 question or answer text read, judged or used in generation by any run; or 3 or more unlogged exposures for any held-out/blind set (v0.4, V-para, v0.2, health/chat/meta fresh sets). Dev-set runs (v0.1, self-tests, MAIN, slices) are listed as proposed rows but do not count toward the kill (EXPOSURES.md l.78 rule: v0.1 dev runs are not exposures).
