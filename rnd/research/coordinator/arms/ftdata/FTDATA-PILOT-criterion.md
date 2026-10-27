# FTDATA pilot criterion (frozen 2026-10-07). Coordinator, overnight loop. Decision 4 of the handoff, DATA PILOT ONLY (no training).
Question: is the LIT-GROUNDED-READING recipe's data pipeline viable (fidelity, cost, time) before the 1k set and the 2-day diagnostic?
Recipe source: coordinator/LIT-GROUNDED-READING-2026-10-06.md (recipe + go bar). Pilot = 50 examples.
Passages: from the local knowledge packs under <workspace>/shared-data (Wikipedia/Wikivoyage/crypto/usgov as the recipe
says), chosen by a seeded random sample (seed 46) of articles, 2–4 passages per example, ≤ 1,200 words total per example. NEVER
bench items: exclude any article whose title appears in boar-eval/bench/v0.1 questions/gold; never read blind/ or rnd/veil.
Questions: one natural user question per example, answerable from the passages, mix of fact/explanation/comparison/how-to, EN.
Teacher: `claude -p` ([usage detail removed]; model opus) given ONLY the passages (no web), instructed to answer in 120–220 words, every
number/date/name taken from the passages, say "not in the passages" for anything missing. Record wall time and tokens per call.
Fidelity filter (deterministic): every number (digits, incl. years) in the answer appears verbatim (after comma/space folding) in
the passages; answer length 120–220 words; no refusal; no URL. Examples failing are kept in the file with pass=false.
Measures: filter pass rate (bar ≥ 60 %); median seconds/example (bar ≤ 120 s); teacher tokens/example; 10-example faithfulness
review by a SEPARATE Opus agent (bar: ≤ 1/10 unsupported claims among passing examples).
Output: arms/ftdata/pilot-50.jsonl ({id, source_titles, passages, question, answer, numbers_checked, pass, reason, seconds}),
PILOT.md (numbers, failure causes, UNKNOWN). Verdict: VIABLE if all three bars pass → the 1k generation is proposed to r4to
(not started tonight). Else: report causes, no second pilot tonight. No paid API keys; only `claude -p` on the [usage detail removed].
