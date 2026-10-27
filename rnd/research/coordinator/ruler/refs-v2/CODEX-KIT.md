# References v2 — Codex half (F2): kit for r4to

TL;DR: three commands on the MacBook, ChatGPT [usage detail removed], about 88 Codex calls with live web search (~1–2 h wall at CONC=2, resumable). Then tell the ruler session; it checks, freezes and logs.

```fish
cd <workspace>/rnd/research/coordinator/ruler/refs-v2
bash run-codex.sh check     # codex version + "Logged in using ChatGPT" + "75 items, 0 done, 75 to do (88 turns)"
bash run-codex.sh pilot     # 1 real call on cw-001; the line must read "cw-001 ok ... search=N" with N >= 1
bash run-codex.sh all       # the rest; rate limit -> stops (exit 3); rerun = resume. CONC=1 bash run-codex.sh all if limits bite
bash run-codex.sh status    # checker: must end with "hard_failures": [] and rows_ok 75
```

## Stop and tell the ruler session (do not work around) if
- the pilot line shows `search=0` (web search did not run: the `web_search="live"` key may differ in your codex version) or `FAIL`.
- a run ends with exit 4 (some items failed twice): send the failed ids line.

## What it does
- Same frozen protocol as the Claude half: `REFS-V2-criterion.md` (sha in `REFS-V2-criterion.sha256`), prompt `prompts/reference.v2.md`, generator `tools/gen_refs_v2.mjs` (run.sh refuses to start if any sha differs).
- Codex call: `codex exec`, gpt-5.6-sol, reasoning high, `web_search="live"`, no shell, read-only sandbox, ephemeral, ignores your config and rules, clean env (no OPENAI_API_KEY).
- One draw per item. Multi-turn items (8) run turn by turn with Codex's own earlier answers; location items (7) say where the user is; every message carries today's date.
- Output: `boar-eval/bench/v0.4/refs/v2/codex.jsonl` (+ `codex.calls.jsonl`, wall time per call). The terminal prints ids, word counts and source counts only; you do not need to read any answer.

## Rules
- Do not read or edit the outputs, the prompt or the generator. Do not regenerate an item that has an ok row.
- Nothing is pushed or posted. The ruler session commits the archive in boar-eval (local) and logs QUEUE + EXPOSURES rows.
- Until both halves are frozen, no app arm may answer any v0.4 item (spec r3 §3.2).
