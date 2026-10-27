// V-0 runner (implements protocol.md, frozen 0eb7cc82…). Usage: node run_v0.mjs out.jsonl
import fs from "node:fs";
import { createRequire } from "node:module";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama, LlamaChatSession } = await import(require.resolve("node-llama-cpp"));
const L = JSON.parse(fs.readFileSync(new URL("./labels.json", import.meta.url)));
const RUN = { s42: "<workspace>/boar-eval/runs/night-2026-10-01/and-qwen-s42", s43: "<workspace>/boar-eval/runs/night-2026-10-01/and-qwen-s43", s44: "<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44" };
const load = (p) => fs.readFileSync(p, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const Q = Object.fromEntries(load("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl").map((q) => [q.id, q]));
const split = (t) => t.split(/(?<=[.!?])\s+|\n+/).map((s) => s.trim()).filter(Boolean);
const LABEL = "This answer is not from an offline source on this phone; check it before relying on it.";
const pos = new Set(L.positives.map(([s, i]) => s + "|" + i));
const items = [...L.positives.map(([s, i]) => [s, i]), ...L.negative_items.flatMap((i) => L.seeds.map((s) => [s, i]))];
const llama = await getLlama();
const model = await llama.loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf" });
const context = await model.createContext({ contextSize: 2048 });
const out = fs.createWriteStream(process.argv[2]);
const traces = {};
for (const [seed, id] of items) {
  traces[seed] ??= Object.fromEntries(load(RUN[seed] + ".traces.jsonl").map((r) => [r.itemId, r]));
  const text = traces[seed][id].answer.text.replace(LABEL, "").replace(/\s*\[\d+\]/g, "").trim();
  const sents = split(text);
  const user = `Question: ${Q[id].question}\n\nAnswer:\n${sents.map((s, i) => `S${i + 1}: ${s}`).join("\n")}\n\nDoes any later sentence contradict what S1 says? Reply with exactly YES or NO.`;
  const seq = context.getSequence();
  const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: "You check answers for internal consistency." });
  const t0 = Date.now();
  const reply = (await session.prompt(user, { temperature: 0, maxTokens: 4 })).trim();
  const ms = Date.now() - t0;
  seq.dispose();
  const tok = (reply.match(/^[A-Za-z]+/) || [""])[0].toUpperCase();
  const parsed = tok === "YES" || tok === "NO";
  const flag = tok === "YES" && sents.length >= 2;
  const r = { seed, id, positive: pos.has(seed + "|" + id), k: sents.length, reply, parsed, flag, ms };
  out.write(JSON.stringify(r) + "\n");
  console.log(JSON.stringify(r));
}
out.end(); await context.dispose(); await model.dispose();
