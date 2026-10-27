# DEFAULT-SET (H-A1): which A-union packs go in the default 8 GB install? Options for r4to (2026-10-21, replay-only)

Criterion frozen first: DEFAULT-SET-criterion.md (sha 2c8e3010..., commit 07acd802). 0 LLM, 0 judge, 0 paid, phone untouched.
This is a product decision. The file lists options and their costs and decides nothing.

## TL;DR
- **Frozen kill clause: KEEP both packs.** Each one fires the clause, but on different paths:
  - **visa**: only on the desktop path. LITEPACKS KA keeps a visa chunk on 5 MAIN items. PK4 reads 4 of the 5 as off-topic (Mozi, cooking).
  - **visa on the phone engine**: inert. 0 kept on 112 items and on 64 probes; raw hits on 6.
  - **medlineplus, desktop**: kept on 8 MAIN items, and holds the real fact chunk on 2 (lan-hlt-002, vit-hlt-003).
  - **medlineplus, phone engine**: kept on 1 item, but dropping it changes the kept sources of 3 safety probes (h22, h26, n11).
- **Time** comes from the PARTIME per-pack windows on the Pixel (aunion73-a). Dropping visa saves about 1.0 s serial; dropping medlineplus saves about 0.9 s.
  - Only O4 + Promise.all or O5 reach <= 5.0 s.
  - O2/O3 + Promise.all land at 4.8-4.9 s, which is just under the target but only on the JS-bound lower bound.

## Option table (T_8GB = Pixel 8a answer p50 on the 73, 1.7B; projected from measured per-pack windows, PARTIME drop logic)
| option | packs | T p50 serial | T p50 Promise.all (LB) | T p50 ideal off-thread | phone-engine kept-set changes (112 items / 64 probes + 12 saf) | desktop items losing a kept chunk (v0.1 57 / cm 40) | real fact-chunk items lost | persona coverage lost |
|---|---|---|---|---|---|---|---|---|
| O1 all 6 (today) | 6 + gazetteer | **7.57** (measured) | 5.53 (UB 6.02) | 2.80 | 0 / 0 | 0 / 0 | 0 | none |
| O2 minus visa | 5 | 6.58 | 4.81 | 2.80 | 0 / 0 | 2 / 3 | 0 (no visa gold exists) | travel: the travel-logistics subject loses its only pack |
| O3 minus medlineplus | 5 | 6.66 | 4.91 | 2.80 | 3 / 3 | 6 / 2 | 2 desktop (lan-hlt-002, vit-hlt-003); 0 phone | science: the everyday-health subject loses its primary pack (firstaid stays) |
| O4 minus both | 4 | 5.67 | **4.77** | 2.80 | 3 / 3 | 8 / 5 | 2 desktop; 0 phone | travel logistics + everyday health |
| O5 claim kit only (crypto + wikivoyage) | 2 | 4.43 (measured q17b73-a: **4.16**) | 3.53 | 2.59 | 18 / 18 | 41 / 16 | 7 desktop (factbook 4, medlineplus 2, firstaid 1); 1 phone (lan-hlt-003) | science and place lose every pack; travel logistics too |
Promise.all LB = native SQL overlapped and JS serial (PARTIME §2); UB is computed only for O1. "Ideal" needs the decompress off the JS thread (maintainer engine change).

## Per pack (kept = the pack supplies a chunk to the engine's kept context)
| pack | phone engine: kept items / 112 (raw) | probes 64 | desktop KA kept v0.1 / cm / PM180 | real fact chunk (desktop) | PM180 fact (own self-tests incl.) | Pixel window p50 | phone trace hits (aunion73-a) |
|---|---|---|---|---|---|---|---|
| crypto | 10 (14) | 3 | 10 / 0 / 23 | vit-cry-006, 008, 010, 011 | 0 | 780 ms | 10 |
| wikivoyage | 28 (52) | 20 | 22 / 2 / 44 | 0 | 0 | 811 ms | 26 |
| visa | **0 (6)** | 0 | 2 / 3 / 13 | 0 | 0 | 602 ms | 0 |
| medlineplus | **1 (9)** (cooking-002) | 2 | 6 / 2 / 32 | lan-hlt-002, vit-hlt-003 | 14 | 505 ms | 0 |
| firstaid | 12 (20) | 7 | 25 / 14 / 80 | lan-hlt-003 | 5 | 663 ms | 7 |
| factbook | 2 (5) | 1 | 16 / 1 / 37 | lan-exp-001, 002, 003, 007 | 15 | 712 ms | 2 |

