# rnd/heldout: the retired held-out sets (public since 2026-10-27)

TL;DR: on 2026-10-27, after the project was submitted, the author retired every held-out set and opened everything that is not private to him or to the app maintainer. The sets are now **public development data**, not a held-out claim: a number measured on them again would validate nothing. This folder holds their **runs, judgments, labels, round reports and method documents**. The **question items and reference answers** are in the sibling repository `boar-bench` (`bench/heldout/<set>/`, and `bench/v0.4/`). The raw `.jsonl` traces are in the Hugging Face dataset `r4topunk/boar-traces` at the same paths (`TRACES.tsv`, sha256).

**Content note (health, crisis and medical-emergency probes).** Several of these sets are safety evaluation probes: they contain questions about medical emergencies, danger, drugs, crisis and self-harm, and the model answers (and judge rationales) to them. AI-reviewed, not clinically reviewed. Nothing here is medical advice. If you are in crisis, contact local emergency services.

## Map (published folder, what it is, where it came from)

| folder here (and in the traces dataset) | what it holds | source folder in the private lab |
|---|---|---|
| `bench-v02/` | bench v0.2 (110 items, written by two blind Claude-family writers): run traces, Opus/Haiku/Codex judgments, pack and deep-tier arms, coverage and similarity files, refs and plan hashes | `blind/bench-v02/` |
| `vitalik-para1/` | V-para (58 = 51 judged + 7 venue items, public name in the record: V-para): cut 3 / cut 6 claim runs, deep-tier, thinking, venue-GPS, cross-family (XFAM) runs, gold venue snapshots (OSM, ODbL) | `blind/vitalik-para1/` and 2 judgment files from `boar-eval/blind/vitalik-para1/` (suffix `.from-boar-eval.jsonl`, different content from the same-named file) |
| `health-fresh1/`, `health-fresh2/`, `health-fresh3/` | health safety sets (120 / 150 / 120 items): and/ios control-vs-arm runs, kiln reports, hand reads, wrong-card checks | `blind/health-fresh1..3/runs` |
| `chat-v3/` | synthetic multi-turn chat set (64 items): R0/R1/R2 runs and hand reads | `blind/chat-v3/runs` |
| `meta-fresh1/` | meta questions about the app (36 items): R0/R3 runs | `blind/meta-fresh1/runs` |
| `localgate/` | probe data for the local gate: judge-labelled `has_fact` / `quote_supports` labels and harvested passages (Wikipedia and pack text); `harvest-packcond` is split in two parts (`cat harvest-packcond.part1.jsonl harvest-packcond.part2.jsonl > harvest-packcond.jsonl`) | `blind/localgate/` |
| `veil-lane/` | the Veil lane: round reports and evidence for the h1/h2/h3/hm/o2 sets, `o2-ab-labels` (three Opus raters and an evaluation model), `offline-proof` (static audit of public APKs, no device data), `threat-model.md`, `options-eth-verifiability.md`, `pr/pr-body.md`, `quarantine/` (Kiln/Plumb-era runs on early sets whose items the engine team had already seen: contaminated, published as dev data), `h2-pool-round/wiki-cache/` (146 Wikipedia article texts, CC BY-SA 4.0, rebuildable from `pages.txt`) | rnd/veil (private lab path) |

The sets without runs here (es-fresh1, es-fresh2, crisis1, hm-fresh1-3, hm-loc1, h1-fresh, h2-fresh, h2-pool, o2 item files) have **items only**, in `boar-bench`. The v0.4 ruler (75 items, references, drafts, critiques, disagreements, the round-2 writer prompts; round 1 followed `rnd/research/coordinator/BENCH-ITEMS-BLUEPRINT-2026-10-20.md`) is in `boar-bench` `bench/v0.4/`; its hashes `f9ad2f2f...` (items) and `23b6febf...` (candidate) were public before and still verify byte for byte.

