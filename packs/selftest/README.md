# Pack self-tests (T-K4b wave 1, T-K6c wave 2; D-K3(b))

> Health and first-aid content here is AI-reviewed, not clinically reviewed; nothing in this file is medical advice.

TL;DR: 20 public questions per Knowledge Pack (wave 1: 7 packs, 140 items; wave 2: boar-factbook + boar-simplewiki-en, 40 items), written by an agent from the pack's own text, with a gold answer, a rubric and verbatim in-pack evidence. They give each pack card a **dev quality number**. They are public, agent-written and **never claim items** (D-K6); held-out pack-matched items stay non-Claude (bench/v0.3/plan/pack-matched.md).

```fish
# checks (0 LLM calls; prints counts only)
arms/packs/.venv/bin/python -I \
  arms/packs/tools/selftest_check.py
# re-run the seeded draw (keeps the hand-written chosen/rejects)
arms/packs/.venv/bin/python -I \
  arms/packs/tools/selftest_draw.py draw
```

The scripts need `zstandard` (venv at `arms/packs/.venv`, `uv venv` + `uv pip install zstandard`); system `python3` lacks it.

## Files

| File | What |
|---|---|
| `<pack>.jsonl` | 20 items, ids `st-<pack>-001…020` |
| `draw-<pack>.json` | seed, strata, cuts, the 60 drawn candidates (id, title, source, views, len, cell), `chosen` (20 ids, jsonl order) and `rejects` (40 ids → one-word reason) |
| `../../arms/packs/tools/selftest_draw.py` | `draw` (seeded sampling), `show <pack> <id>` (article with chunk markers), `fill <pack> <draft.jsonl>` (adds `source{}` from `article_meta` and computes `chunk_index` from the pack) |
| `../../arms/packs/tools/selftest_check.py` | all checks below |
| `../../arms/packs/tools/selftest_common.py` | pack reader (format 2: zstd blocks, UTF-16 chunk offsets as in `wikiPack.ts`) |

Packs: `shared-data/packs/wave1/<pack>.sqlite` (qa-travel-se, qa-ethereum-se, qa-bitcoin-se, qa-health-se, qa-outdoors-se, boar-firstaid-en, boar-medlineplus-en) and `shared-data/packs/wave2/<pack>.sqlite` (boar-factbook, boar-simplewiki-en); `selftest_common.Pack` looks in wave1 then wave2.

## Draw protocol (seed 11)

- Eligible: article text ≥ 1500 bytes; title not closed/duplicate/meta-looking. SE packs also require an accepted answer and ≥ 2 answers.
- Strata: SE packs and medlineplus = length tercile × views tercile (medlineplus views are flat, so 3 cells); firstaid = source (enwiki, enwikivoyage, enwikibooks, appropedia, usgov) × length tercile.
- 60 candidates are drawn round-robin across cells from `random.Random(11)` shuffles. From these the author picked 20 for domain breadth and logged the 40 rejects with a reason (redundant, niche, dated, debugging, code-specific, off-domain, opinion, …).

## Item format

```json
{"id": "st-qa-travel-se-001", "pack": "qa-travel-se", "category": "visas/overstay",
 "style": "first-person|direct|imperative", "question": "…", "answer": "40–120 words, grounded in the article",
 "rubric": ["3–5 facts the answer must contain", "…", "Penalize: …"],
 "in_pack_facts": [{"fact": "…", "quote": "verbatim span ≤ 300 chars", "chunk_index": 2}],
 "source": {"article_id": 32215, "title": "…", "url": "…", "license": "CC BY-SA 4.0",
            "attribution": "Q by … ; A by …", "pack_source": "stackexchange"}}
```

- `chunk_index` is the index of the pack chunk (ordered by `start`) holding the quote; 0 = lead chunk. In SE packs chunk 0 is the question itself, so every evidence quote (taken from answers) sits at ≥ 1.
- SE user display names appear only in `source.attribution` (licence credit), never in question, answer or rubric.

## Checks (`selftest_check.py`)

Schema and ids; answer 40–120 words; rubric 3–5 bullets + exactly one `Penalize:`; 1–3 facts; quote ≤ 300 chars and a verbatim substring of the article; `chunk_index` recomputed from the pack; word-Jaccard(question, quote) ≤ 0.30; no 6-word span shared by question and article; no SE display name from the attribution in question/answer/rubric; English (ASCII share ≥ 0.97 + stopwords); per pack 20 items on 20 distinct articles, ≥ 8 items with a fact at chunk ≥ 1, each style ≥ 5.

