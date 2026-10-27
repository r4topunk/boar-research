// G1-SWA5 dd2 switch test (0 LLM, desktop). Run:
//   <workspace>/boar-eval/adapters/desktop-node/node_modules/.bin/tsx params_test.mts <workspace>/bench-app
// Checks: (1) absent overrides and the three request blocks' default arm leave the engine's init params byte-identical
// (JSON) and set no swa_full key; swaFull:true adds exactly swa_full:true. (2) withSampling: absent = same object;
// temperature/seed on answer completions; probe keeps temperature, gets seed. (3) benchSession history shapes.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const BA = process.argv[2] ?? "<workspace>/bench-app";
const O = await import(`${BA}/src/engineOverrides.ts`);
const S = await import(`${BA}/src/benchSession.ts`);
const REQ = "<workspace>/handoff/pixel8-2026-10-20/bench/requests";
// The engine's own init params (LlamaEngine.ts load(): model, use_mmap, use_mlock, n_ctx, n_threads, n_gpu_layers).
const init = { model: "/data/x/models/gemma-4-e2b-it-q4km.gguf", use_mmap: true, use_mlock: false, n_ctx: 4096, n_threads: 4, n_gpu_layers: 0 };
const J = (x: unknown) => JSON.stringify(x);
let n = 0;
const ok = (c: boolean, m: string) => { assert.ok(c, m); n++; };

O.setActiveOverrides(null);
ok(O.applyOverrides(init) === init, "no overrides: same object");
const blocks: Record<string, any> = {};
for (const r of ["swa5-g-default", "swa5-g-full", "swa5-q17-default"]) blocks[r] = JSON.parse(readFileSync(`${REQ}/${r}.request.json`, "utf8")).engineOverrides;
for (const r of ["swa5-g-default", "swa5-q17-default"]) {
  O.setActiveOverrides(O.parseOverrides(blocks[r]));
  const a = O.applyOverrides(init);
  ok(J(a) === J(init) && !("swa_full" in a), `${r}: init params byte-identical, no swa_full key`);
}
O.setActiveOverrides(O.parseOverrides(blocks["swa5-g-full"]));
const f = O.applyOverrides(init);
ok(f.swa_full === true && J({ ...f, swa_full: undefined }) === J(init), "swa5-g-full: only swa_full:true added");
ok(O.configKey(O.parseOverrides(blocks["swa5-g-full"])) !== O.configKey(O.parseOverrides(blocks["swa5-g-default"])), "full vs default: different config key (reload)");
ok(O.applyOverrides({ ...init, embedding: true }).swa_full === undefined, "embedding contexts untouched");
assert.throws(() => O.parseOverrides({ swaFull: "yes" })); n++;
assert.throws(() => O.parseOverrides({ temperature: -1 })); n++;

// Sampling
const ans = { messages: [{ role: "user", content: "q" }], jinja: true, n_predict: 400, temperature: 0.7, n_probs: 0, stop: [] };
const probe = { messages: ans.messages, jinja: true, n_predict: 1, n_probs: 8, temperature: 1 };
O.setActiveOverrides(null);
ok(O.withSampling(ans) === ans && O.withSampling(probe) === probe, "no overrides: completions untouched");
O.setActiveOverrides(O.parseOverrides({ reload: true }));
ok(O.withSampling(ans) === ans, "overrides without sampling: completions untouched");
O.setActiveOverrides(O.parseOverrides(blocks["swa5-g-default"]));
const a2 = O.withSampling(ans), p2 = O.withSampling(probe);
ok(a2.temperature === 0 && a2.seed === 42 && J({ ...a2, temperature: 0.7, seed: undefined }) === J(ans), "answer: temperature 0 + seed 42 only");
ok(p2.temperature === 1 && p2.seed === 42 && p2.n_probs === 8, "probe: temperature kept, seed 42");

// Sessions
const qs = [{ id: "warmup-000", query: "W?" }, { id: "a-t1", query: "A1?" }, { id: "a-t2", query: "A2?" }, { id: "a-t3", query: "A3?" }, { id: "b-t1", query: "B1?" }, { id: "b-t2", query: "B2?" }];
const spec = S.parseSession({ groups: [["a-t1", "a-t2", "a-t3"], ["b-t1", "b-t2"]] }, qs);
assert.throws(() => S.parseSession({ groups: [["a-t1", "a-t3"]] }, qs)); n++;
assert.throws(() => S.parseSession({ groups: [["a-t1", "zz"]] }, qs)); n++;
ok(S.parseSession(undefined, qs) === null, "absent session = null");
S.setActiveSession(spec, qs);
const ctx = { systemPrompt: "s", maxTokens: 400 };
const w = S.withSession("W?", ctx); ok(w.ctx === ctx, "warm-up outside groups: ctx untouched");
const t1 = S.withSession("A1?", ctx); ok(t1.ctx === ctx, "turn 1: ctx untouched");
t1.record("Answer one.");
const t2 = S.withSession("A2?", ctx);
ok(J((t2.ctx as any).history) === J({ turns: [{ role: "user", text: "A1?" }, { role: "assistant", text: "Answer one." }] }) && (t2.ctx as any).systemPrompt === "s", "turn 2: history = turn 1 Q + A, ctx kept");
t2.record(null, "timeout");
const t3 = S.withSession("A3?", ctx);
ok((t3.ctx as any).history.turns.length === 3, "turn 3 after a failed turn 2: 3 messages (turn 2 user only)");
t3.record("x");
const b1 = S.withSession("B1?", ctx); ok(b1.ctx === ctx, "second group starts fresh");
const log = S.drainSessionLog();
ok(log.length === 4 && log[1].historyMessages === 2 && log[1].error === "timeout" && log[2].historyMessages === 3, "session log rows");
S.setActiveSession(null, []);
ok(S.withSession("A2?", ctx).ctx === ctx, "cleared session: ctx untouched");
console.log(`params_test OK ${n} checks`);