Also restored in v1.1 (original paths, not under `heldout/`): 160 files that v1.0 had removed after an overlap check against the then-private sets (115 `.jsonl` in the dataset, 45 other files in this repository), under `rnd/research/{coordinator/arms,sonar/exp,compass,anvil,ruler}` and `rnd/kiln/`.

## Status and how to read it

- Every set here is **dev data now**. The exposure ledger (`rnd/research/coordinator/EXPOSURES.md`) keeps the history: which set was spent on which claim, by which judge, and what was seen by whom. "Held-out" in older reports means held-out *at the time of that run*.
- Numbers on V-para and v0.2 in this record are Claude Opus judge numbers unless a file says otherwise (the cross-family check is `vitalik-para1/runs-xfam/`, `bench-v02/runs-xfam/`). The final number of the project is the device run on the v0.4 ruler (`rnd/research/coordinator/arms/device-final/`).
- A final held-out number for any later system needs a new set written after this date.

## What was changed on the way out

- Redaction as in v1.0 (`docs/REDACTION.md`): names to roles, local paths and hosts neutral, usage and spend lines removed, per-call spend fields dropped from judgments and reference runs (`listPriceEquivalentUsd`, `costBasis`, API usage token counts), adapter host labels that named a plan shortened to `claude-code`. Item ids, set names and item text are **not** rewritten here (the v1.0 held-out rules were switched off for this tranche), so joins by id work.
- Files that are hash-pinned by other files (judgments pin traces, `SHA256SUMS`, `MANIFEST.json`, `RUN-MAPPING.sha256`) were re-pinned to the released bytes. For the item, reference and plan files, whose hashes were committed while the sets were held out (some publicly), `boar-bench` `bench/heldout/HASHES.md` and `HASHES.tsv` list the original and the released sha256 side by side.
- Venue records in `runs-venuegps`: the `phone` and `contact:*` fields of OpenStreetMap places were dropped (business contact data). Venue coordinates are city-centre landmarks (public squares), kept.
- Third-party emails inside retrieved passages are replaced by `[email removed]`; public BIP test-vector keys in pack text are replaced by a placeholder.
- **v1.1 pre-push pass (2026-10-28):** (a) the 27 test questions of a competitor team's public test set (`vit-fa-*`, removed from the bench in v0.1) came back through the Kiln/Plumb quarantine runs and the o2-ab label inputs; in 26 files (24 `.jsonl` in the dataset, `o2-ab-labels/work/ref-summarizer-input.md` and `rater_input.md` here) their question, rubric, reference, answer and source fields were replaced by `[competitor case text removed in v1.1]`; ids, labels, routes, timings and scores are kept. (b) Competitor names in data, code and file names are now `competitor` (v0.2 similarity files) or `competitor-a` / `competitor-b` (Veil lane: offline-proof reports renamed `competitor-a-1.0.0.*`, `competitor-b-1.1.10.*`). (c) The evaluation-model cache `o2-ab-labels/jev-cache/` lost its gateway metadata and usage counts. (d) `h2-pool-round/wiki-cache/` is the verbatim Wikipedia text again (a spend rule had replaced dollar amounts in it). (e) `ruler/refvar/refs/drawA.jsonl` and `drawB.jsonl` (in the dataset) lost `costBasis` and token counts, as this section says. Every pin that named a changed file was re-pinned.

## Licences and attribution

Our text, rubrics, labels and reports: CC BY 4.0. Retrieved passages and article texts quote Wikipedia/Wikivoyage (CC BY-SA 4.0), OpenStreetMap (ODbL 1.0, (c) OpenStreetMap contributors), Stack Exchange posts (CC BY-SA 4.0; the post authors' display names in `bench-v02/runs-packs` replays are kept because the licence requires attribution), MedlinePlus (public domain). The traces dataset is CC BY-SA 4.0 for that reason. Model answers are outputs of open-weight models (Qwen, Gemma and others) and of the judge/reference models named in each file.
