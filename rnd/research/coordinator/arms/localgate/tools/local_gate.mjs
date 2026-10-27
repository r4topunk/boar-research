// LOCALGATE local boolean classifier (node-llama-cpp, Metal). Reads JSONL {rid,type,state:{rationale_1,rationale_2,text}}
// from --in, writes JSONL {rid,type,p_local,ms} to --out. p_local = P(true)/(P(true)+P(false)) from next-token probabilities
// after the assistant prefix (temperature-free, thinking off: Qwen3-4B-Instruct-2507 has no thinking mode).
// Prefix reuse: requests are sorted by (rationale_1, rationale_2) so the shared system+rationale prefix stays in the KV cache.
// Prints counts/timings only.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
const require = createRequire("<workspace>/wt/eval/eval/package.json");
const { getLlama } = await import(require.resolve("node-llama-cpp"));

const args = Object.fromEntries(process.argv.slice(2).reduce((a, x, i, A) => (x.startsWith("--") ? [...a, [x.slice(2), A[i + 1]]] : a), []));
const MODEL = args.model || "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf";
const CTX = +(args.ctx || 4096);
const MAXTEXT = +(args.maxtext || 3000), MAXRAT = +(args.maxrat || 2500);

export const Q = {
  has_fact: {
    instructions: "Does `text` state the specific fact, figure, name, step or mechanism that `rationale_1` or `rationale_2` say the system answer is missing?",
    criteria: { true: "`text` contains the concrete content (fact, figure, name, step or mechanism) the judge says the answer lacks",
                false: "`text` is about something else, only touches the topic in general terms, or lacks the specific content the judge says is missing" } },
  quote_supports: {
    instructions: "Does `text` contain, in its own words, the specific value, name, date or step that `rationale_1` or `rationale_2` say is missing or wrong in the system answer, not merely the topic?",
    criteria: { true: "`text` states the concrete value, name, date or step itself",
                false: "`text` only discusses the topic, or lacks the specific value, name, date or step" } },
};
const SYS = "You are a strict, calibrated boolean classifier. You read the fields given, then answer one question with exactly one word: true or false. Answer true only when the criteria for true are clearly met.";
const prefix = (s) => `<|im_start|>system\n${SYS}<|im_end|>\n<|im_start|>user\n## rationale_1\n${(s.rationale_1 || "").slice(0, MAXRAT)}\n\n## rationale_2\n${(s.rationale_2 || "").slice(0, MAXRAT)}\n\n`;
const suffix = (t, s) => `## text\n${(s.text || "").slice(0, MAXTEXT)}\n\n## question\n${Q[t].instructions}\n- true: ${Q[t].criteria.true}\n- false: ${Q[t].criteria.false}\n\nAnswer with exactly one word: true or false.<|im_end|>\n<|im_start|>assistant\n`;

const reqs = fs.readFileSync(args.in, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const done = new Set();
if (fs.existsSync(args.out)) for (const l of fs.readFileSync(args.out, "utf8").split("\n").filter(Boolean)) done.add(JSON.parse(l).rid);
const todo = reqs.filter((r) => !done.has(r.rid)).sort((a, b) => (a.state.rationale_1 + "\u0000" + a.state.rationale_2 < b.state.rationale_1 + "\u0000" + b.state.rationale_2 ? -1 : 1));

const llama = await getLlama({ gpu: "metal" });
const model = await llama.loadModel({ modelPath: MODEL, gpuLayers: "max" });
const ctx = await model.createContext({ contextSize: CTX, batchSize: 512 });
const seq = ctx.getSequence();
const tok = (s) => model.tokenize(s, true);
const ids = (words) => [...new Set(words.map((w) => model.tokenize(w, false)).filter((t) => t.length === 1).map((t) => t[0]))];
const T = ids(["true", "True", " true", " True", "TRUE"]), F = ids(["false", "False", " false", " False", "FALSE"]);
const out = fs.openSync(args.out, "a");
const t0 = Date.now(); let n = 0, ntok = 0, reused = 0;
for (const r of todo) {
  const t1 = Date.now();
  let toks = tok(prefix(r.state) + suffix(r.type, r.state));
  if (toks.length > CTX - 8) toks = toks.slice(0, CTX - 400).concat(tok(suffix(r.type, { text: "" })).slice(-200)); // safety (rare)
  const have = seq.contextTokens; let k = 0;
  while (k < have.length && k < toks.length - 1 && have[k] === toks[k]) k++;
  if (k < have.length) await seq.eraseContextTokenRanges([{ start: k, end: have.length }]);
  reused += k; ntok += toks.length - k;
  const input = toks.slice(k).map((t, i, A) => (i === A.length - 1 ? [t, { generateNext: { probabilities: true } }] : t));
  const res = await seq.controlledEvaluate(input);
  const pr = res[res.length - 1].next.probabilities;
  const pt = T.reduce((a, t) => a + (pr.get(t) || 0), 0), pf = F.reduce((a, t) => a + (pr.get(t) || 0), 0);
  const p = pt + pf > 0 ? pt / (pt + pf) : 0.5;
  fs.writeSync(out, JSON.stringify({ rid: r.rid, type: r.type, p_local: p, lo: +(Math.log(pt + 1e-30) - Math.log(pf + 1e-30)).toFixed(3), mass: +(pt + pf).toFixed(4), ms: Date.now() - t1 }) + "\n");
  n++;
  if (n % 50 === 0) process.stderr.write(`[local_gate] ${n}/${todo.length} ${(n / ((Date.now() - t0) / 1000)).toFixed(2)} req/s new_tok=${ntok} reused_tok=${reused}\n`);
}
const s = (Date.now() - t0) / 1000;
console.log(JSON.stringify({ done: n, skipped_already: done.size, seconds: +s.toFixed(1), req_per_s: +(n / s).toFixed(3), new_tokens: ntok, reused_tokens: reused }));
await ctx.dispose(); await model.dispose();
