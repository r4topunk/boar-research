# CHATFAIL S1: L1 prompt line, L2+L3 routing, L4 history filter on CHAT-FU-v1 (2026-10-18, Kiln runner; audit pending)

Verdict: **M4 (decides the engine recommendation): PARTIAL** (A2 - C0 = +0.122, CI 0.000..+0.256, in the +0.10..+0.20 band; v0.1 clause passes; audit pending). **M1 (iPhone note): NO** (A2 - C0 = +0.020). L1-ONLY not met (M4 A1 - C0 = +0.041 = 1/3 of A2's). **L4 not adopted** (A3 = A2 on fulfilled; refusal delta 0.000 on M4, -0.020 on M1, CI includes 0). No recommendation to the app maintainer from this run; next step per the PARTIAL rule: L2b + the format map.
Criterion: arms/chatfail/CHATFAIL-S1-criterion.md sha256 c8fde243... (verified against the sibling .sha256; unedited). Probe set chats.jsonl sha 303876ed... (30 chats, 159 turns, 49 capability: 21 code, 18 format, 10 translate). Detectors tools/fulfilled.mjs sha256 **907a2295bdbdd6f48f2389ee431dde7aecf34480fd4537982810b18bf2c03314** (12 unit answers 6/6 + 6 refusal checks pass), hashed before the first generation. Patches: L1 d38518c1..., L4 62fa0112... (tools/chatfail-l1.patch, chatfail-l4.patch, hashes in chatfail-l1-l4.sha256), L2+L3 f7972d37... (S0, verified). Models: M4 Qwen3-4B-Instruct-2507 Q4_K_M sha 3605803b...; M1 Qwen2.5-1.5B-Instruct Q4_K_M sha 1adf0b11... (= boar-ios catalog.json and wt/pr1 manifest). llama-server b11010 `-t 4 -c 4096 -np 1 --jinja`, seed 42, 0.7/40/0.95/0.05, 1 seed.

## Method (what the numbers are)
- Per turn: class (classifyTask; A2/A3 classifyTaskInContext), follow-up plan + `searchWithFollowUp` around the engine's own `retrieve` (answer.ts run with generate stubbed: k, compress, relevance floor, NO_SOURCE style piece are the engine's; claim kit crypto + wikivoyage-en, shas verified), `assembleChatMessages` + Succinct strings from each arm's scratch tree, history = the arm's own prior answers (pr1 buildChatHistory, last 6 messages; A3 filters declined assistant turns), `/v1/chat/completions` as the desktop-node server backend sends it. Contexts cached per routing (C0/A1 share, A2/A3 share): tools/out/ctx-{base,patched}.jsonl.
- Tables: chat-cluster bootstrap (30 chats, 2000, seed 1). Raw: tools/out/{gen,scored}-{m4,m1}-*.jsonl, stats-*.json.

## M4 (Qwen3-4B)
| arm | fulfilled (49) | code (21) | format (18) | translate (10) | refusal on capability | snowball P(ref_t given ref_t-1) |
|---|---|---|---|---|---|---|
| C0 | 0.633 (0.452-0.809) | 0.381 | 0.722 | 1.000 | 0.061 (0.000-0.153) | 0.25 (n=4) |
| A1 | 0.673 (0.491-0.854) | 0.381 | 0.833 | 1.000 | 0.020 (0.000-0.058) | 0.00 (n=2) |
| A2 | 0.755 (0.641-0.880) | 0.524 | 0.889 | 1.000 | 0.000 | 0.00 (n=1) |
| A3 | 0.755 (0.641-0.880) | 0.524 | 0.889 | 1.000 | 0.000 | 0.00 (n=1) |
Deltas fulfilled: A1-C0 +0.041 (-0.079..+0.178); A2-C0 **+0.122 (0.000..+0.256)** (code +0.143 (-0.133..+0.375), format +0.167 (0.000..+0.400)); A3-A2 0.000. Refusal A2-C0 -0.061 (-0.153..0.000).
v0.1 non-regression (57 non-venue ids, single turn, Haiku 5.5-low judge.v1, both orders, N=4): ratio C0 0.524, A1 0.510; **A1-C0 -0.014 (-0.029..+0.001)**, 40 of 57 answers differ (the 17 identical ones include 15 engine-written FACTS/cards/instant), better/worse/tie 16/21/20. Clause (>= -0.03 or CI includes 0) passes.

