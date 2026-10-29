# Changelog

## v1.1.2, 2026-10-29: device-final raw data, copyright quotations, corrections

Added
- DEVICE-FINAL M1 raw phone data, so the headline can be recomputed: the three phone output files (`arms/device-final/out/df-m1-v04-s42`, `s42b`, `s43`), the two derived trace files, the Opus and Codex judgments of both seeds, and the native-rc lite-s42 twin (outputs, traces, v0.4 questions, two judgments) are in `r4topunk/boar-traces` at the same paths, with sha256 in `TRACES.tsv`. `arms/device-final/tools/m1_agg.py` recomputes `aggregates/m1.json` from them without a model call. The per-item data of M2 to M4 and `native-rc/aggregates/rf.json` (needs the app maintainer's native-app files) are not published. The two arms' `.gitignore` files were changed to match.
- `data/` is now byte for byte the site's `/data/` (387 experiments, facts with `source_public` paths remapped, headline facts sourced, `decisions.md` and `glossary.md`); the 15 extra registry rows of v1.1.1 (13 of them withheld numbers of the app maintainer's app) and 7 internal decisions are gone. See `data/SCHEMA.md`.
- Credit: Boar's creator is named by his public handle @vaipraonde in `README.md` and `NOTICE`; his app's data stays unpublished, by policy.

Changed
- Copyright quotations withheld, as NHS wording was in v1.1.1: MedlinePlus encyclopedia (A.D.A.M.), healthdirect, Red Cross and similar quotations in the safety rules and first-aid-card files (60 files over both repositories; organisation and URL kept, `quotes_withheld` count and a licence note in place of the text). Pinned hashes were re-pinned (`docs/REDACTION-HASHES.tsv`).
- Tester-redaction corruption reverted in the data files (`pt-en.json`, `simplewiki-changed-titles.json`, the wikivoyage-rebuild diffs): only the strings the rule had changed were restored; the rule now applies to prose and logs only.
- Stale documentation fixed: version labels (1.1.2) in `README.md` and `CITATION.cff`; `REPRODUCE.md` (v1.1 layout and path map, public-data row for DEVICE-FINAL, the `floor_metrics.py` versions fe7c70b7 and 63080991, the section 4 step 0 path) and path-map notes in `BOM.md`, `README-claim.md` and `METHODS.md`; experiments count 387 in `CITATION.cff`; no v0.3 items were ever written; Step 1b of the `boar-bench` README (`hf download`, `pipx install huggingface_hub`).
- History wording: each release is one commit and earlier releases remain in the git history (`README.md`, `docs/EXCLUDED.md`, `CITATION.cff`, and the v1.0 and v1.1 entries below). Text withheld by a later release is still readable in the commits before it.
- Account and infrastructure names removed from three `chatroute/out` json files, the bench v0.4 critique log and `p0-deep-memory.md`.
- Licence lines: code MIT, text and data CC BY 4.0, traces dataset CC BY-SA 4.0 (it quotes CC BY-SA passages). The site footer and `for-ai` page no longer say Apache-2.0.

## v1.1.1, 2026-10-28

- v1.1.1: remaining NHS quotes withheld (52 files in the safety rules, first-aid-cards, fa-cards, co-hazard and bench/safety folders; organisation name and URL kept; affected sha256 pins re-pinned, see `docs/REDACTION.md` and `docs/REDACTION-HASHES.tsv`).

## v1.1, 2026-10-27: held-out sets retired and published

