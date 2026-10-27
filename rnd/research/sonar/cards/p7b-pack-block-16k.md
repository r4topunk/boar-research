# P-7b: 16 KB zstd blocks at the packs' existing 8 KB SQLite pages: half the JS decompression for +18 MB
TL;DR: P-7 (8 KB blocks) passed its byte-identity pre-check but failed its size bar (+9.8% / +9.5%). A local simulation reproduces Kiln's numbers exactly (3,531 → 15,015 blocks; table 113.1 → 147.7 MB). It shows the slack comes from ~7.8 KB compressed blobs each spilling into a second **8 KB** page; the packs already use 8 KB pages, not 4 KB. With **16 KB blocks** at the same page size, JIT-off `fzstd` work on the engine's real reads drops **−50%** (p50 555 → 280 ms per question on an M1), for **+16.3 MB on Wikivoyage (+4.6%) and +1.9 MB on crypto (+5.3%)**. Text stays byte-identical.
Lane: Sonar (retrieval latency; F2) · Status: ready-to-test, **criterion frozen 2026-10-02 (late night), before any build** · Priority: A
Axes moved:
- latency ↓: predicted moto retrieval 3.2 s → ~2.1–2.5 s (0.65–0.8×), assuming the phone runs `fzstd` 2.5–4× slower than the JIT-less M1 (UNKNOWN; the run measures it);
- storage +18 MB;
- quality/safety unchanged by construction (pre-check 0).
Fits BOAR? The same rebuild as P-7 with `--block-kb 16`; no code change; page size unchanged (the builder sets `PRAGMA page_size = 8192`).

Evidence (`exp/23-device-retrieval-profile/`: `sim7b.mjs` / `sim7b-cr.mjs` → `sim7b*.txt`, `time7b.mjs` → `time7b.txt`):
- **Method:**
  - the builder's exact flush rule (`scripts/build-wiki-pack.mjs`: an article is appended, then the block is flushed once `blockLen ≥ blockKb·1024`; zstd level 12);
  - applied to every article of the current packs, in id order;
  - blobs stored in a `blocks` table at page sizes 4/8/16/64 KB;
  - decompression timed on the **article ids the engine actually reads** (`reads-wv.json`, `reads-cr.json`: 60 public v0.1 questions, cold cache per question, both packs).
- **Fidelity:**
  - 64 KB reproduces the current packs exactly (Wikivoyage 3,531 blocks, 108.8 MB, table 113.1 MB; crypto 407 blocks, 9.56 MB);
  - 8 KB reproduces Kiln's build (15,015 blocks, 117.1 MB of data, table 147.7 MB; crypto +3.4 MB = +9.4%).
- **Results** (table growth at today's 8 KB pages = file growth; FTS, chunks and lead vectors unchanged):

  | blockKb | MB decompressed / question (wv + cr) | fzstd JIT-off p50 / p90 per question | Wikivoyage | crypto | total |
  |---|---|---|---|---|---|
  | 64 (now) | 1.38 + 2.88 | 555 / 1151 ms | — | — | — |
  | 32 | 0.88 + 1.76 | 380 / 809 ms (−32%) | +8.9 MB (+2.5%) | +0.9 MB (+2.5%) | +9.8 MB |
  | **16** | **0.59 + 1.23** | **280 / 618 ms (−50%)** | **+16.3 MB (+4.6%)** | **+1.9 MB (+5.3%)** | **+18.2 MB** |
  | 8 (P-7, built) | 0.46 + 0.97 | 212 / 510 ms (−62%) | +34.6 MB (+9.9%) | +3.4 MB (+9.4%) | +38 MB |

- **Not chosen:**
  - (a) 8 KB blocks + 16 KB pages: the table is *larger* (145.6 MB), because blobs still straddle pages.
  - 8 KB blocks + **4 KB** pages: the table is only +13.9 MB, but `page_size` is per database. It would also re-page the FTS index and every other table, an effect on size and query I/O this simulation doesn't cover. Not proposed without an FTS measurement.
  - 64 KB pages: wasteful for the FTS random reads.
- **Correction to the step-0 note:** the packs use 8 KB pages (`PRAGMA page_size` = 8192 on both); the slack is 7.8 KB blobs overflowing 8 KB pages.

**Size bar, re-justified for this card** (not retroactive to P-7): **≤ +6% per pack and ≤ +25 MB combined.**
- Storage is the cheapest axis on the target phones: +25 MB is 0.05% of the 50 GB storage budget and ~6% of the 387 MB kit.
- The download cost is seconds on Wi-Fi.
- The 5% bar in P-7 was a round number, not a constraint; 16 KB is predicted at +4.6% / +5.3% (+18.2 MB).

Frozen criterion (arm `p7b-blk16` = `boar-wikivoyage-en` + `boar-crypto` rebuilt with `--block-kb 16`, same recipes as P-7; vs the current packs; engine 0cfd4a77):
0. Desktop pre-check (as in P-7): the 72 items' pre-answer sources (title, section, source, similarity, passage text), `retrieval.raw` and answer text are **byte-identical** to base. Any difference → stop.
1. **Moto g75 retrieval p50 ≤ 0.8× base** on answered items (base = P1 r1/r2, 3.1–3.3 s; 1.5B, airplane mode, 2 reps, same protocol). Predicted 0.65–0.8×.
2. TTFT p50 reported; 0 BOAR kills; 0 errors.
3. Pack size: **≤ +6% per pack and ≤ +25 MB combined** (predicted +4.6% / +5.3%, +18.2 MB).
- If 1 fails with 0 and 3 passing → the measured residual says how much of the 3.2 s is SQL bridge calls; plan B (native byte-returning zstd) then needs its own card.
