# NATIVE-PARITY (2026-10-21): where the app maintainer's native pipeline loses vs our engine, stage by stage, without the phone

TL;DR (steps 1-2: 0 LLM, 0 judge; step 3: 102 generations on the mini + 204 Haiku calls, 0 paid; dev ids only)
- **Harness runs and is faithful.** His engine source (snapshot 5f8cc8f4) compiles unchanged on the desktop JVM (one change in a copy: the 0.7 gate reads a property). Against the device: RC1 Pixel 9/9 rows identical (task, kept titles, context tokens); X6 native run 69/73 kept-title lists identical, 73/73 task (X6 ran an older commit, b075adca).
- **KB-only (his RC1 install) retrieves on 1/97 MAIN questions** (Sahara). The 0.7 gate is not the cause: at 0.5 or 0.3 it fires on 77/97, but the gold fact enters the context on 1 item, and the new hits are noise (rule: 118/134 off-topic; hand read: at least 17 of 20 sampled). The 1,300-topic Standard KB does not hold the content.
- **With our 2 claim-kit packs in his corpus dir, his retrieval matches ours:** a source is kept on 61/97 (ours K0: 33). The gold fact is in context on 21 v0.1 items (ours: 13), and on 12 of our 13 fact items. Lowering the gate here *hurts*: KB noise crowds out pack chunks (fact 21 → 16).
- **X6 gap (−0.089 raw, 4B, both Succinct), exact item decomposition:** our deterministic layers −0.050 (11 items, 56 %) · crypto content his corpus lacked −0.014 (6 items, all vit-cry; our pack fixes 5 of them in his pipeline) · same 4B on items where neither context holds the fact −0.030 (20 items: prompt / grounding / warning wording) · fact in both or only in his context +0.007 (17 items) · unkeyed −0.003.
- **RC1 gap at the 1.5B (step 3): the Detailed persona accounts for all of it.** Ours (Succinct, K1) − his RC1 default (Detailed, KB-only) = **+0.073 raw (+0.028…+0.120)**. Persona alone (his pipeline, Succinct − Detailed) = **+0.077 (+0.038…+0.120)**. His pipeline in Succinct vs ours = **−0.004 (−0.041…+0.033)**. Reading under the frozen rule: persona-dominant. Context row (STYLE15B, n 50): our engine in Detailed = his Detailed (+0.005).

## Harness (tools/, how to rerun)
- `bash tools/run.sh` (MacBook, ~4 min). It copies `wt/native-qa/android-native/engine/src/main/java` to `work/engine-src` and applies `tools/cutoff.patch.sh`, which makes RagPure.ANSWER_MIN_SIMILARITY read `-Dboar.cutoff` (default 0.7). It then starts two llama-server b11010 CPU processes (bge-small Q8_0, sha ec38e8da, ctx 512 as the app; Qwen2.5-1.5B for /apply-template + /tokenize), builds `tools/harness` (Gradle 8.14.3, Kotlin 2.3.0 JVM, org.json + sqlite-jdbc + zstd-jni), and runs `run_vital5.sh`.
- `tools/harness/src/main/kotlin/NativeParity.kt` follows his eval/chat default path (DeviceEvalRunner → AnswerPipeline, fixed model):
  - Classify.classifyTask, then FollowUp.search → Retriever.retrieve(q, 4) → Compress.forAnswer.
  - Persona per ShortAnswer: Detailed falls back to Succinct for health, seed and small talk. Small-model texts are used under 2 GB. maxTokens comes from AppSettings Auto.
  - RagPure.assembleChatMessages → the model's chat template → prompt string + token count.
  - KB = SeedCorpus(builtin corpus.json + corpus-standard.json, sha 2aeff76d) = 1,300 chunks. Packs are opened as DeviceEvalRunner opens them (local-<name>, by name order).
- Configs × cutoffs 0.7/0.5/0.3 × personas Detailed/Succinct on MAIN 97 (v0.1 57 + cooking/money 40):
  - kb: his RC1 install.
  - kbpacks: kb + boar-crypto + boar-wikivoyage-en, kit shas ae9fbd2c / ff8595e3.
  - kbvital5: kb + wiki-vital5, his Encyclopedia tier, catalog sha d3b87d56, downloaded from his public release. This is the X6 corpus.
  - x6replica: X6's 73 questions.
