# Release package spec: Offline Research Bench v0 (`rnd/bench/release-v0/`)

> Owner: Lantern. **Build the package only; DO NOT publish anything** (no git push, no upload, no gh release). Publication is r4to's decision.
> Legal layout: `rnd/bench/legal/README.md` (Veil), §3 and §4. One license per file.

## Layout

```
release-v0/
  README.md                       (Lantern writes; leave a placeholder)
  DATASET_CARD.md                 (Lantern writes; placeholder)
  LEADERBOARD.md                  (Lantern writes; placeholder)
  FINDINGS.md                     (Lantern writes; placeholder)
  LICENSE                         Apache-2.0 full text (copy competitors/a competitor team/LICENSE, 202 lines, canonical)
  NOTICE                          lists every component + license + source (see below)
  MANIFEST.sha256                 sha256 of every file in the package (sorted paths), generated last
  build_release.py                the builder itself (reproducible; reads only local sources)
  code/
    score/      score.py bridge.mjs schema_check.py test_score.py test_safety_veto.py device-metrics.STUB.json
    safety/     safety_check.py build_safety.py test_safety.py rules.v0.1.json overlay.v0.1.json track.v0.1.jsonl README.md
    judge/      judge_bench.mjs
    refs/       gen_refs.mjs README.md       (recipe only)
    questions/  validate.py questions.schema.json
    device/     (Kiln) device-metrics.schema.json template.device-metrics.json README.md from_eval_iphone.py from_kiln_harness.py bench_common.py validate.py examples/*.json
    vendor/boar-eval/   judge-core.mjs venues.mjs firstaid-check.mjs claude-cli.mjs preface.mjs (+ any other module they import),
                        prompts/reference.v1.md, LICENSE (MIT text of boar-app at fd24992: `git -C boar-app show fd24992:LICENSE`), SOURCE.md (repo, commit, original paths, sha256)
    vendor/precheck/    precheck.py (from rnd/lantern/tools/precheck.py; ours, Apache-2.0)
    tests/fixtures/     the single real dng-002 row used by test_safety_veto.py (from rnd/plumb/data/...bench-p3-8.jsonl), + anything else tests need
  data/
    LICENSE                       CC BY 4.0 notice + URI https://creativecommons.org/licenses/by/4.0/legalcode (applies to data/ unless a subfolder has its own LICENSE)
    questions.jsonl               public items NOT from a competitor team (33), same JSON lines as the frozen split
    competitor-app/questions.jsonl    the 27 items whose provenance/source is a competitor repo ; + LICENSE (exact bytes of a competitor repo LICENSE, fetch with gh api) + NOTICE ("Questions from a competitor team test cases (tools/e2e_cases.json, tools/e2e_battery_cases.json), © a competitor team contributors, Apache-2.0, a competitor repo commit 87bb6e9abd; identical blobs in a competitor team/competitor-app. MODIFIED by the bench: rubric and grading fields added; questions verbatim.")
    split-order.json              canonical id order of the frozen split
    merge.py                      recombines questions.jsonl + competitor-app/questions.jsonl in canonical order and VERIFIES sha256 == dc859ebd91b0e02736ff45a5370fc64d42237ac65b93f02d57df619b20bb6b4f (byte-identical to rnd/bench/questions/v0/questions.public.jsonl); writes build/questions.public.jsonl
    gold/osm/food-00{1,2,6}.json  ODbL part of each gold file (everything except Wikivoyage-derived fields) + LICENSE-ODbL (notice "© OpenStreetMap contributors, ODbL 1.0, https://opendatacommons.org/licenses/odbl/1-0/ ; https://www.openstreetmap.org/copyright" + snapshot per file)
    gold/wikivoyage/food-00{1,2,6}.json  the Wikivoyage-derived fields only (names/titles) + LICENSE-CC-BY-SA (CC BY-SA 4.0 URI + attribution: page titles + URLs)
    gold/merge_gold.py            recombines each gold file and VERIFIES its sha256 equals the one in rnd/bench/questions/v0/SHA256SUMS.json
    corpus-manifest.json          copy of rnd/bench/questions/v0/corpus-manifest.json
    heldout.manifest.json         copy (hash only; never the items)
    references.manifest.jsonl     one row per reference: {id, sha256 (of the answer text, utf-8), model_id, cli_version, prompt_version, prompt_sha256, generated_at, web_search: true, tools, account_terms: "consumer (Claude Code [usage detail removed]; API keys removed from env)"} from rnd/bench/refs/v0/claude-code__opus.jsonl + MANIFEST.json ; plus references.MANIFEST.json (copy)
    verdicts/<system>.jsonl       from rnd/bench/judge/v0/*__vs__refs-v0.jsonl: ONLY {queryId, order, mapped (winner + rubric scores), judgeModel, judgeVersion, seed, cliVersion, createdAt, answersSha256, refsSha256}. **NEVER the `rationale` or raw `verdict`** (it describes the reference text).
    systems/<system>.answers.jsonl   from rnd/bench/systems/ (our app/proxy outputs; fine to publish)
    calibration/  sheet.json, key.sealed.json, comparison.json (rnd/bench/calibration/) + hand-labels-bench-calibration.json (rnd/plumb/data/)
    safety/       rules.v0.1.json overlay.v0.1.json track.v0.1.jsonl (data copies, CC BY 4.0; conduct sources quoted inside are short quotations with links)
  results/
    common-instrument/*.report.{md,json}   from rnd/bench/results/v0/common-instrument/
    hand-labelled/boar-p3-iphone13-qwen1.5b.report.{md,json}   from rnd/bench/results/v0/
```

