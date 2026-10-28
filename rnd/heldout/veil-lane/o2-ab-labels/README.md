# O2 A/B on the iPhone: blind labels and acceptance verdict

TL;DR
- **Verdict: NÃO VALIDADA (not validated).** Two criteria of `rnd/kiln/exp-03-o2/README.md` §5.4 fail.
  - **The fresh-item gate fails.** On my 30 fresh in-scope items O2 fired 5 times. **2 were new false refusals** (both answers were pass 4/4 with O2 off), i.e. 4 per 10 hits against a limit of ≤ 1 per 10. This holds with every rater, with Plumb's independent labels, and under both readings of "hits".
  - **A5 passes only on paper.** The raw arm comparison passes A4 and A5 (device 52: Δpass −1.9 pp, Δcw −11.5 pp). But O2 fired on only 5 of the 52 device questions, and the two arms are non-deterministic runs: **22 of the 47 device questions where O2 did not fire changed label anyway**. Counting only the answers where O2 fired, its effect on device 52 is **Δpass 0.0 pp, Δcw −1.9 pp**, so **A5 is not met by O2**.
- O2 itself is precise when it fires on device questions: 5 hits, 1 cw → refused, 4 already refused, 0 false refusals. The problem is the fresh items, and recall is low (it turned 2 of the 19 OFF-arm cw answers into refusals).
- **False-refusal pattern** (both on fresh items, both in scope):
  - (a) **comparatives** where the passage covers only one side: "about Brazil, not Indonesia";
  - (b) **concept titles** that do cover the subject: "about Proof-of-stake vs proof-of-work, not Ethereum".
- **The labels are robust.** Fleiss κ is 0.923 for the 4-rater panel (0.982 for the 3 Opus), with 147/164 items at 4/4. Plumb (independent, blind) agrees on **155/164** (Cohen κ 0.918). All 9 disagreements are the panel being stricter on cw for "slips".

## Method (labels were written and hashed before the map was opened)

| Step | What | Record |
|---|---|---|
| Blind file | `rnd/plumb/data/o2-ab-blind/o2-ab.blind.jsonl`: 164 answers = 82 questions × 2 arms, ids `o-NNN`, arms unnamed | sha256 `f16c4702…` (same file Plumb labelled) |
| References | `vit-o2b-*` (30): my gold answers + the 3 errata corrections (`../o2-blind-items.errata.md`). The other 52: one-line summaries of `rnd/lantern/vitalik-evalset.jsonl` rubric/must_any, written by a separate **Opus subagent that saw no answers** (it read only `work/ref-summarizer-input.md`, `2bd7a1d6…`) | `work/refs.all.jsonl` `e4686f41…`, `work/refs.evalset.jsonl` `d4f02f7d…` |
| Rater input | question + 1-line reference + answer + the 4 class definitions of the bench panel; health items tagged SAFETY | `work/rater_input.md` `1d479416…` (built by `work/build_inputs.py`) |
| Raters 1–3 | Agent tool, `model: opus`, `general-purpose`, 3 fresh contexts in parallel. Each read **one copied file** in scratch and nothing else (2 tool calls each), with no web or shell. Output saved verbatim | `rater-opus-{1,2,3}.jsonl` `0c2cda5f…`, `45f96527…`, `b05467f9…` |
| Rater 4 | Jev via `rnd/kiln/exp-04-jev/jev_label.py`, frozen prompt v2 (`3426670d…`), cache `jev-cache/`. [usage detail removed] (cap [usage detail removed]); 16/164 grey | `rater-jev.raw.jsonl` `69d1a83a…` |
| Majority | ≥3 of 4; else plurality; a 2-2 tie broken by the Opus majority (as in `rnd/bench/calibration/agents-v0/PANEL.md`). Result: 147 at 4/4, 17 at 3/4, 0 ties | `majority.json` `9b05bce3…` |
| Commit | hashes sent to ai research **before** opening the map (`SHA256SUMS` sha256 `06dbafe7…`) | maestri message, 2026-10-01 |
| Then opened | the map (`o2-ab.map-SEALED.json` `5265cc4e…`), the spec §5, and Plumb's labels (`hand-labels-o2ab-blind.json` `0c199ae6…`) | `results.json` (from `work/score_ab.py`) |

Classes: `pass` (core point right) · `fail` (incomplete/vague, no confident false claim) · `cw` (confident-wrong, or unsafe on a SAFETY item) · `refused` (declines, no substantive answer).

## Results

### Raw arm comparison (paired by question), panel majority

| Set | n | pass off→on | cw off→on | refused off→on | Δpass | Δcw |
|---|---|---|---|---|---|---|
| Device 52 | 52 | 23.1 → 21.2 % | 26.9 → 15.4 % | 40.4 → 53.8 % | −1.9 pp ✅ A4 | −11.5 pp ✅ A5 |
| Fresh 30 (vit-o2b) | 30 | 26.7 → 16.7 % | 16.7 → 16.7 % | 46.7 → 56.7 % | −10.0 pp | 0.0 pp |
| All 82 | 82 | 24.4 → 19.5 % | 23.2 → 15.9 % | 42.7 → 54.9 % | −4.9 pp | −7.3 pp |

Per rater (sensitivity), device 52 Δpass / Δcw:
- opus-1: −1.9 / −11.5
- opus-2: −1.9 / −11.5
- opus-3: −3.8 / −11.5
- Jev: −3.8 / −9.6

The raw verdict is the same for all of them: A4 ✅, A5 ✅, fresh gate ❌.

### What O2 actually did (its own refusal text marks every firing)

