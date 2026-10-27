# JUDGE2 feasibility: local open-weights second judge on the Mac mini (2026-10-07, paper study; no runs, no downloads)
**TL;DR:** Feasible without changing judge.v1. Point `BOAR_EVAL_LIB` at a shim directory: it holds a copy of judge-core.mjs (identical bytes) and a `runClaude` that POSTs to llama-server `/v1/chat/completions` with a json_schema grammar. Use **Gemma 4 26B-A4B Q2_K_XL** as the judge. Target **DEEPREAD deep35-R450** (Opus + Sonnet-low/med already judged it), plus 4B-R450 to check ranking. About **83 s/call contended** and **2.6 h per 114 calls** (likely less on an idle mini).
## 1. How judge.v1 calls the model
- `harness/judge.mjs:19-21` loads the lib from `process.env.BOAR_EVAL_LIB ?? scorers/vendor/eval-lib`. That makes it a ready-made injection point. `judge.mjs:93-94` calls `runClaude({prompt: judgePrompt(..), systemPrompt: JUDGE_SYSTEM, model, effort, tools: [], jsonSchema: VERDICT_SCHEMA, timeoutMs: 180_000})`. `judge.mjs:97-98` reads `r.json.structured_output` and exits on the first error (no retry; a rerun resumes). `judge.mjs:101` takes judgeModel from the keys of `r.json.modelUsage`.
- `eval-lib/claude-cli.mjs:19-39` spawns `claude -p` with `--json-schema` (`:33`). It has no HTTP or custom-command path. `:9` strips `OPENAI_API_KEY`/`ANTHROPIC_BASE_URL` on purpose.
- judge.v1 = `eval-lib/judge-core.mjs`: system prompt `:64-75`, user prompt `:77-81`, schema `:52-62`. `bench/v0.2/plan/judge-core.judge.v1.mjs` has the same bytes (`diff` is empty).
- **Structured output is required.** The schema is {scores_A, scores_B: {correctness, completeness, usefulness}, each an integer 1-5; winner ∈ {A, B, tie}; rationale}, with additionalProperties false. llama-server `response_format: {type: "json_schema"}` compiles it to a grammar. Integer min/max and enum support must be checked in the smoke run (UNKNOWN for b11010).
- **Smallest change (0 edits to tracked files):** a shim dir with `judge-core.mjs` (a copy, sha-checked) and `claude-cli.mjs` that does `export *` from the original and shadows `runClaude`. Messages = [system: JUDGE_SYSTEM, user: prompt], with the bytes unchanged. Settings: temp 0, seed 7, `chat_template_kwargs.enable_thinking=false`, max_tokens 400. It returns `{ok, json: {structured_output, modelUsage: {<gguf>: {}}, duration_ms, total_cost_usd: 0}}` and logs raw failures to a sidecar file so the JSON-failure rate can be measured. Tag the run with `--effort gemma4q2`, which gives judgeVersion `judge.v1-gemma4q2` (`judge.mjs:23-24`; the shim ignores effort). `judge.mjs:81` still runs `claude --version` (claude is installed on the mini: `~/.local/bin/claude`).
- **Prompt size (measured, DEEPREAD 57 items):** system + user = median 3,591 chars, p90 4,067, max 4,353. The BOAR answer has a median of 299 chars and the ref 1,555 (5× longer). The Qwen3.6 tokenizer averages 4.21 chars/token (DEEPREAD requests vs traces promptTokens), so a call is about **850-1,030 input tokens**. Output: Opus verdict JSON median 487 chars (p90 618), about **150-200 tokens**. `-c 4096` is enough.
## 2. Cost per call on the mini (CPU ×4, b11010 build-cpu; 900 in / 170 out)
| judge | speeds used (source) | s/call | 114 calls | 228 calls |
|---|---|---|---|---|
| Qwen3.6-35B-A3B Q2_K_XL (on disk) | pp 18.6 / tg 9.43 (DEEPREAD.md:47-48) | ~66 | 2.1 h | 4.2 h |
| same, contended | pp 6.1 / tg 4.66 (MOESCREEN.md:23) | ~184 | 5.8 h | 11.7 h |
| Gemma 4 26B-A4B Q2_K_XL (re-download) | pp 13.2 / tg 11.37, contended (MOESCREEN-gemma4.md:16-17) | ~83 | 2.6 h | 5.3 h |
- Contention caveat: smbd ran at 750-890 % in MOESCREEN, and decode fell from 10.5 to 3.4 tok/s over the run. Gemma has no uncontended prefill figure (UNKNOWN; smoke decode was 16.3 tok/s). Its pp figure came from 143-token prompts. The mini's load was 1.7 at 14:56 today.
- Contended Qwen (~184 s) exceeds the `timeoutMs: 180_000` passed at `judge.mjs:94`, so the shim needs its own 240 s cap. Prompt caching (`cache_prompt: true`, keeping the system + question + notes prefix) cuts prefill by about 30 %. That changes no bytes.
- Disk: the mini has 37 GiB free now. Gemma (10.5 GB) would leave about 26.5 GiB, just above the 25 GiB floor (`DISK-POLICY.md`). RAM peak is about 8.2 GB (Gemma) or 8.4 GB (Qwen).
## 3. Target set
- **DEEPREAD deep35-R450 (57 items, v0.1 EN, refs bd235bb9…):** Opus judge.v1 (`arms/deepread/deep35-R450.judgments.jsonl`, ratio 0.634, pos-cons 96.5 %) and Sonnet-low/med (114 rows each) both exist, so this gives a 3-way comparison. JUDGE-TRIAGE has already used it as the baseline (same-winner 95 %, κ 0.68).
- For ranking, add **4B R450** (`anvil/exp/oracle/runs/qwen3-4b-R450.judgments.jsonl`: Opus judge.v1, same refs/questions sha, 114 ok). Opus has deep35 > 4B by +0.029.
- spctl-v01-s44 (`boar-eval/runs/kiln/speedpack-l1/`) was judged only by Opus judge.v1-med. That allows a 2-way comparison only, and with a different judge version, so it is second choice.
## 4. Risks
- **Q2 judge quality:** Gemma's own closed-book ratio is 0.613, so it knows less than the Claude refs. It will lean on the notes and the ref, which makes it less able to catch errors in the ref. That is the very bias we want to measure, so a Gemma "agree" is weak evidence.
- **Length bias:** the ref is 5× longer than the answer. Weak judges reward length, so expect a lower ratio. Report rubric means per side, not just the ratio.
- **Position bias:** both orders run, and `combineOrders` (`judge-core.mjs:94-98`) turns a disagreement into a tie. Report position consistency against Opus's 96.5 %. If consistency is under 80 %, read the result as noise.
- **JSON:** grammar decoding should make failures near zero. Truncation at max_tokens and a run that hangs are the remaining risk. Haiku needed structured-output retries (JUDGE-TRIAGE).
- **Self-preference:** both arms are Qwen (deep35 = Qwen3.6-35B-A3B, 4B = Qwen3-4B). A Qwen judge would be grading its own family, so **use Gemma**: it is a third family, neither Claude (the refs) nor Qwen (the answers).
- Thinking must be off, as it is for Opus. Opus judge.v1 runs with default effort, so the comparison is of judge systems, not of models alone.
## Recommended setup
Gemma 4 26B-A4B UD-Q2_K_XL (re-download, sha 2a1d26df…, needs r4to's OK) · llama-server b11010 `-t 4 -c 4096 -np 1 --jinja`, under `<runner>/bin/run-heavy`, with the mini idle · BOAR_EVAL_LIB shim on the mini, which needs node (present) · leg A: deep35-R450, 114 calls, about 2.6 h · leg B: 4B-R450, 114 calls, about 2.6 h (5.3 h total) · disk +10.5 GB, delete after.
## DRAFT criterion (to freeze with sha256 before any call)
- Q: how closely does a local, non-Claude judge (Gemma 4 26B-A4B Q2) running judge.v1 bytes agree with Opus judge.v1 on v0.1 EN 57?
- Frozen inputs: deep35-R450.traces.jsonl and qwen3-4b-R450.traces.jsonl (sha at freeze), refs bd235bb9…, questions 568b3ece…, judge-core.mjs sha, shim sha, GGUF sha, seed 7, temp 0.
- Measures: winner agreement % (orders combined, per item) against Opus and against Sonnet-low; Cohen κ on BOAR correctness ≥ 4; ratio Δ (Gemma − Opus) with bootstrap CI; Pearson r on the BOAR mean score; position consistency; per-arm ranking (deep35 vs 4B) preserved yes/no.
- No GO bar: this is calibration only. The result is reported next to the claim's judge-family limitation and is not used to tune anything.
- Stop rules: JSON failure rate > 10 % after 20 calls; median > 4 min/call over the first 10 calls; disk < 25 GiB; the mini needed for a heavy job.
- Exposure: dev set only (v0.1 public). No blind or held-out data is used.
