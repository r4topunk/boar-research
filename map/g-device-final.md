# DEVICE-FINAL

> Living preprint · as of 2026-10-25 · map node G-device-final (concept) · interim record, not a final result.

**DEVICE-FINAL**

Plain: The last benchmark run: the submitted app answers the test sets on the phone itself, overnight.

Technical: Frozen criterion 2026-10-25 03:3x: LabRat 7788924a on a Pixel 8a; M1 ruler v0.4 × seeds 42/43/44 (Claude Opus all seeds, OpenAI gpt-5.6-sol seed 42), M2 65 safety probes, M3 140 on-K13 self-tests, M4 UXMATRIX 60, M5 speed/memory/offline. Claim numbers = M1 + M5. Running as of the 2026-10-25 update; no results recorded.

## Incoming

- uses: [X-406] DEVICE-FINAL: DEVICE-FINAL: final on-phone matrix of LabRat (engine 7788924a; APK 0ad476ca) → https://r4topunk.github.io/boar-research/map/x-406.md

Read chapter 15, One simple app: LabRat: https://r4topunk.github.io/boar-research/research/submission.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-2227] DEVICE-FINAL criterion frozen (sha256 recorded) on 2026-10-25 03:3x, before any matrix generation: LabRat 7788924a answers on a Pixel 8a 8 GB in airplane mode on AC power. Matrix: M1 ruler v0.4 (75 items, 88 turns) on seeds 42, 43 and 44, judged as in RULER-FINAL (Claude Opus vs Claude references on all three seeds; OpenAI gpt-5.6-sol vs its references on seed 42, further seeds optional), reporting per family the U-total, CI, win-rate, refusals, the minimum over families, the three-seed mean and a phone-vs-desktop parity read against the b4ef94f3 desktop twin (not a verdict); M2 the 65 safety probes (0 LLM); M3 the 140 on-K13 pack self-tests and M4 the 60 UXMATRIX items (Claude Haiku labels); M5 latency, time to first token, decode speed, memory, battery temperature, three cold starts and the app's network counters over the night. Claim numbers = M1 (both families named, seeds stated, win-rate first) and M5 (speed, memory, offline); M2-M4 are product numbers. No tuning, no engine change. matrix M1-M5; claim numbers = M1 + M5 (ruler U-total) · set bench v0.4 (exposed); 65 safety probes; 140 on-K13 self-tests; UXMATRIX 60 (dev, development data) · judge Claude Opus + OpenAI gpt-5.6-sol (M1); Claude Haiku 5.5-low labels (M3, M4); none (M2, M5) · n 75 items × 3 seeds + 265 product items · seeds 42, 43, 44 (M1); 42 (M2-M4) · CI not computed · date 2026-10-25 03:3x · caveat: No DEVICE-FINAL result is in this record; the matrix was running as of this update.
- [F-2228] DEVICE-FINAL started overnight on 2026-10-25 at the author's request (final benchmarks with the app running the engine on the phone, for publication): the device eval runner was patched on an eval branch to answer follow-up turns with the chat's history and to record the streamed text the chat shows; engine logic untouched; the unbundled release was installed over the bundled data with the same signing identity; a pre-run smoke and a follow-up-turn check passed. running · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-25 03:3x · caveat: No DEVICE-FINAL result is in this record; the matrix was running as of this update.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-25. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
