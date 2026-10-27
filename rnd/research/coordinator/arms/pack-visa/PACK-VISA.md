# PACK-VISA: boar-visa-en, Wikipedia visa requirements + visa policies (2026-10-19/20; opus agent, track pack-visa)
TL;DR: built **boar-visa-en** = 387 enwiki articles (203 "Visa requirements for X citizens" + 184 "Visa policy of X") at their 2026-10-01 revisions, tables flattened to one text line per destination row; 10,830 chunks, [competitor score removed] indexed, **11,231,232 B, sha256 d1dd0ffb…ad20**. Crowding (public sets): share [competitor score removed] (v0.1) / [competitor score removed] (rivalset), gold unchanged → **default-eligible** (by absence). Self-test (20 items, Haiku L1, 4B cut 7, s42): with 0.366 (0.316–0.422) vs without 0.359 (0.302–0.428), **Δ +0.007 (−0.024…+0.041)**; pack kept on 1/20 items. The rows are right, but fast-tier retrieval ranks Wikivoyage destination pages above them (fact article in the top-20 pool 9/20, in the top-k 1/20). 0 paid API, 80 Haiku calls.

## Deliverables
| what | where |
|---|---|
| pack + .json + .sha256 + card + LICENSE | `shared-data/packs/wave4/boar-visa-en.{sqlite,sqlite.json,sqlite.sha256,card.md,LICENSE.txt}` (MacBook and mini, sha checked on both) |
| card | `arms/pack-visa/boar-visa-en.md` (= wave4 card; written to the card wording rule) |
| self-test | `arms/pack-visa/selftest/boar-visa-en.jsonl` (20 items), `draw-boar-visa-en.json` (seed 11, 60 candidates, 20 chosen, 40 rejects), `draft-boar-visa-en.jsonl`; bench dir `boar-eval/bench/selftest/boar-visa-en/` (questions + refs + MANIFEST) |
| runs | `selftest-runs/st-boar-visa-en-cut7{,-nopack}-s42.{requests,traces,judgments}.jsonl` (+ logs), `replay/` (crowding + diagnostic replays) |
| numbers | `aggregates/selftest-scores-visa.json`, `aggregates/st-*.{gen.json,floor_metrics.txt}`, `aggregates/crowding-visa.json`, `aggregates/convert-info.json` |
| tools | `tools/fetch.py` (API fetch), `tools/aliases.py` (redirects), `tools/convert.py` (HTML → builder JSONL), `tools/st.py` (shared self-test tools, paths redirected), copies of the shared scoring/crowding tools with arm paths (`selftest_to_bench.py`, `selftest_agg.py`, `run_selftest.sh`, `score_selftest.sh`, `localjudge_agg.py`, `crowding_agg.py`, `crowding.sh`) |

## Steps and numbers
| step | what | numbers |
|---|---|---|
| titles | grep of the enwiki-20261001 multistream index on the mini | 651 titles → 387 non-redirect articles (API `prop=info`); 0 without a revision before the snapshot |
| fetch | MediaWiki API, revision current at 2026-10-01T00:00Z, `action=parse&oldid`, serial, ≥ 2 s apart, descriptive UA without personal data (a first run with a generic UA got HTTP 429) | 387 pages, 181 MB HTML, ≈ 32 min; revision months 2026-09 184 / 08 92 / 07 43 / 03–06 63 / 2025 5 |
| aliases | visa-titled redirects from enwiki-20261001-redirect.sql.gz | 264 redirects to 111 targets; 254 kept as aliases |
| convert | `tools/convert.py` | 387 docs, 8.11 M chars, 806 tables, 53,918 row lines, 0 lines starting with `\|`; demonym context ("citizens of X") on 177/203 requirements articles |
| build | BOAR builder on the mini (Metal) | 3 s; 387 articles / 10,830 chunks / 10,830 indexed / 387 lead vecs; 10.7 MiB |
| self-test | seed-11 draw (369 eligible ≥ 1500 B; strata family × length tercile), 13 requirements + 7 policy articles | shared checks PASS: 20 items, non-lead 20/20, styles 7/7/6, 0 item failures |
| crowding | replay as a peer to the claim kit, deep tier, k 6, pool 20, public v0.1 (60) + rivalset (72) | v0.1 share 0.009 (1/111), raw6 4 slots, gold res raw6/kept 16/14 = base; rivalset [competitor score removed] (0/88), raw6 7 slots, travel items 0/45 kept slots; p50 +12/+14 ms → **default-eligible** |
| scoring | `score_selftest.sh boar-visa-en 42 [--no-pack]` → Haiku 5.5-low L1, N = 4, both orders | 40 + 40 judge rows, 0 failures; with raw 0.366 / above_min 0.194; without 0.359 / 0.184; Δ raw +0.007 (−0.024…+0.041), above_min +0.010 (−0.026…+0.052); better/worse 6/8; win/tie/loss 0/0/20 both |
| gen checks | `selftest_agg.py` | with pack: retrieval fired 18/20, kept 28 slots of which 1 from the pack (1 item), fact article in raw 1/20, kept 0/20; tasks chat 10 / research 5 / lookup 4 / compare 1; p50 24.0 s (no pack 16.8 s) |
| diagnostic | replay of the 20 self-test questions, fast tier, pool 20, 0 model calls (`replay/selftest-fast-pool20.jsonl`) | fact article in pool-20 on 9/20 (ranks 0–8), in the top-k on 1/20 (item 001); top slots go to Wikivoyage destination pages; 3 items retrieve nothing |

