# Bench v0.2: pre-registered knowledge-coverage split of the judged ratio (blind-safe tooling)
TL;DR: Give every keyed v0.2 item a coverage class (is its answer in the kit BOAR ships, only its article, or nothing), computed mechanically after the items are frozen. Report the judged ratio per class next to the headline raw ratio. On v0.1 the Android 4B scores 0.56–0.61 on in-kit items vs 0.44–0.46 on items whose article isn't installed. The split must be pre-registered in v0.2's frozen analysis plan, or it reads as cherry-picking.
Lane: Sonar (F3 support) · Status: **adopted as bench v0.2 pre-run addendum 01** (boar-eval 0539719, `bench/v0.2/plan/addendum-01-coverage-split.md`; tool frozen fe7ba6a1…) · Priority: A
Axes moved: none of the engine's. This is claim honesty and interpretability. It tells readers (and the post author) how much of the gap to frontier+web is knowledge BOAR doesn't ship versus answers it gets wrong with the knowledge present. It is consistent with r4to's framing decision: the bar is on the raw ratio, with side-by-side views. This is one more pre-declared view, not a replacement.
Fits BOAR? Desktop script only (`tools/coverage_classes.py`, stdlib + Python 3.14 zstd). It reads the installed packs and the items file. No engine change, no download.

Blind-safety (MANDATE: never open `rnd/veil/`):
- Sonar never opens v0.2 items. The coordinator or Veil runs `coverage_classes.py ITEMS --out PATH` after freezing; the tool prints aggregate counts only and writes per-item classes to the runner's path.
- Classes are mechanical: answer key (precheck `must_any`/`must_k`) × referenced article titles (Wikipedia/Wikivoyage URLs in `reference_sources`) × installed pack text. No judgment, no BOAR traces, nothing that could leak BOAR's behaviour into item writing.

Evidence (public v0.1 only, `tools/coverage_classes.py --vital5`, 2026-10-02):

| Class (kit A + vital5) | Items | Android Qwen3-4B s42 (no vital5) | Android 4B + vital5 s42 |
|---|---|---|---|
| in-kit-key: the key is in the installed text of a referenced article | 21 | 0.562 | 0.610 |
| in-kit-no-key: the article is installed, the key isn't (intro-only, etc.) | 13 | 0.577 | 0.548 |
| not-in-kit: no referenced article installed | 18 | 0.461 | 0.436 |
| unkeyed: venue / first-aid / judge-only, not classified | 8 (5 judged) | 0.419 | 0.405 |

- Read: the 4B is above 0.50 where the knowledge is in the kit and well below it where it isn't. The flat E1(a) total hides this split.
- Caveat: one seed per run, small classes. Both runs are classified against the vital5 kit, while `and-qwen` ran without vital5. The runner should classify each run against its own kit (drop `--vital5` for kit A).

Protocol for v0.2 (to pre-register in the frozen analysis plan, before any BOAR run):
1. Every factual item gets a precheck answer key (`must_any` and/or `must_k`) and its reference URLs. These are Veil's normal fields. Without a key an item is "unkeyed" and stays out of the split.
2. After freezing (items + references hashed), the runner executes `coverage_classes.py` with the **claim kit's** packs.
   - Store the output's sha256 in the analysis plan.
   - Pack shas: those in the corpus manifest.
