# health gate B+FU

> Living preprint · as of 2026-10-25 · map node G-health-gate-bfu (concept) · interim record, not a final result.

**health gate B+FU**

Plain: BoarLite's rule for health questions: when no trusted health source is found, it shows a fixed safe text with the emergency number instead of a model answer.

Technical: Predicate = the app's lexical health test OR 11 lexical rules (B: drugs, doses, vitals, child fever, symptoms, poisoning, alcohol, pregnancy, child dosing, trauma, altitude, diving) OR a short follow-up of a health turn (FU); runs after retrieval; health sources = firstaid, MedlinePlus, health Q&A packs. Final candidate: 41 of 65 safety probes fixed text, 0 new false fires on 251 non-health dev items; rules fitted on the probes.

## Incoming

- uses: [D-196] BoarLite: minimal health path; a fixed line replaces the ported warning line (D4); factbook v1 stays (D3 reverted); port the bench search → https://r4topunk.github.io/boar-research/map/d-196.md

Read chapter 15, One simple app: LabRat: https://r4topunk.github.io/boar-research/research/submission.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-2192] Health detector B+FU (prototype): the app's lexical health test OR 11 lexical rules (drug names, dose units and events, vitals, child fever temperature, symptoms, poisoning, alcohol, pregnancy, child dosing, trauma, altitude, diving) OR a short follow-up of a health turn; it gates 37 of 65 probes, including all 4 answers that had invented a dose figure, with 0 new fires on 251 non-health dev items and 1 of 40 adversarial items. 37 / 65 gated; 4 / 4 invented-dose answers; new false fires 0 / 251 and 1 / 40 · set 65 F3-SAFETY probes (dev) (dev, development data) · judge none (0 LLM) · n 65 probes; 251 + 40 non-health items · seeds UNKNOWN · CI not computed · date 2026-10-24 18:23 · caveat: Rules fitted on the same 65 probes (in-sample). Rejected: title overlap with health articles (gated 5 of 19 health self-tests) and a port of the mmBERT health detector (106 MB, 2-3 days). Health content: AI-reviewed, not clinically reviewed. Nothing here is medical advice.
- [F-2193] B+FU landed in BoarLite (a9ca9dd1): with retrieval, 41 of 65 probes get the fixed text, including the 4 invented-dose answers and 12 probes beyond ENGINE-RC's 41; on 60 health self-tests the predicate fires on 19 and the fixed text shows on 12, all 12 with only a Simple English Wikipedia or Vital-articles article kept, which the gate does not count as a health source; 2 of 60 UXMATRIX cooking items (food poisoning, an allergy) also get the fixed text. 41 / 65 probes; 12 / 60 health self-tests; 2 / 60 UXMATRIX items · set 65 F3-SAFETY probes (dev); 60 health self-tests (pack-written); UXMATRIX 60 (dev, development data) · judge none (0 LLM) · n 65 probes; 60 health self-tests; 60 UXMATRIX items · seeds UNKNOWN · CI not computed · date 2026-10-24 18:29 · caveat: Follow-up check: 12 fires on 96 follow-up turns (6 by the follow-up rule, all health follow-ups); 2 follow-up-only fires on 50 long-session turns (one debatable). The 12 Wikipedia-only self-tests are the Wikipedia-health limitation (see the 19:32 decision). Health content: AI-reviewed, not clinically reviewed. Nothing here is medical advice.
- [F-2210] BoarLite final candidate b4ef94f3 (search port ON_NO_HEALTH): 0-LLM gate on the 65 probes with history searched as the app does gives 41 fixed text, 1 exposure answer and 23 model answers, identical with the port off (the port changes no health path); the invented-dose and blood-pressure probes stay fixed; the health predicate is byte-identical (0 new false fires); release APK 3,044,169,517 B with no INTERNET permission. 41 fixed / 1 exposure / 23 model of 65; APK 3,044,169,517 B · set 65 F3-SAFETY probes (dev) (dev, development data) · judge none (0 LLM) · n 65 probes · seeds UNKNOWN · CI not computed · date 2026-10-24 19:40 · caveat: Engine tests, device-test compile and debug build pass. Health content: AI-reviewed, not clinically reviewed. Nothing here is medical advice.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-25. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
