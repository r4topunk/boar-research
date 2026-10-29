# 18 · Reproduce it (appendix)

> Closed record · research record 1.1.2 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/reproduce/ · Markdown twin: https://r4topunk.github.io/boar-research/research/reproduce.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: —

**In one sentence.** Everything that can be rerun is public, and what cannot be rerun is named.

## For curious readers {#curious}

Yes, almost all of it. The benchmark questions, reference answers, judge prompt and scoring code are public, and you can run them on your own app with a few commands. Since 27 October that includes the sealed question sets and the new exam, with stored run traces for many experiments, including the raw phone outputs, traces and judgments of the final exam. What you cannot rerun exactly: the judge outputs (the judge is a closed model, so reruns agree closely but not bit for bit). Still private: personal correspondence, the app maintainer's data, spend records and the private lab's working history (the public repos keep one commit per release; earlier releases remain in history).

*Facts: [D-195]*

## For tech people {#tech}

### Plug your app into the same answer key

Everything you need to measure your own assistant is public: 60 v0.1 questions (57 judged), frozen Opus-plus-web references with provenance, the judge, the scorers and the floor metric. Write one trace per question with `itemId`, `answer.text` and `error: null`, run the judge with your own Claude Code login, and compute the three scales. The research record holds frozen criteria, arm reports, aggregates, the negative-results registry and pack cards; the engine is a public upstream commit plus each arm's patch.

**Published 2026-10-27:** the retired held-out sets and the second ruler v0.4 (items, both reference halves, drafts) in boar-bench (`bench/heldout/`, `bench/v0.4/`), with their runs in boar-traces; byte-identical to the hashes committed before opening, except documented redactions. **Not reproducible:** bit-identical judge outputs, the detector runner profile (not released). Rerun steps: [How to reproduce the key results](https://github.com/r4topunk/boar-research#how-to-reproduce-the-key-results-step-by-step) in the boar-research README. **Still private:** personal correspondence, the app maintainer's data, usage and spend records, credentials, the private lab's working history (the public repos keep one commit per release; earlier releases remain in history).

**Open fronts (as of 2026-10-28):** nothing in this chapter is pending. DEVICE-FINAL (OF-8) landed on 2026-10-25; its arm is public in boar-research under rnd/research/coordinator/arms/device-final/ (report, frozen criterion with its sha256, aggregates, tools). DEVICE-FINAL's M1 raw phone outputs, traces and judgments are in boar-traces (rnd/research/coordinator/arms/device-final/, listed with sha256 in TRACES.tsv); RETBENCH, PACKPROOF, UXMATRIX and X2B-BUDGET have their reports, frozen criteria and aggregates in boar-research, and their raw runs and judgments are not published (boar-traces holds only the PACKPROOF and UXMATRIX request files). The two fronts still open, the claim text (OF-5) and the shaped-pack publication (OF-7), are listed with what would change in the status file; the dropped fronts (OF-1 deep tier on a phone, OF-2 expert streaming on Android, OF-3 v0.3) keep their decision ids.

## For AI professionals {#ai}

### The record for this chapter

**Key facts:** engine = public upstream commit `0cfd4a77` + arm patch; bench = boar-bench v0.1 (questions, references, judge, scorers); models and packs listed in BOM.md of boar-research; not reproducible: bit-identical judge outputs (closed model), the emergency-detector runner profile (not released); rerun steps: [How to reproduce the key results](https://github.com/r4topunk/boar-research#how-to-reproduce-the-key-results-step-by-step) in the boar-research README. Updated 2026-10-28: the retired held-out sets and the second ruler v0.4 (items, both reference halves, drafts) were published on 2026-10-27 in boar-bench (`bench/heldout/`, `bench/v0.4/`) with their runs in boar-traces, byte-identical to the hashes committed before opening except documented redactions; the [D-195] rule (no v0.4 text before the result card) ended with the record. Still private: personal correspondence, the app maintainer's data, usage and spend records, credentials, the private lab's working history (the public repos keep one commit per release; earlier releases remain in history). The 2026-10-18 → 10-25 arm reports are public in boar-research under rnd/research/coordinator/arms/, among them RETBENCH (retbench/), PACKPROOF (packproof/), UXMATRIX (uxmatrix/), X2B-BUDGET (x2b-budget/) and DEVICE-FINAL (device-final/). DEVICE-FINAL's M1 raw phone outputs, traces and judgments are in boar-traces (rnd/research/coordinator/arms/device-final/, listed with sha256 in TRACES.tsv); RETBENCH, PACKPROOF, UXMATRIX and X2B-BUDGET have their reports, frozen criteria and aggregates in boar-research, and their raw runs and judgments are not published (boar-traces holds only the PACKPROOF and UXMATRIX request files).

### 10 What can be rerun, by whom, at what cost

The engine is a public upstream commit (0cfd4a77) plus per-arm patches; the benchmark (questions of every set, frozen references with provenance, judge, scorers, floor metrics), the raw run traces and the v0.3 plan are public; models and packs are listed with licences and revisions in the bill of materials. Every judgment row records judge model, CLI version, judge version and the sha256 of traces, questions and references, and everything after the judge is deterministic given the judgment rows. A full v0.1 judge pass is 114 calls (≈ 5 min at four shards). The retired held-out sets and the second ruler's items, references and drafts were published on 2026-10-27 (boar-bench bench/heldout/ and bench/v0.4/, runs in boar-traces; byte-identical to the hashes committed before opening, except documented redactions listed in bench/heldout/HASHES.md), so they can be rerun, but they are no longer unseen. Not reproducible from public material: bit-identical judge outputs (closed model; σ_judge ≈ 0.003) and the emergency-detector runner profile (base-model licence unknown; not released). Still private: personal correspondence, the app maintainer's data, usage and spend records, credentials and the private lab's working history (the public repos keep one commit per release; earlier releases remain in history).

*Facts: [F-371] [F-241] [F-242] [F-243] [F-959]*

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-241] Every judgment row records judgeModel, cliVersion, judgeVersion and the three input shas. 6 provenance fields · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed
- [F-242] Judge versions are tagged and never pooled: judge.v1 (Opus), judge.v1-low (cheap effort), judge.v1-med. tags (judge.v1 ratio) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · caveat: citation fix: the version tag is built at l.33
- [F-243] Everything after the judge (traces → metrics) is deterministic given the judgment rows. deterministic · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed
- [F-371] Resume safety: a cached judgment row is reused only if traces, questions and references sha256, judge version and model all match; else exit 7. exit 7 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-13
- [F-959] One full v0.1 judge pass is 114 judge calls (57 items × 2 orders). 114 calls · set v0.1 (status UNKNOWN) · judge Opus judge.v1 · n UNKNOWN · seeds UNKNOWN · CI not computed

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-195] 2026-10-21 · No public upload of v0.4 items or references; labels of FACT-AVAIL quarantined (coordinator-only) until the result card · why: held-out discipline. · status: kept (Update 2026-10-27: the rule ended with the record; the v0.4 items, both reference halves and drafts were published in boar-bench (bench/v0.4/), with their runs in boar-traces.)

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.1.2, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
