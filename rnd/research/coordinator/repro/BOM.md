# Bill of materials: BOAR claim build "cut 7" (poidh #31)

> **Public-release path map (v1.1.2).** This file was written for the first single-package release. Read `boar-eval/...` as `boar-bench/...` (sibling repository) and `engine/...` and `tools/...` as this folder (`rnd/research/coordinator/repro/`); other workspace-relative paths resolve in `boar-research` or `boar-bench` unless `docs/EXCLUDED.md` lists them as withheld. Full table: [REPRODUCE.md](REPRODUCE.md), section "v1.1 layout".

TL;DR: everything needed to rebuild the claim engine and run the public dev bench v0.1 on a plain Mac. Required assets total **3.03 GB** (models, packs, detector); optional places kit 42.7 MB; deep research config 12.3 GB more. Grand total with everything: **15.4 GB** (limit 50 GB). Sizes are bytes; every sha256 below was recomputed on the file or taken from the host's own LFS record (noted). Copyable fetch script with size and sha checks: `tools/fetch-assets.sh` (`--check` = HEAD only).

Status of hosting: HF files below are public today. The emergency detector and the two APKs are not hosted yet (owner decision pending); their sha256 are fixed here.

## A. Claim build (cut 7): required to reproduce

| # | Asset | File | Bytes | sha256 | Licence | Host / URL (revision) | Install path | Req. |
|---|---|---|---|---|---|---|---|---|
| 1 | Answer model Qwen3-4B-Instruct-2507, Q4_K_M | `Qwen3-4B-Instruct-2507-Q4_K_M.gguf` | 2,497,281,120 | `3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597` | Apache-2.0 (base `Qwen/Qwen3-4B-Instruct-2507`) | https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF/resolve/a06e946bb6b655725eafa393f4a9745d460374c9/Qwen3-4B-Instruct-2507-Q4_K_M.gguf (rev `a06e946b`; LFS oid = sha) | desktop `${BOAR_SHARED_MODELS}/` (default `<runner>/shared-models/`); phone: app-managed download, pinned in the engine's `src/models/manifest.ts` | required |
| 2 | Embedding model bge-small-en-v1.5, q8_0 | `bge-small-en-v1.5-q8_0.gguf` | 36,806,944 | `ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514` | MIT (base `BAAI/bge-small-en-v1.5`) | https://huggingface.co/CompendiumLabs/bge-small-en-v1.5-gguf/resolve/d32f8c040ea3b516330eeb75b72bcc2d3a780ab7/bge-small-en-v1.5-q8_0.gguf (rev `d32f8c04`; LFS oid = sha) | same dir as #1 | required |
| 3 | Knowledge pack: crypto | `boar-crypto.sqlite` | 36,093,952 | `ae9fbd2c7a46a46a815d46d0283e7b192adb4c342b38a2adc4881e8f9d8831fb` | mixed per document: CC0 (EIPs/ERCs/specs), CC BY-SA 4.0 (Yellow Paper, Wikipedia), MIT (ethereum.org), each BIP's own licence; per-document record in the pack | https://huggingface.co/datasets/r4topunk/boar-packs/resolve/a55c1ec8a5fe8bbda99c4197c33474637bef1958/topics/boar-crypto.sqlite (dataset rev `a55c1ec8`; LFS oid = sha) | desktop `<runner>/shared-data/crypto/` (or any dir in `BOAR_EVAL_PACK_DIRS`); phone: in-app download | required |
| 4 | Knowledge pack: Wikivoyage EN | `boar-wikivoyage-en.sqlite` | 351,092,736 | `ff8595e32f56b8b84e20464afd8bf88532d47d2d82d799e3df8489440004b66e` | CC BY-SA 4.0 (Wikivoyage; attribution per article inside the pack) | https://huggingface.co/datasets/r4topunk/boar-packs/resolve/9557c7b2a50a1c37fdf36d41db4cd0fdc8c33c0b/wiki/en/boar-wikivoyage-en.sqlite (dataset rev `9557c7b2`; LFS oid = sha) | desktop `<runner>/shared-data/packs/`; phone: in-app download | required |
| 5 | Emergency detector v3b, encoder (mmBERT-small fine-tune, q8_0 + q4_0 token table) | `sonar-mmbert-small-emergency-v3b-q8te4.gguf` | 106,210,784 | `a86fe8b98801c005692cb05012c84510e76dd10d0b1e50f12cb52e50d8abec0f` | base `jhu-clsp/mmBERT-small` is **MIT** (HF model card, rev `abc32620`, https://huggingface.co/jhu-clsp/mmBERT-small); the fine-tuned weights are ours, trained only on synthetic and card-derived EN/PT/ES messages (data files `synth` 2,201 messages, `aligned`, `cards`, `terse-live` 631 items; written by Claude subagents from a spec, or derived from the project's own health cards, which are AI-reviewed, not clinically reviewed); release licence **not yet chosen (MIT proposed; owner decision)** | **not hosted yet** (upload needs owner OK). Built from the base model by `rnd/research/sonar/exp/30-learned-detector` (private; training data not exported) | desktop: any dir; pass `BOAR_DETECTOR_HEAD`; llama-server loads the gguf (see REPRODUCE.md); phone: bundled in the product APK | required for the claim numbers (see note 1) |
| 6 | Emergency detector v3b, head (JS dense 384x384, GELU, LayerNorm, 384x2, softmax) | `sonar-mmbert-small-emergency-v3b.head.json` | 1,696,707 | `766434de8971875cdad1ba6ebd11dd8f6378a7def77ae73380c98fef46d27c36` | as #5 | as #5 | next to #5 | required (as #5) |
| 7 | Detector host: llama.cpp tag `b11010` | source build, CPU, `llama-server` | n/a (source) | commit `4bc272fd729bd094c0422e4b8353da8d2fec91f8` | MIT | https://github.com/ggml-org/llama.cpp (tag `b11010`) | build dir of your choice | required with #5 |
| 8 | Engine base: boar-app commit `0cfd4a77` (merge of PR 61) | git commit | n/a (git) | commit `0cfd4a77badd01297af8dc9a3a10924f8a895105` | MIT ("aoair contributors") | https://github.com/UPSTREAM_REPO/boar-app (also the fork https://github.com/r4topunk/boar-app); commit is in upstream `main` | clone anywhere; `BOAR_APP=<clone>` | required |
| 9 | Engine patch cut 6 (detector-max routing; reference for the lineage) | `engine/cut6.vs-0cfd4a77.patch` | 672,205 | `824e0b35fcdfe46b25bdb824516b5ccec387247d14a461f7bbfd9fb332fb953b` | MIT (derivative of #8) | in this package | `engine/` | reference |
| 10 | Engine patch FACTS r6 (cut 6 to cut 7) | `engine/facts-r6.vs-cut6.patch` | 819,676 | `0eee6a0bf1f73e9ca939c915e06c26c2d5c8804b2462bee36a67b551cd3ae995` | MIT | in this package | `engine/` | reference |
| 11 | **Engine patch cut 7, one cumulative patch against `0cfd4a77`** (`git diff 0cfd4a77 6d0b93b1`) | `engine/cut7.vs-0cfd4a77.patch` | 1,490,053 | `0fba26b8c55aa776b0cfa397998c82741bdbe50cfc4ed5dd2059ad6a2cee7f26` | MIT | in this package | `engine/` | **required** |
| 12 | Harness snapshot (runner, judge, scorers, protocol, public dev bench v0.1 with refs manifests only) | this directory tree | @@EXPORT_BYTES@@ (@@EXPORT_FILES@@ files) | `MANIFEST.sha256` has sha256 `@@MANIFEST_SHA@@` (the manifest lists every file except BOM.md, REPRODUCE.md and itself) | MIT for code written by this project; bench v0.1 items and gold carry their own licences, see `boar-eval/bench/v0.1/DATASET_CARD.md` | in this package | repo root | required |
| 13 | Product APK | [step 5: product APK] | [step 5] | [step 5] | [step 5] | [step 5] | phone | [step 5] |
| 14 | BOAR Bench APK, cut 7, no-network variant (debuggable, debug-signed; engine tree `7c96e59e…` = desktop cut 7; FACTS table bundled; audit NO-NETWORK-BY-CONSTRUCTION) | `boar-bench-0cfd4a77-cut7-nonet-7c96e59e001b.apk` | 77,862,520 | `6eb8cb45349ce8b67365c5ffec7f76a0f18564dd2f18e60c3267e7a7656bcdc6` | MIT (boar-app) + bench-app (local) | not hosted (owner decision); local `bench-app/build/`, mini `<runner>/bench-app/build/`; report `bench-app/reports/cut7-nonet/` | phone (adb install; kit via `push-kit.sh`) | optional (measurement app, not the product) |

Tree hashes the engine rows must reproduce (printed by `engine/verify-trees.sh`):
- cut 7: git tree object `17d42f2027bdd3b95f2956655d5e49b9924db1a1`; BOAR content hash (`engine/tree-hash.mjs`: sha256 over sorted file hashes of `src assets locales modules package.json tsconfig.json`) `7c96e59e001b6273baa4f8dcaa7c696c1aa8f356321914b29e38fe58a900cf79`. The content hash is the "tree" the claim documents quote (`7c96e59e...`, and `b0f53fe0...` for cut 6).
- cut 6: git tree object `8916837ff6bfd9c63a4e741577dd351b57b4692d`; content hash `b0f53fe0d30abb8395e95971e3be4dfc4b406d394bf346dedb525a2678479daa`.

Notes
1. Detector: the claim runs used the route gate plus this detector (`BOAR_RUNNER_PROFILE=ship`, `BOAR_DETECTOR=mmbert`). Without it the runner falls back to the lexical health predicate: it runs, but health/emergency routing differs and numbers are not the claim's. The health and safety cards the detector feeds are AI-reviewed, not clinically reviewed.
2. Pack revisions: #3 and #4 are pinned to the dataset commits recorded in `boar-eval/bench/v0.1/corpus-manifest.json`; the file sha256 is what the runner enforces (`config.kit[].sha256`), so a later dataset commit with the same file would also work. The sidecar `boar-crypto.sqlite.json` in the original working directory carries a stale sha; ignore it.
3. Licence of the packs is per document and share-alike where the source is (Wikipedia, Wikivoyage); the dataset card (https://huggingface.co/datasets/r4topunk/boar-packs) is the authority.

## B. Optional: places kit (venue questions, "with device location and the user's area tile")

Not used by bench v0.1 (no `--places`). Used by the venue path; 5 of the 9 tiles are the area tiles of the 7 venue questions of a withheld set, the other 4 come from an earlier kit.

| # | Asset | File | Bytes | sha256 | Licence | Host / URL | Install path | Req. |
|---|---|---|---|---|---|---|---|---|
| 15 | Gazetteer (GeoNames cities15000) | `world-places.sqlite` | 22,962,176 | `215ce4663b2f79dbf25e9cacab90cd8aa0a8711721663a733cb53bc49d972892` | CC BY 4.0, GeoNames | https://huggingface.co/datasets/r4topunk/boar-packs/resolve/0d75f30fc9d439a7b4e3685c6fcd5a34236f33f6/places/world-places.sqlite | `--places <dir>` | optional |
| 16-24 | Area tiles (OSM extract, Wikivoyage listings), 1 degree each | `t-N35E139` 9,900,032 `8fcd37b7...`; `t-N35E140` 663,552 `2cb90347...`; `t-N38W010` 1,781,760 `45b508b5...`; `t-N39W001` 1,093,632 `63400dac...`; `t-N41E044` 585,728 `a492031a...`; `t-N46E014` 724,992 `269ea288...`; `t-N50E019` 1,040,384 `bea75d9b...`; `t-N52E013` 3,706,880 `0accffdf...`; `t-S14W072` 208,896 `b6f769d6...` (all `.sqlite`; full sha256 in `tools/fetch-assets.sh`) | see left | sum 19,705,856 | ODbL 1.0 (c) OpenStreetMap contributors for the database; CC BY-SA 4.0 for Wikivoyage text | same dataset, path `places/tiles/<name>.sqlite`, rev `0d75f30f` (dataset head on 2026-10-10; sha256 of all 9 tiles and the gazetteer equal the local kit files, kit SHA256SUMS sha `94821014...`) | same dir | optional |

Total of section B: 42,668,032 bytes.

## C. Deep research config (reported separately, NOT the claim build)

Recommended config in the draft: cut 6 + Qwen3.6-35B-A3B + thinking budget 512. Needs a 12 GB phone that does not exist in our lab; desktop only so far.

| # | Asset | File | Bytes | sha256 | Licence | Host / URL (revision) | Install path | Req. |
|---|---|---|---|---|---|---|---|---|
| 25 | Deep model Qwen3.6-35B-A3B, UD-Q2_K_XL | `Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf` | 12,290,628,576 | `96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7` | Apache-2.0 | https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/resolve/a483e9e6cbd595906af30beda3187c2663a1118c/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf (rev `a483e9e6`; LFS oid = sha) | `<runner>/shared-models/` | deep config only |
| 26 | Deep patch chain, one cumulative patch (cut 6 + thinking on the deep branch + budget 512) | `engine/deep-dt512.vs-0cfd4a77.patch` | 673,484 | `49e5fb2936053baf82195e5bc91ecaa506ab40d65c9c602ced6521ee7a131ade` | MIT | in this package | `engine/` | deep config only |
| 27 | Device engine for the deep model: bmoe v0.28.0 (BigMoeOnEdge, llama.cpp fork `dce96985`) | source build (`build-bmoe.sh host|android`) | n/a (source; Android payload 12.4 MB stripped) | commit `374f562c920e2209b093f3349dad8ecbae439956` | Apache-2.0 | https://github.com/Helldez/BigMoeOnEdge | build dir | deep config only |
| 28 | llama.cpp `b11010` `llama-server` (desktop deep path) | as row 7 | n/a | `4bc272fd...` | MIT | as row 7 | as row 7 | deep config only |

Deep tree hashes: git tree object `e216bc9062fc828eb709ae0c017c9edf308345f2`; content hash `8ce8b0fc572aa7909c6590f7a014e8a038f4c961decf3c01d03a6da3d9573000` (identical to the tree used for the measurements: all 38 changed files byte-identical on the machine that ran them). The patch chain is: cut 6 patch (row 9) + a one-line `thinking: true` change on the deep branch + `DEEP_THINKING_BUDGET` 1024 to 512; row 26 is the cumulative result.

## D. Size check

| Group | Bytes |
|---|---|
| A, assets that are downloads (rows 1-6) | 3,029,182,243 |
| A, patches + harness (rows 9-12, indicative) | about 8.1 MB |
| B places kit | 42,668,032 |
| C deep model | 12,290,628,576 |
| Total without the product APK (Bench APK 77,862,520 B included below; product APK in step 5a) | **15,362,478,851 + about 8.1 MB < 50 GB** |
