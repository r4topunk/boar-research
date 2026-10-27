# FTDATA pilot (50 examples), 2026-10-07. Criterion FTDATA-PILOT-criterion.md, sha aa09070f… (verified unchanged)
**Numbers** (tools/fidelity_filter.py on pilot-50.jsonl; n=50, 0 teacher failures, 0 retries, 0 web requests, model claude-opus-5-5)
| Measure | Value | Bar |
|---|---|---|
| Filter pass rate | **41/50 = 0.82** (strict variant, bare domains like "Ready.gov" count as URL: 37/50 = 0.74) | ≥ 0.60 |
| Median s/example (question + answer call, wall) | **10.6 s** (p90 14.8, max 18.6; answer call alone median 6.8 s) | ≤ 120 s |
| Teacher tokens/example (mean, 2 calls) | 4,077: input 4 + cache-creation 3,332 + output 741 (output incl. thinking) | — |
| Faithfulness review (10 passing, seeded) | **PENDING**: review-sample-10.md for the coordinator's separate Opus reviewer | ≤ 1/10 |
| Failure causes | too_long 9 (222–241 words); number_not_in_passages 0 (431 numbers checked in 43 answers); url 0; refusal 0 | — |
Pass by pack: enwiki 22/26, enwikivoyage 8/10, crypto 5/7, usgov 6/7. Words min/median/max 188/210/241. Teacher wall total 565 s. "not in the passages" in 36/50 answers. Qtypes: fact 13, explanation 13, how-to 12, comparison 12.

**Pipeline**: sample_passages.py (seed 46) → teach.py (2 `claude -p` calls/example) → fidelity_filter.py → review_sample.py.
CLI: `claude -p --model opus --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --system-prompt …`,
auth = claude.ai [usage detail removed]; API-key/gateway env vars stripped from the child env. Question: separate opus call on gold passages only (Q_PROMPT in tools/teach.py).
**Exact teacher prompt** (byte-exact: A_SYSTEM/A_PROMPT in tools/teach.py; blank lines around passages elided below) — system: "You are a careful research assistant. You have no tools and no internet. You answer only from the passages given." User:
```
Answer the user's question using ONLY the passages below. Do not use outside knowledge.
- Write 120 to 220 words of plain prose (no headings, no bullet lists, no URLs).
- Every number, date and name you write must be taken from the passages, written as it appears there. Do not compute
  or estimate new numbers.
- If the question asks for something the passages do not contain, say that it is "not in the passages" and answer
  the rest.
- Some passages may be unrelated to the question; ignore them.

Passages:
[1] <title>\n<text> … (blank line between passages)
Question: <question>
Answer:
```
**Deviations / choices not fixed by the criterion**
- Sources: enwiki 26 + enwikivoyage 10 (packs/boar-wiki-sample.sqlite), crypto 7 (crypto/boar-crypto.sqlite), usgov 7 (preparedness-v3 en pack, source 4: Ready.gov + Army FM 21-76). Quotas are mine.
- Passages = pack chunks (~1,000 chars). 24/50 examples have 1 distractor chunk from another article (recipe's gold+distractor share). Gold text ≥ 200 words (my floor, so 120–220 words is reachable); total 218–823 words (≤ 1,200).
- Bench exclusion: 65 titles from v0.1 reference URLs + gold city/wikivoyage fields, plus any title found in a v0.1 question; 0 sampled articles hit it.
- Filter bugs fixed after the first pass (same data, no re-generation): number tokens are maximal digit/dot runs ("0.5.17" was split into 0.5 + 17) and a number may match folded OR raw passages (folding joined "under 25 110 kr" into 25110). Bare domains and e-mails copied from the passages are not URLs (strict count reported above). First-pass filter result was 36/50 = 0.72.
**UNKNOWN**
- Faithfulness (third bar) not measured yet; verdict VIABLE/NOT pending it. The filter checks digits only: names, spelled-out numbers and paraphrased claims are unchecked.
- 36/50 answers use "not in the passages": unclear how many are true gaps vs filler to reach 120 words; risk of teaching a disclaimer habit.
- Opus overshoots 220 words in 9/50 (median 210): a hard word cap or a 200-word target would likely fix it; not tried (no second pilot).
- Recipe mix not tested (no unanswerable, partial-context, or number-heavy strata; no quote-then-answer format). 1k cost extrapolated: ~4.1k tokens and ~11 s per example → ~3 h sequential.

## Verdict (coordinator, 2026-10-07 00:28)
Faithfulness (REVIEW-10.md, independent Opus reviewer): 1/10 examples with an unsupported claim (1 of 136 claims, 0 contradicted) = bar
met exactly; 4 further borderline claims counted supported (a stricter reviewer → 4/10, FAIL); filler disclaimers 4/12. All three bars
pass by the letter → **VIABLE**. Per the criterion the 1k generation is PROPOSED to r4to, not started. Required changes before 1k:
(1) hard 200-word cap in the prompt + post-hoc trim rule (9/50 losses were length); (2) replace the "say 'not in the passages'" instruction
with "answer only what is asked; omit absent facts" (36/50 disclaimers, 4/12 filler → decline-habit risk, see LIT safety-drift row);
(3) strict reviewer rubric (borderline = unsupported) on a 20-sample at 1k. Cost projection at 1k: ≈ 3 h wall, ≈ 4.1 M teacher tokens.
