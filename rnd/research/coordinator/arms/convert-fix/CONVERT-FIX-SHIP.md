# CONVERT-FIX-SHIP (2026-10-21): simplewiki r2 published, Wikivoyage rebuilt but not published

TL;DR: 0 LLM, 0 judge, 0 Opus, 0 paid, no git push. **boar-simplewiki-en r2 (sha e14bdff1, 481,017,856 B) published** at `topics/boar-simplewiki-en/r2/` on hf.co/datasets/r4topunk/boar-packs (commit d4ff5720); r1 files (c751768b, commit 9e51caf6) untouched. Wikivoyage convert-fix rebuild (sha 34130f66) passes parity but is **not published**: no D-K3 self-test/coverage/crowding artefacts, no hub folder, and the convert-only patch removes only 9 % of its artefacts.

## 1. Parity replay, simplewiki (0 LLM; `replay-retrieval.sh`, tree kiln-local/be-0cfd4a77-cut7-litepacks, `--tasks-from` LITEPACKS K3 traces)
Kit = K3 (crypto ae9fbd2c, wikivoyage ff8595e3, factbook/medlineplus/firstaid v3proto) + simplewiki A = published c751768b / B = candidate e14bdff1. Items: 280 = v0.1 60 + cm 40 (MAIN 97 incl. v0.1 57) + 180 pack self-tests. Run A = K3 reference traces 279/280 (the 1 diff is cooking-se-002, a places-route item, not pack-related).
| measure | A -> B |
|---|---|
| kept sources changed | **1/280**: lan-cmp-003 ("bigger than India"): Tripura (changed article) enters, one duplicate "Wikivoyage: India" leaves; gold in neither |
| raw lists changed | 8/280; 5 involve a changed article (lan-rsn-003 Cheetah, lan-cmp-003 Tripura, cooking-se-013 Tay Bridge disaster, outdoors-se-016 Lepidodendron, firstaid-019 2010 Haiti earthquake) |
| raw changes with no changed article (finding) | 3: lan-cmp-004, ethereum-se-010 (order-only swaps of unchanged articles), firstaid-011 (unchanged "Dirty Work" album replaces "Radiation Emergencies" in raw slot 4). Cause: corpus-wide FTS/df statistics shift; none reaches kept |
| raw recall@5 vs v0.1 gold | 13/39 -> 12/39: lan-rsn-003 loses Cheetah from raw slot 4 (not kept in A or B, so the answer context is unchanged) |
| kept slots from simplewiki | 160/336 -> 161/336 (0.476 -> 0.479); claim kit + pack on v0.1: 37/91 -> 38/91 |
| items whose kept simplewiki article changed text | 9/280: lan-rsn-001, lan-cmp-003, lan-exp-003, lan-exp-005, lan-cmp-005, travel-se-019, factbook-019/020, simplewiki-005 |
- **C1/FACTPRESENT items:** lan-rsn-001 keeps "Great Wall of China" in A and B; the lead chunk that sits in context [1] (K1 prompt dump) now reads "In total, the wall stretches 21196.18 km." (was "stretches ."). The other 9 FACTPRESENT real items (lan-hlt-002/003/001, lan-exp-003, vit-trv-003, vit-hum-004, lan-ref-002/003, lan-rsn-004): raw and kept identical. vit-hum-004 unchanged (motive absent from the pack, as C1 says).
- Chunk-level kept passages are not replayed (article titles only); packHeadPass/X2b act after retrieve() and are not replayed.

## 2. Self-test / card clauses (0 LLM)
- simplewiki self-tests (20): raw and kept identical 20/20; source article kept 12/20 (A) = 12/20 (B) = card; pack passage in raw 18/18; in_pack_facts quotes found verbatim 17/20 in both (3 pre-existing misses: 018, 019, 020; no new miss). 1/20 (005, keeps "Chile") holds a changed article: its Haiku score was not re-run (0 judge rule), card says so.
- Publish-script checks: size/sha vs manifest, card carries sha + size, 20 self-test lines, leak regex: all pass. Crowding flag unchanged (user-selected only; slot share +0.003).
- Coverage probe (jev) not re-run: paid, and content change is numbers only.

## 3. Wikivoyage rebuild (mini, `ship/wvcf-build.sh`, pass 1 + embed-only pass 2 with builder-cf lib md5 cd17fa24)
- Wall ≈ 3.3 min (pass 2 138 s); disk 26 GiB before and after (floor 25). 351,133,696 B (+40,960 B, +0.01 %), sha256 34130f664c2c87e518ca6b61a465b9a8233d9200b130a478eb7b4882d40aa321; 34,002 articles, 548,035 chunks (-16), format 2, dims 384, emb ec38e8da, integrity ok, lead_vecs 34,002.
- Artefact chunks 877 -> **801** (-9 %), broad 2,180 -> 2,024. Wikivoyage uses unit templates the convert-only patch leaves dropped; the WIKIVOYAGE-REBUILD v2 whitelist candidate (080408a9) is the better Wikivoyage ship.
- Parity (K3, simplewiki A): raw and kept identical **280/280**; 900 articles changed text.
- Verdict: not published (D-K3 b-d artefacts missing; pinned ff8595e3 in shipped/device-day kits; nothing swapped).

## 4. Publish
- `rnd/kiln/packs/publish_pack.py` gained `--subdir` (new revision folder; refuses to overwrite existing hub paths), `--pack-dir`, `--release-note`. Command: `publish_pack.py boar-simplewiki-en --subdir r2 --pack-dir shared-data/packs/candidates/boar-simplewiki-en-convfix --release-note "..." --go`.
- Hub after upload: r1 files at `topics/boar-simplewiki-en/` (sqlite LFS sha c751768b, commit 9e51caf6) unchanged; r2 files at `.../r2/` (LFS sha e14bdff1, commit d4ff5720). Root README not changed.
- Card `research/packs/boar-simplewiki-en.md` updated (r2 sha/size/counts, revision section, Published line); `boar-wikivoyage-en.md` gained a rebuild note.

## 5. Files (`ship/`)
replay-{A,B,WV}.jsonl (K3), replay-claimkit-v01-{A,B}.jsonl, parity-*.json, simplewiki-changed-titles.json (8,073 changed titles), scan-wikivoyage-convfix.json, ship_compare.py, wvcf-build.sh. Requests/traces = `cat arms/litepacks/runs/req/lp-K3-{v01,cm,st}-s42.requests.jsonl` and `arms/litepacks/traces/lp-K3-{v01,cm,st}-s42.traces.jsonl`.

## UNKNOWN
- Answer-level effect (judge) of r2: not measured; at most 9/280 dev items can move (kept article text changed).
- Whether the 3 corpus-statistics rank shifts matter on the phone engine (simplewiki is not in A-union).
