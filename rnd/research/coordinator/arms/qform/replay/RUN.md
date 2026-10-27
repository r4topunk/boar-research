# QFORM replay run (2026-10-21 22:2x, MacBook, 0 LLM, 0 judge, 0 paid)

Tree: <workspace>/kiln-local/be-0cfd4a77-cut7-litepacks (MacBook copy of the K1 tree; ARM `cut7-headpass-x2+litepacks`, COMMIT 0cfd4a77badd0129, src/routing/answer.ts sha256 prefix 0d1ac07d verified).
Merged pack: shared-data/packs/persona-a-union-merged/boar-aunion-merged.sqlite, sha256 7e86674b59b5... (verified by `--verify-sha`, matches). The tool accepted the merged file as one pack (`local-boar-aunion-merged`), so no six-file fallback.
Embedding: shared-models/bge-small-en-v1.5-q8_0.gguf sha256 ec38e8da142596ba... (CPU, `--cpu-embed`). node v25.9.0, tsx v4.23.15, node-llama-cpp 3.21.1 (wt/eval/eval/node_modules).
Questions: items/qform.questions.jsonl (432, sha256 f34e6dd67219b32c...), items/qform.jsonl sha256 3b6a7c1c4909f3a8...

## Tool and the one deviation
Stock tool: boar-eval/adapters/desktop-node/tools/replay-retrieval.ts (sha256 prefix 7fdaf786ca017628). It prints only titles/sections/similarity (no chunk text or ids), which a quote match needs, so the run used a copy,
tools/replay-qform.ts (sha256 prefix 6bd17a2e8c524e4a), that differs only in marked `QFORM` places: absolute HERE path, `--wide N` (a second `retrieve(q, N)` per item, recorded as `wideFull`, does not feed the engine), `--settings-json`,
`--forward-opts` (both default off = stock behaviour), and extra output fields (`rawFull`, `wideFull`, `keptFull` = last non-empty `sources` event with chunkId/docId/title/body/score, `reasonCodes`, `question`).
`--topk` was NOT used: it replaces the k the engine plans (3 lookup, 4 chat/research/compare), so `kept` would no longer be what the app keeps. Instead: raw = retrieve() at the engine's k, wide = retrieve(q, 12) beside it.

## Command (primary, stock settings = the phone's retrieval config: quickFirst only, no head pass, no dense append)
```
export BOAR_REPLAY_CACHE=<workspace>/boar-eval/runs/replay-cache
cd <workspace>/rnd/research/coordinator/arms/qform
<workspace>/boar-eval/adapters/desktop-node/node_modules/.bin/tsx tools/replay-qform.ts \
  --questions items/qform.questions.jsonl --tree <workspace>/kiln-local/be-0cfd4a77-cut7-litepacks \
  --packs <workspace>/shared-data/packs/persona-a-union-merged/boar-aunion-merged.sqlite \
  --gate search --cpu-embed --verify-sha --wide 12 --out replay/qform.replay.jsonl
```
Result: n 432, retrieved 430 (2 answered by the FACTS instant rule, no retrieval: factbook-08-F5, crypto-06-F3), 93 s. First run indexed the seed corpus into a new cache dir appdir/3ffc878d5f961d21 (25 MB).
Gate `search` (always SEARCH when asked), detector = the engine's lexical predicate (no mmBERT).
Rerun (replay/qform.replay.rerun.jsonl): raw, wide and kept chunk ids identical on 432/432 (deterministic).

## Secondary run (K1 settings, same questions)
`--forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}'` -> replay/qform.replay.k1settings.jsonl (K1 arm settings, as in lp-K1 requests). Kept lists differ on 365/432 (head pass adds neighbour chunks). Matrix: aggregates/matrix.k1settings.{json,md}.

## Scoring
tools/matrix.py (0 LLM): gold hit = candidate title+body contains the normalised quote (lowercase, punctuation stripped, whitespace collapsed) or chunk id == gold merged chunk id (items/facts.json). Wilson CI on hit@kept; paired F0 - Fi bootstrap over facts (B 2000, seed 11).
tools/keep_loss.py: reasonCodes of items with gold in raw but not kept. tools/check_forms.py: the QFORM.md scripted form checks (0 violations).
