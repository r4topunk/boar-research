# Reproducing the BOAR claim build (cut 7) and the public dev bench v0.1

TL;DR: you can rebuild the exact claim engine from a public commit plus one patch and check its tree hash; you can run the 60-question public dev bench v0.1 end to end on a plain Mac and judge it with your own Opus account (the frozen references are public since v1.0). Since v1.1 the retired held-out sets (bench v0.2, V-para and the rest) are public too, as development data, and their exposure ledger is public (section 6). Bill of materials with sizes, hashes, licences and URLs: [BOM.md](BOM.md).

## v1.1 layout (read this first)

This guide was first written for a single package with the folders `engine/`, `tools/` and `boar-eval/`. In the public release (v1.1.2) it is split over two sibling repositories, `boar-research` (this one) and `boar-bench`; clone both side by side (`boar-bench` and `boar-research` in the same parent directory) and read every `boar-eval/...` path below as `boar-bench/...`. Where a file moved, the new place is:

| Path in the guide | Where it is now |
|---|---|
| `boar-eval/` | the repository `boar-bench` (run harness commands from its root) |
| `engine/` (patches, `verify-trees.sh`, `tree-hash.mjs`) and `tools/` (`fetch-assets.sh`, `plain-mac-deps.sh`) | `boar-research/rnd/research/coordinator/repro/` (this folder; called `$REPRO` below) |
| `adapters/desktop-node/configs/claim-cut7-v01.json` | `$REPRO/claim-config-cut7.json` (cut 7 claim config, seed 44; the commands below change the seed) |
| `bench/v0.1/refs/gen_refs.public.mjs` | `boar-bench/bench/v0.1/refs/gen_refs.mjs` (regenerates the 27 new items only; the 60 frozen answers are `bench/v0.1/refs/refs.jsonl`) |
| `bench/v0.2/plan/floor_metrics.py` | `boar-bench/metrics/floor_metrics.py` (this copy, sha256 63080991..., adds `--floor-missing` and `--strict`; its default output is unchanged. The frozen copy in the v0.2 plan folder, `bench/heldout/bench-v02/live/v0.2/plan/floor_metrics.py`, is the older fe7c70b7... version without those two flags; the v0.3 plan folder has the 63080991 copy) |
| bench v0.2 (110 items), V-para (58 items) | `boar-bench/bench/heldout/bench-v02/live/v0.2/` and `boar-bench/bench/heldout/vpara1/`; their runs are in `boar-research/rnd/heldout/` and, as raw `.jsonl`, in the traces dataset (`TRACES.md`) |
| `EXPOSURES.md` | `boar-research/rnd/research/coordinator/EXPOSURES.md` (public) |
| `claim-record/`, `claim-scripts/`, `PROVENANCE.tsv` | not shipped (see section 6); the claim results are in `CLAIM-RESULTS-cut3.md`, `CLAIM-RESULTS-cut6.md`, `CLAIM-RUNS-cut3.md` and `CLAIM-RUNS-cut6.md` in `boar-research/rnd/research/coordinator/` |

Set once, from the root of `boar-bench` (section 4 assumes you stay there): `REPRO="$PWD/../boar-research/rnd/research/coordinator/repro"`.

## 1. What the claim says (copied from the claim draft v3.8, section 1; three scales, always together)

"Raw" = sum of the judged BOAR scores / sum of the reference scores (mean of correctness, completeness, usefulness, both A/B orders). "Floor removed" subtracts the judge's minimum score (1 on each 1-5 axis) from both sides; a system that declines every question already gets raw 0.306 (always-decline point D = 0.306). "Win rate" = pairwise wins over the reference answer. Bar of the bounty: more than 50 % as good as internet + frontier AI.

| Set | n | Raw (95 % CI) | Floor removed | Above always-decline | Win / tie / loss vs reference |
|---|---|---|---|---|---|
| V-para (bounty-style questions, written by our team; claim runs on cut 3 and cut 6; later spent by other arms) | 51 judged + 7 venue | 0.413 (0.384-0.445) | **0.261** (0.224-0.299) | 0.154 (0.112-0.200) | 0 of 51 |
| bench v0.2, 110 new questions (written blind; now exposed, treated as development data) | 110 | 0.513 (0.479-0.550) | **0.389** (0.347-0.435) | 0.299 (0.250-0.351) | 0 / 0 / 110 |
| bench v0.1 (public dev set; the engine was tuned on it), cut 6, two desktop runs | 57 judged | 0.558 and 0.560 | not reported in the draft | not reported | not reported |
| same 57 items on an 8 GB Galaxy A15, cut 6, airplane mode | 57 judged | 0.561 (0.507-0.617) | not reported | not reported | not reported |