3. Reports show, side by side:
   - the raw ratio (the bar);
   - the floor-removed and above-always-decline views (r4to's decision);
   - **the per-class ratio with item counts.**
   - No class is ever reported alone.
4. Classes are computed once per frozen kit. A kit change (e.g. adding a pack) means a new, declared classification, never a silent re-split.

Test: no boar-eval arm. Done when the analysis plan for v0.2 includes step 2's hash and step 3's table, and a dry run on v0.1 public reproduces the table above.
Cost: ~1 h for the runner (run the script, paste the table). Risk: misuse as cherry-picking. Pre-registration and "never alone" address that.

## v0.2 classification (pre-run; coordinator, boar-eval a913563; aggregates only)

| Kit | in-kit-key | in-kit-no-key | not-in-kit | unkeyed |
|---|---|---|---|---|
| kit A | 16 | 15 | 79 | 0 |
| kit A + vital5 | 30 | 44 | 36 | 0 |

(110 v0.2 items.)
- With kit A, 72% of v0.2 items reference no installed article; with vital5, 33%.
- The per-class view must always name the kit it was computed against.
- `key_in_context.py` is frozen alongside (84182b67).

## Pre-registered prediction for option 6 (deep tier, 35B-A3B), written 2026-10-02 13:10 BRT, before any deep-arm run

The deep arm runs on the `and-qwen` kit (no vital5, no big pack) with a 400-token context (Anvil `deep-tier-streamed-moe`). If its gain over the 4B fast tier comes from the larger model's stored knowledge, as Summit and Anvil expect, then on bench v0.1 with `coverage_classes.py` (kit A, no `--vital5`):
- **P1.** The paired Δratio (deep − fast, same items) is larger on `not-in-kit` + `in-kit-no-key` items than on `in-kit-key` items.
- **P2.** On `in-kit-key` items, |Δratio| ≤ 0.05: the knowledge is already in the context, so the reader matters less there.
- This is a falsifiable diagnostic, not a pass/fail criterion for the arm (that's Anvil's frozen Δ ≥ +0.05). If P1 fails, the deep tier's gain is not knowledge but reasoning/synthesis, which changes how the claim should describe it.
- The runner computes it from the arm's judgments + `coverage_classes.py`. I'll do it read-only when the judgments land.

### Preliminary check (seed 42 only, 2026-10-02 15:15; `exp/16-deep35-coverage/result-s42.txt`)

deep35-s42 vs its fast-tier base srv-s42 (Qwen3-4B, server backend); kit-A classes on public v0.1.

| Items | n | Fast | Deep | Δ |
|---|---|---|---|---|
| all | 57 | 0.518 | 0.545 | +0.028 |
| in-kit-key | 11 | 0.628 | 0.613 | −0.015 |
| not-in-kit + in-kit-no-key | 41 | 0.500 | 0.536 | **+0.036** |
| unkeyed | 5 | 0.419 | 0.473 | +0.054 |

- **P1 holds, P2 holds** (preliminary): the deep reader's gain sits where the kit doesn't carry the answer, i.e. stored knowledge.
- Final read after s43 is judged.
- Not the arm's verdict: that is Anvil's frozen Δ ≥ +0.05, read by Kiln.

### Final check (2 seeds, 2026-10-02 16:45; `exp/16-deep35-coverage/result-final.txt`)

Pairs: (srv-s42, deep35-s42) and (and-qwen-s43, deep35-s43). The s43 fast base is the node backend; no srv-s43 exists. Item bootstrap 2,000, seed 11.

| Items | n | Δ deep − fast | 95% CI |
|---|---|---|---|
| all | 57 | +0.055 | +0.019 … +0.092 |
| in-kit-key | 11 | +0.026 | −0.047 … +0.094 |
| not-in-kit + in-kit-no-key | 41 | **+0.064** | **+0.019 … +0.110** |
| unkeyed | 5 | +0.039 | +0.000 … +0.113 |

- **Aligned to Kiln's base** (coordinator request; `result-final-aligned.txt`): both fast bases on the server backend (`srv/srv-s42`, `maple/qwen-srv-s43`):
  - all **+0.060** [+0.023, +0.096], identical to Kiln's deep35 Δ;
  - in-kit-key +0.036 [−0.038, +0.106];
  - out-of-kit **+0.069** [+0.023, +0.114];
  - unkeyed +0.042 [+0.001, +0.107].
  - P1 and P2 still hold. These aligned numbers supersede the mixed-backend table above.
- **P1 HOLDS, P2 HOLDS.** The deep tier's measurable gain sits on items whose answer the kit doesn't carry (its CI excludes 0); on in-kit items the change is within ±0.05 and the CI spans 0.
- Claim wording this supports: "the deep mode adds stored knowledge beyond the offline kit", not "it reasons better on what the kit provides".
- Kiln's arm verdict: quality passes (+0.060), phone memory fails (10.0–10.3 GiB vs ≤ 8 GiB).

## Details

Why this matters for the claim: S1's fallback framing says the CI may include 0.50. A decomposition showing "above 0.50 on what the offline kit covers, below on what it doesn't" is honest. It is also actionable for anyone extending BOAR's packs, and it is the evidence behind Summit's reading that the 4B's gap is partly knowledge. It doesn't move the headline number.

Limitations:
- `must_any` terms are a loose proxy for "the answer is in the text": a term can appear in an unrelated sense.
- Reference URLs are Opus+web's choices, so an item answerable from an article the reference didn't cite is misclassified as not-in-kit. That is an UNKNOWN share.
- Article-level (whole installed text), not passage-level, so it says the kit *contains* the answer, not that retrieval *finds* it. Retrieval reach is `key_in_context.py`'s job.
