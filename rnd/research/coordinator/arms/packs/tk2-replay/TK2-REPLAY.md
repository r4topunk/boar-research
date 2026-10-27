# TK2-REPLAY — is the T-K2 sources patch label-only? (2026-10-13 22:3x; 0 LLM / 0 judge / 0 paid; public items; opus/medium runner, text saved by the coordinator)

**No. On the 180 self-test items the kept list changes on 52/180; v0.1 (kit only) is identical 60/60.** Two mechanisms: (1) the "Stack Exchange: " / "Simple English Wikipedia: " title prefixes make `onTopic` DROP own-pack passages on 17 items (pure drops: travel-001, bitcoin-001/007/012, ethereum-005, simplewiki-010 go kept → empty; ethereum-005/006 lose the fact article; simplewiki-010 loses the fact chunk; bitcoin kept slots 34 → 24); (2) the patch's topic-source rule makes codes 10–12 (factbook, medlineplus, simplewiki) eligible for title lookup, which cut 7 never did → retrieval changes on 40 items (kept on 35), net +7 fact chunk / +6 fact article kept, concentrated in factbook (fact article 5 → 12; "Wikivoyage: Kyrgyzstan" etc. replaced by the Factbook country page) and simplewiki (+1/+1). Firstaid unchanged. The SELFTEST cut-7 scores are effectively the OFF cell.

| set | kept identical | raw identical | prompt identical | fact chunk kept | fact article kept | fact chunk in top 6 | empty-kept |
|---|---|---|---|---|---|---|---|
| 180 total | 128/180 | 140 | 77 | 35 → 42 (+8/−1) | 61 → 67 (+9/−3) | 55 → 66 (+11/−0) | 42 → 47 (+7/−2) |
| travel SE | 19 | 20 | 11 | 1 → 1 | 6 → 6 | 8 → 8 | 6 → 7 |
| ethereum SE | 16 | 20 | 4 | 2 → 2 | 7 → 5 | 3 → 3 | 4 → 5 |
| bitcoin SE | 12 | 20 | 4 | 1 → 1 | 2 → 2 | 1 → 1 | 2 → 5 (kept slots 34 → 24) |
| health SE | 19 | 20 | 13 | 1 → 1 | 5 → 5 | 4 → 4 | 10 → 10 |
| outdoors SE | 18 | 20 | 8 | 5 → 5 | 10 → 10 | 8 → 8 | 7 → 7 |
| firstaid | 20 | 20 | 20 | 1 → 1 | 3 → 3 | 1 → 1 | 5 → 5 |
| medlineplus | 16 | 14 | 9 | 10 → 10 | 11 → 11 | 13 → 14 | 4 → 4 |
| factbook | 7 | 5 | 7 | 3 → 9 | 5 → 12 | 4 → 12 | 1 → 1 |
| simplewiki | 1 | 1 | 1 | 11 → 12 | 12 → 13 | 13 → 15 | 3 → 3 |
| v0.1 (60, kit only) | 60/60 | 60 | 60 | gold kept 8 → 8 | — | gold in top 6 9 → 9 | 10 → 10 |

Definitions = packroute `step0.py` (item's own pack only); empty-kept = retrieved something, kept nothing. Prompt diffs on the 52 same-kept/different-prompt items are the `[n] title` lines only (e.g. `[1] MedlinePlus: Heart Valve Diseases`, `[1] CIA World Factbook (archive): Guatemala`, `[1] Stack Exchange: Winter Camping: …`).

**Patch application:** all src hunks of packs-sources.vs-dt512.patch applied cleanly to cut 7 (packs.ts 3, passages.ts 1, passages.types.ts 2, wikiPack.ts 9, + test file; builder script skipped — cut 7 has no scripts/). Result `tk2.vs-cut7.patch` sha256 d2d09813…; OFF = byte-identical copy of cut 7 src; both cells reproduced twice (180/180, 60/60).

**Reading / recommendation (for the loop, pack line owner, and for PR 1):** the patch mixes a product-necessary change (correct source labels + credit) with two behaviour changes that were never judged. Cheapest path: (a) keep the bare title for `onTopic` / `termCoverage` (prefix only in the rendered label) → removes mechanism 1; (b) decide the topic-source title-lookup rule explicitly (it is a retrieval change: +7 fact chunks, factbook 5 → 12 articles) and replay again; then a judged re-score of the 180 (Haiku L1, Opus if near a threshold) before PR 1 cites any quality statement. Until then the published pack cards' numbers describe the OFF behaviour.

**Files:** tools/{replay-tk2.ts (groundst replay-gs.ts + prompt capture), replay-tk2.sh, run_tk2.sh, compare_tk2.py}; aggregates/compare.json; runs/st-<pack>.{off,on}.jsonl ×18, v01-kit.{off,on}.jsonl, diff-items.jsonl, st180-offon-items.jsonl, run.log. Trees: kiln-local/be-0cfd4a77-cut7-tk2off (OFF) and -tk2 (ON), 17 MB each, node_modules symlinked to cut 7. MacBook free 7.8 GiB at the end (replay caches of this run removed).