## Reading
- The pack is small (11 MB), cleanly licensed, and its rows answer the bounty's offline-traveller question shape ("can a <nationality> enter <country>, for how long, eVisa or on arrival") directly. The 4B's answers without it repeat wrong defaults (e.g. 90 days visa-free for Indonesians in Japan; the pack says 15 days, conditional on registration).
- It does not help today because retrieval does not bring it into context: lexical/title matching favours the Wikivoyage country page named in the question, and this pack has no popularity prior (views 0). The crowding pass is the same fact seen from the other side: it takes no slots.
- Levers (not run; each needs its own frozen criterion): (a) a views prior or a title boost for "Visa requirements for <demonym> citizens" when the question names a nationality and a destination; (b) a nationality-to-article router (203 fixed titles, demonym table from the leads); (c) question-to-row dense matching (format v3). (b) is the cheapest and closes the loop on this question shape.

## Deviations
- **Text source**: the mini holds only the enwiki-20261001 *index* (stage-B text was range-fetched and deleted), so the article text came from the MediaWiki API (allowed as the fallback), pinned to the revision current at 2026-10-01T00:00Z to keep the dump's snapshot date. API HTML instead of wikitext because the visa tables are template-built ({{yes|…}}, {{flag|…}}); the builder's wikitext cleaner drops them.
- **User-Agent**: the first API run got HTTP 429 with a generic UA; it was restarted with UA `BOAR-pack-builder/0.1 (offline research build; <API etiquette URL>)` (no personal data) and 2 s spacing; no further 429s.
- **Crowding sets**: the rule is "both sets" = v0.1 + v0.2, but the v0.2 question file and replays live under `blind/`, which this track may not read. Used v0.1 public + the public rivalset (a competitor team 72-item eval; 20 travel items; no gold → gold clause vacuous there). Verdict default-eligible on both; a v0.2 replay by the coordinator would complete the rule.
- **File locations**: self-test jsonl/draw, card and tools live in `arms/pack-visa/` (commit scope = own arm dir) instead of `rnd/research/packs/` and `arms/packs/tools/`; shared tools were imported or copied, never edited. The boar-eval bench dir `bench/selftest/boar-visa-en/` is written but not committed (boar-eval is another repo; not in this track's commit scope). Pack wave dir = `shared-data/packs/wave4/` (shared with the boar-nist-crypto track; distinct file names).
- **Port**: the self-test generation uses the shared runner, whose adapter starts its own llama-server on an OS-assigned free localhost port and stops it at exit (port 8195 unused; no fixed port touched). No server on the mini.
- **Coverage probe (D-K3c)** not run: it needs V-para (blind) and jev (paid API), both outside this track.
- **Conversion defect kept**: one article (Swedish citizens) carries a stray "Liberia /" prefix on later rows from a malformed source row; destinations and values are correct; noted in the card.
- Card/catalogue: `rnd/research/packs/README.md` and DISK-LOG not edited (outside commit scope); the coordinator can add the row (sha above).

## Disk
- Mini: `<runner>/shared-data/packs/wave4/boar-visa-en.*` 11.3 MB + `<runner>/kiln/pack-visa/` 8.2 MB (index grep, aliases, converted JSONL). Free 34 GiB after. MacBook: `shared-data/packs/wave4/boar-visa-en.*` 11.3 MB, `shared-data/packs/work-visa/` ≈ 200 MB (rendered-page cache 181 MB = rebuild input, class B; deletable, re-fetchable with tools/fetch.py in ≈ 32 min).