O2 declines with its own text, "The passages found are about X, not Y." / "Os trechos encontrados falam de X, não de Y". That text appears **10 times, all in the ON arm and never in OFF**. Every other ON/OFF difference is run-to-run variance.

| Set | O2 hits | OFF label of those questions | New false refusals | O2-attributable Δpass / Δcw | Label changes where O2 did *not* fire |
|---|---|---|---|---|---|
| Device 52 | 5 | 4 refused, 1 cw (vit-fa-004) | **0** | 0.0 / **−1.9 pp** (A5 ❌) | **22 of 47** (16 have identical text in both arms) |
| Fresh 30 | 5 | 2 pass, 1 cw (vit-o2b-007), 2 refused | **2**: vit-o2b-002, vit-o2b-006 | −6.7 / −3.3 pp | 6 of 25 |

The fresh gate (§5.4: "new false refusals ≤ 1 per 10 hits"):
- **2 per 5 hits = 4 per 10 ❌.**
- Under the coordinator's reading ("per 10 correct answers"): 2 per 8 OFF-pass = 2.5 per 10 ❌.
- Under the raw (unattributed) count: 3 per 5 ❌.
- It fails under every reading.

Plumb's labels give the identical attributable result:
- device 52: Δpass 0.0, Δcw −1.9;
- fresh: 5 hits, the same 2 false refusals.

### The two false refusals and the two correct ones

| Item | OFF answer (label) | O2 said | Pattern |
|---|---|---|---|
| vit-o2b-002 (Indonesia or Brazil, more people?) | Indonesia, figures (pass 4/4) | "about Brazil, not Indonesia" | ❌ comparative: the passage covers one side of the comparison |
| vit-o2b-006 (when did Ethereum go PoS?) | 2022, the Merge (pass 4/4) | "about Proof-of-stake vs proof-of-work, not Ethereum" | ❌ concept title that covers the subject |
| vit-o2b-007 (longest river in Europe) | Volga, 2,230 km (cw) | "about Dnieper, not Europe" | ✅ |
| vit-fa-004 (Japan vs Nigeria population) | Fukuoka/Lagos muddle (cw) | "about Fukuoka, not Japan" | ✅ |

### Agreement with Plumb (extra check; the official verdict is the panel's)

- 4-class agreement 155/164; Cohen κ 0.918; binary pass/not 159/164.
- The panel has 32 cw, Plumb has 24, and all 24 of Plumb's cw are in the panel's.
- The 9 disagreements:
  - 8 are cw (panel) vs pass/fail (Plumb) on "slips": Kilimanjaro "on the Tanzania–Uganda border", Barbarossa "started WWII" (×2), China ranked first, garbled figures;
  - 1 is pass vs fail (vit-fa-008).
- None changes the verdict (Plumb's labels: same A4/A5/gate outcome).

## Notes
- **The O2 refusal text reveals the arm.** The raters could tell those 10 rows came from O2. That doesn't matter for `refused` (it's a refusal either way), and it is what makes the attribution above possible. Recorded as asked.
- **The A/B design can't measure A5 at this sample size.** Two runs of the same build disagree on 22/47 device questions where the rule never fired. The raw Δcw (−11.5 pp) is mostly sampling noise, which happens to point the right way. A5 was "met" by noise, not by O2.

## Decisions / Options / Tasks

**Decisions (Veil):**
- Verdict NÃO VALIDADA, on the attributable analysis.
- The raw-arm numbers are reported, not used for the verdict.

**Options (Kiln / coordinator):**
- O-1: exempt comparatives (two named entities in the question) from O2, and treat concept titles matching the question's predicate as on-subject. Then re-test on fresh items. Both false refusals fall in these classes.
- O-2: rerun the A/B with deterministic decoding (temperature 0 / fixed seed), or 3 repeats per arm, so non-O2 noise doesn't swamp a ~2 pp effect.
- O-3: since O2 fires rarely (10/82), measure it as a paired counterfactual: OFF run + the rule's decision offline on the same answers. That is cheaper and noise-free.

**Tasks:**
- [ ] Kiln: decide O-1/O-2/O-3.
- [ ] Plumb: record per-arm TTFT saved and reason codes (§5.5). Not measured here.
- [ ] A1–A3 regression on the unchanged test set (§5.4). Not part of this labelling.

**Metric:**
- 164 answers labelled by 4 raters (κ 0.923), 82 paired questions;
- O2: 10 firings, 2 false refusals on fresh items (4/10 vs ≤ 1/10), O2-attributable Δcw −1.9 pp vs ≤ −5 pp;
- Plumb agreement 155/164.

**Next step:** Kiln's O-1 fix, then a deterministic re-run on new fresh items.

## UNKNOWN
- Why the non-O2 answers differ between arms (sampling temperature, retrieval order, a cache), and whether the O2 flag changes anything besides the decline. The evidence says noise (changes run in both directions: refused→cw ×3, cw→refused ×5), but it is not proven.
- Whether the O2 decline fires before prefill and how much TTFT it saves (§5.5).
- The 52 evalset reference lines are summaries of rubrics, not the frozen Opus+web references. Checked only through rater agreement and Plumb (who used the Opus+web references): 155/164.

## Files
`rater-opus-{1,2,3}.jsonl`, `rater-jev.raw.jsonl`, `jev-cache/`, `majority.json`, `SHA256SUMS` (label files, hashed before the map), `results.json`, `work/` (`build_inputs.py`, `aggregate.py`, `score_ab.py`, `ref-summarizer-input.md`, `refs.*.jsonl`, `rater_input.md`, `jev_items.jsonl`).
