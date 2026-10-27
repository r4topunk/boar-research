# LITE5: X2b transfers to the lite 1.7B: LEVER-shaped, +0.080 (+0.033…+0.130) on selftest20, which brings the 1.7B level with the plain 4B (2026-10-15 23:57; Haiku 40, Opus 0, 0 paid)

X2b (X1 neighbours + budgeted dense append outside the keep step, HEADPASS-X2b) on Qwen3-1.7B Q4_K_M: fact in context goes from 6/20 to 12/20, and paired Δ(ON − OFF) = **+0.080 (+0.033…+0.130)** raw. Head to head ON/same/OFF = 11/6/3. The frozen clause (Δ ≥ +0.03 and CI low > 0) gives **LEVER-shaped (Haiku, dev, n = 20)**. With X2b the 1.7B scores the same as the 4B without it: −0.008 (−0.074…+0.064). It is still −0.072 (−0.114…−0.033) below the 4B with X2b.

## Frozen inputs
- Criterion `LITE5-criterion.md` v2 sha `9ba8bbf3…4009` (frozen 23:5x local; its header says "2026-10-16 00:0x", a mislabel left in place to keep the sha). Mechanism: HEADPASS-X2 1b70f6f3… + addendum 1 4b3578e7…. Inputs: LITE2 (628f60c2…, LITE2.md 81426218…) and LITE3 (LITE3.md a37dd0f3…). Smoke verdict PASS (3 items: mean prompt 738 vs a budget of 1047.67; marker `headpass:` 3/3).
- **Freeze history, disclosed:** v1 (077b1dbd…) had G2 "ON − OFF promptTokens ≤ 600 per item", measured on `timing.promptTokens`. The 0-call gate failed it on one item (factbook-001, +633; aggregates/gate5.v1-FAIL.json). The 4B X2b traces show the same +633 on that item and the same growth on all 17 LLM items. So the gate counted with the server tokenizer, while the budget is defined on the engine count. The mechanism did not behave differently. I re-froze v2 before any judge call (0 Haiku spent, no judged number seen), with G2 = "growth equal to the 4B X2b run". The ON traces were reused, not regenerated.
- Tree: kiln-local/be-0cfd4a77-cut7-headpass-x2 (patch 0fba26b8…). Adapter: **be/adapter-lite5.ts 5785ffc4…** = 8dd1faff + the qwen3-1.7b entries + the BOAR_SERVER_EXTRA_ARGS hunk (tools/adapter-lite5.vs-8dd1faff.patch 21bf555e…). The original be/adapter.ts (8dd1faff) is untouched.
- Model: sha b139949c… (downloaded to the MacBook, verified). b11010 with `--reasoning off`, seed 42, -t 4, MacBook M1 Pro. ON requests = the 4B X2b requests with only the modelId changed (mkreq_lite5.py asserts they equal LITE2's requests apart from runId, arm, the 2 settings and the sidecar sha).
- **Host caveat:** OFF = LITE2's rows from the mini (M4). I re-generated OFF on the MacBook (0 judge, aggregates/hostid.json): kept 20/20, prompt tokens 20/20, errors 0, but answer text identical on only 5/20. So the Δ includes one host re-sample of 15 generations, comparable to drawing a new seed.

## 0-call gate (v2, aggregates/gate5.json): PASS
G0: 0 errors, 0 empty, 0 reasoning tokens, no `<think>`. G1: headpass codes and kept lists identical to the 4B X2b traces 20/20. G2: growth equals the 4B's on 17/17 (p50 +400, max +633 server count). G3: changed 17/20. G4: fact present 12/20 (bar 10). X2b fired on 17/20, appending 40 chunks.

## Δ (Haiku 5.5-low N=4, both orders, paired.mjs, 2000 boots; W/T/L vs gold 0/0/20 in every arm)
| comparison | ratio a / b | Δ raw (CI) | floor-adj Δ (CI) | h2h a>/=/b> |
|---|---|---|---|---|
| **1.7B X2b − 1.7B OFF** | 0.510 / 0.430 | **+0.080 (+0.033…+0.130)** | +0.099 (+0.041…+0.161) | 11 / 6 / 3 |
| 1.7B X2b − 4B plain | 0.510 / 0.518 | −0.008 (−0.074…+0.064) | −0.015 (−0.104…+0.075) | 4 / 5 / 11 |
| 1.7B X2b − 4B X2b (descr.) | 0.510 / 0.582 | −0.072 (−0.114…−0.033) | −0.095 | 2 / 3 / 15 |
| (prior, 0 calls) 4B X2b − 4B plain, same 20 | 0.582 / 0.518 | +0.064 (+0.008…+0.128) | +0.080 | 11 / 3 / 6 |

## Splits (declared; LITE3 estimator Σboar/Σref; OFF → ON, Δ, up/same/down; 4B plain and 4B X2b in brackets)
- By reach: **newly present (6)** 0.367 → 0.521, **+0.154**, 6/0/0 [0.506, 0.658]. Present under OFF (6) 0.455 → 0.539, +0.084, 4/0/2 [0.544, 0.555]. Absent in both (8) 0.459 → 0.486, +0.027, 3/3/2.
- By LITE3 bucket: **invented (7)** 0.356 → 0.500, **+0.144**, 6/0/1 [4B 0.447]. not_read (3) +0.166, 3/0/0. thin (6) +0.006, 2/1/3. other (1) +0.063. Health-safety (3, deterministic) +0.011 (judge noise).
- Reading: the gain sits where X2b puts the fact into the context (+0.154 there, ≈ the 4B's +0.155 on the 180). Most of the invented bucket was a reach problem, which matches LITE4's null result for a prompt rule. *Thin* does not move.

## Cost (MacBook, 17 LLM items, OFF re-generated on the same host)
Prompt tokens p50 438 → 815 (+400 paired). Total p50 3.30 → 5.86 s, ttft 2.39 → 4.35 s (prefill). Answer words p50 33.5 → 38.5.

## Stage 6 kit slice (random20-v02, script-only; aggregates/kit-identity.json)
X2b does not engage without a format-v3 pack: `headpass:no-user-pack` + `headpass:dense:nosidecar` on 15/20, no headpass add on any item, kept 20/20 and prompt tokens 20/20 identical to LITE2's kit traces, errors 0. By the frozen rule the 40 reserved Haiku calls were not spent: kit-only behaviour is unchanged, as it was for the 4B.

## Verdict
**LEVER-shaped (Haiku, dev, n = 20, one seed, cross-host OFF).** X2b transfers to the lite tier. It recovers the 1.7B's reach deficit and closes its gap to the plain 4B on pack questions (from −0.088 in LITE2 to −0.008). The cost is +400 prompt tokens and ≈ +2.5 s on the desktop. Caveats: pack-matched dev items with agent-written gold; Haiku only; n = 20; OFF comes from another host. Next: an Opus or larger-n confirmation (the 180 self-tests on the 1.7B), plus phone prefill timing for +400 tokens.

## Files
`LITE5-criterion.md` (+ .sha256, v1 + .v1.sha256), `smoke.verdict.json` (+ v1), `arm-st-L5.conf`, `tools/{adapter-lite5.vs-8dd1faff.patch, mkreq_lite5.py, run_lite5_gen.sh, gen_all.sh, hostid.py, fic.py, gate5.py, split5.py, mkreq_kit.py, kitid.py}`, `runs/` (lite5-{on,off}-st20-*, smoke/, x2b4b-st20 Haiku rows copy), `aggregates/{lite5.json, gate5(.v1-FAIL).json, fic.json, hostid.json, split5.json, kit-identity.json, L1-*.json, think-*.json, gen-st20.txt}`. v0.2: `blind/bench-v02/runs-lite5/lite5-on-kit-v02-s42-slice.*`. Exposure: the kit slice was 20 generations, 0 judge calls, counts only; EXPOSURES row 2026-10-15 LITE5. rnd/veil/ was not read. The 1.7B is kept on the MacBook (free 9.0 GiB ≥ 8; DISK-LOG). No servers are left running (only the :8094 detector, untouched).
