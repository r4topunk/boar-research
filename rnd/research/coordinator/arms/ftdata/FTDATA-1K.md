# FTDATA 1k (grounded-reading SFT set), 2026-10-07. Criterion FTDATA-1K-criterion.md, sha 1a6b43dc… (verified OK before and after)
Run 09:30 → 14:07 (4 h 37 min wall, MacBook only), 1,000/1,000 completed, 0 teacher failures, 0 retries, model claude-opus-5-5 only.
Prompt: prompt-1k.txt, sha256 37ba84d4a631fa60ba1a39740f76692645b663751fdc3314239aa7b96b2302f3 (answer call; question call byte-identical to pilot).

| Measure | Value | Bar |
|---|---|---|
| Filter pass rate (frozen filter, tools/fidelity_filter_1k.py) | **982/1000 = 0.982** | ≥ 0.70 |
| Disclaimer rate (passing answers with ≥ 1 phrase) | **3/982 = 0.003** (3 phrases total, all "passages do not"; 3/1000 over all answers) | ≤ 10 % |
| Strict faithfulness review (20 passing, seed 48) | **PENDING (separate reviewer)**: review-sample-20.md | ≤ 2/20 |
| Median s/example (question + answer call) | 11.51 s (mean 12.58, p90 16.43, max 87.4) | (stop rule ≤ 30) |
| Teacher tokens/example (mean, 2 calls) | 4,087.5: input 4 + cache-creation 3,305.9 + output 777.6 (output incl. thinking); 4.09 M total | — |
| Trimmed (201–230 raw words → last sentence ≤ 200) | 150 (147 passing); trimmed length min 149 words; 0 trimmed below 120 | — |
| Failure causes | number_not_in_passages 14, too_long 3 (raw 231, 231, 234), refusal 1, too_short 0, url 0, disclaimers>1 0 | — |
| Numbers checked | 6,817 numbers in 859 answers; 24 not found (in 14 answers) | — |
| Raw answer words min/median/max | 124 / 188 / 234; final median (passing) 185 | — |
| Web requests / rate-limit retries | 0 / 0 | stop if any web; 429 run > 10 min |
| Strict-URL sensitivity (bare domain = URL) | 78 passing answers name a bare domain → strict pass 904/1000 = 0.904 | — |

Pass by pack: enwiki 511/520, enwikivoyage 197/200, crypto 138/140, usgov 136/140. Pass by qtype: fact 246/250, how-to 246/250,
explanation 245/250, comparison 245/250. With a distractor chunk: 501/506 pass. Pilot comparison: disclaimers 36/50 → 3/1000; too_long 9/50 → 3/1000.

**Stop-rule checkpoints** (teach-1k.log; pass rate / median s / web / 429 retries) → all CONTINUE
- 10:00 n=100: 100/100 = 1.000 / 12.17 / 0 / 0
- 10:56 n=300: 296/300 = 0.987 / 12.17 / 0 / 0
- 11:52 n=500: 491/500 = 0.982 / 12.00 / 0 / 0
- 12:49 n=700: 688/700 = 0.983 / 12.16 / 0 / 0
- 13:40 n=900: 885/900 = 0.983 / 11.67 / 0 / 0
- 14:07 n=1000 (final): 982/1000 = 0.982 / 11.51 / 0 / 0

**Deviations / implementation choices** (pilot tools unchanged, sha-verified; all 1k code in new files *_1k.py)
- Filter bugs found after the run, NOT fixed (criterion: report both numbers). (a) Pilot number regex rejects a number preceded by a dot:
  ".616", ".253", ".255", ".307", ".220", "Pt.8" are verbatim in the passages → 11 of 14 number failures are false. (b) Pilot REFUSAL regex
  `as an AI` has no word boundary and matched "as well as an airport" (ft1k-0621) → false refusal. Frozen 982/1000 = 0.982;
  corrected (a) 993/1000; corrected (a)+(b) **994/1000 = 0.994**. Remaining 3 real number failures are decade derivations ("1970s", "1920s", "1980s").
