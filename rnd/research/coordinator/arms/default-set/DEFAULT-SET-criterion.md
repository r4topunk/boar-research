# DEFAULT-SET criterion (H-A1, frozen 2026-10-21 before the phone-engine replay and the projections of this arm)

Hypothesis: ruler/hypotheses-round4-2026-10-21.json id "H-A1 DEFAULT-SET", with the two judges' edit applied (the 180 pack self-tests are
reported separately, never in the kill clause, because some were written from medlineplus/visa). 0 LLM, 0 judge, 0 paid, no phone.

## Known before freezing (stated honestly)
PK4-PACK-PRUNE (desktop LITEPACKS adapter, A-union KA replay) is already on disk: on v0.1 57 + cooking/money 40, medlineplus is kept on 8 items
and visa on 5; medlineplus holds a real fact chunk on 2 (lan-hlt-002, vit-hlt-003). So the kill clause below fires on the desktop path for
both packs by the existing data. The phone-engine path (the one T_8GB measures) is new here and is reported next to it.

## Options (each one the default 8 GB install; all keep the gazetteer)
O1 all 6 A-union packs; O2 minus visa; O3 minus medlineplus; O4 minus both; O5 claim kit only (crypto + wikivoyage).

## Data
- Path P (phone engine): boar-eval replay-retrieval.sh, tree bench-app/engine (0ca54d87, the Pixel APK engine), --gate rules, engine k, the
  six format-2 A-union files from shared-data/packs/persona-a-union, one run per option. Kept = the engine's pre-answer sources list.
  Items: MAIN 97 (coverage-matrix/main-97.ids) union the phone 73 (aunion73-a request: v0.1 60 + 12 saf + warmup) union the 64 LITESAFETY
  probes. Determinism check: O1 vs pk5/replay-six.jsonl kept titles on the 97.
- Path D (desktop LITEPACKS KA): PK4-PACK-PRUNE items (reused, not re-run).
- Phone traces: aunion73-a retrievedTitles (pack hits, reported only).
- Fact chunk: RAG-FUNNEL gold_K3 + oracle-real gold-labels.tsv Y/P (real items), PK4 fact_kept, FACT-REACH owners; matched by title on path P
  (format-2 chunk ids differ from the v3proto ids).
- Time: partime_analyze.py drop() logic on perq-aunion73-a.json (serial, Promise.all JS-bound LB, ideal parallel), per option; O5 also the
  measured q17b73-a p50.
- Persona: PERSONA-MAP-v1-draft families (travel = wikivoyage + visa; science = medlineplus + firstaid; place = factbook; tech = crypto).

## Kill clause (per pack, on MAIN 97 union the phone 73; PM 180 reported only)
Keep a pack (visa or medlineplus) in the default install if, on EITHER path, any holds:
(a) it supplies a kept chunk on >= 4 items; (b) it holds the fact chunk on >= 2 items; (c) dropping it changes the kept sources of >= 1 of the
64 safety probes or 12 saf items on path P. Otherwise "droppable on coverage". Separately: if device-day arm C shows < 0.8 s off the search
p50, the time projection is void.
Output is an options table for r4to (product decision); the arm decides nothing about the install.
END FROZEN
