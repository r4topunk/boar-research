# Changelog

## v1.1, 2026-10-27: held-out sets retired and published

- Author decision after submission: open everything that is not private to him or to the app maintainer. No git history (still one snapshot).
- Added `rnd/heldout/` (1,277 files: 569 from the v0.2 and V-para run folders, 708 from health-fresh1-3, chat-v3, meta-fresh1, localgate, the Veil lane and the 160 files restored from the v1.0 overlap removal; 696 `.jsonl` files go to `r4topunk/boar-traces`, 581 other files stay here). Item files and the v0.4 ruler are in `boar-bench`. Map: `rnd/heldout/README.md`.
- The 160 files removed in v1.0 after the held-out overlap check are back at their original paths (`TRACES.md`, `docs/EXCLUDED.md`).
- Updated: `README.md` (held-out section, status), `docs/EXCLUDED.md` (what still stays out: private relays, spend, maintainer, credentials, history, unlicensed competitor sets), `rnd/research/coordinator/EXPOSURES.md` (every set retired), `BOM.md`, `NOTICE`, `DATA-CARD.md`, `TRACES.md`, `TRACES.tsv` (path, bytes, sha256 for all traces).
- Redaction map for the tranche: the v1.0 map without the held-out exclusions and id/set renames, plus per-call spend fields and API usage token counts dropped from references and judgments, adapter host labels that named a plan shortened, third-party emails and public BIP test keys scrubbed, OSM `phone` / `contact:*` dropped. Hash-pinned files were re-pinned.
- Content note on the health, crisis and medical-emergency probe sets: safety evaluation probes; AI-reviewed, not clinically reviewed; if you are in crisis, contact local emergency services.
- Pre-push pass (2026-10-28): competitor test-case text (`vit-fa-*`) removed from 26 added files (ids and scores kept); competitor names in the new data, code and file names replaced (`competitor`, `competitor-a`, `competitor-b`); gateway metadata and usage dropped from the evaluation-model cache; the Wikipedia cache restored verbatim; `costBasis` and token counts dropped from `ruler/refvar/refs/draw{A,B}.jsonl`; a file name with an unexpanded template (`sonar/exp/11-passage-selection/rows-k${process.env.K}.json`) renamed `rows-k-unset.json`; `docs/REDACTION-HASHES.tsv` released column brought up to date for 71 rows (including stale v1.0 rows); `TRACES.tsv` regenerated. Details: `rnd/heldout/README.md`.

## v1.0, 2026-10-26: full open record, history not exported

- Supersedes the earlier curated release (415 files: nine arms, reports, pack cards, BOM). This snapshot is the whole publishable working tree of the research lab, taken from the private repository's working tree at one point in time. **No git history is exported**; there is a single initial commit.
- 31,810 files, 1136 MB under `rnd/`, no file over 20 MB. 10,878 files were changed by redaction (names to roles, local paths and hosts made neutral, usage and spend lines removed); each has its original and released sha256 in `docs/REDACTION-HASHES.tsv`, and every sha256 written inside the record for those files was re-pinned to the released bytes.
- Added: `README.md` (map, reading order, reproduction steps), `docs/TIMELINE.md` (from `rnd/research/QUEUE.md`), `docs/HOW-THE-LAB-WORKED.md`, `docs/REDACTION.md`, `docs/EXCLUDED.md`, `DATA-CARD.md`, `BOM.md`, `NOTICE`, `CITATION.cff`, `data/` (the publication content base: public rows only).
- Licensing change: code and scripts are now MIT (the earlier release used Apache-2.0 for scripts); text stays CC BY 4.0; engine patches stay MIT.
- Not included: held-out and burnt evaluation sets, the app maintainer's data, private relays, competitor score tables, third-party raw web snapshots, spend ledgers, credentials, model weights (see `docs/EXCLUDED.md`).
- 2026-10-27: second leak pass before the first push (private correspondence lanes, maintainer-device scores, competitor questions and scores, spend residue removed; see `docs/EXCLUDED.md`); `tools/verify-criteria.py`, `docs/PIN-EXCEPTIONS.md` and `CONTRIBUTING.md` added; the engine base is reachable through the author's public fork.

- Raw `.jsonl` traces moved to the Hugging Face dataset r4topunk/boar-traces (same paths, sha256 in TRACES.tsv). 160 files that carried held-out item text were removed after a coordinator-run overlap check against the private held-out sets.
