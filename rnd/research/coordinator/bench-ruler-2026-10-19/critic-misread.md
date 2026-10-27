Text was checked against `<workspace>/BOUNTY_31.md` (B31, line numbers below). V1, V2 and V3 are the X posts already quoted in the designs, at the URLs listed in their source registers.

## A. Errors shared by all three designs

1. **Speed is a must, but every design scores it as optional.** B31:19 says "Your submission must:" and B31:28 adds "respond at speeds that feel usable for real lookups on a phone". B31:60 then says "judged against **the requirements above and** the bar".
   - Traceable writes "No pass threshold".
   - Robust writes "Latency axis (not a gate)".
   - Judge-eye has phone wall-clock bands, but they only feed a sensitivity number.

   The text gives no number, but that does not make speed a "report only" item. Each design needs a pre-registered speed verdict, labelled as our choice (for example, first useful content within N seconds on the named phone).

2. **Quality and speed can come from different configurations.** None of the designs requires the headline U to be measured on the same tier and configuration whose latency is reported. A deep tier that takes minutes per answer could carry U while the fast tier carries the speed numbers. That breaks the "and" in B31:60. Judge-eye's "speed-qualified U" sees the problem but leaves it as a sensitivity number.

3. **"frontier AI models" is plural, but the reference is one model, picked for convenience.** B31:7 reads "internet search + frontier AI models". All three default to Claude Opus 5.5 + web "because rivals use it". That is a comparability argument, not a reading of the text. The second family is optional in traceable and robust.
   - Judge-eye over-corrects the other way: "better of R-A and R-B per item" is a per-item oracle that no user has, so the denominator ends up stricter than "internet + frontier models".

4. **"casual" is outweighed by "difficult".**
   - B31:7 asks for "a **casual** info lookup and research tool".
   - Traceable makes "difficult" at least 50 % of every stratum. Judge-eye makes it at least 30 %.
   - The source is V2's "less effective at difficult questions". That is an observation about where the apps he tried failed, not a spec for the item mix.
   - Robust is closer ("Single facts, not trivia hunts") but sets no cap.

   Over-weighting hard items turns a casual-lookup bar into a hard-question bar.

5. **The blog's pairwise test is treated as the post author's method for this bounty.** All three cite "I fed both outputs into an LLM to ask which is better" as "the post author's own method". That sentence (blog, 2026-04-02) describes a side-by-side of research tools months before the bounty. It is fine as background. It is not evidence of how he judges #31, and the ruler must not say "matches the post author's method".

6. **Laptop speed quotes are presented next to phone numbers.** The blog says "anything slower than 50 tok/sec" and V3 says "20-30 TPS … 100+". Both are about laptop or desktop models. All three print them as bands beside phone tok/s. Traceable and robust state the caveat, but a band table still reads as a threshold.
   - The only phone-relevant anchors in the text are B31:9 ("~10 tokens/sec from 1B models that break on anything interesting"), which is the failure baseline, and B31:28 ("feel usable").
   - Decode tok/s is also the wrong unit for a RAG app, where prefill and retrieval dominate. The unit should be wall-clock time to useful content.

7. **"Meets the bar" adds a CI condition the text does not have.** B31:60 says only ">50%". Requiring the CI lower bound above 0.50 is a conservative choice of ours. That is fine, but the report must show the literal point-estimate reading next to it. Traceable does this best. Robust adds a second condition (PPI-corrected point > 0.50) with no anchor in the text.

8. **A ratio of rubric points is not "X% as good".** Each design says its scale has "a real zero", so "U reads literally as X% as useful" (traceable; robust says "floor-free by construction"). Anchoring the zero fixes the origin, not the spacing. Nothing shows that a 2/4 answer is half as useful as a 4/4, and the PPI human check corrects judge bias, not what the scale means.
   - The only operationalisation with a natural ratio reading is the binary task-success ratio ("a casual user could act on this"). That maps directly to V1 "it's utility" and B31:60 "useful".
   - All three demote it to secondary. At minimum it should be co-headline.

## B. Traceable

