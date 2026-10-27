# boar-nist-crypto (NIST cryptography standards)
TL;DR: 1.76 MB format-2 pack of six NIST publications split by section, plus a cryptography subset of the CSRC Glossary. All text is US public domain ("Source: NIST"). It is **user-selected only**, not in the claim kit. On the 4B it is shadowed by boar-crypto: self-test score +0.008 vs no pack, inside the noise. Built 2026-10-19 (PACK-NIST arm).

## What it is
| field | value |
|---|---|
| id / file | `boar-nist-crypto` / `shared-data/packs/wave4/boar-nist-crypto.sqlite` (mini: `<runner>/shared-data/packs/wave4/`) |
| sha256 | `e45b16d546f7ca7905547fcb95930cb348d9a953abf9ebe8cfbde9cf8b5df81a` |
| size | 1,761,280 B |
| articles / chunks | 521 / 1,619 (all indexed); 230 alias redirects (glossary abbreviations) |
| format | formatVersion 2, dims 384, bge-small-en-v1.5 q8_0 lead vectors (embedding sha ec38e8da…), params leadChars 2500 / chunkChars 1000 |
| source code | `usgov` (the app labels it "US government") |
| page_id range | 16e9 + doc# × 1e6 + seq; glossary 16.009e9 (own docs) / 16.0095e9 (grouped) |

## Sources (fetched 2026-10-19; input sha256 in `build/inputs.SHA256SUMS`)
| document | date | docs in pack |
|---|---|---|
| FIPS 203 ML-KEM | 2024-08-13 | 31 |
| FIPS 204 ML-DSA | 2024-08-13 | 39 |
| FIPS 205 SLH-DSA | 2024-08-13 | 42 |
| FIPS 186-5 DSS (RSA, ECDSA, EdDSA) | 2023-02-03 | 48 |
| NIST SP 800-208 (LMS, HSS, XMSS) | 2020-10 | 44 |
| NIST IR 8547 **initial public draft** (PQC transition) | 2024-11-12 | 12 |
| CSRC Glossary export, crypto subset | 2026-10-19 | 271 own-entry docs + 34 grouped docs (625 of 9,140 terms) |

- The IR 8547 titles carry "(Initial Public Draft)", and its body text says "(draft)". It is a draft, not a final rule.
- **Glossary filter.** Only definitions are kept whose cited source is a NIST crypto publication: FIPS, SP 800-38/56/57/67/71/90/106/107/108/131/132/133/135/152/175/185/186/208/227/232, or IR 8547/8105/8413. Definitions sourced from CNSSI, ISO, IETF and other non-NIST documents are dropped.

## Licence
- Public domain in the US: works by NIST employees are not subject to US copyright. NIST grants a royalty-free worldwide licence for foreign reprint and derivative works.
- Credit line: "Source: NIST" / "Republished courtesy of the National Institute of Standards and Technology".
- The statements, verified on nist.gov on 2026-10-19, are quoted in `shared-data/packs/wave4/boar-nist-crypto.LICENSE.txt`.
- Every row carries `license` and `attribution`: "Source: NIST. <doc>, <date>; <doi>".

## Build
```fish
# MacBook (pdftotext/qpdf), converter = arms/pack-nist/tools/nist_to_jsonl.py
cd <workspace>/shared-data/packs/work/nist
python3 -I <workspace>/rnd/research/coordinator/arms/pack-nist/tools/nist_to_jsonl.py raw conv
node <workspace>/rnd/kiln/packs/convert/validate.mjs conv
# mini: arms/pack-nist/build/mini-build.sh (= kiln/packs/scripts/build.sh, Metal lead embeddings, 3 s)
```
- **Sectioning** comes from each PDF's outline (`qpdf --json` outlines).
  - Numbered depth ≤ 2, plus Appendix X and Abstract, each open a doc ("FIPS 204 — 3.4 Hedged and Deterministic Signing"). Deeper entries become `##` headings.
  - Dropped: front matter, Contents, Lists, References, Index.
  - Removed: running headers, page numbers and the draft's line numbers.
  - Layout columns become " · ".

## Measured (dev, public; details in arms/pack-nist/PACK-NIST.md)
- **Self-test** (20 public items, cut 7 4B, Haiku 5.5-low, N = 4, both orders):
  - with the pack: 0.430 raw
  - without: 0.422
  - Δ +0.008 (−0.012…+0.030), better/worse 5/4, win 0/20
  - Pack passages were kept on 3/20 items; the fact article on 1/20.
- **Crowding (v0.1 public 60, deep replay k 6).** Share of kept slots 0.000 (0/111), gold unchanged (res raw6 16, kept 14). It passes by absence.
  - v0.2 was not run, because its replays read blind/.
  - Status: user-selected only.
- **V-exact vx-002.**
  - String check: every rubric fact is in the pack (ML-DSA 41 docs, SLH-DSA 44, XMSS 72, LMS 52, the IR 8547 quantum-vulnerable table 1, Falcon 1).
  - Retrieval as a peer pack: 0 NIST passages in the pool of 20.

## Known gaps
- Tables, formulas and pseudocode come out of pdftotext approximately; math glyphs are sometimes doubled (𝐻𝐻).
- A few section docs start with the tail of a wrapped heading ("lic Draft").
- FIPS 206 (FN-DSA / Falcon) is not public as a final standard; only IR 8547 mentions Falcon.
- The IR 8547 final version was not found on CSRC (2026-10-19); the pack holds the ipd.
- As a peer pack, boar-crypto (Wikipedia ML-KEM/SPHINCS+/PQC articles) outranks it on crypto questions. Re-cutting it into boar-crypto is the measured way to reach those questions (PACK-NIST §Re-cut).