- Sampler (tools/sample_passages_1k.py): usgov source 4 has 206 articles (173 gold-eligible); pilot draw marks distractors used and would
  exhaust the pool and loop forever. 1k: distractor articles not marked used (gold stays unique) → 12 repeated distractor draws, 28 articles
  are gold in one example and distractor in another. Exhaustion guard added (never fired: 0 relaxed gold draws).
- Sampler: latent pilot bug (overflow ≥ last passage blanked the distractor and left 1,399 words) hit ft1k-0649 only; fix truncates the
  longest passage instead (1,200 words), no RNG use, the other 999 examples byte-identical to the unfixed run.
- Pilot-title exclusion = 74 lowercase titles of passages-50.jsonl across all packs (26 draws rejected); bench exclusion as pilot (65 titles, 0 hits).
- Mix: enwiki 520 / enwikivoyage 200 / crypto 140 / usgov 140 (pilot ×20); 506 with one distractor; passages 2/3/4 = 103/396/501; 200–1,200 words.
- Qtype shuffle seed 47 (pilot 46): 250 per type. Web-request and 429-run conditions checked on every call (stricter than checkpoint-only).
- Trim: sentence end = [.!?] + optional closing quote/bracket + whitespace; abbreviations/initials ("U.S.", "e.g.", "Dr.") not treated as ends.
- Disclaimer regex also accepts a curly apostrophe ("passages don’t"); 0 such hits.
- review-sample-20.md per example: id, passages ("[i] title" + full text, as the teacher saw them), question, answer; no role/pack/qtype/rubric.

**UNKNOWN**
- Faithfulness (third bar) not measured; verdict pending the separate strict reviewer. The filter checks digits only: names, spelled-out
  numbers and paraphrased or interpretive claims are unchecked.
- Disclaimers fell 72 % → 0.3 %: unknown whether absent facts are now silently omitted (intended) or filled from outside knowledge (reviewer must check).
- Set has 0 abstention, partial-context or number-heavy strata (recipe asks ~10 % / ~15 % / ~20 %); answers cluster at 150–200 words
  (median 185), so length may still be a learned signal (recipe warns against it).
- 147 passing answers were trimmed at a sentence boundary: completeness loss from the trim not measured.

## Verdict (coordinator, 2026-10-07 14:13; criterion 1a6b43dc…, read once)
Bars: filter pass 0.982 ≥ 0.70 PASS; disclaimers 0.3 % ≤ 10 % PASS; strict review (REVIEW-20.md, independent Opus, borderline = unsupported) **16/20 examples with ≥ 1 unsupported-or-contradicted claim vs ≤ 2/20 → FAIL**. Totals: 258 claims, 216 supported (83.7 %), 41 unsupported, 1 contradicted; outside-knowledge fill 4/20; factual-only sensitivity 10/20 (still FAIL).
**FTDATA 1k = FAIL.** The LoRA diagnostic is NOT authorised (arms/loradiag/LORA-DIAG-criterion.DRAFT.md stays a draft). No second generation without r4to.
Reading: the two prompt changes removed the disclaimers (72 % → 0.3 %) but the teacher now fills gaps with interpretive framing ("severe", "minor party", "deliberately", causal "so/which is why") and, in 4/20, with outside knowledge; the digit filter cannot see this (0 foreign numbers in 16 failing answers). Training on these targets is the Gekhman risk the LIT doc names (teaching unsupported claims). The pilot's 1/10 was the lenient rubric; under the strict one the pilot would also have failed (4/10 borderline).
Options for r4to (not started): (a) close the line, keep ftdata-1k.jsonl as an unverified set; (b) claim-level rejection pass, no regeneration: a Sonnet-low verifier marks each sentence supported/unsupported against the passages and unsupported sentences are deleted (≈ 982 Sonnet calls, ≈ 1 h, 0 teacher tokens), then a fresh strict 20-review by a separate agent; LoRA only if ≤ 2/20; (c) new 50-pilot with the recipe's quote-then-answer format (≈ 200k teacher tokens) before any 1k.
