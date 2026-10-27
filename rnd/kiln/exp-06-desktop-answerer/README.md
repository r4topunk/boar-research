# exp-06: BOAR's real answer engine on the desktop (Mac mini)

Date: 2026-10-01 · Author: Kiln (R&D) · Request: r4to via ai research #2 · Rule 0: the engine stays on local branches. This harness is an eval tool and could become a PR later, with r4to's OK.

## TL;DR

- **`runner/answerer.ts` runs `createAnswerer` from `src/routing/answer.ts`, the chat's real orchestrator.** It loads the app's `src/` from a checkout at a commit (`setup-tree.sh`, `git archive <sha>`), and the commit is written on every row.
  - Real code it exercises: fixed routes, the gates (onTopic / compressContext), checkCitations / attributeCitations, geo, WikiPack, depth, and the compact-tier declines.
  - Native pieces are swapped:
    - llama.rn generation → node-llama-cpp;
    - embeddings, SQLite and the file system → the eval runner's Node shims;
    - device RAM and platform → **simulated** (`--ram-gb`, `--platform`), so the app's own code makes its device decisions.
- **DoD met.**
  - **vitalik58 runs end to end:** 54 unique questions, 0 errors, **2 min 34 s** on M4 CPU with 4 threads.
  - **Against the iPhone 13 (Plumb's run 2, same build 14de107, same packs):** on all 52 shared questions, **tier 52/52 and shown sources identical 52/52**. Decline 44/52, cited titles 43/52.
  - **The device itself repeats at the same rate:** run 1 vs run 2 on the same build gives decline 33/38 and cited 32/38, with only 19/38 identical answers.
  - So the deterministic half (route, tier, retrieval, source gates) matches 100%. The generated half differs from the phone as much as the phone differs from itself.
- **Known differences from the device:** sampler and RNG implementation, chat-template renderer, no KV-prefix reuse, and desktop speeds (§4). Absolute TTFT and tok/s are not phone numbers.

## 1. Run

```bash
# MacBook: put boar-app src at a commit on the mini (nothing copied into this harness)
bash rnd/kiln/exp-06-desktop-answerer/setup-tree.sh 14de107        # -> the mini:<runner>/kiln/app-14de107 (+ kiln/ runner)
# mini, heavy queue: iPhone 13 profile (4 GB, iOS), the run-2 kit (essential corpus + crypto + Wikivoyage), quick mode
<on the mini> "bash -lc 'cd <runner>/kiln/app-14de107 && <runner>/bin/run-heavy Kiln kiln/node_modules/.bin/tsx kiln/answerer.ts \
  --commit 14de107 --model qwen2.5-1.5b-instruct-q4km --questions kiln/questions.vitalik58.jsonl --out kiln/runs/p2-iphone13-1.5b.jsonl \
  --ram-gb 4 --platform ios --pack \$HOME/boar/shared-data/crypto/boar-crypto.sqlite,\$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite'"
# Android 8-12 GB profile:  --ram-gb 12 --platform android --model qwen3-4b-instruct-2507-q4km
python3 compare_device.py runs/p2-iphone13-1.5b.jsonl ../../plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-14de107-device.jsonl [--all] out.md
```

**Flags:**
- `--settings '{"quickFirst":true,"alwaysComplete":false}'` (answerSettings)
- `--pack a.sqlite,b.sqlite` (real pack files, symlinked into a per-config app dir)
- `--places world-places.sqlite,<city>.sqlite`
- `--corpus essential`
- `--threads`, `--seed 42`, `--gpu` (default off: CPU generation)
- `--ids`, `--limit`, `--label`

The question's `context.lat/lon` simulates the GPS fix for "near me" items.

**Node deps are symlinked, not installed:**
- `<tree>/node_modules` → `<runner>/official-6c3d6c6/node_modules` (app deps);
- `<tree>/kiln/node_modules` → `<runner>/eval-runner/eval/node_modules` (node-llama-cpp 3.21.1, tsx).

No download. The mini's disk is untouched apart from 17 MB of tree.

## 2. What each row has (`runs/*.jsonl`)

| Field | Content |
|---|---|
| `id`, `question`, `category` | the item |
| `commit`, `model`, `device {ramGb, platform}`, `settings`, `label` | the configuration |
| `tier`, `outcome`, `reasonCodes`, `route` | the app's route and receipt reason codes. `route` keeps the task / instant / places / grounding / generate codes |
| `sources` [{title, section, source, similarity}], `shownSources` | final sources, and what the chat showed (kept on a decline, like the device's `retrievedTitles`) |
| `citedIdx`, `citedTitles` | from the `done` event |
| `answer` | final text as the user sees it |
| `flags {weak_sources, declined, warnings}`, `error` | |
| `receipt {ttftMs, totalMs, retrievalMs, prefillMs, promptTokens, tokens, tokPerSec, timedOut}` | `ttftMs` is the app's own (first visible text of any tier: an instant snippet counts). `prefillMs`/`tokPerSec` come from the node-llama-cpp generation |
| `host {cpu, loadAvg1m}`, `packs [{id, sha256}]`, `createdAt` | provenance |

## 3. Agreement with the iPhone (DoD)

**Device:** iPhone 13, iOS 26.6.2, build `rc6eval-r11-0459` = `build/model-ab-rc6-eval` @ `14de107`, llama.rn rc.6, Qwen2.5-1.5B, kit `boar-crypto` + `boar-wikivoyage-en`, quick mode (`rnd/plumb/run-commands.md`). File: `rnd/plumb/data/…__iphone-14de107-device.jsonl`.

| | Desktop vs iPhone (all 52 shared) | Sample of 10 (seed 20261001) | **iPhone vs iPhone** (run 1 vs run 2, same build, 38) |
|---|---|---|---|
| Tier | **52/52** | 10/10 | 38/38 |
| Shown sources, identical title sets | **52/52** | 10/10 | 38/38 |
| Declined | 44/52 (85%) | 8/10 | 33/38 (87%) |
| Route codes identical | 37/52 | 6/10 | — |
| Cited titles identical | 43/52 (83%) | 8/10 | 32/38 (84%) |
| Answer text identical | — | — | 19/38 |

Files: `results-sample10.md` (per id: sources, citations, both answers) and `results-all.md`.

**Where they diverge, and why:**
- **Every divergence is after generation**, in the compact tier's citation gate.
  - Example: `vit-fa-015`. The desktop draft had no `[n]` → `grounding:uncited-with-sources-declined-compact`; the device draft had one → answered.
  - Example: `vit-hlt-001`, `vit-hum-005`. Both declined, but by different codes: `uncited-…` on the desktop vs `all-citations-removed-…` on the device.
- **Route codes** differ only in those decline codes. Nothing before generation differs: classification, retrieval, compression, instant tier and the source gate.
- **Causes of the different drafts:**
  - (a) Sampler: node-llama-cpp 3.21.1 vs llama.rn rc.6 (llama.cpp b11192). Same parameters (temp 0.7, top_k 40, top_p 0.95, min_p 0.05, seed 42), different sampler chain and RNG, so different tokens.
  - (b) Chat template: node-llama-cpp's `resolveChatWrapper` vs llama.rn's jinja render. Same GGUF template, possibly different whitespace or BOS.
  - (c) KV-prefix reuse: the app prefills its fixed answer prefix in llama.rn; here every answer is a fresh context (§4).
  - The device itself gives a different answer text on 19 of 38 repeats, so (a) alone explains the level.

## 4. Known differences from the device

| Area | Desktop | Device | Effect |
|---|---|---|---|
| Generation runtime | node-llama-cpp 3.21.1, CPU 4 threads (M4) | llama.rn rc.6, CPU (Metal off) | Different drafts at temp 0.7 (see §3). For a stable A/B, compare desktop vs desktop on the same commit and seed |
| Speed | prefill p50 2.8 s, 56.6 tok/s, total p50 3.0 s per answer (M4) | ~13-15 tok/s, TTFT 4-7 s (iPhone 13) | Desktop timings are an upper bound, never device numbers |
| KV prefix | fresh context per answer (`setAnswerPrefix` no-op) | fixed prefix prefilled once | Prefill time only |
| Memory / jetsam | not simulated (RAM is simulated only for the app's decisions) | real | No OOM path |
| Embeddings | node-llama-cpp (Metal) via the shim | llama.rn CPU | Float noise; shown sources still identical 52/52 |
| Telemetry | `getModelSpeeds` empty, `recordExecution` captured in memory | device history | Deep-tier auto-eligibility. Not reached on the compact tier |
| Multipass | not wired (`alwaysComplete: false`, as in the run) | wired | The "complete" mode is not measurable yet |
| Places | only the packs given with `--places` (this run: none) | the cities installed on the phone | Same as run 2 here (no places kit) |

**Total time:**
- First setup: ~28 s, which embeds the 5,300 corpus chunks once, cached per (tree, corpus, packs).
- Later setups: ~1 s, plus 0.7 s to load the model.
- 54 questions: **154 s**. The device took ~10 min for 52.

## UNKNOWN

- llama.rn's exact default sampler chain (penalties, typical-p) vs the parameters set here. Assumed equal to the eval runner's defaults.
- Whether node-llama-cpp's template render is byte-identical to llama.rn's for Qwen2.5.
- An Android 12 GB / Qwen3-4B profile was not compared with a device: no Android device run exists on this build.

**Metric:** desktop vs iPhone on 52 questions: route and sources 52/52; decline 85%, the same as the device's own 87% repeatability.
**Next step:** exp-07 (T2, expansion on a miss), measured with this harness, desktop vs desktop, same commit and seed.