- **The floor comes back.** "An honest 'I don't know offline' … scores 1. It never scores 0". On a 0–4 scale, a system that always declines then scores about 1/3.5 ≈ 0.29 U for free. That is the same artefact the design claims to fix (flaw A1), and it contradicts "0 = useless".
- **Hedged offline answers get too much credit on time-sensitive items.** They "can still score up to 3" (Actionable). An offline answer to a time-sensitive question that is hedged with its knowledge date is usually not actionable. This leans against "internet search" (B31:7) in the app's favour.
- **Equal 1/6 weights are presented as neutral, but the six strata are ours.** Lookup and Travel are promoted to equal standing with the four named types in B31:27. The bounty does foreground travel (B31:7 "People travel…"), so travel at 1/6 is an under-read if anything. The stratum list should be labelled our construction.
- **The 1B arm runs on "same corpus, same protocol".** B31:9 and B31:50 mean a plain 1B model, which is what the post author tried. A 1B model with RAG over our corpus is a different and stronger baseline, so "1B-fail" items become harder to show. Run a plain 1B; 1B+RAG is optional.
- **Venue items rest on OSM tags.** V2's eval is "Tell me the **best** vegan restaurants". "Best" is a quality judgement that internet search answers from reviews, and OSM cannot grade it. Traceable has a human check of the reference's picks, which is the closest of the three, but "best" is still unscored.

## C. Judge-eye

- **The "Meets bar" verdict adds gates that are not in the bounty:**
  - CE rate ≤ ref + 5 pp and ≤ 10 %
  - "safety slice 0 harmful errors"
  - "no required stratum U < 0.30"

  B31:60's bar is ">50% as good", and B31 has no safety, error-rate or per-stratum floor. These are labelled "our choice" but folded into the verdict, so a submission at U = 0.6 could be called "Below bar" because of a rule we invented. Report them as guardrails, not inside the bar.
- **the post author's only named eval sits outside the headline.** The current-city venue items are a "separate score", but V2 says "my eval is 'Tell me the best vegan restaurants in [city I am currently in]'". Leaving them out of U under-reads the clearest public signal. "Precision of named venues that exist and are vegan-tagged" also ignores "best".
- **Fresh items are left out of U** ("reported apart"). Of the three designs, this one most under-reads "internet search" (B31:7).
- **Some stratum anchors are circular.** The Honesty stratum is anchored to "judge rule 'a correct I am not sure…'", which is our own judge.v1 prompt, not a public source. The stratum weights 15/15/12/12/14/20/6 are invented to the percent and presented as "derived from a quote".
- **The sitting model is our invention.** "10–15 questions in one go" and "≥ 6 USEFUL of 12" have no public source. They are labelled as assumptions, which is fine, but they must never appear as the post author's behaviour.
- **The reference cap is still there.** Raising it to 400 words keeps a cap that nothing in "internet search + frontier AI models" supports.
- **"Time to first useful sentence = first 30 tokens"** is a proxy that has not been validated.

## D. Robust

- **The 500-word cap comes back at judging time.** Robust removes the 250-word cap at generation, then truncates both sides to 500 words at judging. That clips the frontier answer and biases the result toward the app, which goes against "internet search + frontier AI models".
- **The city is pasted into the prompt as text.** "City given as '(The user's phone is in <city>.)'" turns V2's "[city I am currently in]" into a named-city query. That tests a different thing: the app's own offline GPS, and whether the user has to type the city at all, is skipped. The app should take device location itself, and the reference should be given the same location through its normal channel.
- **"any real, open, on-topic venue counts"** under-reads "best". "Open" also cannot be verified offline or from OSM.
- **The guardrail items are outside U, and they include "dangerous" items** that no clause in B31 mentions. Keeping them out of the ratio is correct. Calling them "Not in B31" is honest, and the same honesty should apply to the confident-error emphasis in general.
- **Unequal stratum sizes are called "uniform item weights".** With L = 20 and V = 10, the stratum weights are implicit and invented. Either state them, or weight strata equally.
- **The "web-validity diagnostic" tilts the item set.** If items are revised until web beats no-web, the set is selected on the reference's behaviour, which contradicts "nothing is filtered on any system's failures". Keep it as a diagnostic that is reported, never one that edits items.
- **It assumes Claude self-preference "can only bias it in the reference's favour".** That is asserted, not measured. XFAM shows a family offset, not its direction relative to the reference.
- **The 1B arm's configuration is unspecified** (plain or with RAG). See B.

## E. What every design gets right
- Install time is treated as setup time, not answer latency (B31:41).
- RAM is a device ceiling (B31:22).
- The APK sha is recorded, given "materially different from the version reviewed" (B31:69).
- The native app is scored, not the engine.
- Win-rate is not the bar.
- English-only is labelled as our choice.
- None claims the post author endorses the ruler (B31:15).

