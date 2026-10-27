# NOTES35 — 35B-written notes pack served to the 4B (tooling)

TL;DR: Vital Articles Level 3 (1,002 titles, Wikipedia's list only) → breadth-first order → the 35B on the mini writes one
150–250-word note per title → a format-2 knowledge pack (`boar-notes35.sqlite`, built by the claim tree's own builder) →
replay retrieval with the curated kit + notes → hit-rate gate (sources ≥ 15 % on the 110 v0.2 ids) before any judge call.
HANDOFF-2026-10-11 §2 / §4 step 7. No judge calls in this tooling.

## Files (sha256)

| file | sha256 |
|---|---|
| `topics/vital3.jsonl` (1,002 rows: title, section, subsection, path, rank, revid 1379525978) | `6e36bbfe94392f04dda730649c9f32fa4f4051a400fda8e1d1e2f0da434f18e4` |
| `topics/order-bf.txt` (rank, title, section path; TSV) | `7a617aa76b0857096403b0a4eb0ed5af5041c906e770481769c6a82db8ecdbdf` |
| `topics/vital3.raw.json` (API responses: wikitext + links; `--from-cache` input) | `815dc341746c8c732b2730de2d4ae36b4b3140d56bd7e7794f953955b50d72e3` |
| `tools/note.system.md` (system prompt, pinned by `.sha256`) | `57e3d36b2a761dc76183b3fb02a0487396dc7fa537be601cc3a68de0bb6814eb` |
| `tools/topics.mjs`, `gen_notes.mjs`, `gen_notes_mini.sh`, `build_notes_pack.mjs`, `hitrate.py` | `shasum -a 256 tools/*` |

Section counts (all | first 300 of order-bf): Arts 40|28, Everyday life 55|28, Geography 110|28, Health, medicine and
disease 46|27, History 80|27, Mathematics 43|27, People 97|27, Philosophy and religion 58|27, Science 224|27,
Society and social sciences 154|27, Technology 95|27. Small sections run out first: from rank ≈ 440 the order is
dominated by Science and Society.

## Commands (coordinator)

```bash
A=<workspace>/rnd/research/coordinator/arms/notes35
# 0. topics (done; rerun only to refresh the list -- new revid => new shas)
node $A/tools/topics.mjs                     # or --from-cache (no network)

# 1. generation on the mini (copy the arm dir, then run under nohup; never touches :8094)
#    The 35B GGUF was DELETED on the mini 2026-10-10: re-download first (rnd/kiln/MODELS.md URL, verify sha 96b9c0af...).
rsync -a $A/tools $A/topics the mini:boar/kiln/notes35/
<on the mini> 'nohup <runner>/kiln/notes35/tools/gen_notes_mini.sh 300 <runner>/kiln/notes35/run-a > /dev/null 2>&1 &'
<on the mini> 'cat <runner>/kiln/notes35/run-a/STATUS; tail -2 <runner>/kiln/notes35/run-a/gen.log'   # DONE / FAIL ...
#    extend to all 1,002 later (resumes; same out dir): gen_notes_mini.sh 1002 <runner>/kiln/notes35/run-a
#    optional thinking: third arg = budget (e.g. 512): gen_notes_mini.sh 300 <runner>/kiln/notes35/run-t512 512
scp the mini:boar/kiln/notes35/run-a/notes.jsonl $A/run-a/notes.jsonl

# 2. pack (MacBook: needs Node >= 23.8 for zstd and wt/cut7/node_modules; file name = kit id)
node $A/tools/build_notes_pack.mjs --notes $A/run-a/notes.jsonl --out $A/run-a/pack/boar-notes35.sqlite
#    prints {"id":"boar-notes35","sha256":"..."}; <out>.json = builder summary + notes35 provenance

# 3. replay (retrieval only, no LLM, no judge) with the curated kit + notes, and the same without notes as control
cd <workspace>
K=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
boar-eval/adapters/desktop-node/tools/replay-retrieval.sh --tree wt/cut7 --questions <v0.2 questions> --ids <110 ids> \
  --packs $K,$A/run-a/pack/boar-notes35.sqlite --out $A/run-a/replay-v02.notes.jsonl
#    (v0.2 is a held-out-style set: log the retrieval-only exposure in EXPOSURES.md + QUEUE)

# 4. gate: sourcesHitRate >= 0.15 -> PASS (counts only)
python3 -I $A/tools/hitrate.py $A/run-a/replay-v02.notes.jsonl $A/run-a/notes.jsonl [--ids <ids file>]
```

## Pack format decision

Format 2 (`boar-knowledge-pack`, formatVersion 2), the curated kit's format (crypto and wikivoyage meta both say
formatVersion 2), built by `wt/cut7/scripts/build-wiki-pack.mjs` unchanged, fed a JSONL shard (`--shards x.jsonl` with
{page_id, title, text, source, url, license}, build-wiki-pack.mjs:279-282) plus `--manifest` (topic-pack meta, like the
crypto pack). One note = one article `# <title>\n\n<note>`; chunking 1000/1500 chars, contentless FTS5, zstd blocks,
df, int8 lead vectors from bge-small-en-v1.5 q8_0 (sha ec38e8da…, `BOAR_EMBEDDING_GGUF` = shared-models copy).
Why format 2 and not format 1 (build-knowledge-pack.mjs): the engine loads both (packs.ts:130 → WikiPack; packs.ts:239
format-1 path), but only format-2 packs get the "article named in the question goes first" path (retrieve.ts:184-190,
`via: "title"`), which is how a topic note should be found.
Source code: `articles.source = 0` (enwiki). The engine has no "notes35" code (wikiPack.ts:108; unknown codes fall back
to enwiki, wikiPack.ts:513; the builder rejects unknown names, build-wiki-pack.mjs:74/279); enwiki is the only code
that keeps the plain title (packs.ts:213) and is the default of `resolveTitle`. The tag lives in
`article_meta.url = https://notes35.boar.invalid/<title>`, `license = "NOTES35 generated note (<model>)"`, and
`meta.sources = {"notes35": …}`; `hitrate.py` detects note chunks by that URL (not by title: the crypto pack has
enwiki articles such as "Sahara" that collide with Vital titles).

## Smoke results (MacBook M1 Pro, CPU llama-server b11010, Qwen3-4B-Instruct-2507 Q4_K_M, port 8098, stopped after)

- `smoke/notes.4b.jsonl` (first 3 of order-bf): 249 / 219 / 224 words, 405 / 300 / 301 tokens, 15.7 / 11.2 / 11.5 s
  (≈ 31 tok/s); second invocation resumed (2 skipped, 1 generated). `--think-budget 64` request accepted.
- `smoke/notes.smoke10.jsonl` (10 Vital titles that public v0.1 items mention): 210–240 words, 290–342 tokens, mean 11.9 s.
- `smoke/pack/boar-notes35.sqlite`: 10 articles, 17 chunks, 155,648 bytes, sha 35294d9d… (smoke only, 4B-written).
- Replay (wt/cut7, crypto + wikivoyage + notes, 10 v0.1 ids in `smoke/replay10.ids`): note chunks in raw on 4/10 items,
  in engine-kept sources on 3/10 (titles: Adam Smith, Singapore, Nile; 6 of 31 raw chunks); control without notes 0/10.
- `smoke/mini-script-test/`: `gen_notes_mini.sh` end-to-end with the 4B (env overrides), STATUS DONE, server stopped, :8094 untouched.

## Expected generation time (35B on the mini)

4B smoke: ≈ 315 completion tokens per note. Deep tier decode on the mini ≈ 10 tok/s (≈ 9.5 measured in DEEPTHINK) →
≈ 32 s decode + a few s prefill ≈ **35 s/note** without thinking: N = 300 ≈ 3 h, N = 1,002 ≈ 10 h.
With `--think-budget 512`: + ≤ 512 reasoning tokens ≈ + 50 s → ≈ 85 s/note: 300 ≈ 7 h, 1,002 ≈ 24 h. Model load ≈ 1–2 min.

## Risks

- **Hallucinated notes become cited facts.** The 4B treats pack chunks as sources and the chunk is labelled
  "Wikipedia — https://notes35.boar.invalid/…" (engine unchanged; enwiki label). Control: the judge's correctness
  dimension on the slice; read a random sample of notes before the pack goes into any run; any claim/device use
  needs an engine label for generated notes ("AI-generated note", not "Wikipedia").
- Crowding: the DEEPWIKI lesson (a general corpus displaced curated chunks at k = 6); here 1,000 short notes vs a 98k
  wiki, but check curated-source displacement in the replay (notes in raw vs curated sources lost) before the slice.
- Coverage ceiling: Level 3 is broad topics (Moon, Nile); bench items ask specifics. Hit-rate measures reach, not answer
  content; notes may define the topic but miss the asked fact.
- Tiny-pack idf: the pack's own nIndexed (≈ 1.7k chunks at N = 1,000) sets its BM25 idf; the 10-note smoke is not
  representative of ranking at N = 1,000.
- Generation non-determinism across llama-server builds/threads even with seed 42.
