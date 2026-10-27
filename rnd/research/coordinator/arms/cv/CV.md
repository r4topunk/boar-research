# CV: computed verdict on cut 3 (engine engineer, 2026-10-04, DEV only)

TL;DR: router + 4B facts call + deterministic verdict + render, built on cut 3 (branch `coord/cv` in wt/cv, local commits, nothing pushed). L0 routing PASS (94 % / 0 control FF / 0 dev fires); 210 DEV answers generated once per arm; accuracy NOT scored (coordinator, against the key). Desktop timing: no added time.

## Built (src/routing/computedVerdict.ts, verdictUnits.ts; hook in answer.ts)
- **Router (EN):** compare (which-form / yes-no, optional ratio "twice", figures given in the question kept), threshold (number+unit, count, year, event vs event), superlative yes/no (scope and "by area/volume" kept; year superlatives and "measured from" abstain), plus two model-free kinds: city distance compare (bundled city table) and two literal figures ("100 °F vs 40 °C"). Vetoes health/danger/card/calculator/venue/country-facts/money/opinion/personal words. answer.ts only calls it on the fast tier, no health, no detector fire, not PT/ES, no reused sources/place, after all earlier instant paths.
- **Facts call:** one short call (temp 0, no thinking). llama.rn takes a grammar but `GenerateOptions` does not pass one, so: strict `<item> | <number> | <unit> | <year>` lines, items listed by name (a first version with numbered items made the 4B answer with the index: "1 | km/h"), scale words in the unit ("9.98 | million km²"), lenient parser (name-keyed, falls back to order).
- **Verdict:** units normalised (m/km/mi/ft/nmi, m²/km²/sq mi/ha, kg/lb, g/cm³, km/h/mph, °C/°F/K, people, USD, %, counts, signed years). Abstain on parse failure, unknown unit, wrong unit family, missing item, tie, superlative item absent from the model's list.
- **Render:** verdict line, `Facts:` block (with conversions), a "model's recall, not checked" line, then at most 2 model sentences kept only if every number is in the facts and no hedge/"contradict"/"error" words. 2 model calls per CV answer.
- Note: CV answers carry no "not from an offline source" preface (they have their own recall line) and no sources.

## L0 routing (arms/cv/router-dev.txt, dev-fires.jsonl; tool tools/cv-router.mts)
- 146/155 verdict items fire (94.2 %; bar 80). Misses: 5 rank-position, "oldest university", "measured from base to peak", Cleopatra, "further west".
- Controls: 0/55 fires. Sonar EN dev messages: 0/1,328 (dev-fires.jsonl empty). Also v0.1 EN (60): 4 fire, all true comparisons (Brazil/Russia, polar bear/grizzly, moose/bison, crocodiles); V-exact 0/11.
- Routing was tuned on these DEV questions.

## Runs
- Script `rnd/kiln/l1/cv-dev.sh` (seed 44, Android 12 GB 4B, kit A, detector v3b on, places kit-vexact, runner be-ship 949eee03; trees be-0cfd4a77-cut3 a67c70db and be-0cfd4a77-cv built with setup.sh + patched runner copied from the cut3 tree). Traces: `boar-eval/runs/kiln/cv-dev-cut3-s44/traces.jsonl`, `cv-dev-cv-s44/traces.jsonl` (210/210 valid, 0 errors), log `cv-dev.gen.log`.
- CV answered 118 of the 146 routed items (48 compare, 30 threshold, 25 superlative, 11 year, 2 distance, 2 literal); 28 routed items abstained to the normal path. CV items are the traces with reason code `answer:computed-verdict`.
- Run tree used patch sha 9c4250fa…; the final patch differs only by a test bound in answer.test.ts (copy of the run patch: `cv-on-cut3.vs-0cfd4a77.run-9c4250fa.patch`).
- **Timing** (`cv-timing.txt`, desktop mini): items CV answered: cut 3 median 13.27 s, CV 12.59 s, paired diff median -0.47 s (bar <= +2 s); all 210: -0.30 s.

## Scorer
`tools/cv-score.mts --key K --cut3 … --cv …` (key format and the first-sentence heuristic for cut 3 answers are documented in its header; abstained items use cut 3's answer). Tested on a fake key in the scratchpad only. Gold folder was never opened.

## Deliverable
`cv-on-cut3.vs-0cfd4a77.patch` sha256 455559f6a4cd3b10bda3916a1e8f11fd6dec7c2b104850c4b13a2614212317f2; vitest 1356/1356 (cut 3 had 1285: +71 = 10 units, 57 CV, 4 answer integration); tsc clean; applies cleanly to a fresh `git archive 0cfd4a77`.

## UNKNOWN
- Accuracy vs the key (coordinator).
- The 4B's recall is the ceiling: seen on DEV, Moon mass 7.3e19 kg, Danube 2,010 km, absolute zero 0 °C each give a confidently wrong verdict. CV trusts the figures (same R5 as VG); no self-consistency check was added (cost: another call).
- Superlative: the model's own top 3 decides; omissions of the true leader give a wrong "Yes".
- Fire rate on real traffic; phone latency (2 calls); grammar-constrained output on llama.rn.

## Revision 1 (coordinator ruling after L0: accuracy +16.6 pp PASS, 6 wrong-where-cut-3-right FAIL)
- **Change (only this):** `routeVerdict` no longer calls the superlative router, so "is X the largest ..." and rank questions take the normal path. Nothing else touched (commit "CV rev 1"); the superlative code stays in the file, unreachable.
- **(a) Routing:** DEV verdict items 103/155 fire (66.5 %: compare 53/55, threshold 50/50, superlative/rank 0/50 by design; the 80 % routing bar of the original criterion no longer applies to the 50 excluded items), controls 0/55, Sonar EN dev 0/1,328. Section "REVISION 1" in `router-dev.txt`.
- **(b) Same answers for still-routed items:** I dumped `routeVerdict` plans for the 210 probes plus 1,223 Sonar dev messages before and after: 1,433 questions, 43 changed, every one superlative -> null, all other plans byte-identical. So the facts prompts, parser and render for the remaining items are unchanged, and the existing `cv-dev-cv-s44` traces stand for them (the 25 CV superlative answers drop out, the 43 removed questions revert to cut 3's normal answer, text-identical in the earlier run for non-CV items). No re-run.
- **(c) Patch:** `cv-on-cut3.vs-0cfd4a77.patch` sha256 8271ec3b4656f8420d23a1cb39eb591a075ac9f5d705725e0e921819762c6618; vitest 1353/1353 (3 superlative tests replaced by one router negative); tsc clean; applies cleanly to a fresh `git archive 0cfd4a77`.
