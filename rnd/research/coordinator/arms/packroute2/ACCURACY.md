# PACKROUTE-2 stage 0a — **FAIL at step 0a** on both wordings (2026-10-13 14:4x; criterion sha d67fd81c…; 0 judge / 0 paid; MacBook; stage 0b not run)

Setup: claim 4B (Qwen3-4B-Instruct-2507 Q4_K_M, sha 3605803b…) on llama-server b11010 CPU (`-t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --cache-ram 0`), `/v1/chat/completions`, temperature 0, seed 42, max_tokens 16, cache_prompt false. System = role + 9 installed non-kit packs (id: description) + `none` ("general or about travel/crypto, which the base app already covers") + "reply with exactly one pack id or none"; user = the question. Exact-id parse (whitespace/quotes/period stripped), else `invalid`. tools/classify.py → runs/routes-*.jsonl, aggregates/accuracy[.v2].json.

| gate G1 | need | v1 (descriptions d55c0bc8…, prompt 0286b1f5…) | v2 retry (+3 example stems/pack; 5373bfce…, prompt ba357f4c…) |
|---|---|---|---|
| own pack on 180 | ≥ 153 | **105 (0.58)** | **109 (0.61)** |
| `none` on 24 kit items (9 v0.1 + 15 v0.2) | ≥ 21 | **10** (5 + 5) | **11** (4 + 7) |
| SE family (100) / topic family (80) | — | 65 / 40 | 72 / 37 |
| invalid (180 / v0.1 60 / v0.2 110) | — | 2 / 2 / 1 | 2 / 3 / 4 |
| verdict | | FAIL | FAIL |

Per pack own/20 (v1 → v2): travel 16→14, ethereum 19→19, bitcoin 17→15, health-se 7→14, outdoors 6→10, firstaid 17→14, medlineplus 2→3, factbook 19→19, simplewiki 2→1.
Confusion (v1; v2 in brackets):
- medlineplus → qa-health-se 12 [15], → firstaid 6 [1]: the two health packs are not separable by description; the model prefers the Q&A pack.
- simplewiki → none 15 [18]: the `none` = "general" rule absorbs the general-encyclopedia pack (by construction of the prompt).
- outdoors → firstaid 10 [5]; health-se → firstaid 8 [4], → none 4 [2]; travel → none 3 [5].
- invalids are near-misses of ids: "simplewiki-en" ×2, "outdoors-se", "boar-outdoors-en" (v1).
- Kit `none` misses go to a crypto/travel SE pack (v1: bitcoin 5, travel 5, other 4; v2: bitcoin 5, travel 4, other 4): kit crypto/travel questions look like SE questions.
Route distribution (v1 / v2): v0.1 60: none 24 / 26, factbook 12 / 12, ethereum 6 / 6, firstaid 5 / 5, other 13 / 11; v0.2 110: none 52 / 58, firstaid 14 / 11, travel 12 / 7, bitcoin 8 / 8, factbook 8 / 8, other 16 / 18.

Latency (MacBook M1 Pro CPU, 4 threads; ms per call):
| | v1 | v2 |
|---|---|---|
| cold (no prefix cache), 350 calls p50 / p90 | 5,076 / 5,712 | 9,518 / 11,208 |
| prefix-cached, 20 items p50 / p90 (prompt tokens processed p50 28) | 619 / 792 | 668 / 794 |
| choices identical cached vs cold | 20/20 | 20/20 |
Phone estimate (×3): cold ≈ 15 s (v1) / 29 s (v2); cached ≈ 1.9–2.0 s per question. A few v1 calls ran while vitest ran (±1–3 s on ~5 items; p50 unaffected).

