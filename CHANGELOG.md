# Changelog

## v1.0, 2026-10-26: full open record, history not exported

- Supersedes the earlier curated release (415 files: nine arms, reports, pack cards, BOM). This snapshot is the whole publishable working tree of the research lab, taken from the private repository's working tree at one point in time. **No git history is exported**; there is a single initial commit.
- 31,810 files, 1136 MB under `rnd/`, no file over 20 MB. 10,878 files were changed by redaction (names to roles, local paths and hosts made neutral, usage and spend lines removed); each has its original and released sha256 in `docs/REDACTION-HASHES.tsv`, and every sha256 written inside the record for those files was re-pinned to the released bytes.
- Added: `README.md` (map, reading order, reproduction steps), `docs/TIMELINE.md` (from `rnd/research/QUEUE.md`), `docs/HOW-THE-LAB-WORKED.md`, `docs/REDACTION.md`, `docs/EXCLUDED.md`, `DATA-CARD.md`, `BOM.md`, `NOTICE`, `CITATION.cff`, `data/` (the publication content base: public rows only).
- Licensing change: code and scripts are now MIT (the earlier release used Apache-2.0 for scripts); text stays CC BY 4.0; engine patches stay MIT.
- Not included: held-out and burnt evaluation sets, the app maintainer's data, private relays, competitor score tables, third-party raw web snapshots, spend ledgers, credentials, model weights (see `docs/EXCLUDED.md`).
- 2026-10-27: second leak pass before the first push (private correspondence lanes, maintainer-device scores, competitor questions and scores, spend residue removed; see `docs/EXCLUDED.md`); `tools/verify-criteria.py`, `docs/PIN-EXCEPTIONS.md` and `CONTRIBUTING.md` added; the engine base is reachable through the author's public fork.

- Raw `.jsonl` traces moved to the Hugging Face dataset r4topunk/boar-traces (same paths, sha256 in TRACES.tsv). 160 files that carried held-out item text were removed after a coordinator-run overlap check against the private held-out sets.