## M1 (Qwen2.5-1.5B)
| arm | fulfilled (49) | code | format | translate | refusal on capability | snowball |
|---|---|---|---|---|---|---|
| C0 | 0.612 (0.429-0.800) | 0.476 | 0.611 | 0.900 | 0.041 (0.000-0.093) | 0.00 (n=3) |
| A1 | 0.612 (0.447-0.776) | 0.571 | 0.556 | 0.800 | 0.000 | 0.00 (n=1) |
| A2 | 0.633 (0.467-0.800) | 0.476 | 0.611 | 1.000 | 0.041 (0.000-0.133) | 0.33 (n=3) |
| A3 | 0.633 (0.467-0.800) | 0.476 | 0.611 | 1.000 | 0.020 (0.000-0.067) | 0.00 (n=2) |
Deltas fulfilled: A1-C0 0.000 (-0.140..+0.157); A2-C0 **+0.020 (-0.116..+0.184)**; A3-A2 0.000; refusal A3-A2 -0.020 (-0.067..0.000). No v0.1 run on M1 (not in the criterion).

## Reading
- The live failure does not reproduce as a model refusal on M4: C0 on c01 refuses only t4 and writes one-line inline snippets at t5/t6 (smoke, as the criterion allowed). The baseline already fulfils 0.63, not ~0 (translate 10/10 with no help). The measurable M4 gain is routing: code asks 8 to 11 of 21 fenced answers, format 13 to 16 of 18.
- Frozen detector is strict: an inline backtick one-liner or prose about code is "not fulfilled". Not-frozen diagnostic, code asks with a fenced block: M4 C0/A1/A2/A3 = 8/8/11/11 and an inline-only snippet in 6/10/6/6 more; M1 10/12/10/10. Only the audit can say how much of the gap is detector.
- L1 alone moves refusals (M4 0.061 to 0.020; M1 0.041 to 0.000) but not fulfilled. L4 has nothing to drop on M4 (A3 answers = A2 byte-for-byte on the capability turns); snowball n is 1-4 pairs per cell, too small to read. The only refusal on a non-capability turn is the engine's own health decline (c14 t1, identical in all arms; it matches the REFUSAL regex).
- M1 A2 does not improve: 18 turns still fail, 5 of them c01 (a prose definition of a smart contract at every turn, even routed to `code` with no context), 3 refusals/prose in c21/c24, 8 format turns (shorter/table/list shape missing). The routing gain seen on M4 is absent.

## Deviations (all logged, none changes a frozen clause)
1. Max tokens 512 for every class: the reference engine has no per-class cap (DEFAULT_MAX_TOKENS 512); the criterion's "code task cap" does not exist. 0 answers hit the cap.
2. L1 styleReminder text: "Keep it short: 2-3 sentences, unless the user asks for code, an example, a table or a translation. No lists unless..." (criterion wording, inserted after the cap it exempts; the task brief's shorter wording was not used).
3. Not replayed: route gate (stubbed SEARCH as replay-retrieval's default), engine pre-generation shortcuts for compact models (M1 would answer "I didn't find this in this phone's library" on some source-less turns), health post-processing. The 8 turns where the engine answers without the model (first-aid cards/health decline: c13 t1, c14 t1, c15 t1, c16 t1, c17 t1, c27 t1/t3/t4) use the engine's text, no call; v0.1: 15 such items. Compression is keyed to the user's words, not the planner's text (answer.ts unchanged).
4. Driver ran on the MacBook, llama-server on the mini over ssh -L 8191 (nohup server log <runner>/kiln/chatfail-server-m{4,1}.log). L4 filters declined turns inside the 6-message window (slice then filter), engine REFUSAL regex only (the S1 detector adds phrases and is used for scoring only).
5. Interim M4 report sent to main before M1. No reuse of HONESTPROMPT generations (criterion decision); smoke_diff: C0 vs HONESTPROMPT S0 byte-identical on the 1 comparable turn, A1 vs C0 differ only by the two L1 strings on 18/18 smoke turns.

## Pending / cost
- **Audit not done by the runner:** arms/chatfail/audit-sample.jsonl (51 answers: 20 code A2/A3 x M4/M1, 20 random fulfilled=0, 11 first-aid c27) for one Opus auditor. The PASS clause "0 new WRONG health instructions" cannot be closed until it returns; the M4 verdict is PARTIAL regardless.
- Calls: Haiku 230 (228 + 2 preflight, cap 236), Opus 0, paid 0, web 0. Mini generation wall: M4 chat 83 min + v0.1 10.5 min, M1 30 min (kill_if: 0 empty answers, disk 41 GiB free). No commits, no pushes; wt/pr1 untouched; mini back to :8094 only.
- Files: arms/chatfail/{CHATFAIL-S1.md, audit-sample.jsonl, tools/{fulfilled.mjs,fulfilled.test.mjs,fulfilled.sha256,chatfail-l1.patch,chatfail-l4.patch,setup-s1.sh,contexts.ts,gen.mts,score.mjs,stats.py,v01_traces.py,run_v01_judge.sh,v01_agg.py,build_audit.py,smoke_diff.mjs,chatfail-server.sh}}, scratch/s1-*, tools/out/*.