Reading: the zero-shot 4B router beats the vote router (0.58–0.61 vs 0.25 accuracy) but is far from the 0.85 bar; its errors are structural, not wording: overlapping packs (medlineplus vs health-se vs firstaid; outdoors vs firstaid) and the `none` = "general" rule colliding with simplewiki and with SE-looking kit questions. The declared retry (+4 own, +1 none) does not change the verdict. Per the criterion: FAIL at step 0a; no stage 0b replays, no stage 1.
Engine side (ready, unused): wt/packs `packRoute: "llm" | "llmq"` + `packRouteChoice` (AnswerDeps.routePack; replay `--routes`); default off byte-identical on the new tree (kit-only v0.1 off/router/quota 60/60 ×3; single-pack off 20/20 ×9 vs PACKROUTE diff-*; aggregates/identity.json); vitest src/rag 34 files / 231 tests pass, tsc 0 errors. Patch packroute2.vs-dt512.patch (sha 71f783de…; whole-file diffs of the PACKROUTE files vs dt512, so packs.ts/retrieve.ts also carry the T-K2/packDense2 hunks and need wikiPack.ts from packdense2.vs-dt512.patch to apply).
Tools for 0b (written, not run): tools/replay-pr2.{ts,sh}, tools/run_step0b.sh (only `diff` run), tools/step0b.py.

## 0b diagnostic (verdict unchanged: FAIL at 0a) — v2 routes (higher-scoring wording), 0 LLM / 0 judge
tools/run_step0b.sh (WORDING=v2; modes off,llm,llmq,off) → runs/all9-{st180,v01}.v2.jsonl, blind/…/packroute2-all9-v02.v2.jsonl (script-only); tools/step0b.py --wording v2 → aggregates/step0b.json. Identity: this tree's P = PACKROUTE P 180/180, 60/60, 110/110. Invalid route → undecided (every pack).

| 180 self-test (fact chunk raw6 / fact article kept) | S (oracle) | P (peers) | R4 (llm) | R4Q (llmq) | need |
|---|---|---|---|---|---|
| all | 67 / 68 | 42 / 46 | **33 / 31** | **43 / 49** | ≥ 60 / ≥ 61 and ≥ P |
| SE (100) | 24 / 28 | 10 / 14 | 16 / 13 | 17 / 20 | |
| topic (80) | 43 / 40 | 32 / 32 | 17 / 18 | 26 / 29 | |
| empty kept | 48 | 42 | 73 | 53 | |
G2: R4 FAIL (below P), R4Q FAIL (above P by +1 / +3, below the bar).

Per routing outcome (fact article kept; S / P / R4 / R4Q):
| route (v2) | n | S | P | R4 | R4Q |
|---|---|---|---|---|---|
| own pack | 109 | 33 | 22 | **33** | 33 |
| other pack | 36 | 16 | 5 | 0 | 0 |
| none | 33 | 18 | 15 | 0 | 10 |
| invalid (= every pack) | 2 | 0 | 0 | 0 | 0 |
A correct route recovers the full oracle value (+11 vs peers on 109 items). A wrong route costs everything peers had on that item (−5 for another pack, −15 for none), so the net is −15 (R4) or +3 (R4Q, which keeps 10 of 15 on none).

G3 (kit no-harm, RULE 26; OFF = kit only):
| | OFF | P | R4 | R4Q |
|---|---|---|---|---|
| v0.1 lost-context | — | 1 (lan-rsn-003) | 0 | 0 |
| v0.2 lost-context | — | 3 (v02-crypto-B02, v02-honesty-refusal-A03, -B05) | **2** (v02-crypto-B02, v02-honesty-refusal-B05) | **4** (v02-crypto-B02, -honesty-refusal-A03, -A05, -B05) |
| empty kept / retrieving, v0.1 · v0.2 | 11 · 28 | 9 · 15 | 8 · 27 | 8 · 22 |
| gold kept, v0.1 (≥ 12) · v0.2 resolvable (≥ 4) | 12 · 4 | 23 · 3 | 15 · **1** | 20 · **1** |
| retrieval p50 ms, 180 (router call excluded) | — | P2 410.8 | 140.2 (×0.34) | 153.3 (×0.37) |
G3: R4 and R4Q FAIL (v0.2 lost-context ≠ 0, v0.2 gold kept 1 < 4); cost passes. Router call adds 619–668 ms cached / 5.1–9.5 s cold on the MacBook (×3 for a phone).
Reading: retrieval is cheaper behind a top-1 route, but at 0.61 accuracy the wrong routes (38 %) outweigh the right ones. Break-even vs P ≈ 0.68 accuracy (0.256/0.378); ≥ 0.85–0.9 to reach 90 % of S (the G2 bar); a peers fallback on `none` is still needed (corrected 2026-10-13, LEDGER-FIXES §2: the earlier "≥ 0.85 to beat P" conflated the two).