Reading: the bar is not met on the bounty-style set (floor removed 0.26, win rate 0). A no-web Haiku scores raw 0.588 on the V-para items. The raw 0.50 on v0.2 is partly a rubric-floor artefact: lead with floor-removed and win rate. Cut 7 = cut 6 + an instant facts tier that fires on 0 of the 110 v0.2 and 0 of the 58 V-para questions, so the cut 6 numbers above are cut 7's on those sets (engine replay: identical answers); on v0.1 it changes 8 answers (projected +0.027, not judged). The numbers were measured on cut 3 and re-run on cut 6 (v0.2 raw 0.512 vs 0.513). Source scale of the judge: `judge.v1` (Claude Opus, `claude -p`, both orders, no `--effort`), references written by Claude Opus 5.5 with web search (`reference.v1`). Same model family on both sides of the comparison: see the caveats in the claim draft.

Your v0.1 numbers will differ from the table: the references are generated by you (section 4), and a different reference set moves the ratio. What should hold: raw ratio of the same order (about 0.5-0.6 on the 57 items), declines near zero on non-medical questions, and the per-item pattern of which items fail.

## 2. Prerequisites

| Need | Why | Tested |
|---|---|---|
| Apple-silicon Mac, macOS, 16 GB RAM, about 10 GB free disk (20 GB with the deep model) | node-llama-cpp runs Qwen3-4B Q4_K_M on CPU for generation; the claim runs used a Mac mini M4 16 GB | packaging machine: M1 Pro 16 GB |
| Node >= 22.5 (engine shims use `node:sqlite`), pnpm, Python 3 with numpy, git, curl, shasum | harness, scorers, tree check | Node 25.9.0, pnpm 11 |
| cmake + ninja + a C++ toolchain | build llama.cpp `b11010` for the emergency detector | claim machine (build script) |
| `claude` CLI (Claude Code) logged in to an account that can run Opus | reference generation and judge only; paid, closed model | n/a |
| Environment: the plain-Mac layout follows the runner defaults (`$HOME/boar/{shared-models,shared-data/packs,shared-data/crypto,kiln}`) | no env vars needed if you keep it | yes |

Environment variables (all optional; defaults in brackets): `BOAR_APP` [`$HOME/boar-app`] clone of the public engine; `BOAR_EVAL_HOST` [`local` = this machine, no ssh; set an ssh host to use a remote box]; `BOAR_EVAL_BASE` [`boar`, directory under `$HOME`]; `BOAR_EVAL_HEAVY` [empty on local; on a remote box `~/${BOAR_EVAL_BASE}/bin/run-heavy Kiln` = CPU lock wrapper]; `BOAR_EVAL_APP_NM`, `BOAR_EVAL_RUNNER_NM` [node_modules dirs to link into the tree; `tools/plain-mac-deps.sh` creates one]; `BOAR_SHARED_MODELS` [`$HOME/boar/shared-models`]; `BOAR_EVAL_PACK_DIRS` [`$HOME/boar/shared-data/packs:$HOME/boar/shared-data/crypto`]; `BOAR_EVAL_MIN_FREE_GIB` [15]; `BOAR_EVAL_RUNNER_DIR` [`be`; the claim used `be-repo`]; `BOAR_RUNNER_PROFILE` [`ship` = route gate on, as in the claim]; `BOAR_DETECTOR`, `BOAR_DETECTOR_URL`, `BOAR_DETECTOR_HEAD`, `BOAR_DETECTOR_THR` [emergency detector].

## 3. (a) Rebuild cut 7 and check the tree

```bash
git clone https://github.com/UPSTREAM_REPO/boar-app "$HOME/boar-app"            # public, MIT
git -C "$HOME/boar-app" cat-file -t 0cfd4a77badd01297af8dc9a3a10924f8a895105   # expect: commit
cd "$REPRO"
shasum -a 256 -c cut7.vs-0cfd4a77.patch.sha256                              # patch sha 0fba26b8...
./verify-trees.sh "$HOME/boar-app" /tmp/boar-vt .                           # builds throwaway worktrees, prints both hashes, removes them
```
Expected output (both lines per tree must read `OK`): cut 7 git tree `17d42f2027bdd3b95f2956655d5e49b9924db1a1`, content hash `7c96e59e001b6273baa4f8dcaa7c696c1aa8f356321914b29e38fe58a900cf79`; the deep research tree `e216bc9062fc828eb709ae0c017c9edf308345f2` / `8ce8b0fc572aa7909c6590f7a014e8a038f4c961decf3c01d03a6da3d9573000`. By hand: `git worktree add --detach /tmp/t 0cfd4a77 && cd /tmp/t && git apply --index <patch> && git write-tree`. The patch is one cumulative `git diff 0cfd4a77 6d0b93b1` (cut 6 patch + FACTS r6, patches listed in BOM rows 9-11).

