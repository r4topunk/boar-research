# SECTIONHIT — was the fact's passage in the deep tier's kept context? (PACKCOND, 0 calls, 2026-10-12)

**Verdict: no passage-selection headroom.** In the reading buckets (retrieved-not-used 7 + used-wrong 5 = 12), the F0 *article* is not in kept in 6/12 (4 never reach raw). The fact section is kept in 3/12; the article is kept without the fact section in 3/12. Keeping 3 sections or ranking sections by rare-term + number overlap would recover **0 additional** items.

## Method
- `tools/sectionhit.ts` (+ `.sh`; copy of replay-p4b.ts plus `--sectionhit`) reruns the P4/P4b OFF engine replay: wt/packcond, `--deep --gate rules --k 6 --pool 20 --tasks-from` the H v0.2 s42 traces, deepcovfb cache. Raw matches the traces 32/32; raw, kept and codes match p4b-v02.jsonl 32/32. `refOf` now records the chunk id, so each raw/kept pack chunk resolves to (article, section).
- Each P1 F0 hit is resolved to its article, `sectionAt` heading, chunk index and is_lead (articlePassages' lead rule). **All 105 hits resolved.** Each is matched by chunk id and by article + heading against raw[] and kept[].
- Ranks (1 = lead): engine `fact_section_rank` = position in `articlePassages(aid, stems(query), 10, action, explain)` (the title path keeps lead + 2 = ranks ≤ 3; "below floor" = score ≤ 0.15, not returned); `rank_unfiltered` = same order, no floor; `alt_rank` = idf of rare query stems (df ≤ 2 %) + query numbers present. Best hit per item: kept chunk > kept section > raw chunk > raw section > article kept > article raw.
- Outputs: `aggregates/sectionhit.json` (32 rows plus `summary`; ids, titles, headings, ranks, booleans) via `tools/sectionhit_agg.py`; `blind/bench-v02/runs-packcond/sectionhit-v02.jsonl` (script-only).

## Counts by P1 bucket (best F0 hit per item)
| bucket | n | art raw | art kept | sec raw | sec kept (= exact chunk) | in lead | art kept, sec not | sec kept, cut <0.98 | engine rank 1/2/3/4/>4/below floor |
|---|---|---|---|---|---|---|---|---|---|
| retrieved-not-used | 7 | 4 | 3 | 2 | 1 | 0 | 2 | 1 (0.96) | 2/2/0/1/1/1 |
| used-wrong | 5 | 4 | 3 | 3 | 2 | 0 | 1 | 2 (0.78, 0.77) | 1/1/1/0/1/1 |
| used-right | 7 | 7 | 6 | 5 | 4 | 2 | 2 | 4 | 1/4/1/0/1/0 |
| dropped-by-grounding | 7 | 4 | 0 | 2 | 0 | 0 | 0 | 0 | 0/2/1/1/0/3 |
| not-retrieved | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1/2/0/0/0/3 |
| all | 32 | 19 | 12 | 12 | 7 | 2 | 5 | 7 | 5/11/3/2/3/8 |

The engine ranks the fact section ≤ 3 for 19/32 items (7/12 in the reading buckets). Losses happen around section ranking (article retrieval, k = 6, grounding, compression), not in it.

## Headroom: article kept, fact section not kept (n = 5; minimum rank over the item's hits in the kept article)
Engine / unfiltered / alt ranks: reasoning-B10 (used-right) 8/8/13; comparison-A04 (used-right) 2/1/1; comparison-B02 (retrieved-not-used) 6/6/8; crypto-A01 (retrieved-not-used) 1/1/1; travel-local-A01 (used-wrong) 5/5/5.
- **Keep 3 sections (adds rank 4): 0 additional. Alt ranker top 2/3: 0 additional.** Both only pick up the same 2 items, which already rank ≤ 3; their articles entered raw as BM25 chunks without the lead (not the title path).
- **Gate for a selection lever:** at most 2/12 reading-bucket items (ranks 5 and 6), and only with nSections ≥ 5, which conflicts with the 400-work budget.
- **"Add the lead for a kept BM25-path article":** reaches 2/5, but only 1 is a reading item, and that item's lead hit has p 0.66.

## Reading the 12 reading-bucket items
- 6/12 no F0 article in kept (P1's pack-level F2 leniency: retrieval failures); 3/12 article without the fact section; 3/12 the fact chunk itself kept = true reader failures unless compression removed the fact (kept bodies 0.96 / 0.78 / 0.77 of the chunk's characters).
- Only p ≥ 0.7 hits (P1 `hits[]` includes 34/105 with p < 0.7): 8/12, 2/12, 2/12. Same conclusion.

## Caveats
- jev hits are per chunk, sections can span chunks, articlePassages keeps one chunk per section (chunk rank ≠ section rank on 5 best hits). Kept text is post-compression (≤ 400 tokens): "section kept" does not prove the fact sentence survived (fact text unknown by design).
- action/explain read from the engine query (as P4b); 5 health-strict items all in dropped/not-retrieved; first retrieve call only; n = 12 on a dev set = directional counts.

## Rerun (bash/zsh, from <workspace>, ~16 s, no LLM, no judge)
```
export BOAR_REPLAY_CACHE=$PWD/rnd/research/coordinator/arms/deepcovfb/cache; A=rnd/research/coordinator/arms/packcond; R=blind/bench-v02/runs-packcond
$A/tools/sectionhit.sh --questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl --ids "$(paste -sd, $A/inpack-H-v02.ids)" --deep --gate rules --k 6 --pool 20 --tree wt/packcond --tasks-from blind/bench-v02/runs-dt512v02/dhv-H-v02-s42.traces.jsonl --gold boar-eval/bench/v0.2/gold/sources.json --sectionhit --out $R/sectionhit-v02.jsonl --agg $A/aggregates/sectionhit.json 2> $R/sectionhit-v02.log
python3 -I $A/tools/sectionhit_agg.py $A/aggregates/sectionhit.json
```

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file; the gate is stated only with the result (no pre-registration).
