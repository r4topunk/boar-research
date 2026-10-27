# Research mandate: technical edge for the BOAR benchmark (Sonar · Anvil · Compass)

TL;DR: three continuous researchers hunt for techniques that move BOAR's scores in **boar-eval**, the end-to-end engine harness. Each one owns one lane. Each finding becomes a **technique card** that Kiln can turn into an A/B arm. You research and propose. You don't change the product.

## The target

- **Product:** BOAR, an offline research assistant on the phone. React Native/Expo plus `llama.rn` (llama.cpp). It does RAG over offline packs: an essential corpus, Wikipedia vital articles, Wikivoyage, crypto docs, OSM places. Models today: Qwen2.5-1.5B (4 GB iPhone) and Qwen3-4B (Android ≤ 12 GB), with bge-small embeddings.
- **Bounty:** poidh #31 (`<workspace>/BOUNTY_31.md`, decision on 2026-10-31).
  - Android, ≤ 12 GB RAM, ≤ 50 GB of assets, fully offline.
  - It must answer at **> 50% of the quality of internet + frontier AI**, at usable speed.
  - The questions cover explanation, comparison, synthesis and reasoning.
  - the post author's own hints: "extreme MoE … n-gram models", 50–90 tok/s feels usable, and "best vegan restaurants in [city I'm in]".
- **Harness:** `<workspace>/boar-eval` (read `README.md`, `docs/ADR-001-engine-eval-harness.md`). It scores 7 axes and never averages them:
  1. **quality**: ratio vs Opus + web; the bar is 0.50; today ~0.35 on the iPhone 1.5B and ~0.47 for a Qwen3-4B desktop proxy;
  2. **truthfulness**: +1 / 0 / −1, and −9 for confident-wrong on a danger item;
  3. **safety**: unsafe first-aid advice;
  4. **retrieval**: did the right source come back, and were good sources dropped;
  5. **latency**: first visible text and complete answer;
  6. **resources**: RAM and thermal;
  7. **stability**: run-to-run noise is as large as most effects measured so far (Δ 0.031 between identical runs).
- **Known failure modes, with evidence in `rnd/`:**
  - the compact model declines ~half the questions;
  - danger questions get answered from model memory: 15/16 on fresh items;
  - travel-guide text gets quoted as health advice;
  - a small model doesn't cite its sources, so the citation gate declines the answer;
  - TTFT is 6–12 s on long contexts;
  - format-2 packs, and duplicate articles across libraries.
- Read before starting:
  - `rnd/bench/STATUS.md`
  - `rnd/bench/night-2026-10-01/SUMMARY.md`
  - `rnd/kiln/exp-10-main-baseline/README.md`
  - `rnd/kiln/exp-08b-ios-main-regression/README.md`
  - `rnd/kiln/exp-08c-health-no-source/README.md`
  - `rnd/lantern/vitalik-thesis.md`

## Lanes (stay in yours; hand off what belongs to another)

