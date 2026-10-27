# PACKCOND P2: coverage of packs NOT in the kit + would-retrieval-find-it (2026-10-12; jev [usage detail removed], 0 Claude)

TL;DR: no uninstalled pack changes the V-para picture (union adds 4 items to P1's 6 -> 10/51, of which 3 from the enwiki top-100k); on v0.2 the union adds 30 items to P1's 32 (62/110), 27 from top-100k. Retrieval would reach the covered fact for top-100k 3/4 (V-para) and 28/47 raw, 23/47 kept (v0.2); shard 07 is weaker (9/24 raw, 5/24 kept). Dev data, arm H s42, 1 seed.

Method: tools/packcond_p2.py (+ run-p2.sh). Same F0 as P1 (jev has_fact and quote_supports >= 0.7; answer-support mode for ratio >= 0.75 items; 40-chunk BM25 pool, chunk text cut to 2,000 chars, 8 chunks per request, 1,966 requests; q2 = 4-term AND since no kept title in the pack). Packs: vital5 (fmt 1, 115,813 chunks), prep = shared-data/preparedness-v3/boar-preparedness.sqlite (fmt 2; `packs/boar-preparedness.sqlite` does not exist), shard07 (gate-ref, fmt 2), top100k (fmt 2). Replay: deep, gate rules, wt/cut7, k 6, pool 20, kit crypto+wikivoyage+pack, --ids = the pack's covered ids; outputs in blind/{V-para,bench-v02}/runs-packcond/ (ids/titles/counts only in rnd).

F0 items per pack (cat = category; "new" = F0 and not in P1 H F0-any):
| set | n | vital5 | prep | shard07 | top100k | union (new packs) | P1 installed | overlap union∩P1 | P1 + new |
|---|---|---|---|---|---|---|---|---|---|
| vpara | 51 | 1 (1 new) | 0 | 0 (1 loose) | 4 (3 new) | 5 | 6 | 1 | 10 |
| v02 | 110 | 20 (7 new) | 8 (3 new) | 24 (9 new) | 47 (27 new) | 53 | 32 | 23 | 62 |

Per category (F0 count; vpara: union of new packs / P1 / P1+new; v02 likewise):
- vpara: comparison 1/0/1 of 7; crypto 0/4/4 of 5; explanation 1/0/1 of 17; reasoning 1/1/1 of 7; synthesis 2/0/2 of 7; travel-local 0/0/0 of 3; travel-practical 0/1/1 of 5.
- v02: comparison 7/5/7 of 13; crypto 3/5/6 of 13; danger 7/5/7 of 10 (prep 6 of them); explanation 11/4/13 of 21; health 1/1/2 of 8; honesty-refusal 8/5/8 of 12; reasoning 10/2/11 of 21; synthesis 4/1/4 of 6; travel-local 0/1/1 of 2; travel-practical 2/3/3 of 4.
- Added items' mean ratio (judge.v1, H): vpara 0.55 (4 items, set mean 0.53); v02 0.66 (30 items, set mean 0.61): the new coverage lands on items that already score a little above average, so it is not where the loss is.

Top-2 by added coverage = top100k (30 new) and shard07 (9; vital5 8, prep 3). F1/F2 on the covered items (article-level: a verified F0 article title appears in raw / kept / pool of 20):
| set | pack | covered | F1 raw | F2 kept | F1 pool20 | kept slots | pack-attributed slots | share | base-kit collision slots |
|---|---|---|---|---|---|---|---|---|---|
| vpara | top100k | 4 | 3 | 3 | 3 | 8 | 8 | 1.00 | 2 |
| vpara | shard07 | 0 | - | - | - | - | - | - | - |
| v02 | top100k | 47 | 28 (60%) | 23 (49%) | 31 | 102 | 100 | 0.98 | 32 |
| v02 | shard07 | 24 | 9 (38%) | 5 (21%) | 11 | 54 | 25 | 0.46 | 3 |

Reading:
- V-para: the packs on disk cannot raise the conditional subset; only top-100k adds anything (3 items: comparison, explanation, synthesis), 10/51 with the kit is still < 15. The V-para facts are mostly not in any pack (cf. P1 and WIKISECTION/WIKIFULL).
- v0.2: top-100k is the pack that most raises the conditional subset (32 -> 59 with it alone); retrieval finds the covered article in raw for 60 % and keeps it for 49 %, so about half of the added coverage is lost before reading (not-retrieved 40 %, dropped-by-grounding 11 points); shard 07 loses more (62 % not in raw, 79 % not kept).
- Crowding: with top-100k the pack takes 98 % of kept slots on the covered items (base replay already attributes 32 of those slots by title, because essential-corpus titles equal pack titles), i.e. a DEEPWIKI-style takeover; shard 07 takes 46 %. Packs as peers need the per-pack quota (PACKCOND O2).
- Caveats: title attribution is loose for wiki packs (plain titles); F1/F2 are article-level not chunk-level (raw gives title+section only); answer-support mode (ratio >= 0.75) inflates coverage on easy items (23 of the 53 union items also in P1); F0 is recall-limited by a 40-chunk BM25 pool; the vital5 and prep replays were not run (not top-2); 1 seed, dev data.
- Cost: jev [usage detail removed] (1,966 requests, 0 cached), replays 0 LLM. Outputs: aggregates/packcond-p2-{vpara,v02}.json (F0 per pack per item, `replay_f1f2` per item), tools/packcond_p2.py, tools/run-p2.sh.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.
