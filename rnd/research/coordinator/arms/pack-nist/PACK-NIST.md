# PACK-NIST: NIST cryptography standards pack (2026-10-19, track pack-nist)

TL;DR
- **Pack.** `boar-nist-crypto`: 1,761,280 B, sha256 `e45b16d5…5df81a`, 521 docs and 1,619 chunks.
  - Contents: FIPS 203/204/205/186-5, SP 800-208, IR 8547 ipd (sections), plus a CSRC Glossary crypto subset (625 terms).
  - Licence: US public domain, "Source: NIST".
  - Location: `shared-data/packs/wave4/`, with its card, LICENSE and sha256 file.
- **Self-test** (20 public agent-written items, cut 7 4B, Haiku 5.5-low N = 4, both orders, 120 calls):
  - with the pack 0.430 raw vs without 0.422; **Δ +0.008 (−0.012…+0.030)**; win 0/20.
  - Pack passages kept on 3/20 items.
- **Crowding** (frozen D-K3d rule; run on v0.1 public only): share 0.000 (0/111 kept slots), gold not lower → passes by absence.
  - The v0.2 half was not run (it reads blind/).
  - **Verdict: user-selected only**, as a separate pack. It is not a re-cut of the kit's boar-crypto (reasons below).
- **V-exact vx-002.** The string check finds every rubric fact in the pack. As a peer pack it never reaches vx-002's retrieval pool. A re-cut into boar-crypto (measurement build, not shipped) puts NIST IR 8547 §3.1 into kept.
- **Re-cut measurement:**
  - on the self-tests, the fact article is kept on 1/20 items as a peer vs 7/20 in the re-cut;
  - the judged score does not follow: re-cut 0.418 vs no pack 0.422, Δ −0.004 (−0.079…+0.059);
  - this matches the earlier finding that the 4B is reading-bound.
- Cost: 0 paid API, 120 Haiku calls, about 9.4 MB downloaded, mini disk +about 120 MB (inside the 1 GiB budget).
- Port 8196 was used and stopped; 8191, 8094, Docker and ollama were not touched.

## 1. Sources and licence check
| doc | URL (doi) | PDF bytes | sha256 (first 12) |
|---|---|---|---|
| FIPS 203 | 10.6028/NIST.FIPS.203 | 1,252,341 | fe1f12f32a7e |
| FIPS 204 | 10.6028/NIST.FIPS.204 | 3,291,746 | 57239b9f84c0 |
| FIPS 205 | 10.6028/NIST.FIPS.205 | 1,055,752 | 8ef34228276f |
| FIPS 186-5 | 10.6028/NIST.FIPS.186-5 | 1,844,414 | fbb9c7c2ba44 |
| SP 800-208 | 10.6028/NIST.SP.800-208 | 872,986 | 9ac6bee3da87 |
| IR 8547 ipd | 10.6028/NIST.IR.8547.ipd | 722,379 | 6b551b4ff985 |
| CSRC glossary-export.zip | csrc.nist.gov/csrc/media/glossary/glossary-export.zip | 759,283 | 3e7b3fbe4dc8 |

**Public-domain statement (read on nist.gov on 2026-10-19).**
- Source page: "Copyright, Fair Use, and Licensing Statements for SRD, Data, Software, and Technical Series Publications".
- It says: "Works authored by NIST employees are not subject to Copyright protection within the United States; foreign rights are reserved."
- It grants a "non-exclusive, perpetual, paid-up, royalty-free, worldwide right to reprint works in all formats … and derivative works".
- Requested credit: "Republished courtesy of the National Institute of Standards and Technology."
- nist.gov/oism/copyrights adds: "information presented on NIST sites are considered public information and may be distributed or copied".

The glossary file's own comment credits the CSRC Glossary (NISTIR 7298 Rev. 3). Definitions sourced from non-NIST documents (CNSSI, ISO, IETF, …) were dropped, so no third-party text is carried. The full statement is in `shared-data/packs/wave4/boar-nist-crypto.LICENSE.txt`.

## 2. Build
| step | what | numbers |
|---|---|---|
| download (mini) | `build/mini-download.sh`, curl | 7 files, 9.4 MB; HTTP 200 for all (a HEAD request for FIPS 203 returned 404, the GET worked) |
| text (MacBook) | `pdftotext -layout` (poppler; the mini has no pdftotext) | 6 PDFs → 1.29 MB of text |
| sectioning | `tools/nist_to_jsonl.py`; sections come from the PDF outline (`qpdf --json`) because the T-K1 `convert.mjs pdf` splitter keys on Army "Chapter N" layout | 340 outline entries, 324 headings located on their page; 216 section docs + 305 glossary docs = 521 rows; validate.mjs 0 errors |
| build (mini) | `kiln/packs/scripts/build.sh` (Metal lead embeddings) | 3 s; 521 articles, 1,619 chunks (100 % indexed), 230 redirects |
| install | `shared-data/packs/wave4/` on the mini and the MacBook | sha `e45b16d546f7ca7905547fcb95930cb348d9a953abf9ebe8cfbde9cf8b5df81a` (`.sha256` file next to it) |

