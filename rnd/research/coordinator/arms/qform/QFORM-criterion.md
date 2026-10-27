# QFORM-criterion (FROZEN 2026-10-21 22:3x, before any replay or generation; the plan text of QFORM.md at freeze time)

Owner: coordinator (main). Asked by r4to 22:2x: "write questions only for content we have in the packs; see how the model answers with the references, but mainly understand the different aspects of user questions and whether they find the pack document or not."

## Why this is the right next measurement
RAG-FUNNEL on real dev items: fact in no installed pack S1 45/97 (coverage), in a pack but not retrieved S2 8, retrieved but dropped S3 17, kept but answered wrong S4 17, kept and used S5 5. S2+S3 = 25/97 are *retrieval* losses on facts we do have; nobody has measured them as a function of question form. DECODE-GROUND showed the decoder is not the wall. The retrieval replay is 0-LLM (engine's own `answer()` with the LLM stubbed), so the whole matrix costs no judge calls.

## Design
- **Pack set** = the verdict arm's A-union (r4to 20:28): boar-factbook, boar-firstaid-en, boar-medlineplus-en, boar-crypto, boar-wikivoyage-en, boar-visa-en (merged file shared-data/packs/persona-a-union-merged/boar-aunion-merged.sqlite, sha 7e86674b). Gazetteer not involved (place questions are excluded).
- **Facts**: 8 per pack = 48. For factbook / firstaid / medlineplus: 8 of the 20 public self-tests each (seed 42 draw; gold answer, rubric and verbatim in-pack quote already exist). For crypto / wikivoyage / visa: 8 facts authored from the pack text by the agent (one chunk each, verbatim quote, 1-sentence gold, 2–4 rubric points). Agent-written = **dev only, never claim items** (D-K6).
- **Forms** (8 per fact, English, written from the fact + the chunk, not from each other):
  | form | what the user does | retrieval risk it probes |
  |---|---|---|
  | F0 | the base question (self-test or authored direct question, names the entity) | baseline |
  | F1 | entity-free paraphrase (describes the thing, never its name/title) | dense vs lexical; title match |
  | F2 | telegraphic keywords (2–4 words, no verb) | short-query embedding |
  | F3 | situational first person ("I'm in …, my … , what should I …") | long query, intent words dilute |
  | F4 | misspelled / colloquial (1–2 typos in content words, slang) | FTS tokenisation, embedding robustness |
  | F5 | yes/no verification of a TRUE statement | the answer term is in the query |
  | F6 | false-premise variant (wrong number / wrong entity attribute) | distractor pull |
  | F7 | comparison with a second entity (the fact + one other) | k-slot competition |
  | F8 | follow-up fragment as a 2nd turn without history ("and how long does that take?") | underspecified query |
  Checks (0 LLM, scripted): F1 contains no token of the title/entity; F2 ≤ 4 words; F4 differs from F0 by ≤ 2 character-level edits per content word; F5/F6 are declaratives with "?"; every form ≥ 3 words. 48 × 9 = 432 queries.
- **Retrieval replay** (MacBook, boar-eval/adapters/desktop-node/tools/replay-retrieval.sh, `--packs` the merged A-union file, engine tree = the K1 litepacks tree be-0cfd4a77-cut7-litepacks (same as DECODE-GROUND), `--gate search`, `--cpu-embed`): per query record candidates (raw) and kept with chunk ids/scores. Gold hit = a candidate whose text contains the normalised verbatim quote (or same article id + chunk index). Metrics per form × pack: hit@raw, hit@kept, median rank of the gold, mean top score, n. Also the engine's search query string (the rewrite) per form.
- **Answers with the reference** (secondary, after the matrix): Qwen3-1.7B on the mini, A-union kit, the 48 facts × forms {F0, F1, F3, F8} = 192 answers; judged Haiku 5.5-low judge.v1 N 4 both orders against the self-test / authored gold + rubric; split by gold-kept yes/no. Reads: (a) when the gold is kept, does the form still change the answer; (b) the reading gap by form. Cap Haiku 400, Opus 0, paid 0, phone 0.

## Frozen reads (QFORM-criterion.md, frozen before the replay)
- Primary: hit@kept per form (48 each) with Wilson 95 % CI, and the F0 − Fi paired drop. A form whose hit@kept drops ≥ 20 points vs F0 (CI excluding 0) is a **named retrieval hole**; a hole that the engine's query rewrite could address (keyword, misspelling, follow-up) becomes an engine note; a hole in F1 (entity-free) is a dense-embedding limit and goes to the pack card.
- Secondary: per pack; raw-vs-kept gap (keep step losses by form); search-query rewrite effect.
- Prediction (before the run): F0 hit@kept ≈ 0.70–0.85 (self-tests were built on retrievable chunks); F2 and F4 lose 15–30 points; F1 loses 25–40; F8 is the worst (< 0.4); F5/F6 ≈ F0; F7 −10. Secondary answers: with the gold kept, F0 vs F1 answer quality within ±0.05.