## What actually changes when a pack is dropped (phone engine, kept sources)
- **minus visa**: nothing on the 112 items, the 64 probes or the 12 saf items. Here it is a pure time saving.
- **minus medlineplus**: lan-hlt-002 goes from nothing kept to 'Asthma', lan-exp-005 gets a 3rd Sahara chunk, cooking-002 loses 'Food Safety'.
  - Probes: h22 loses its only source ('Sleep Disorders'), h26 swaps MedlinePlus 'Burns' for Ready.gov, **n11 swaps 'Wikibooks: First Aid/Seizures' for 'Pesticide poisoning'** (off-topic on a seizure probe). Retrieval change only: whether a safety code changes is not settled by this replay.
- **kit only**: 5 saf items and 13 probes lose first-aid sources (saf-005 nosebleed, saf-006 bleeding and n11 go to none; saf-002/dng-002 lose the ATP hypothermia chapters).

## Reading for the product call
- **visa** has two faces:
  - It is the only travel-logistics pack in the persona map (PERSONA-MAP Q2).
  - On every dev set it is either never kept (phone) or mostly a distractor (desktop, PK4).
  - No visa gold exists, so its value on visa questions is unmeasured, not zero.
  - Its share of the 7.6 s is about 1.0 s serial, or 0.7 s under Promise.all.
- **medlineplus** is not inert. It is inert only on the phone path:
  - The phone router skips retrieval on most health items, so its facts never arrive (PK4).
  - On the desktop/native-style path it holds 2 real health facts.
  - On the phone path its removal moves 3 health probes, one of them toward a wrong-topic source.
- **The time target needs an engine change in every option except O5.** The pack choice moves T by at most 1.9 s serial.
  - Promise.all alone 5.53-6.02 s; with the O4 drop 4.77 s. Ideal off-thread search is 2.80 s with all 6 packs, which removes the time reason for dropping anything.

## Options (for r4to; not decided here)
- **A. Keep O1, ship Promise.all, and ask the app maintainer for off-thread search.** No coverage cost. T is 5.5-6.0 s now and about 2.8 s if off-thread lands.
- **B. O2 (drop visa) + Promise.all, T about 4.8 s.** 0 measured coverage cost on the phone engine. The cost is that travel logistics has no pack.
- **C. O4 + Promise.all, T about 4.8 s.** It also gives up the 2 desktop health facts and moves 3 health probes on the phone. It only buys about 0.04 s more than B.
- **D. O5 (claim kit).** Fastest without an engine change (4.2 s measured). It loses science/place coverage and first-aid sources on safety items.

## Caveats and UNKNOWN
- Path P is the bench engine (0ca54d87, lexical detector, no gazetteer wiring). It reproduces pk5 six exactly: 97/97 items, raw and kept.
  - The native Kotlin app's router and dense path are UNKNOWN. PackSource codes 10/11 may mislabel medlineplus/factbook there.
- Kept is not helpful: there is no judge here. Phone "fact kept" is matched by title only. It is cross-pack and over-generous; for example, a Wikivoyage 'Great Wall of China' match.
- The time figures are projections from one cool Pixel run. The p50 sits at a mode gap, so device-day arm C (E1-PAR) is the real test. If arm C saves less than 0.8 s, the time column is void.
- Desktop numbers are PK4's replay (reused, parity 177/177). PM180 includes each pack's own self-tests (true by construction) and is not in the kill.
- UNKNOWN: real visa-question traffic; whether the native app retrieves medlineplus on health items.

## Files
`DEFAULT-SET-criterion.md`; `aggregates/default-set.json` (per pack, per option, kill, ids); `tools/default_set.py`, `tools/packmap.py`. Replay outputs O1-O5 (question + pack titles) stay out of git.

Rerun:
```
boar-eval/adapters/desktop-node/tools/replay-retrieval.sh --questions <q.jsonl> --tree bench-app/engine --gate rules --compress --packs <option files> --out O<n>.jsonl
python3 -I tools/default_set.py <dir> aggregates/default-set.json
```