## 3. Self-test (D-K3b)
- Draw (`tools/selftest_draw.py`, seed 11, copy patched with a pack-specific stratum):
  - strata: document family × length tercile; 206 eligible articles, 21 cells, 60 candidates;
  - 20 picked for breadth: ML-DSA ×3, ML-KEM ×2, SLH-DSA ×2, SP 800-208 ×3, FIPS 186-5 ×3, IR 8547 ×5, glossary ×2;
  - 40 rejects with a one-word reason in `selftest/draw-boar-nist-crypto.json`. Most rejects are pseudocode or math internals.
- Items: `selftest/boar-nist-crypto.jsonl`.
  - Checks (`tools/selftest_check.py`) PASS: 20/20, 0 failures, 17 with a fact at chunk ≥ 1, styles 7/7/6.
  - Bench dir: `boar-eval/bench/selftest/boar-nist-crypto/` (boar-eval repo, not committed here).
- Generation:
  - cut 7 tree `kiln-local/be-0cfd4a77-cut7` (patch 0fba26b8, adapter 6298e5d3), 4B Q4_K_M;
  - the llama-server ran on **:8196** with the adapter's exact spawn args, passed through `--server-url` (`tools/run_selftest_8196.sh`);
  - MacBook detector :8094 used read-only; 0 errors in 60 generations.
- Judge: Haiku 5.5-low via `deepthink/tools/shard_judge.sh`, N = 4, both orders, 40 rows per run (all ok).
- Paired Δ (`tools/paired_delta.py`): per-item bootstrap, B 2000, seed 11, the same method as SELFTEST-SCORES.

| run | kit | raw | above_min | pack passage kept (items) | fact article kept / in raw | p50 s |
|---|---|---|---|---|---|---|
| nopack | crypto + wikivoyage | 0.422 | 0.264 | 0 | 0 / 0 | 41.5 |
| **peer (shipped pack)** | + boar-nist-crypto | **0.430** | 0.273 | 3 | 1 / 1 | 22.3 |
| re-cut B (measurement only) | boar-crypto + NIST rows, wikivoyage | 0.418 | 0.258 | 11 | 7 / 9 | 32.0 |

| comparison | Δ raw (95 % CI) | Δ above_min | better / worse |
|---|---|---|---|
| peer − nopack | +0.008 (−0.012…+0.030) | +0.009 (−0.014…+0.036) | 5 / 4 |
| re-cut − nopack | −0.004 (−0.079…+0.059) | −0.007 (−0.101…+0.073) | 7 / 6 |
| re-cut − peer | −0.012 (−0.085…+0.050) | −0.016 | 6 / 8 |

How to read these runs:
- Win vs gold is 0/20 in all three runs.
- p50 times are not comparable: the runs shared the MacBook with other sessions (load average up to 24).
- The self-test number is a dev number with agent-written gold, and comes from one seed.

## 4. Crowding (D-K3d) and the re-cut decision
- Probe: `tools/crowding_agg_nist.py` (a copy of `packs/tools/crowding_agg.py`, restricted to v0.1).
  - Replay: deep retrieval replay `replay-crowd.sh --deep --gate rules --k 6 --pool 20 --tree wt/packs`, claim kit vs claim kit + the pack, v0.1 public (60).
  - Output: `aggregates/crowding-nist-v01.json`.
- v0.1 result: share of kept slots 0.000 (0/111); raw top-6 share 0.058; resolvable gold raw6 16 → 16, kept 14 → 14; 0 items lower; 0 kept lists changed. **PASS** on v0.1, by absence.
- v0.2 half: not run. Its replay reads `blind/bench-v02/…`, which this track may not touch, so the frozen two-set rule is incomplete.
- Pool: the pack's passages reach raw on 7 v0.1 items. All 7 are off-topic (humanities and health items), and the gate drops all of them.
- **Why the pack is invisible as a peer.**
  - `retrieve.ts` fuses each pack's own BM25 hits.
  - On crypto questions boar-crypto's Wikipedia/EIP articles (ML-KEM, SPHINCS+, EIP-8051 ML-DSA precompile, …) fill the slots.
  - So the NIST pack reaches raw on only 6/20 of its own self-test items in the fast tier, and 11/20 in deep.
- **Re-cut measurement.** Two builds from the boar-crypto JSONL shards, without the Wikipedia redirect dump, so neither is the published file:
  - A = crypto only (sha 4a038552…); B = crypto + the 521 NIST rows (sha bd7f3981…, 36.8 MB).
  - v0.1 replay: gold identical (16/14 → 16/14); 1 kept list reordered (vit-cry-007, same three titles).
  - V-exact: vx-002 kept changes from [PQC, Quantum cryptography, PQC, NSA cryptography] to [PQC, Quantum cryptography, PQC, **NIST IR 8547 §3.1 Use Cases**].
  - Self-test reach: fact article kept 1 → 7/20.