## Path rules (release copies only; never edit the originals)

- No `<home>` absolute path anywhere in the package (grep must be empty). Replace with paths relative to the package or env vars:
  - `BOAR_EVAL_LIB` default → `code/vendor/boar-eval` (relative to the package root, resolved from the script's own location).
  - score.py: precheck import → `code/vendor/precheck`; default questions → `build/questions.public.jsonl` (run `data/merge.py` first; if missing, print how to build it); gold path → `data/gold/merged/` produced by `merge_gold.py`; safety dir → `code/safety`.
  - gen_refs.mjs: questions/prompt paths → package-relative (it remains a recipe; it must still verify the questions sha).
  - device converters: `os.path.relpath(..., "<workspace>")` → relpath to cwd.
- Card markdown/json in results/ may contain local paths in "Inputs"/"input_paths": replace the local prefix with `<local>/` (do not change numbers).

## Definition of done (Lantern will re-check every item)

1. `python3 data/merge.py` → byte-identical split (sha `dc859ebd…6b4f`); `python3 data/gold/merge_gold.py` → 3 gold files with the original sha256.
2. From a fresh copy of the package in /tmp (cp -R), with NO access needed to <workspace>: `python3 code/score/test_score.py`, `python3 code/safety/test_safety.py`, `python3 code/score/test_safety_veto.py` all pass; re-scoring one system (`code/score/score.py --answers data/systems/proxy-macmini-qwen3-4b.answers.jsonl --judgments <verdicts converted or original judgments?>`) — NOTE: the bridge needs full judgment rows (it reads `verdict`?). If summarize() needs only `mapped`, make the scorer work from `data/verdicts/` and show it reproduces the published ratio for all 4 systems exactly; if it needs `verdict`, say so and stop (do not publish rationale).
3. `grep -r "<users-dir>/" release-v0` empty; no file contains any reference answer text (check: no 40-char substring of any reference answer appears anywhere in the package); no held-out item id/text (ids `vit-o2b-*`) appears; no `rationale` key appears.
4. MANIFEST.sha256 matches; build_release.py re-run is byte-identical.
Report: file tree with counts, DoD 1–4 evidence, anything you could not do.