- Per-row outputs live in work/out/*.jsonl (not committed, 10 MB). Aggregates: `aggregates/native-parity.json` (tools/agg.py), `x6-attribution.json` (tools/x6attr.py), `s3-attribution.json` (tools/s3_agg.py).

## Stage table (MAIN 97; ours = LITEPACKS K0, 1.7B, claim kit, MacBook s42; fact = FACTPRESENT lexical rule, share ≥ 0.5)
| stage | ours K0 | his kb 0.7 (RC1) | his kbpacks 0.7 | his kbvital5 0.7 (X6) |
|---|---|---|---|---|
| retrieval runs (router) | 85 (12 answered by deterministic layers) | 97 (no router; every task type retrieves) | 97 | 97 |
| ≥ 1 source kept | 33 | **1** | 61 | 46 |
| gold fact in kept context (v0.1, keyed 52) | 13 | **0** | 21 | 21 |
| of our 13 fact items: his keeps nothing / no fact | – | 12 / 13 | 0 / 1 | 5 / 6 (all vit-cry) |
| kept titles vs ours (both kept, n 33) | – | – | Jaccard 0.70; ≥ 1 title shared on 33/33 | – |
| prompt tokens p50 (Detailed / Succinct) | 295 (Succinct) | 278 / 240 | 485 / 446 | 334 / 268 |
Other differences in the native path: no deterministic layers, no grounding drop, no warning line, and no decline. Detailed applies to 91/97 questions; the other 6 fall back to Succinct.

## Cutoff sweep (0 LLM; 0.3 = 0.5 to within 2 chunks, because the semantic path has its own 0.55 floor)
| corpus | cutoff | fired | fact kept (v0.1) | new gated chunks / items | off-topic by rule (no question word in title) |
|---|---|---|---|---|---|
| kb | 0.7 → 0.5 | 1 → 77 | 0 → 1 | 134 / 77 | 118 (88 %); hand read 20: ≥ 17 off-topic (e.g. Great Barrier Reef for world population, Blockchain for EIP-4444) |
| kbpacks | 0.7 → 0.5 | 61 → 87 | **21 → 16** | 55 / 42 | 46 (84 %) |
| kbvital5 | 0.7 → 0.5 | 46 → 97 | 21 → 27 | 179 / 76 | 78 (44 %) |
Reading: with the Standard KB (alone or next to our format-2 packs), 0.7 is not the binding problem; lowering it only adds noise. It is binding for format-1 Wikipedia packs (vital5: +6 facts, but 56 % of the new chunks still off-topic). A maintainer change to the gate is not the first ask.

## Attribution
- X6 (4B, Succinct both, 57 ids, existing Haiku rows, tools/x6attr.py): see TL;DR. Bucket ids are in aggregates/x6-attribution.json. Our-fact flags come from RAG-FUNNEL K0, used only where the K0 kept titles equal the phone cut 7 kept titles (true for all 43 keyed generated items).
- Step 3 (1.5B, criterion NATIVE-PARITY-S3-criterion.md sha 4d1d4042, plus a budget-line addendum a868f8c1 written before any judge call). Generation: mini, b11010 -t 2, seed 42, native Sampling defaults. Judge: Haiku 5.5-low judge.v1-low, N 4, both orders, 204 calls.

| arm (51 CV5 ids) | raw (CI) | floor-adj (CI) | win/tie/loss | output tokens p50 |
|---|---|---|---|---|
| O ours, Succinct, K1 kit (ship15b-packs P) | 0.385 (0.340–0.440) | 0.220 (0.165–0.288) | 0/2/49 | – |
| N-S his pipeline, Succinct, KB-only | 0.389 (0.342–0.442) | 0.226 (0.167–0.293) | 0/1/50 | 44 |
| N-D his RC1 default, Detailed, KB-only | 0.312 (0.288–0.339) | 0.129 (0.098–0.163) | 0/0/51 | 392 (1,979 chars) |
Paired: O − N-D +0.073 (+0.028…+0.120), floor-adj +0.091 · N-S − N-D +0.077 (+0.038…+0.120), better/worse 27/12 · O − N-S −0.004 (−0.041…+0.033). Persona share 1.06. Valid: 51/51 non-empty per arm, 0 at the token cap.

## Maintainer-note sentence (NOTE-1/NOTE-5 input)
"On the same model, your pipeline in Succinct scores the same as ours (−0.004 raw, 51 dev questions); the gap to your RC1 default is the Detailed persona (+0.077 for Succinct). The Standard KB keeps a source on 1 of 97 dev questions, and lowering the 0.7 gate only adds off-topic passages. With our two packs listed in your catalog, your retrieval keeps the gold fact as often as ours (21 vs 13 items). What is left of the 4B gap on the X6 is our deterministic answer layers (−0.050 of −0.089)."

## Deviations and limits
- The harness needs no change to his code, apart from the cutoff property in a scratch copy. Embeddings come from llama-server b11010 CPU, not his JNI build; the device parity checks above bound the drift. Prompt tokens are counted with the Qwen2.5 tokenizer, also for the 4B rows (Qwen3 tokenizer, close).
- Comparator: "ours" stage rows are the 1.7B LITEPACKS K0 traces (same kit and retrieval as the cut 7 phone run: 43/43 titles equal on keyed generated items), not a 4B rerun. The routing-r1 inventory was not needed (route codes read from the traces).
- The fact rule is lexical (RAG-FUNNEL caveat: noisy both ways). Our 13 come from the dumped context; his come from the kept bodies, by the same rule.
- Step 3: one seed, Haiku (compresses gaps), dev ids, generation on a loaded mini (-t 2; timing not a metric). The STYLE15B context row was read while that arm's file was fresh (n 50); it carries no rule.
- Extra work: one download (wiki-vital5, 164 MB, CC BY-SA, his own public release, sha verified), kept in work/dl.
