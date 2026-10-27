// P3-0 runner (frozen with protocol.json). Usage: node run_p3_0.mjs <s44 prompts dump.jsonl> <s44 traces.jsonl> out.jsonl
import fs from "node:fs";
import { createRequire } from "node:module";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama, LlamaChatSession } = await import(require.resolve("node-llama-cpp"));
const [dumpPath, s44Traces, out] = process.argv.slice(2);
const P = JSON.parse(fs.readFileSync(new URL("./protocol.json", import.meta.url)));
const RUNS = "<workspace>/boar-eval/runs/night-2026-10-01/";
const load = (p) => fs.readFileSync(p, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const dump = Object.fromEntries(load(dumpPath).map((r) => [r.itemId, r.messages]));
const t44 = Object.fromEntries(load(s44Traces).map((r) => [r.itemId, r]));
const traces = {};
const trace = (run, id) => ((traces[run] ??= Object.fromEntries(load(RUNS + run + ".traces.jsonl").map((r) => [r.itemId, r]))))[id];
const split = (t) => t.split(/(?<=[.!?])\s+|\n+/).map((s) => s.trim()).filter(Boolean);
const titles = (r) => JSON.stringify((r?.retrieval?.kept ?? []).map((s) => s.title));
const llama = await getLlama();
const model = await llama.loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf" });
const context = await model.createContext({ contextSize: 4096 });
const w = fs.createWriteStream(out);
for (const [kind, items] of [["pos", P.positives], ["neg", P.negatives]]) for (const it of items) {
  const tr = trace(it.run, it.id), msgs = dump[it.id];
  if (!tr || !msgs || titles(tr) !== titles(t44[it.id])) { w.write(JSON.stringify({ kind, ...it, excluded: true, why: !msgs ? "no dump" : "shown sources differ" }) + "\n"); continue; }
  const answer = tr.answer.text, sents = split(answer);
  const list = sents.map((s, i) => `S${i + 1} «${s.split(/\s+/).slice(0, 6).join(" ")}…»`).join(" ");
  const check = P.check_turn.CHECK.replace("{LIST}", list);
  const seq = context.getSequence();
  const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: msgs.find((m) => m.role === "system").content });
  session.setChatHistory([{ type: "system", text: msgs.find((m) => m.role === "system").content },
    { type: "user", text: msgs.find((m) => m.role === "user").content }, { type: "model", response: [answer] }]);
  const reply = await session.prompt(check, { temperature: 0, maxTokens: 12, budgets: { thoughtTokens: 0 } });
  session.dispose(); seq.dispose();
  const labels = [...new Set([...reply.matchAll(/S(\d+)/gi)].map((m) => Number(m[1])))];
  const parsed = labels.length > 0 || /\bnone\b/i.test(reply);
  w.write(JSON.stringify({ kind, ...it, k: sents.length, reply, labels, parsed,
    hit: kind === "pos" ? labels.some((l) => it.targets.includes(l)) : undefined,
    falseFlag: kind === "neg" ? labels.length > 0 : undefined, guardKeep: labels.length > sents.length / 2 }) + "\n");
}
w.end(); await context.dispose(); await model.dispose();
