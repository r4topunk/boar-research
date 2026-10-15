# FACTS r5 criterion (frozen 2026-10-06 22:45, before any code). Coordinator decision under the maintainer's autonomous-loop mandate.
Why: r4 FAILED on lowercase-homonym precision (10/22 wrong fires, 5 of them pre-existing in r3). The binding constraint is
precision on lowercase typing, the CF failure class. r5 changes the r3 guard; recall rules of r4 are kept.

Scope (code only; asset unchanged f4d3ab2e…; base wt/facts 45d5d058 = r3; r4 WIP patch 0d8adc47… may be reused):
A. TWO-SIDED NEIGHBOUR GUARD for EVERY resolved name, any casing, one-word or multi-word: the token immediately before and the
   token immediately after the name span (skipping "the/a/an/of/in/at/on/for/to/and/or", punctuation, numbers) must be either
   absent (span at the edge), a question word, a property-lexicon word (tall/high/big/long/population/people/capital/currency/
   language/continent/border(s)/area/size/elevation/height/length/bigger/larger/smaller/taller/longer/…), a hedge/time word
   (roughly/about/approximately/exactly/today/now/currently/called/please/again/anyway), a unit word (m/km/feet/ft/miles/sqkm),
   a comparison connector (or/than/vs/versus/compared), or a token of ANOTHER resolved table entity. Any other lowercase or
   capitalised content word adjacent to the span (pen, hilton, broil, times, base, metro, fare, valley, memorial, agreement,
   prime, eye, tech, city when not part of the label) → the question is unanswerable (no fire). Mount/Mt/River/Lake/Mountain next
   to an entity of that kind still counts as part of the name (r3 exception kept).
B. Question openers "whats/what's/hows/how's/wheres/where's" and imperative "size of / capital of / population of / elevation of
   / height of / length of" at position 0 count as questions without "?".
C. A multi-word n-gram that equals (case-folded) exactly one label/alias of exactly one entity resolves even if one of its words
   is on the risk list ("lake victoria", "new zealand"); the one-word risk list stays for one-word spans.
D. r4 rules kept: safe-lowercase multi-word names; typo-tolerant "the" (thw/teh/hte/tje/th).
Nothing else: no templates, no data, no new properties. Time box 3 h agent time.

Gates (deterministic; same commands as r3; scorer v2 frozen in tools/recall_score.mts):
- G1 tsc 0 + full vitest green (+ an "r5" test block ≥ 8 cases incl. paris hilton / mont blanc pen / cuba libre / london broil /
  everest base camp must NOT fire; mount everest / lake victoria / whats the capital of the philippines must fire).
- 13 DATA-REVIEW probes 0 fires, output identical to r3. r4 fresh probes (probes-r4-fresh.txt): 1/22 fires (kuala lumpur tower only).
- G2 precheck 7/8, 8 target answers byte-identical to r3. G3 0/52 v0.1, 0/12 safety, 0/11 V-exact, dev chat 2/192 same items.
- G4 replay non-target raw 52/52 identical to cut 6. G5 warm p95 ≤ 1 ms.
- Dev sets (sets 1 and 2, scorer v2): report recall/precision/FP vs r3 (30/40, 26/40) and r4 (33/40, 28/40). Guidance only.
- ADVERSARIAL LOWERCASE NEAR-MISS SET (nearmiss-lc.jsonl, 40 items, written by a SEPARATE agent blind to the code, sha frozen
  in nearmiss-lc.sha256 before the r5 agent's final build; run ONCE by the r5 agent after its final commit; no edit after):
  FP must be 0/40. Any fire → FAIL, report, stop.
Blind set 3 (recall-set-3.jsonl e59e99f0…): run ONCE by the coordinator after all gates are green, never by the r5 agent.
Verdict on set 3 (unchanged from r4): PASS recall ≥ 85 % AND FP 0/20 AND precision ≥ 90 %; PARTIAL recall 75–84 % AND FP 0/20;
FAIL otherwise. No rescue. Set 3 burnt after the run. Judge: none. Dev only (no the private held-out dir, v0.2, V-para).
Follow-up if PASS/PARTIAL (separate criterion, not this one): deterministic precheck of FACTS fires on the signal20 slice and on
v0.1, then the judge on changed items only (Sonnet-low L1, Opus confirm), as the cut-7 input.