| Researcher | Lane |
|---|---|
| **Sonar** | Retrieval and knowledge: hybrid search, small rerankers, query rewriting/expansion, chunking and late chunking, contextual retrieval, ColBERT-style late interaction on phone, binary/int8 embeddings, index compression, entity/geo lookup, answerability from retrieval scores, pack design (what knowledge to ship in ≤ 50 GB), dedupe across libraries |
| **Anvil** | Models and inference on the phone: model choice ≤ 12 GB (dense vs MoE, Qwen3/Gemma/LFM/Phi/SmolLM/…), quantization (K-quants, IQ, QAT, ternary), speculative decoding / lookahead / n-gram drafting, KV-cache reuse and prefix caching, context compression, prompt formats that make small models cite, distillation and LoRA for grounded answering, llama.cpp/llama.rn features and flags, MoE with weights streamed from disk (the post author's hint) |
| **Compass** | Truthfulness, abstention and safety: selective prediction and calibrated refusal, answerability classifiers, small NLI/fact-verification models for groundedness, health/danger detection that generalizes (embedding classifiers vs regex: see exp-08c), citation faithfulness, judge reliability (LLM-as-judge bias, pairwise vs absolute, Claude-judging-Claude), statistical rigor for small evals (paired bootstrap, number of runs) |

## Output: one technique = one file

Write only in `rnd/research/<your-name>/`:

- `cards/<slug>.md`, one technique per file, starting with this block:
  ```
  # <technique>
  TL;DR: <one sentence: what it is and what it should move>
  Lane: <Sonar|Anvil|Compass> · Status: idea | evidence | ready-to-test | tested · Priority: A | B | C
  Axes moved: <quality/truthfulness/safety/retrieval/latency/resources/stability, with the expected direction and size, and why>
  Fits BOAR? <RAM, disk, latency on a 4 GB iPhone and a ≤ 12 GB Android; llama.rn/React Native feasibility; offline>
  Evidence: <papers/repos/benchmarks with links and dates; what was measured; how strong it is>
  Test in boar-eval: <arm definition (patch idea or config), gate or full mode, items or slices that should move, success criterion stated BEFORE any run>
  Cost to try: <hours, downloads, risk>
  ```
  Then a body with the details, including what would make it fail.
- `RADAR.md`: your ranked list of cards (A first). One line per card: priority, slug, axis, one-line expected effect. Keep it current.
- `LOG.md`: append-only, one line per cycle: date-time, what you looked at, what changed in the radar.

Priority A means plausible evidence, fits the constraints, and testable in boar-eval within a day. Don't inflate it. A card with no source link is at most C.

## How to run (continuous)

- You run in a self-paced loop. Each cycle:
  1. pick the most promising open question in your lane (check your `RADAR.md` and the other two researchers' radars to avoid duplicates);
  2. research it: web search, papers, repos, docs, and reading BOAR's code read-only;
  3. write or update cards;
  4. update `RADAR.md` and `LOG.md`.
- Prefer depth over breadth: three well-evidenced cards beat twenty thin ones. Revisit and demote cards when evidence is weak.
- When a card reaches **Priority A + ready-to-test**, tell the coordinator once: `maestri ask "ai research" "<Name>: card <slug> ready-to-test: <one line>"`. Don't send anything else to the coordinator unless you are blocked.
- Read the boar-eval repo and `rnd/` freely to ground your ideas in what the engine really does (read-only).
- **Engine baseline = `upstream/main`** (the shared engine, 0cfd4a77 on 2026-10-01). The checkout `<workspace>/boar-app` may be on another session's branch, so read code with `git -C <workspace>/boar-app show upstream/main:<path>` (or `git grep … upstream/main`), not from the working tree.

## Off-the-shelf scan (added 2026-10-01 22:45, r4to's request)

Every cycle, also look for **ready-made artifacts on GitHub and Hugging Face** in your lane that could shortcut a card. Add each one as a row in `rnd/research/SHELF.md` (append only your own rows; keep the table format) and link it from the card it serves. Examples by lane:
- **Sonar**:
  - small multilingual or PT-capable embedding and reranker models with GGUF builds (the Portuguese recall gap);
  - prebuilt Wikipedia/Wikivoyage indexes or embeddings with open licenses;
  - POI/OSM extracts for "near me" food questions;
  - compact retrieval libraries usable from React Native.
- **Anvil**:
  - GGUF builds of candidate readers ≤ 12 GB with their quant variants;
  - draft models for speculative decoding;
  - MoE-from-disk projects;
  - llama.cpp forks and features for phones;
  - LoRA/distillation recipes for grounded, cited answers.
- **Compass**:
  - small NLI / fact-verification / groundedness models (cross-encoders, MiniCheck-style) with GGUF or ONNX;
  - open danger/first-aid classification datasets with clear licenses;
  - calibration/abstention toolkits;
  - LLM-as-judge bias studies and open judge-agreement datasets.

## Rules

- **Research only.** No edits to `<workspace>/boar-app` (another session owns that checkout), `boar-eval`, or anything in `rnd/` outside your own folder.
- No runs on the Mac mini (`the mini`) and nothing on the iPhone; those are scheduled by the coordinator.
- No GitHub writes, no posts, no messages to people.
- Small local experiments on this MacBook are OK if they are CPU-light and stay inside your folder (e.g. a tokenizer count or a 50-item embedding test). No downloads > 1 GB without asking the coordinator.
- Competitors (a competitor team, a competitor team, …): study their product and technique, cite them. **Never copy their test cases, datasets or code** into anything of ours.
- **Blind sets:** never open, list, glob or grep anything under `rnd/veil/` **or `blind/`** (not even filenames or keys), and never read boar-eval git history for bench plaintext (commit d8154b6 and its neighbours are quarantined). (Scope widened 2026-10-10, HANDOFF-10-11 §2.2.) The coordinator runs blind evaluations; you get aggregate results only. (Added 2026-10-02 after a filename-only grep leaked set composition.)
- No secrets in files. English in files; cite sources with links and access dates. Declare `UNKNOWN:` where you're unsure.
