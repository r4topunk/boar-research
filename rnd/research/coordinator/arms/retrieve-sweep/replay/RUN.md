# RETRIEVE-SWEEP stage 1 replays (2026-10-21/22, MacBook, 0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone)

Base tree: <workspace>/kiln-local/be-0cfd4a77-cut7-litepacks (answer.ts 0d1ac07d..., not edited). One APFS clone per arm
(`cp -c -R`) under kiln-local/rs-<arm>, patch applied there; each arm is an env switch, unset = byte-identical baseline.
| arm | clone | env switch | patch (patches/) sha256 | patched files (sha256 prefix in the clone) |
|---|---|---|---|---|
| A GROUND-DENSE | rs-A | RS_GROUND_DENSE=0.78 / 0.74 | A.patch 61a9447e7a79966f | answer.ts 7a16afbb09f8 |
| B KEYQ | rs-B | RS_KEYQ=1 | B.patch d80aa5ad556099a9 | retrieve.ts d85d5f06d652 |
| C SIBLING | rs-C | RS_SIBLING=1 (+ K1 settings) | C.patch 408a637381e66e6a | answer.ts 580a1fd4f299, wikiPack.ts f26f67327411, packs.ts 252df4ae5a19 |
| D DIVERSITY | rs-D | RS_DIVERSITY=1 | D.patch 8a15c4f921217ce9 | retrieve.ts 40fbaa742f41, wikiPack.ts cc1fe25a077e |
| E MINSIM | rs-E | RS_MINSIM=0.62 | E.patch ec90690c56f523aa | retrieve.ts 8e16335eaeed |
| F COMBO (exploratory A74+B) | rs-F | RS_GROUND_DENSE=0.74 RS_KEYQ=1 | F.patch a85df22826648efd (= A + B) | answer.ts 7a16afbb09f8, retrieve.ts d85d5f06d652 |

Switch-off identity (tools/proofdiff.py, 20 QFORM items seeded 11 = replay/proof20.questions.jsonl, vs B0; C vs B1): raw/wide/kept chunk ids and
reason codes identical 20/20 for A, B, C, D, E, F (replay/*.off20.jsonl). Determinism: B0w vs the QFORM B0 replay 432/432, B1w vs the QFORM K1 replay
432/432, C rerun (wall tool) vs first C run 432/432.

Tool: tools/replay-sweep.ts (sha256 da1978bf2075c255) = arms/qform/tools/replay-qform.ts + two SWEEP-marked additions: per-item `wallMs`
(answer() up to the stubbed generation, minus the extra wide-12 retrieve) and the LITEPACKS adapter's catalog entry for qwen3-1.7b-q4km
(not in the tree's catalog; same entry be/adapter-lite5.ts supplies).
Driver: tools/replay.sh (sets) + tools/run_all.sh (all runs, sequential so wall times are comparable). Log: replay/run_all.log.
```
cd <workspace>/rnd/research/coordinator/arms/retrieve-sweep
tools/run_all.sh base A B D E C            # B0w/B1w QFORM (wall), A0.78/A0.74, B, D, E, C on QFORM + MAIN (~45 min; C ~20 min)
tools/replay.sh <base tree> ../decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl replay/B0.main.jsonl main
FENV="RS_GROUND_DENSE=0.74 RS_KEYQ=1" FARGS="" tools/run_all.sh F
python3 -I tools/sweep.py                  # -> aggregates/sweep.{json,md}
```
Sets.
- QFORM 432: ../qform/items/qform.questions.jsonl, merged A-union pack (boar-aunion-merged.sqlite 7e86674b), gate search, lexical detector,
  `--wide 12`; stock settings except C (`--forward-opts --settings-json {"packHeadPass":"a2","packDense2":"append-budget"}`). B0/B1 = the
  existing QFORM replays (not rerun for hits; rerun only for wall as B0w/B1w).
- MAIN 97: ../decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl (item.question), K1 kit = shared-data/crypto/boar-crypto.sqlite (ae9fbd2c),
  shared-data/packs/boar-wikivoyage-en.sqlite (ff8595e3), shared-data/packs/v3proto/boar-simplewiki-en.sqlite (99bcec30, has chunk_vecs), K1
  settings for every arm, model entry qwen3-1.7b-q4km, ram 12 GB, gate + detector score from the funnel's K1 traces (replay/funnel-K1.traces.jsonl =
  RAG-FUNNEL job out/K1-V01 + K1-CM). All on the MacBook (no mini needed). Parity of the switch-off replay vs those traces: raw titles 97/97,
  kept titles 91/97; FACTPRESENT on its kept list: S2/S3 present 0/25, S4/S5 present 22/22 (= funnel labels).
Implementation notes. The merged A-union pack has no chunk_vecs and pack hits carry no similarity, so A and C embed chunk text on the fly
(bge-small, "title\nbody" cut at 1500 chars; same embedder as the query); with a sidecar (simplewiki on MAIN) C uses the int8 chunk vectors.
C reads at most 60 chunks per article, siblings of the first two pack articles among the grounded sources, budget = the compression token
budget minus the grounded sources' tokens. D's family = title past its library label, up to the first " — " or ":" (so "ATP 4-02.11"); applied in
WikiPack's keyword loop (backfilled by the next candidate) and on both fusion input lists. E changes only gateByRelevance on the dense list
(bundled corpus + format-1 packs); format-2 pack hits are never gated by it. Diagnostic: replay/Adiag0.qform.jsonl = A with tau 0.0001 (no keep
filter) = the keep-step ceiling.