## 4. (b) Run bench v0.1 end to end on the desktop-node adapter

```bash
# 0. assets (about 2.9 GB) and node deps; run from the root of boar-bench (cd there first if you are not)
REPRO="$PWD/../boar-research/rnd/research/coordinator/repro"   # as in the layout section; skip if already set
"$REPRO/fetch-assets.sh"                    # models + 2 packs, size and sha256 checked; --check = dry run
"$REPRO/plain-mac-deps.sh" "$HOME/boar-repro-deps"   # prints the two export lines for BOAR_EVAL_APP_NM / BOAR_EVAL_RUNNER_NM; run them
pnpm install --no-frozen-lockfile --filter @boar-eval/protocol --filter @boar-eval/desktop-node

# 1. emergency detector (needed for the claim numbers, BOM rows 5-7; files not hosted yet, see BOM)
git clone --depth 1 --branch b11010 https://github.com/ggml-org/llama.cpp "$HOME/boar/llama-b11010"   # commit 4bc272fd...
(cd "$HOME/boar/llama-b11010" && cmake -S . -B build-cpu -G Ninja -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=OFF -DLLAMA_CURL=OFF && cmake --build build-cpu -j 4 --target llama-server)
DET="$HOME/boar/shared-models/emergency-detector"                           # put the two v3b files here and check their sha256 (BOM)
"$HOME/boar/llama-b11010/build-cpu/bin/llama-server" -m "$DET/sonar-mmbert-small-emergency-v3b-q8te4.gguf" --embeddings --pooling mean \
  -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 &

# 2. requests: one per question, config = claim config (cut 7, Qwen3-4B, crypto + wikivoyage kit, quickFirst on)
for S in 44 45; do
  mkdir -p runs/repro/cut7-v01-s$S
  sed "s/\"seed\": 44/\"seed\": $S/" "$REPRO/claim-config-cut7.json" > runs/repro/cfg-s$S.json
  pnpm -s -C packages/protocol exec tsx src/makeRequests.ts --questions "$PWD/bench/v0.1/questions.public.jsonl" \
    --config "$PWD/runs/repro/cfg-s$S.json" --run-id cut7-v01-s$S > runs/repro/cut7-v01-s$S/requests.jsonl
done

# 3. engine tree = 0cfd4a77 + cut 7 patch (same code path as the claim runs; prints the tree location)
export BOAR_APP="$HOME/boar-app" BOAR_EVAL_RUNNER_DIR=be-repo
adapters/desktop-node/setup.sh 0cfd4a77 --patch "$REPRO/cut7.vs-0cfd4a77.patch" --arm cut7
node "$REPRO/tree-hash.mjs" "$HOME/boar/kiln/be-0cfd4a77-cut7"             # expect 7c96e59e... (same hash as section 3)

# 4. run (60 questions; a few minutes to an hour per seed depending on the Mac), traces are validated against the protocol
for S in 44 45; do
  BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD="$DET/sonar-mmbert-small-emergency-v3b.head.json" \
  adapters/desktop-node/run.sh --commit 0cfd4a77 --arm cut7 --requests runs/repro/cut7-v01-s$S/requests.jsonl --out runs/repro/cut7-v01-s$S/traces.jsonl
done
```
`run.sh` ends with `validate.ts`: every trace line must parse and no item may be missing or extra. Without the detector leave out the three `BOAR_DETECTOR*` variables: the runner falls back to the lexical predicate and your numbers are then not the claim's (BOM note 1). If a step fails in `setup.sh` on disk space set `BOAR_EVAL_MIN_FREE_GIB`.

## 5. (c) Judge and score with your own references and judge

