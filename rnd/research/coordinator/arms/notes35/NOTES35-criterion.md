# NOTES35: does a pack of encyclopedic notes written offline by the 35B raise the 4B claim build? (frozen 2026-10-10 23:4x, coordinator)

## Tags
Tags: none

## Question
The deep tier's gain over the 4B is 84 % on items with no usable gold: the 35B knows things the curated kit (crypto + Wikivoyage) lacks. NOTES35 writes that knowledge down offline: the 35B (Qwen3.6-35B-A3B UD-Q2_K_XL via llama-server on the mini, thinking off, temp 0.3) writes one 150–250-word encyclopedic note per topic from the Wikipedia Vital Articles Level-3 list (≈ 1,000 topics, breadth-first order over sections; topics never come from bench items), the notes become a format-compatible knowledge pack (`boar-notes35`, bge-small embeddings, format 2 via the claim tree's own `scripts/build-wiki-pack.mjs`; notes are stored as source 0 (Wikipedia) because the engine has no "notes35" source code, so the 4B will cite them as Wikipedia — a research caveat, a shipping version needs a source label; notes carry a `notes35.boar.invalid` URL for identification) added to the 4B cut 7 kit. Arm **N** = cut 7 + notes pack; control **C** = same-backend single-pass 4B (v0.2 Haiku rows, 110 ids) at L1, **K** = cut 6 claim rows (Opus) at L2. Reopen: the 4B side is closed for model, prompt, retrieval ranking and corpus size (DEEPWIKI-class packs crowd slots); NOTES35 is a new mechanism (knowledge transfer from the deep model into the kit, item-independent), parked in HANDOFF-10-11 §2 behind steps 3–5 (all NO on 10-10).

## Fixed inputs
- Topics: `topics/vital3.jsonl` (sha `6e36bbfe…; 1,002 titles, Wikipedia revid 1379525978`), order `topics/order-bf.txt` (sha `7a617aa7…`); system prompt `tools/note.system.md` (sha `57e3d36b…`); generator `tools/gen_notes.mjs`, mini script `tools/gen_notes_mini.sh`; params temp 0.3 / top_p 0.9 / max_tokens 450 / thinking off.
- Pack builder `tools/build_notes_pack.mjs` → `shared-data/packs/boar-notes35-<N>.sqlite` (+ .json manifest, sha recorded in the result file); kit entry `{"id":"boar-notes35","sha256":"(pack manifest sha, recorded in NOTES35.md per stage)"}` appended to C's requests (file must be named boar-notes35.sqlite: the adapter finds kit packs by name); engine tree cut 7 unchanged (MacBook `kiln-local/be-0cfd4a77-cut7`, adapter 4a22a4e).
- Replay hit-rate: `replay-retrieval.sh --tree wt/cut7 --packs crypto,wikivoyage,notes` on the 110 v0.2 ids (coordinator, script-only; ids + titles only) → `tools/hitrate.py`.

## Power
expected_delta: +0.02 raw on v0.2 if notes reach the context on ≥ 15 % of items (source: HANDOFF-10-11 §2 "unknown; +0.02 if notes reach context"; FACTS, the item-shaped precedent, fired 0/168 held-out-style; DEEPNORAG shows packs are worth +0.045 to the deep tier). Honest prior: the gate at stage A is the real test; a judged Δ in (0, 0.025) is undetermined at this n.
n: 110 (v0.2, s42) for the direction; 51 × 2 seeds on V-para only for a LEVER
seeds: 1 on v0.2; 2 on V-para
mde: 0.025 raw on v0.2 one seed; 0.03 on V-para two seeds
slice: random20-v02.ids (sha a3e43672…)
l1_futility: stop only if Haiku Δ ≤ 0 AND h2h ≤ control; any Haiku Δ > 0 → Opus N=4 on the same 20 ids
reopen: 4B corpus family (closed 10-01 for the enwiki pack, DEEPWIKI 10-10 for the deep tier): new mechanism = model-written notes (dense, question-shaped knowledge, 1,000 topics, ≈ 1 MB), not a crawled corpus; hit-rate gate before any judge call.

## Stages and rules
A. Generation stage 1: first 300 titles of the breadth-first order on the mini (≈ 300 × ≈ 35 s ≈ 3 h; one 35B server; STATUS file). Build the pack. **Gate A (0 calls):** replay on the 110 v0.2 ids: share of items with ≥ 1 note chunk among the engine's kept `sources` ≥ 5 % (extrapolating to ≥ 15 % at 1,000 topics, assuming linear coverage) AND ≥ 1 note in `raw` on ≥ 15 %; else NO at step 0 ("notes do not reach the 4B's context"), no more generation.
B. Generation stage 2: titles 301–1,000 (≈ 7 h). Build the pack. **Gate B (0 calls):** kept-sources hit-rate ≥ 15 % on the 110 ids; else NO at step 0.
C. L1 slice (random20-v02, s42, MacBook, server backend as MP4B): Haiku N=4 vs C (40 calls); futility / near-miss rules. D. Full 110 s42 → Haiku vs C (220) → if Δ > 0 or near-miss: Opus vs K (220). E. Verdict: LEVER = CI low > 0 and Δ ≥ +0.03 raw; SMALL = CI low > 0 and Δ < +0.03, or Δ ≥ +0.02 with CI low > −0.01 ("not decided at MDE 0.025"); NO otherwise. F. LEVER → V-para 2 seeds (Opus 204) vs K.
Secondary readings: correctness Δ on items where a note was kept (hallucinated notes become cited facts: the correctness dimension is the control); note-cited share; retrieval time.
One generation per stage; ≤ 1 post-hoc split (items with a note kept vs not), hypothesis only.

## Stop rules and budget
Mini: disk ≥ 25 GiB (the notes pack is ≈ 1–3 MB), one 35B server at a time (never while a deep arm runs), never restart Docker, never stop the detector :8094. Judge: ≤ 40 Haiku at C, ≤ 220 Haiku + 220 Opus at D (week cap: Opus ≤ 600 — 295 spent on 10-10; Haiku ≤ 400 — 160 spent). Generation time cap 11 h total.

## Outputs and exposure
`arms/notes35/NOTES35.md`, `aggregates/`, `topics/`, `tools/`, pack manifest; traces/judgments under `blind/bench-v02/runs-notes35`. EXPOSURES row per judged stage; the replay reads v0.2 ids and titles only (script-only).
