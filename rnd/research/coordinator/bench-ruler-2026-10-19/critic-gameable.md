Ranked by how easily a rival or judge could attack each point in public. Each item gives the attack and then the minimum fix.

**1. A contestant writes the ruler, and outsiders cannot check the "pre-registration".**
- All three designs pre-register by sha256 in private repos (boar-eval and boar-rnd). Anyone can rewrite a private commit, so an outsider sees a hash that appeared after the results.
- We already switched the headline once after claim runs (CRITIQUE B#6). The new U metric is again being chosen after we know V-para is 0.26–0.44.
- **Fix:**
  - Publish the spec, the item-set hash and the APK sha256 somewhere public and timestamped before any run, for example a poidh comment, a Farcaster cast or OpenTimestamps. This needs r4to's OK.
  - Put a conflict-of-interest line at the top: "BOAR is an entrant; this ruler is ours, not the bounty's; the post author has not endorsed it (B31:15)."

**2. Forking paths in how the metric is chosen.**
- Traceable's done-check ("re-score the v0.1 dev set end to end") means the team will see U on our own outputs before freezing weights, anchors and the CE penalty.
- **Fix:**
  - Freeze the formula, anchors, weights and verdict ladder before any app output is scored under it. The dev pilot may test that the code runs, with numbers hidden.
  - Any later change becomes v1.1 and must be reported next to v1.0.

**3. The traceable design brings back the rubric floor it says it removes.**
- "An honest 'I don't know offline' … scores 1. It never scores 0." An always-decline arm then gets about 1/3.5 ≈ 0.29 U. That is the same artefact as raw 0.306 (audit-metric.md:8).
- **Fix:**
  - Abstain = 0 on every scored stratum. Robust already does this, crediting abstention only on G items.
  - Run a pre-registered **decline arm** and require its U ≤ 0.05 as a validity check.

**4. Speed: every design misreads a phone anchor, in our favour.**
- All three call the post author's numbers "laptop statements" and add no phone threshold. But B31:9 ("His past attempts got ~10 tokens/sec from 1B models") and V1 ("I've gotten like 10 TPS with 1B models … on a fully offline phone" context) describe a **phone** attempt he called unsatisfying.
- Our phone decodes at 5.5 tok/s (DEVICE-X6:16). That is below his failure anchor. A ruler that will not gate on the one axis where we are under his stated baseline looks self-serving.
- **Fix:**
  - Print decode tok/s and p50 time-to-complete next to U, compared against "~10 tok/s (B31:9, phone)".
  - Pre-register a **speed-qualified U** as a co-headline: only answers that finish within a declared wall time count. Judge-eye proposes 60 s; label it as our choice.
  - State that the 10 TPS complaint was joined to "break", so whether speed alone counted as failure is ambiguous.

**5. The item writer is an interested party who knows our corpus.**
- r4to drafts the items in all designs. He knows which topics the packs cover (Wikipedia, Wikivoyage, OSM, the SE packs), and "not filtered on failures" cannot be checked.
- **Fix, three parts:**
  - (a) Publish every drafted item, including rejected ones and the reason for each rejection.
  - (b) Generate slots from a public, seeded procedure: a random entity, city or country from a published list, combined with a stratum template. The author fills wording only.
  - (c) Report a **corpus-coverage audit**: the share of items whose key facts appear in the app's index, compared with the same share on V2-style items. Also accept items from contributors through traceable's bring-your-own-questions kit and report them separately.

**6. Family collisions are still present.**
- The robust design uses OpenAI and Gemini as writers and OpenAI as judge J2. J2 would then grade against key facts its own family wrote. Judge-eye and traceable leave the writer's family open.
- **Fix:** no family appears in both the writer and judge roles. For example, Gemini writes, and Claude plus OpenAI judge.
- The Claude-reference / Claude-judge overlap is acceptable only because it is conservative. State that, and measure it as J1−J2 on the reference's own utility (robust already does).
- "Stricter judge chosen per pre-registration" (robust) is ambiguous. Define it as min(U_J1, U_J2), computed per bootstrap resample.

**7. The human calibration is done by contestants and is not blind in practice.**
- r4to and the app maintainer have read thousands of BOAR answers and will recognise its style and citation format. That makes the PPI correction a channel for the authors' own bias.
- **Fix:**
  - At least one labeller who is not on the team, ideally a bounty contributor.
  - Rewrite the format of both answers the same way (plain text, citations as "[source: title]" with no domain).
  - Publish the labels. If no outsider is available, keep human labels as a reported κ only. Do not use them to correct the headline.

**8. Kept citations break arm blinding.**
- Traceable and judge-eye keep citations visible. Web URLs against offline-pack titles reveal which answer is which.
- **Fix:** normalise every citation to a title-only token for both arms. Report a no-citation sensitivity run.

**9. Venue gold is circular, and robust moves it into the headline.**
- The app answers from OSM, and the gold is OSM `diet:vegan` (VENUEGPS-2 caveat). Robust's V stratum inside U imports that circularity into the number.
- **Fix:**
  - Grade each venue a system names by human verification on the open web: it exists, is open, is vegan or vegan-friendly, and is in the city. Apply this to **both** arms.
  - Use a gold list only as a hint.
  - Until that is done, keep V out of U and report it on its own line as "the post author's own eval".

**10. Small n per stratum, and gates driven by noise.**
- Judge-eye gates on "no stratum U < 0.30" with 6–14 items per stratum, where a stratum CI is about ±0.15–0.20.
- PPI with 40 labels spread over 6–9 strata gives about 5 labels per stratum, so per-stratum κ means nothing.
- **Fix:**
  - Gate only on pooled quantities.
  - Report per-stratum U with its CI, and never as pass/fail.
  - Report κ pooled.
  - Use at least 80 held-out items, or label a smaller set "indicative".

**11. Weights are our choice, presented as derived from the text.**
- Judge-eye uses 20% travel, 6% honesty and so on. Its honesty stratum is anchored to **our own judge prompt**, not to any public clause, which breaks the traceability rule.
- **Fix:**
  - Headline = equal weight per bounty-named stratum (traceable).
  - Print per-stratum results so readers can reweight.
  - Pre-declare one alternative weighting (travel×2) as a sensitivity run.

**12. The construct of the reference.**
- `claude -p` plus WebSearch is not the product a user would run. Our own anchor shows web adds nothing the judge can see (1.029), and the 250-word cap shortchanges "internet".
- **Fix:**
  - Uncap the reference, or cap both arms the same way.
  - Keep the fresh stratum F in the headline (robust).
  - Keep robust's **web-validity check**: web beats no-web on L/T/V/F, or the report says the items do not test "internet".
  - Who adjudicates reference errors must not be the item author alone. Report U with and without the flagged items.
- Traceable lets a hedged stale answer score up to 3 on F items. Cap it at 1, since it does not answer the question.

**13. Checklist scoring rewards length, against "casual".**
- 3–7 key facts per item favour long answers.
- **Fix:**
  - At most 3 core facts carry most of the weight, and the rest are optional.
  - Log answer length per arm.
  - Report a length-controlled sensitivity run.

**14. The ruler cannot rank entries, but the contributor path is a ranking.**
- B31:67 says "select a winner they believe best satisfies". None of the designs says how rival apps would be scored. A ruler that only scores BOAR does nothing for judges, and a ruler we apply to rivals invites claims of sabotage.
- **Fix:**
  - Publish frozen items (dev split), references, judge prompts and `rejudge` with a simple input format: a question goes in, answer text plus timing comes out. Any entrant can then run it.
  - Offer to run rivals' public builds and share every trace so they can rebut.
  - Prove the scale works with separability: decline < 1B < app < offline laptop 35B < reference, with CIs that do not overlap. The laptop arm (O3, V2's "models that can run on a laptop") shows that 0.50 is reachable at all. A bar nobody can pass contradicts the bounty's premise.

**15. Unsourced claims about "the post author's queries".**
- Robust calls the 11 V-exact items "the post author's verbatim queries, already public". Four of them ("Tell me about Japan", PQ signatures, Mozi, and the Gríma Farcaster post) come only from **screenshots** in V2 or from a Farcaster post with no URL in our notes. "Paris to Rome and back" is our paraphrase of a blog example.
- **Fix:**
  - Cite each item to its exact public media or post URL, or label it "inferred from screenshot".
  - Mark Paris–Rome as a paraphrase.
  - Re-verify V1–V3 live; we read them through the fxtwitter mirror.

**16. The scored build is not what was submitted.**
- Every past number comes from the TypeScript engine, and the native app scores −0.089 against it.
- **Fix:**
  - Headline only on the native APK, on a phone, in airplane mode, with its sha256 matching the poidh claim build (B31:69).
  - Freeze the APK **before** the item hash is created, so tuning on the items is impossible.

**17. Win-rate presentation.**
- Rivals report 0 wins alongside a [competitor score removed] ratio. If we lead with U and bury W/T/L, we make the move we criticise in their claims.
- **Fix:** print W/T/L in the headline row on every card.

**18. Unverified gates.**
- GrapheneOS is untested, and "a few minutes" has not been timed.
- **Fix:** print "UNVERIFIED", never "pass". Time the install twice, excluding and including the download.

**19. Internal dates leak into a public document.**
- The designs mention 10-20, 10-23 and 10-25 as deadlines. The public text says "October 31st, 2026" (B31:64), and the issuer says there is no fixed deadline.
- **Fix:** cite only the public date in the public ruler.

## Best design
Use a hybrid built on **robust**:
- Its floor-free checklist utility (abstain = 0), hashed held-out split, native app scored on the phone, web-validity check, decline/1B/app/reference separability, and non-Claude item writers.
- Add **traceable**'s source register, its "no source, cut it" rule and the bring-your-own-questions judge kit. These are the strongest defence against "we wrote the ruler we pass".
- Add **judge-eye**'s speed-qualified U, anchored to the phone baseline of ~10 tok/s (B31:9), plus its confident-error rate.

Drop these parts:
- traceable's abstain = 1 floor
- judge-eye's invented stratum weights, its honesty stratum anchored to our own judge prompt, and its per-stratum gates
- robust's OSM-gold venue items in the headline and its writer/judge overlap with OpenAI

Robust survives best because its zero point and its held-out split are the hardest to game. The other two add the credibility it lacks: public traceability and an honest speed reading.

## Must-have
- Public, timestamped pre-registration (spec + item-set sha256 + APK sha256) before any run, plus a conflict-of-interest line: we are an entrant; the ruler is not the bounty's; the post author has not endorsed it (B31:15, B31:62)
- Source register: every rule, stratum and threshold cites exact public text (B31 line or the post author URL) or is labelled 'our choice'; V-exact items cite their post/screenshot URL or are labelled paraphrase/inferred (B31:60 'the bar described in the post author's post')
- Primary metric has a true zero: useless, generic or decline answers score 0; a measured decline arm U <= 0.05 validates this (B31:7 '>50% as good')
- Scored system = the submitted native APK on a <=12 GB phone in airplane mode, sha256 matching the claim build; APK frozen before the item hash (B31:22, B31:56, B31:69)
- Headline = min over two judge families of U, with the CI lower bound > 0.50 for MEETS, the point-above band and the below band printed; no family both writes items and judges (B31:60)
- Items: human-authored from a published seeded slot procedure, non-Claude assist, every drafted and rejected item published, corpus-coverage audit reported; contributors can add their own questions through the kit (B31:67 'spirit', anti-cherry-pick)
- Strata cover lookup, explanation, comparison, synthesis, reasoning and travel at equal weights, per-stratum results with CIs printed; a fresh/time-sensitive slice is kept in the headline (B31:7 'casual info lookup', B31:27)
- Reference = frontier model + live web, uncapped or capped the same as the app, frozen and archived; a web-validity check shows web beats no-web on lookup/travel/fresh items (B31:7 'internet search + frontier AI models')
- Current-city vegan eval with device location given to both sides, venues verified by humans for existence, vegan status and city on the open web (not OSM membership), reported on its own line (V2 https://x.com/VitalikButerin/status/2103762130554204651)
- Separability arms decline < 1B < app < offline laptop model < reference with non-overlapping CIs; 1B-fail demo items listed (B31:50, B31:9, V2 'models that can run on a laptop')
- Speed printed next to U: decode tok/s, p50/p90 TTFT and time-to-complete on the phone vs the ~10 tok/s phone anchor; speed-qualified U as a co-headline (B31:28, B31:9, V3)
- W/T/L both orders, confident-error rate per arm and legacy raw and floor-adjusted ratios in the headline row, never hidden (blog 'ask which is better'; comparability with rivals)
- Arm blinding: citations normalised to title-only tokens for both arms, length logged, length-controlled sensitivity run (judge validity for B31:60)
- Human calibration with at least one labeller outside the team, format-normalised, labels published; if that is not possible, report κ only and apply no correction (credibility for the contributor path, B31:67)
- Gates table: no INTERNET permission plus 0 bytes captured during the run, no GMS, <=50 GB installed, <=12 GB RAM, GrapheneOS 'verified' or 'UNVERIFIED', install stopwatch excluding and including the download (B31:21-26, B31:41)
- Entrant-agnostic kit: frozen dev items, references, judge prompts and rejudge with a question-to-answer+timing interface any app can run; traces shared with rivals for rebuttal (B31:67 'select a winner … best satisfies')
- Only public dates and sources: the decision date 'October 31st, 2026', no private chat, X quotes re-verified live before publishing (B31:64)