Opus is a closed, paid, non-deterministic model, so your judge outputs will not match ours byte for byte. Since v1.0 the 60 frozen reference answers of bench v0.1 are public (`bench/v0.1/refs/refs.jsonl`, pinned by `bench/v0.1/refs/MANIFEST.json`, prompt `prompts/reference.v1.md`, sha d5144343...), and `harness/judge.mjs` picks them up and checks the pin, so you can judge against the same references we did. Only if you want references of your own: `node bench/v0.1/refs/gen_refs.mjs` writes new answers for the 27 items that were generated for v0.1 (sequential Opus + web-search calls; flags `--ids`, `--limit`; the other 33 items reuse answers frozen earlier by `bench/v0.1/build.py`, so those cannot be regenerated byte for byte); pass your own file to the judge with `--refs`.
```bash
# from the root of boar-bench
# judge.v1, both orders, no --effort. 57 judged items x 2 orders = 114 calls per run (venue-list items are scored against OSM gold, not by the judge; the claim counts 57 judged items)
for S in 44 45; do
  node harness/judge.mjs --traces runs/repro/cut7-v01-s$S/traces.jsonl --out runs/repro/cut7-v01-s$S/judgments.jsonl \
    --bench bench/v0.1 --seed 7        # add --refs <file> only for references of your own
done
# the three scales + CI (stratified two-level bootstrap, seed 11, 2000 resamples; D = 0.306)
mkdir -p runs/repro/score; for S in 44 45; do for k in traces judgments; do cp runs/repro/cut7-v01-s$S/$k.jsonl runs/repro/score/cut7-v01-s$S.$k.jsonl; done; done
python3 metrics/floor_metrics.py --runs cut7-v01-s44 cut7-v01-s45 --dir runs/repro/score --decline-ratio 0.306 --questions bench/v0.1/questions.public.jsonl
python3 scorers/score.py --traces runs/repro/cut7-v01-s44/traces.jsonl --judgments runs/repro/cut7-v01-s44/judgments.jsonl --bench bench/v0.1 --json runs/repro/score/s44.json
```
Cost: 114 judge calls per run, 228 for two seeds (plus up to 27 reference calls if you regenerate references); a full re-judge of every arm in our work was in the hundreds of calls per arm. Our own confirmations reused the verdicts of answers that were byte-identical to an already judged run, which brought a cut 6 confirmation down to about 34 fresh calls. The judge stops on the first rate-limit and resumes when rerun. Cross-checks we measured: a second Claude judge (Fable) agreed with Opus on 453 of 456 verdicts; a local Gemma judge picks the same winner on 86-88 % of items but scores 0.11 higher. Both are the same-family caveat, not a fix.

Health and safety: the v0.1 safety track (`bench/v0.1/safety`) and the health cards in the engine are AI-reviewed, not clinically reviewed. Do not read a good score as medical validation.

## 6. (d) What a reviewer can and cannot reproduce (v1.1)

