# PK-5 criterion addendum 1: judged parity screen on the 16 changed items (frozen 2026-10-21, before any generation)

Why: step 1 identity was 83.5 pct (< 95 pct). The coordinator ordered a judged parity screen before the phone step. Haiku 5.5-low (judge.v1-low), N = 4 shards, both orders. **Cap: 70 Haiku calls total for PK-5** (pk5_cell.sh CAP=70 counts this arm dir only). 0 Opus, 0 paid.

Items: pk5/diff16.ids (sha 6901bbdb5b90884f) = the 16 MAIN 97 items whose kept sources changed in step 1 (15 v0.1, 1 cooking-se).

Deviation from the coordinator's wording ("against the existing KA answers' judgments"), decided here and recorded: the existing KA cells (coverage-matrix q17 KA main) ran the LITEPACKS settings (packHeadPass a2 + packDense2 append-budget) with the v3proto factbook/medlineplus/firstaid files. HEADPASS-X2b skips packs by id (crypto, wikivoyage), so a merged pack would get the head pass on its wikivoyage/crypto rows: merged vs KA would mix the merge with a head-pass change. The phone runs neither setting. So both arms are generated fresh in the phone's retrieval configuration, and the gate compares them to each other:
- S = the 6 A-union phone files (shas = persona-a-union/SHA256SUMS), settings {quickFirst: true, alwaysComplete: false} (no head pass, no dense append) = the phone engine's retrieval (cut 7 retrieval; batchret is byte-identical);
- M = the merged pack only (boar-aunion-merged, sha 7e86674b...), same settings.
Requests pk5/req/pk5-S (sha 8849972cea763186) and pk5-M (dbc3571ac8b83641) = the coverage-matrix lp-KA v01/cm requests for the 16 ids (items, model qwen3-1.7b-q4km, seed 42, device) with settings and kit replaced. Pack dirs via env files pk5/six.env / pk5/merged.env (BOAR_EVAL_PACK_DIRS on the mini = <runner>/kiln/pk5/packs-six | packs-merged).
Runner: tools/pk5_cell.sh (sha ad030a5d8dc53ce7; = coverage-matrix/tools/run_cell.sh with pack sets S|M, these requests, cap 70 on this arm's own calls), mini LITEPACKS system (base tree be-0cfd4a77-cut7-litepacks, llama-server b11010 CPU, --reasoning off, LITEDECLINE_OFF=5). Judgment reuse: byte-identical answers reuse existing Haiku judgments (coverage-matrix reuse pool + matrix aggregates incl. q17-KA-main-97).

## Rule (pooled over the 16; U and CE-unwarned as in agg_run / matrix_report: CEu = not declined, not refusal-like, not warned, corr <= 1.5)
- PASS = U(M) - U(S) >= -0.02 AND CEu(M) - CEu(S) <= +1 (counts). Then the phone step runs as in PLAN.md and PK5-criterion.md step 2.
- FAIL otherwise: stop, report, phone untouched.
- If the cap would be exceeded before both arms are judged: no verdict, report pending.
Reported, not gating: U(M) and U(S) vs the existing KA cell (q17-KA-main-97) on the 16, item-level changes, declines.

## Budget
calls_cap: Haiku 70 / Opus 0
opus_clause: none
(r1, 04:50, before any judge call: this block only restates the cap above in the format the judge preflight requires; S generation had finished, no judgment existed; nothing else changed.)