- Author decision after submission: open everything that is not private to him or to the app maintainer. One commit for the release (earlier releases remain in the git history; the first entry here originally said history was not exported, corrected in v1.1.2).
- Added `rnd/heldout/` (1,277 files: 569 from the v0.2 and V-para run folders, 708 from health-fresh1-3, chat-v3, meta-fresh1, localgate, the Veil lane and the 160 files restored from the v1.0 overlap removal; 696 `.jsonl` files go to `r4topunk/boar-traces`, 581 other files stay here). Item files and the v0.4 ruler are in `boar-bench`. Map: `rnd/heldout/README.md`.
- The 160 files removed in v1.0 after the held-out overlap check are back at their original paths (`TRACES.md`, `docs/EXCLUDED.md`).
- Updated: `README.md` (held-out section, status), `docs/EXCLUDED.md` (what still stays out: private relays, spend, maintainer, credentials, history, unlicensed competitor sets), `rnd/research/coordinator/EXPOSURES.md` (every set retired), `BOM.md`, `NOTICE`, `DATA-CARD.md`, `TRACES.md`, `TRACES.tsv` (path, bytes, sha256 for all traces).
- Redaction map for the tranche: the v1.0 map without the held-out exclusions and id/set renames, plus per-call spend fields and API usage token counts dropped from references and judgments, adapter host labels that named a plan shortened, third-party emails and public BIP test keys scrubbed, OSM `phone` / `contact:*` dropped. Hash-pinned files were re-pinned.
- Content note on the health, crisis and medical-emergency probe sets: safety evaluation probes; AI-reviewed, not clinically reviewed; if you are in crisis, contact local emergency services.
- Pre-push pass (2026-10-28): competitor test-case text (`vit-fa-*`) removed from 26 added files (ids and scores kept); competitor names in the new data, code and file names replaced (`competitor`, `competitor-a`, `competitor-b`); gateway metadata and usage dropped from the evaluation-model cache; the Wikipedia cache restored verbatim; `costBasis` and token counts dropped from `ruler/refvar/refs/draw{A,B}.jsonl`; a file name with an unexpanded template (`sonar/exp/11-passage-selection/rows-k${process.env.K}.json`) renamed `rows-k-unset.json`; `docs/REDACTION-HASHES.tsv` released column brought up to date for 71 rows (including stale v1.0 rows); `TRACES.tsv` regenerated. Details: `rnd/heldout/README.md`.

## v1.0, 2026-10-26: full open record

- Supersedes the earlier curated release (415 files: nine arms, reports, pack cards, BOM). This snapshot is the whole publishable working tree of the research lab, taken from the private repository's working tree at one point in time. It was published as one commit; earlier releases remain in the git history (this entry first said that no history was exported, corrected in v1.1.2).
- 31,810 files, 1136 MB under `rnd/`, no file over 20 MB. 10,878 files were changed by redaction (names to roles, local paths and hosts made neutral, usage and spend lines removed); each has its original and released sha256 in `docs/REDACTION-HASHES.tsv`, and every sha256 written inside the record for those files was re-pinned to the released bytes.
- Added: `README.md` (map, reading order, reproduction steps), `docs/TIMELINE.md` (from `rnd/research/QUEUE.md`), `docs/HOW-THE-LAB-WORKED.md`, `docs/REDACTION.md`, `docs/EXCLUDED.md`, `DATA-CARD.md`, `BOM.md`, `NOTICE`, `CITATION.cff`, `data/` (the publication content base: public rows only).
- Licensing change: code and scripts are now MIT (the earlier release used Apache-2.0 for scripts); text stays CC BY 4.0; engine patches stay MIT.
- Not included: held-out and burnt evaluation sets, the app maintainer's data, private relays, competitor score tables, third-party raw web snapshots, spend ledgers, credentials, model weights (see `docs/EXCLUDED.md`).
- 2026-10-27: second leak pass before the first push (private correspondence lanes, maintainer-device scores, competitor questions and scores, spend residue removed; see `docs/EXCLUDED.md`); `tools/verify-criteria.py`, `docs/PIN-EXCEPTIONS.md` and `CONTRIBUTING.md` added; the engine base is reachable through the author's public fork.

- Raw `.jsonl` traces moved to the Hugging Face dataset r4topunk/boar-traces (same paths, sha256 in TRACES.tsv). 160 files that carried held-out item text were removed after a coordinator-run overlap check against the private held-out sets.
