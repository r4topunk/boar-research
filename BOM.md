# Bill of materials: models, packs, datasets, large files, licences

TL;DR: everything the numbers in this repo depend on, with the exact file, sha256, source and licence. Nothing large ships here (no file over 20 MB): models and packs are linked, not copied. "rev" = the Hugging Face revision; UNKNOWN where the file came from the upstream app's model catalog and no revision was recorded.

## Models

| piece | used for | file (bytes) | sha256 | source @ rev | licence | ships here |
|---|---|---|---|---|---|---|
| Qwen3-4B-Instruct-2507 Q4_K_M | claim build, fast tier (cut 6 / cut 7) | `Qwen3-4B-Instruct-2507-Q4_K_M.gguf` (2,497,281,120) | `3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597` | upstream app catalog (its model manifest); HF rev UNKNOWN | Apache-2.0 | link only |
| bge-small-en-v1.5 q8_0 | engine embeddings, similarity gate | `bge-small-en-v1.5-q8_0.gguf` (36,806,944) | `ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514` | upstream app catalog; HF rev UNKNOWN | MIT | link only |
| Qwen3.6-35B-A3B UD-Q2_K_XL | deep tier (desktop; device plan via bmoe) | `Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf` (12,290,628,576) | `96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7` | `unsloth/Qwen3.6-35B-A3B-GGUF` @ `a483e9e6cb` | Apache-2.0 | link only |
| Qwen3.6-35B-A3B UD-IQ3_XXS | deep-tier quant ceiling (closed) | `Qwen3.6-35B-A3B-UD-IQ3_XXS.gguf` (13,211,155,424) | `9c964e657212fea1f24905dd7b0a89b82fd807d19fab0b41da14251b07b88fbe` | `unsloth/Qwen3.6-35B-A3B-GGUF` @ `a483e9e6cb` | Apache-2.0 | link only |
| Qwen3-4B-Thinking-2507 Q4_K_M | THINK4B (closed) | `Qwen3-4B-Thinking-2507-Q4_K_M.gguf` (2,497,281,152) | `ddd52e18200baab281c5c46f70d544ce4d4fe4846eab1608f2fff48a64554212` | `unsloth/Qwen3-4B-Thinking-2507-GGUF` @ `f40adb104d` | Apache-2.0 | link only |
| Gemma 4 26B-A4B UD-Q2_K_XL | GEMMATHINK (closed); local judge test | `gemma-4-26B-A4B-it-UD-Q2_K_XL.gguf` (10,546,934,240) | `2a1d26dfe6ea00a467940a5728316af6edb366bbdba950d65b85d232392fb658` | `unsloth/gemma-4-26B-A4B-it-GGUF` @ main (rev UNKNOWN) | Gemma terms | link only |
| Qwen3.5-35B-A3B UD-Q2_K_XL | MoE screen (closed) | `Qwen3.5-35B-A3B-UD-Q2_K_XL.gguf` (12,156,754,560) | `855b8d11f4b52e7ea4b9eeea2fbe3555c4d96d5b7b74702b6144810db3e77270` | `unsloth/Qwen3.5-35B-A3B-GGUF` @ main (rev UNKNOWN) | Apache-2.0 | link only |
| bge-reranker-v2-m3 Q4_K_M | HEADPASS-X3 reranker | `bge-reranker-v2-m3-q4km.gguf` (438,376,864) | `e186a244ed455b4ab66ec64339ce7427a6ae13f5c0b5e544de96e50f0f8b3673` | rev UNKNOWN | Apache-2.0 upstream (verify for the quantised file) | link only |
| Emergency detector v3b (mmBERT-small + classification head) | cut 6 / cut 7 runner profile `ship` | gguf + head | `a86fe8b9…` / `766434de…` | trained locally | base-model licence UNKNOWN | **not released** |
| Engine base | cut 6 / cut 7 | boar-app commit `0cfd4a77` (public, upstream main) | — | upstream boar-app (the app maintainer's public repository) | MIT | linked; our diffs ship as `rnd/research/coordinator/arms/*/*.patch` |
| On-device deep engine | deep-tier device plan | bmoe v0.28.0 | — | public release | see upstream | link only |

Earlier screened models (Qwen3.5-4B, Qwen3.5-9B, Ministral-3-8B, Gemma 4 E4B, Qwen2.5-1.5B) are listed with their shas in the closed-arm reports; none is used by a headline number.

## Knowledge packs

All packs are published as one dataset: r4topunk/boar-packs (revision: record the commit at publish; UNKNOWN here). One card per pack in `rnd/research/packs/`, with source, snapshot, counts, sha256 and build command.

| pack | role | sha256 | licence |
|---|---|---|---|
| `boar-crypto` | claim kit | `ae9fbd2c…31fb` | mixed per row: CC0, BSD, PD, MIT, CC BY 4.0, CC BY-SA 4.0 (Wikipedia, specs) |
| `boar-wikivoyage-en` | claim kit | `ff8595e3…b66e` | CC BY-SA 4.0 |
| `kit-vexact-places` + 4 area tiles | venue items (`--places`) | `rnd/research/packs/kit-vexact-places.md` | GeoNames CC BY 4.0; OSM POIs ODbL 1.0 |
| `qa-health-se`, `qa-outdoors-se`, `qa-bitcoin-se`, `qa-ethereum-se`, `qa-travel-se`, `qa-cooking-se`, `qa-money-se` | pack stack arms | per card | CC BY-SA 2.5 / 3.0 / 4.0 per post (Stack Exchange dump 2024-04-02) |
| `boar-firstaid-en` (v4) | pack stack arms | per card | CC BY-SA + US public domain |
| `boar-medlineplus-en` | pack stack arms | per card | public domain (NLM), credit line |
| `boar-factbook` | pack stack arms | per card | CC0 (factbook.json archive of a US government work) |
| `boar-simplewiki-en` | pack stack arms | per card | CC BY-SA 4.0 |
| `boar-wiki-en-top100k`, `boar-wiki-en-07`, `wiki-vital5`, `boar-preparedness` | closed arms / reference | per card | CC BY-SA 4.0 (+ US PD for preparedness) |

## Datasets and evaluation sets

| set | role | where | licence |
|---|---|---|---|
| bench v0.1 (60 public items, frozen references) | dev, public | https://github.com/r4topunk/boar-bench | CC BY 4.0 (our items/gold); CC BY-SA 4.0 for Wikivoyage-derived gold; ODbL for 3 OSM venue golds; quotation with links for 25 items quoting a public author's posts |
| longsession-v1 (10 sessions × 5 turns) | multi-turn dev slice | https://github.com/r4topunk/boar-bench | CC BY 4.0 |
| v0.2 (110), V-para (58: 51 judged + 7 venue), fresh sets, Veil-lane sets | retired 2026-10-27, public dev data | items: https://github.com/r4topunk/boar-bench `bench/heldout/`; runs: `rnd/heldout/` and https://huggingface.co/datasets/r4topunk/boar-traces | CC BY 4.0 (our items and reports); CC BY-SA 4.0 (retrieved Wikipedia text); ODbL (OSM gold) |
| bench v0.3 / v0.4 | v0.4 = claim ruler, retired 2026-10-27, public | https://github.com/r4topunk/boar-bench `bench/v0.4/` (hashes `f9ad2f2f...` items, `23b6febf...` candidate verify) | CC BY 4.0 |
| Pack self-tests (180 items over the 9 published packs) | pack scoring | shipped: `rnd/research/packs/selftest/` (also in boar-bench `bench/selftest/`) | per pack source (CC BY-SA 4.0 / CC0 / public domain), see boar-bench `bench/selftest/DATA-CARD.md` |
| Wikidata fact table (FACTS arm) | cut 7 fact lookup | embedded in `rnd/research/coordinator/arms/facts/*.patch` | CC0 (Wikidata) |

## Judge

| piece | use | reproducible? |
|---|---|---|
| Claude Opus via Claude Code CLI (`claude -p`), prompt/schema `judge.v1` | every claim and decision number | closed, paid; not bit-reproducible |
| Claude Haiku 5.5 (low effort), same prompt, 4 shards | L1 triage | closed, paid |
| Gemma 4 26B-A4B local judge (JUDGE2) | ranking check only | open weights; κ 0.32 / 0.55 vs Opus |

UNKNOWN: HF revisions of the two catalog models and of the packs dataset commit; the reranker quant's upstream licence; whether Gemma's terms allow redistributing a quantised file (we only link); the emergency detector's base-model licence.

## Files not shipped (by design) and what stands in for them

| what | size / sha256 | where it is | why it is not here |
|---|---|---|---|
| GGUF model files listed above | 0.04-13.2 GB each, sha256 in the table | the "source @ rev" column | weights are not versioned and are third-party licensed |
| Knowledge-pack SQLite files and vector sidecars | 0.5-30 GB in total | Hugging Face dataset `r4topunk/boar-packs`; rebuild scripts in `rnd/kiln/packs/` and cards in `rnd/research/packs/` | large, regenerable |
| Emergency-detector model (mmBERT-small + head) | see `rnd/research/coordinator/repro/BOM.md` | not hosted; base-model licence unknown | licence unclear |
| Git bundles of unpushed engine worktrees (`rnd/archive/*.bundle`, `*.tgz`) | 0.0-1.2 MB each | kept privately | binary, cannot be scrubbed |
| Brand images (`rnd/research/brand/logo-v2/export/*.png`) | 20-65 KB each | kept privately | binary assets |
| Learned-detector heads `bge-head.head.npz`, `e5-head.head.npz` | 3,588 bytes each | `rnd/research/sonar/exp/30-learned-detector/results/` (BOM only, not copied) | model files |

The retired held-out sets are described in `rnd/heldout/README.md`; what stays out is in `docs/EXCLUDED.md`.

- `bge-head.head.npz`: 3588 bytes, sha256 `b48102154d41347008ffa6b9484746756a13082647a4ad443de696b0e616f541`
- `e5-head.head.npz`: 3588 bytes, sha256 `2ab75c08c2259879e609d15424adee239abf8bd83e908b7e7db1a4ab10d098a8`

## Run traces

All `.jsonl` run traces (8,833 files, about 825 MB) are published as the Hugging Face dataset https://huggingface.co/datasets/r4topunk/boar-traces at the same paths; per-file sha256 in `TRACES.tsv`.
