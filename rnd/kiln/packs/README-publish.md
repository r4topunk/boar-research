# publish_pack.py

TL;DR: publishes a wave-1 knowledge pack to the public HF dataset `r4topunk/boar-packs`. Default is a dry run; `--go` uploads.

```sh
cd <workspace>/rnd/kiln/packs
.venv-hf/bin/python publish_pack.py --list                       # what the hub holds under qa/ and topics/ (names, sizes)
.venv-hf/bin/python publish_pack.py qa-health-se                 # dry run: plan, checks, root README diff
.venv-hf/bin/python publish_pack.py qa-health-se --go            # upload (one commit "wave 1: qa-health-se")
.venv-hf/bin/python publish_pack.py --root-readme                # dry run of the root README section
.venv-hf/bin/python publish_pack.py --root-readme --go           # append section "Wave 1 (2026-10-12)" (commit "wave 1: root README section")
```

Ids: qa-travel-se, qa-ethereum-se, qa-bitcoin-se, qa-health-se, qa-outdoors-se (-> `qa/<id>/`), boar-firstaid-en, boar-medlineplus-en (-> `topics/<id>/`). `--family qa|topics` overrides the destination family.

## What it uploads per pack (`<family>/<id>/`)
- `<id>.sqlite` from `shared-data/packs/wave1/` (streamed from disk).
- `<id>.sqlite.json`: the manifest, with the `file` field cut to the basename (the original holds an internal absolute path, so the hub copy differs from the local one).
- `README.md`: generated from `rnd/research/packs/<id>.md` (internal paths, task ids and scripts locations stripped; adds eligibility flag + reason from the crowding probe T-K4a, size/sha256, install line, self-test pointer).
- `LICENSE.md`: template per pack type (SE: CC BY-SA, per-post version counts from the card, attribution in `article_meta`; MedlinePlus: NLM public domain + credit line; first aid: CC BY-SA 4.0 + public domain).
- `selftest.jsonl`: the 20 public items from `rnd/research/packs/selftest/<id>.jsonl`.

## Checks (a mismatch blocks `--go`)
sqlite size and sha256 vs the `.json` manifest; card contains the same sha and size; self-test has 20 lines; leak regex (internal paths, task ids, hostnames, emails) over README/LICENSE/manifest/selftest.

## Notes
- All files of a pack go in a single `create_commit` (atomic) rather than separate `upload_file` calls; output after `--go` is the commit URL and the file list only.
- The root README is NOT touched by a pack upload: run `--root-readme --go` once after the packs are up (it lists all 7; it refuses to append twice).
- The eligibility table in the script (`META`) is hard-coded from `arms/packs/T-K4a.md`; edit it if the verdicts change. Per D-K4, upload only after r4to's OK per pack.
- Needs the token in the venv's HF login; the script never prints it.

- Always re-run the dry run immediately before `--go`: card edits after the first dry run can reintroduce internal paths (2026-10-13).