- **Decision (conservative; reversible): ship as a separate user-selected pack, not a re-cut.** Reasons:
  - (1) The claim kit is frozen at cut 7, and a re-cut changes boar-crypto's sha (D-G2).
  - (2) A re-cut needs the v0.2 kit no-harm replay, which reads blind/ and so is coordinator-only.
  - (3) The judged gain from the re-cut is 0 on the 4B (−0.004), so nothing measured justifies touching the kit before 10-23.
  - The re-cut stays the **only measured path that puts NIST text in front of vx-002**. Do it post-claim, together with the O-G1 kit no-harm replay.

## 5. V-exact (public, string check only)
- Target: **vx-002** "Which signature algorithms are quantum resistant?" Its rubric names FIPS 204/205, SP 800-208, Falcon/FN-DSA, and says RSA/ECDSA are not quantum resistant.
- String check (`tools/vexact_strings.py` → `aggregates/vexact-vx002-strings.json`), counts are docs in the pack:

| needle | docs |
|---|---|
| ML-DSA | 41 |
| CRYSTALS-Dilithium | 4 |
| SLH-DSA | 44 |
| SPHINCS+ | 5 |
| XMSS | 72 |
| LMS | 52 |
| hash-based | 89 |
| lattice-based | 72 |
| "Quantum-vulnerable digital signature algorithms" table (IR 8547 §4.1: ECDSA/EdDSA/RSA deprecated after 2030, disallowed after 2035) | 1 |
| Falcon | 1 (IR 8547 §2.1) |
| Shor | 1 |

- **The needed passages are in the pack.**
- Retrieval:
  - peer pack: 0 NIST passages in vx-002's pool of 20;
  - re-cut: IR 8547 §3.1 kept, with §4.1 (the table) at pool rank 6.
- V-exact retrieval replays: `replay/vx-{base,nist,recutA,recutB}.jsonl`.

## 6. Deviations
- **v0.2 crowding not run.** Its replays read blind/, which this track is barred from, so the crowding verdict rests on v0.1 public only. Status is therefore user-selected only, which D-G2 requires before the claim anyway.
- **No V-para coverage probe (D-K3c).** It needs blind V-para and paid jev, both out of scope for this track.
- **Self-tests ran on the MacBook,** as waves 1–3 did, with my own llama-server on :8196 through `--server-url`. The adapter otherwise picks a random port. The mini was busy with CHAINWHEN (4 threads on :8191).
- **Tool copies are arm-local** (`tools/selftest_*.py`, `crowding_agg_nist.py`): wave4 pack dir, OUT_DIR = this arm, a nist stratum. `selftest_agg.py` also strips the "US government: " label, because without that it reported 0 pack passages kept. The shared `arms/packs/tools` and `rnd/research/packs/` were not modified. The self-test items live in `arms/pack-nist/selftest/`, not `rnd/research/packs/selftest/`, and the card is `arms/pack-nist/boar-nist-crypto.card.md` (copy next to the pack), not `rnd/research/packs/`.
- **New PDF splitter (outline-based).** The T-K1 `convert.mjs pdf` path is tuned to Army manuals ("Chapter N"), so `pdftotext` is reused but sections come from the PDF outline.
- **IR 8547 is the initial public draft.** No final version is listed on CSRC as of 2026-10-19, and the titles say so.
- **Re-cut builds lack the Wikipedia redirect dump.** A/B were compared with each other, and the re-cut self-test run was compared with the published-kit runs.
- p50 latencies are confounded by host load.

## 7. Files
- `tools/`: nist_to_jsonl.py, run_selftest_8196.sh, selftest_* copies, crowding_agg_nist.py, paired_delta.py, vexact_strings.py
- `build/`: mini-download.sh, mini-build.sh, mini-recut-build.sh, convert-info.json, manifest.json, inputs.SHA256SUMS, boar-nist-crypto.sqlite.json
- `selftest/`: boar-nist-crypto.jsonl, draw-boar-nist-crypto.json, draft-boar-nist-crypto.{py,jsonl}
- `runs/`: requests, traces, judgments, ids, status and logs for nopack / peer / recutB
- `replay/`: crowding and reach replays (v0.1, V-exact, self-test)
- `aggregates/`: gen checks, floor_metrics, delta-*.json, crowding-nist-v01.json, selftest-reach-replay.json, vexact-vx002-strings.json
- Pack: `shared-data/packs/wave4/boar-nist-crypto.{sqlite,sqlite.json,sqlite.sha256,LICENSE.txt,card.md}`
- Re-cut builds (measurement only, not for install): `shared-data/packs/work/nist/recut/{A,B}/boar-crypto.sqlite`

## UNKNOWN
- Whether the pack crowds or helps on v0.2 (blind; the coordinator can run `crowding.sh` with the wave4 label).
- Whether a deep-tier reader (35B) uses the NIST passages the re-cut reaches. The 4B does not.
- Whether a NIST-specific routing hint (for queries naming FIPS/NIST/"quantum resistant") would beat a re-cut. Not tried.
