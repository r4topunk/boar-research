# PACKSHAPE criterion (frozen 2026-10-23 before any pack build or replay; never edited after)

Question: if the worst pack (boar-factbook) states its facts as short self-contained sentences (country name + fact) instead of
table-like "Field (sub): value" rows, does the right chunk reach the 1.7B more often (delivery) and is it read right (reading)?
Direction (r4to 15:3x): no model change; we build the packs. Second target (boar-firstaid-en) only if time allows, under its
own addendum criterion (health: structure only, no medical wording change, "AI-reviewed, not clinically reviewed").

## Variant boar-factbook-shaped (tools/shape.py; sha recorded at build time in PACKSHAPE.md)
- Same source data: the text of the v3proto boar-factbook pack (sha 4ce447e8, = published pack c5854353 + chunk_vecs sidecar), read
  read-only; same 261 entries, page_id, url, licence (CC0), attribution, aliases, views 0. No new facts: every number token of a
  shaped article must occur in the original article text (checked by tools/check_facts.py; any violation = build invalid).
- R1 lead = one-line summary sentence built only from Key facts fields (government type, location, capital, population, area);
  it is the article's first chunk (no heading), so it is the lead the builder embeds in lead_vecs.
- R2 Key facts lines -> 4 field groups (capital, population and area / languages, religions and people / government, currency
  and economy / climate and internet code).
- R3 every other Factbook field (one paragraph of 'Label (sub): value' lines) = one field group; a group under 12 words merges
  with the next field of the same category (at most 3 fields, at most 60 words).
- R4 one line -> one sentence "<Country>'s <label> is|are <value>." (number and unit stay in one sentence: values are not split
  except at '; '); a yearly series of one field -> one sentence; notes -> "Note on <Country>'s <field>: ...".
- R5 Background prose: sentence split; a sentence without the country name (or an alias) gets "<Country>: " in front.
- R6 chunk title = section heading "<Country>: <field group>"; sentences packed in order, <= 120 words and <= 950 chars per
  chunk (continuations "(2)"); a single sentence over the cap is cut at '; ' or ', ' with "<Country> (continued): ".
- Build: the mini builder's build-wiki-pack.mjs (attribution support, sha recorded) with the wt/packcond libs, default params
  (leadChars 2500, chunkChars 1000, blockKb 64, zlevel 12, embedTop 0), name "CIA World Factbook (CC0 archive, data as of
  2026-09-11), shaped (PACKSHAPE)", then the HEADPASS-X2 chunk_vecs sidecar (sidecar_embed.mini.mjs, bge-small q8_0 int8, same
  text rule). File kiln-local/shape-packs/shaped/boar-factbook.sqlite (same file name, so pack id and docIds stay
  local-boar-factbook). Not in shared-data, never published. Pipeline check: the unshaped text through the same builder
  (--no-embed) must reproduce the v3proto chunk spans (10,543) exactly; if not, stop and report.

## Arms and sets (0 LLM, MacBook replays, tree kiln-local/rs-SEFIX read-only, SEFIX-124 env, NOWIKI run.sh recipe)
- BASE = K13 (compose kits.py kit(10)), re-run here; identity vs nowiki/replay/{main,st}.K13.* on kept chunk ids.
- SHAPED = K13 with v3proto/boar-factbook.sqlite replaced by the shaped file. Nothing else changes.
- ST20 = the 20 factbook self-tests (packproof in/on-k13.requests.jsonl); the other 120 on-k13 self-tests are replayed too
  (secondary: crowding on other packs, health losses).
- MAIN 97 = decode-ground dg-S-K1-main-s42 requests (chunk-level facts by coverage-map/tools/chunklevel.py score()).

## Metrics
- ST20 own article in raw / kept (docId pack:local-boar-factbook:a<own id>).
- ST20 own fact chunk kept (primary): BASE = a normalised in_pack_facts quote is a substring of one kept own-article factbook
  chunk body (as diagnose.py); SHAPED = a kept own-article chunk whose section heading (body prefix) maps, via
  provenance.json, to a source unit (Key-facts line / field paragraph / Background paragraph) whose normalised text contains
  the quote. Secondary on both arms: the loose rule (>= 80 % of the quote's tokens of length >= 4 inside one kept chunk body).
- MAIN: chunk-level delivered /92 (BASE expected 42), kept-set changes /97, factbook share of kept slots, MAIN health losses
  (health items losing a kept health-pack doc, NOWIKI score.py rule).
- Pack size (bytes), chunks, build + sidecar wall time.

## Gate (stage 1, 0 LLM) - all three must hold
(a) ST20 own fact chunk kept SHAPED - BASE >= +5 (of 20); (b) MAIN chunk-level SHAPED >= 41 (= 42 - 1; if BASE != 42, BASE - 1);
(c) 0 MAIN health losses.

## Stage 2 (only if the gate passes; cap Haiku 60, Opus 0, paid 0, phone 0)
- Generation: the 20 factbook items, SHAPED kit, Qwen3-1.7B Q4_K_M (b139949c) Succinct, seed 42, 512 max tokens, mini under the
  kiln slot lock with the PACKPROOF recipe (tools/run_mini_off.sh pattern, -t 4); the shaped pack copied to a scratch dir on the
  mini (not shared-data). Live kept titles vs the SHAPED replay reported.
- Labels: Haiku 5.5-low, call A only (N 1), the PACKPROOF label.mjs prompt/schema byte-identical, units built by the PACKPROOF
  prep.py construction (blinded: the unit carries no arm). Compared with the existing PACKPROOF ON labels (resolved; and A-only).
- Decision: LEVER-CANDIDATE if correct-any SHAPED >= BASE + 5 of 20 (0.25 -> >= 0.50) AND read-right-when-delivered (correct-any
  among SHAPED items with the own fact chunk kept) >= 0.6. DELIVERY-ONLY if the gate passed but the decision fails.
  If the gate fails: NO (delivery), stage 2 not run, reading not measured.

## Predictions (written before any build)
- P1 ST20 own fact chunk kept: BASE 7 -> SHAPED 11 (+4; gate (a) fails narrowly).
- P2 ST20 own article kept: 8 -> 11.
- P3 MAIN chunk-level 42 -> 42 (+-1), factbook share of kept slots up (more, smaller chunks).
- P4 MAIN health losses 0.
- P5 if stage 2 runs: correct-any 0.25 -> 0.40, read-right-when-delivered 0.65.
- P6 shaped pack size +60 % to +120 % (31.8k chunks vs 10.5k; country name repeated), build + sidecar < 10 min on the MacBook.

## Rules
Never tune on the outcome: shape.py is frozen with this file (rule changes = a new arm + criterion). No blind/, rnd/veil/,
boar-eval/bench/v0.4. Never touch wt/engfix, rs-ARTCAP, rs-D2Q, Docker/ollama/:8094 on the mini. No push, no upload.
