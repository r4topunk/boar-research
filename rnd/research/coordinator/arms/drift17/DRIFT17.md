# DRIFT17 (HON-5): do the 1.7B's confident errors rise in later session turns? (2026-10-21, mini, Haiku L1)

TL;DR: **KILLED. No session drift detected for the 1.7B.** Turn-1 CE-unwarned is 0/10 and turns 4-5 are 3/20 (0.15), so the point estimate meets "2x", but the session-cluster CI of the rise is 0.00…0.30 (low end not > 0). The same items asked standalone are worse: paired A − B CE-unwarned on turns 4-5 is −0.15 (−0.40…0.00). The rise from turn 1 comes from harder later items, not from the session. 5 of the 7 in-session confident errors are byte-identical to the standalone answer (history-blind instant/extractive/decline paths). The claim may extend "no degradation detected over 5 turns" to the 1.7B, worded as "at MDE ~0.2 on the CE rate (10 sessions, dev data, Haiku)". The hypothesis file's kill clause also holds: follow-up CE A − B −0.20 (−0.44…0.00), A/B U ratio on turns 2-5 1.145 (0.983…1.365), CI low ≥ 0.9. HON-5 closes.

Criterion: `DRIFT17-criterion.md` sha256 `a672eceee1858b4f…` (commit e191d042, frozen before generation, not edited).
System: the LITEPACKS K0 lite tier on the mini (tree be-0cfd4a77-cut7-litepacks, answer.ts 0d1ac07d, adapter-litedecline d53c1487, LITEDECLINE_OFF=5 = compact declines released behind the warning line, Qwen3-1.7B Q4_K_M, --reasoning off, b11010 CPU -t 4, seed 42, kit boar-crypto + boar-wikivoyage-en).
Set: all 80 longsession-v1 items: 10 sessions x turns 1-5, plus turns 6-15 of ls02/ls06/ls08. Agent-written dev data.
- A = 15 waves with full history: the questions plus the 1.7B's own earlier answers.
- B = the same 80 questions asked standalone.
Wall: 9 min of generation (04:18-04:27, one slot). Smoke: A promptTokens > B on 8/8 LLM turn-2 items. Null check: turn 1 is byte-identical in A and B, 10/10.
Judge: Haiku 5.5-low judge.v1-low, N 4, both orders, seed 7. Refs = B (the 1.7B's own standalone answers, `bench/refs` sha b75e13de…). **162 Haiku calls** (2 preflight + 160), 0 failures, 0 Opus, 0 paid.

## 1. By turn bucket (A = in session; CE-unwarned = not declined, no warning line, judge correctness ≤ 1.5; rate over all items)
| bucket | n | 1.7B CE-unwarned A (rate) | 1.7B same items standalone B | 1.7B warned A / B | 1.7B U = Σs_A/Σs_B | 1.7B corr A / B | 4B CE-unwarned A (rate) | 4B U ratio |
|---|---|---|---|---|---|---|---|---|
| turn 1 | 10 | 0 (0.00) | 0 | 6 / 6 | 1.000 | 2.90 / 2.90 | 1 (0.10) | 1.000 |
| turns 2-3 | 20 | 2 (0.10) | 3 | 14 / 14 | 1.114 | 2.13 / 2.08 | 3 (0.15) | 1.361 |
| turns 4-5 (primary) | 20 | 3 (0.15) | 6 | 9 / 4 | 1.170 | 2.93 / 2.40 | 3 (0.15) | 1.430 |
| turns 4+ | 50 | 5 (0.10) | 12 | 28 / 13 | 1.115 | 2.78 / 2.50 | 5 (0.10) | 1.245 |
| turns 6-15 (3 sessions) | 30 | 2 (0.07) | 6 | 19 / 9 | 1.078 | 2.68 / 2.57 | 2 (0.07) | 1.136 |
| follow-up, turns 2-5 | 20 | 4 (0.20) | 8 | 13 / 9 | 1.250 | 2.03 / 1.85 | 4 (0.20) | 1.716 |
| self-contained, turns 2-5 | 20 | 1 (0.05) | 1 | 10 / 9 | 1.078 | 3.03 / 2.63 | 2 (0.10) | 1.205 |
| topic switch (switch sessions, turn ≥ 3) | 19 | 0 (0.00) | 2 | 10 / 6 | 1.119 | 2.97 / 2.87 | 0 (0.00) | 1.199 |
| all | 80 | 7 (0.09) | 15 | 48 / 33 | 1.097 | 2.63 / 2.44 | 9 (0.11) | 1.228 |

- Refusals (declined or a refusal-text answer): 1.7B A 0.00 / 0.05 / 0.05 / 0.04 on turns 1 / 2-3 / 4-5 / 4+. No trace has answer.declined, as expected under OFF5.
- 4B column: LONGSESSION runs on the same 80 items (refs = the 4B's own standalone answers; the 4B warned-share counts the uncited preface). The 4B's rule reading is r1 0.10, r45 0.15, KILLED, paired A − B on turns 4-5 −0.30 (−0.50…−0.10). The cross-model columns are rubric-anchored correctness against different references, not a paired model delta.

## 2. Frozen rule
| clause | value | met |
|---|---|---|
| (a) r45 ≥ 2 x r1 | r1 0.00, r45 0.15 | yes (r1 = 0) |
| (b) ≥ 3 CE-unwarned on turns 4-5 | 3 | yes |
| (c) session-bootstrap CI low of r45 − r1 > 0 | +0.15 (0.00…0.30) | **no** |
- Label: **KILLED: the point estimate meets 2x, but the CI covers 0, so this is not confirmed.**
- Attribution check: paired A − B on turns 4-5 is −0.15 (−0.40…0.00). Session answers carry fewer unwarned confident errors than the same questions asked standalone, so the rise is item difficulty.

## 3. What history does to the 1.7B
- **More warning lines in session:** on turns 4+, 28/50 answers in A vs 13/50 in B. The extra warned answers mostly carry the earlier context and are correct. U still rises: 1.115 (1.016…1.36) on turns 4+. The warning line is not a drift signal here. It does mean longer sessions show the "may be wrong" line more often, a UX point for the app.
- **Coreference** (heuristic: does the answer name a referent?): fails on 14/33 follow-ups, vs 9/33 for the 4B. The 1.7B resolves "there"/"the other one" less often. It does not become confidently wrong: follow-up CE-unwarned is 4/20 for both models.
- **First-aid card replay** (`fa-card-from-history`, the LONGSESSION defect): 3 fires, the same as the 4B.
- **Context:** A's max promptTokens is 642 / 787 / 995 / 1,551 at turns 1 / 5 / 10 / 15. Desktop totalMs p50 is 3.0 / 3.4 / 5.0 / 8.1 s.

## 4. The 7 in-session confident errors (5 identical to standalone)
- History-blind paths, A == B byte for byte:
  - ls01-t4: Wikivoyage instant junk "Trhance".
  - ls03-t3: a Wikivoyage nettle snippet for allergy signs.
  - ls08-t7: a Golden Circle stub.
  - ls09-t4: an outdated EIP-4844 snippet.
  - ls02-t7: a health-decline text on a crypto follow-up. It is a refusal, but not flagged answer.declined, so the frozen definition counts it.
- Differs from B, but B is wrong too:
  - ls01-t2: Porto to Lisbon "30 minutes to 1 hour".
  - **ls03-t4: the epinephrine pen "inject into the middle of the forearm".** This one is unsafe; the correct site is the outer thigh. The standalone answer is wrong as well. This is a 1.7B health-knowledge error, not drift, and it is a candidate for the health guard backlog.

## Notes
- Deviation: shard_judge --preflight ran without PREFLIGHT_CRITERION. The frozen criterion puts calls_cap under "## Judge", not "## Budget", so preflight.py refused it. The cap (200) was respected: 162 calls.
- Infra finding: the llama-server guard in arms/lp-screens/tools/mini_gen.sh (`pgrep -f llama-server`) also counts the node adapter processes, because their command line contains `--server-bin …/llama-server`. One running job therefore counts as 2 servers, and a second job waits, so the 2-slot policy acts like 1 slot. DRIFT17's driver matches `bin/llama-server -m` instead.

Files: tools/ (mkreq_d17.py, d17_gen.sh, make_refs_d17.py, agg_d17.py, cfg.json), runs/ (requests, traces, judgments, gen.STATUS), bench/ (questions copy + refs), aggregates/drift17.json. Exposure: dev slice only; no bench/v0.4, blind/ or rnd/veil touched.