| Claim number | Reproducible by you | Why / what you get |
|---|---|---|
| Engine = cut 7 | **Yes** | public base commit + one patch; tree hashes in section 3 |
| bench v0.1 end to end (answers, traces, retrieval, timing, your own judge numbers) | **Yes** | public dev set and public frozen references (`boar-bench/bench/v0.1/`), harness in `boar-bench`; the judge is a closed paid model, so numbers move a little |
| Every aggregate of a recorded arm from its stored traces and judgments | **Yes** | no model, no judge; fetch the traces from the dataset (`TRACES.md`) and run the arm's `tools/` scripts, see the README of `boar-research`, step R3 |
| bench v0.1 reference answers | **Yes** (read them) | public: `boar-bench/bench/v0.1/refs/refs.jsonl`; 27 of the 60 can be regenerated with `gen_refs.mjs`, the other 33 reuse earlier frozen answers |
| bench v0.2 (110 questions) | **Yes, as development data** | questions, references, plan and hashes are public since v1.1 (`boar-bench/bench/heldout/bench-v02/live/v0.2/`; plan hashes in `plan/SHA256SUMS`); the set was exposed after the claim runs (four claim-grade runs and a deep-tier arm used it), so it is development data and a final number needs a new set written outside the Claude family; the runs are in `rnd/heldout/` and the traces dataset |
| V-para (bounty-style, 51 + 7) | **Yes, as development data** | items, gold and runs are public since v1.1 (`boar-bench/bench/heldout/vpara1/`); blind to the engine builders when the claim runs were made, spent since by deep-tier and venue arms; the ruling and every exposure are in the public ledger `rnd/research/coordinator/EXPOSURES.md` |
| bench v0.3 | n/a | no v0.3 items were ever written (the OF-3 front was dropped); only the plan, schema and tooling exist (`boar-bench/bench/v0.3/`) |
| bench v0.4 ruler (75 items) and the DEVICE-FINAL phone run (0 of 71) | Items, references, the raw phone outputs and judgments, and the M1, M3 and M4 aggregates: yes. Running it again: needs the device | items and references are public (`boar-bench/bench/v0.4/`); the report is `rnd/research/coordinator/arms/device-final/DEVICE-FINAL.md`. **Public data of the arm.** In the traces dataset `r4topunk/boar-traces`, at `rnd/research/coordinator/arms/device-final/` (sha256 in `TRACES.tsv`): the raw M1 phone outputs (`out/df-m1-v04-s42.jsonl`, `s42b`, `s43`), the derived traces (`traces/dev-s42` and `dev-s43`) and the Opus and Codex judgments (`judge/dev-s42` and `dev-s43`, `.opus` and `.codex`); the native-rc lite-s42 twin (outputs, traces, judgments) is under `arms/native-rc/` there. In `boar-research`, same path: the criterion, the report, the tools, the status files and the aggregates `aggregates/m1.json` to `m4.json`; `tools/m1_agg.py` recomputes `m1.json` from the dataset files with no model call. Also public since v1.1.2: the M2 to M4 phone outputs and the M3/M4 labels (dataset, same arm folder), the M1 request files (`req/`) and `ruler/factavail/out/factavail-items.json` (this repo). **Not published:** the M2 replay passages (`arms/x2b-budget/replays/B600/`), the desktop judge units M3/M4 are prepared from, and the paired block of `native-rc/aggregates/rf.json`, which needs the app maintainer's native-app files (withheld). `DEVICE-FINAL.md` (section Public data) lists every file. `TRACES.tsv` and the arm's `.gitignore` list exactly what is public. The run itself needs the Pixel 8a and the app. |
| Same-hardware determinism | Partly | on one machine, rebuilt trees reproduced 105 of 110 answers byte for byte between cut 3 and cut 6; identity across different Macs was not tested |
| Phone results (A15: 73/73 questions, p50 49 s; 0.561 vs desktop 0.558/0.560) | No (needs the device and the Bench APK) | see section 8 |
| Deep research config | Desktop only; needs the 12.3 GB model on disk and RAM to hold it (our runs used a 16 GB Mac mini) | reported separately, not the claim build; section 9 |

Not shipped in this release: the original `claim-record/` and `claim-scripts/` folders of the first package and its `PROVENANCE.tsv` (it listed every file the package edited, with sha256 before and after). Their content that is safe to publish is in the claim result and run records named in the layout table above; the redaction map of the public release is `docs/REDACTION.md` and `docs/REDACTION-HASHES.tsv`.

## 7. Known gaps in this draft (found while packaging)

- The plain-Mac path was exercised up to model loading (setup builds the cut 7 tree with the expected content hash; requests build; the runner starts and stops at the missing GGUF); a full 60-question run on a clean machine, the detector start, and the judge/score commands on real v0.1 output were not executed here.
- The detector files are not hosted; until they are, section 4 step 1 cannot be followed by an outsider (BOM row 5).
- In v1.1 `bench/v0.1/validate.py`, `build.py`, `similarity.json` and the held-out split manifest are in `boar-bench`; `python3 bench/v0.1/validate.py --skip-heldout` is the check to run. `scorers/tests` are in `boar-bench` too; two Python tests skip by design because the real-run fixtures they need are not published.
- `BOM.md`, `README-claim.md` and `METHODS.md` in this folder still use the original package paths (`engine/`, `boar-eval/`, workspace-relative paths); each now starts with a path-map note that points to the table at the top of this guide.

## 8. Install on a phone

Not written for this release. How the phone runs were done: `boar-bench/devices/DEVICE-KIT.md`; the final on-phone matrix and its method: `rnd/research/coordinator/arms/device-final/DEVICE-FINAL.md`.

## 9. Deep research config (separate, not the claim)

Cut 6 + Qwen3.6-35B-A3B (UD-Q2_K_XL) + thinking budget 512: tree check with the `deep-dt512` lines of `verify-trees.sh` (in this folder); run through `--backend server --deep-model qwen3.6-35b-a3b-ud-q2kxl` with a `llama-server` b11010 build (see the adapter README); device engine bmoe v0.28.0 (BOM section C). Measured on V-para floor removed 0.44 and on v0.2 0.51 (development data); win rate stays 0. It needs a 12 GB phone; none was available.