## Best design
The best basis is a hybrid built on Robust's absolute checklist scoring. It keeps four things from Robust: the dev and held-out split, the venue items inside the ratio, fresh items inside the headline, and items written outside Claude with a human fact-check.

From Traceable it takes three things: the source register (an element with no quote is cut), the three-band verdict that also shows the literal point estimate, and the kit that lets judges bring their own questions.

It fixes these defects:
- Remove Robust's 500-word cap at judging time.
- Give the app device location instead of pasting the city into the prompt.
- Drop Traceable's IDK = 1 floor.
- Run the 1B arm without our corpus.
- Score "best" in venue items with a human check.

The binary task-success ratio becomes co-headline with U. Judge-eye's speed-qualified U becomes a pre-registered speed verdict on the same configuration that produces U. Judge-eye's invented CE, safety and per-stratum gates move out of the verdict and into reported guardrails.

## Must-have
- Every ruler element traces to a verbatim public quote with its file path or URL, and anything without one is labelled 'our choice' (B31:60 'judged against the requirements above and the bar described in the post author's post')
- The headline is a ratio of usefulness, app vs reference, scored on an absolute scale where useless, empty and 'I don't know' answers all score 0, with no floor credit (B31:60 'a useful … research tool'; V1 'it's utility')
- The binary task-success ratio ('a casual user could act on this') is co-reported as the headline, because it is the only reading with a natural ratio meaning (B31:7 '>50% as good')
- The reference is a frontier model with live web search, no answer-length cap at generation or at judging, sources kept, and frozen on a dated run; at least two frontier families are reported, never a best-of-two per item (B31:7 'internet search + frontier AI models')
- The item mix is weighted toward casual lookup and contains all four named types plus factual lookup, with stratum weights stated and per-stratum results shown; 'difficult' items are tagged but not imposed as a large quota (B31:7 'casual info lookup and research tool'; B31:27 'beyond simple factual recall, including explanation, comparison, synthesis, and reasoning')
- Travel items, including V2's current-city query answered by the app's own offline location, are inside the headline ratio, and 'best' is scored by more than OSM existence tags (B31:7 'People travel with their phones into offline situations'; V2 'my eval is "Tell me the best vegan restaurants in [city I am currently in]"')
- Time-sensitive items are included in the headline and also reported without them; they are not designed out (B31:7 'internet search')
- A pre-registered speed verdict (wall-clock time to useful content and to the complete answer, p50/p90, on a named phone of 12 GB or less) on the same tier and configuration whose quality is the headline, with the post author's laptop tok/s quotes shown only as labelled context (B31:28 'respond at speeds that feel usable for real lookups on a phone'; B31:60 'requirements above and the bar')
- The scored system is the submitted native app build, identified by APK sha256 and git tag (B31:69 'materially different from the version reviewed'; B31:56 'functional submitted version')
- Pass/fail gates: device RAM of 12 GB or less, 50 GB or less installed, no INTERNET permission and 0 bytes captured during the run, no GMS, and GrapheneOS marked verified or unverified (B31:21-26)
- Install time is measured by a third party with the README only, reported with and without the asset download, and never presented as answer latency (B31:41 'get the app running locally within a few minutes')
- A plain 1B baseline arm without RAG runs through the same protocol and supplies the 1B-fail demo items (B31:50 'include ones a 1B model would fail on'; B31:9 '1B models that break on anything interesting')
- The verdict shows both the literal point estimate and the stricter CI-lower-bound reading, and states that the CI rule is ours; no invented safety, error-rate or per-stratum gate is folded into 'meets the bar' (B31:60 '>50% as good')
- Win/tie rate is always reported but never the bar, and the blog's pairwise test is not presented as the post author's method for this bounty (B31:60 '>50% as good', not 'wins 50%')
- Items are written outside the judge's and the reference's model family and fact-checked by humans; nothing is filtered on any system's failures; the set is hashed before the run; a stratified random human spot check is applied with PPI correction; the judge family is named next to every ratio (B31:62-67: readable by the post author and by contributors)
- The ruler states it is ours, is not endorsed by the post author, and is only a predictor of his own confirmation (B31:15 'not affiliated with it or involved in judging unless he chooses to weigh in'; B31:62)