Result 2026-10-12: 7/7 packs PASS, 0 item failures. Result 2026-10-13 (after the wave-2 tool changes): 9/9 packs PASS, 0 item failures.

## Wave 2 (T-K6c, 2026-10-13)

Same protocol, seed 11, same checks. Differences:

- **Draw strata (new rules in `selftest_draw.py`).**
  - boar-factbook: region from the `article_meta.url` path (africa / europe / asia = central-asia + east-n-southeast-asia + middle-east + south-asia / americas = north-america + central-america-n-caribbean + south-america / oceania = australia-oceania) × tercile of the Key-facts `Population:` value (stored in the draw file's `views` field). Entries without a Key-facts population (oceans, Antarctica, World) are excluded: 239 eligible, 15 cells.
  - boar-simplewiki-en: broad topic × length tercile. Topic comes from a keyword heuristic on title + first 1,200 chars (science, history, geography, biology/health, technology, arts/society; the top topic needs ≥ 2 hits, otherwise the article is skipped). List-of, year, decade, month/day, leap-year and disambiguation titles are excluded: 44,208 eligible, 18 cells. The heuristic is noisy (for example Sherwood Anderson was labelled biology/health), so each item's `category` is the author's own label, not the cell.
- **Comparison items cite two articles.** Every wave-2 fact has an `article` field (article id), and `selftest_check.py` checks the quote and chunk_index against that article, plus the 6-gram rule against every cited article. The second article is listed in the draw file under `comparison_partners` (partner id → the item's primary article id). `source{}` stays the primary article.
- **Attribution.** boar-simplewiki-en's `article_meta` has no attribution column, so `Pack.meta()` builds the CC BY-SA credit line (`"<title>", Simple English Wikipedia contributors (<url>)`). The factbook carries its own CC0 credit line.
- **Non-lead.** factbook chunk 0 is the "Key facts:" block, so chunk ≥ 1 means a narrative or section fact. In simplewiki, chunk 0 is the lead (or an infobox "Key facts" line followed by the lead).

| Pack | Mix | Non-lead | Check |
|---|---|---|---|
| boar-factbook | capital/population/area 6, economy/currency/GDP 4, government/independence 3, geography/climate/hazards 3, languages/religion/demographics 2, comparison 2 (Maldives–Seychelles, Austria–Ireland); 5 regions × 3 size tiers | 20/20 items have a fact outside Key facts | PASS |
| boar-simplewiki-en | science 4, history 3, geography 2, biology/health 2, technology 3, arts/society 3, comparison 3 (Laetoli–Homo rhodesiensis, Tar pit–Biomass, Hyundai–S-Class); 0 title-only "what is X" questions (all why/how/when/compare) | 20/20 | PASS |

Styles: 7 first-person / 7 direct / 6 imperative in both packs.

Scoring: the shipped scripts in `arms/packs/tools/` score the published packs; see `arms/packs/SELFTEST-SCORES.md` for the results.

## How to score (the card's quality number)

1. Build the pack-installed kit: the claim kit with this pack added (same engine cut, same seed policy as the arm being carded).
2. Generate answers to the 20 questions with the desktop-node adapter (one seed).
3. Judge with the pipeline judge (`boar-eval/harness/judge.mjs`), **Haiku 5.5 effort low (L1)**, sharded **N = 4**, **both A/B orders** (20 × 2 = 40 calls per pack), using each item's `answer` as the reference side and its `rubric` as the item rubric.
4. Card number = the judge's quality ratio (pack answer score / reference score, averaged over both orders) plus the win/tie/loss count. Report it as "self-test, agent-written, dev"; never pool it with bench or claim rows, never compare it to Opus-judged numbers.

Run the self-test with and without the pack (claim kit only) on the same 20 items when you want the pack's lift rather than its absolute level; the paired Δ is the more useful card line.

## Caveats

- Agent-written (Claude family) questions and gold answers: fine for a public dev number, not for claims (judge-contamination rule).
- Questions were written from the article that answers them, so retrieval is favoured (each question has a known in-pack source); the number measures "can the kit find and use the pack", not coverage of real user needs. Coverage is T-K4's jev probe.
- Gold answers are short (59–97 words) compared with the bench's Opus+web references, so ratios are not comparable with v0.1/v0.2/V-para ratios.
- `judge.mjs` reads references from a bench dir (`--bench`/`--refs`); the self-test items are scored through the adapter scripts in `arms/packs/tools/` (see `SELFTEST-SCORES.md`).
