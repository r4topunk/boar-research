// Offline replay: Kiln exp-01 captured app prompts (lantern52, rows with sources) on Qwen2.5-1.5B Q4_K_M,
// three prompt arms, scored by the 0cfd4a77 compact citation gate (gate.mjs).
// Usage: node run.mjs <arm A0|A1|A2> <temperature> <seed> <out.jsonl>
import fs from "node:fs";
import { createRequire } from "node:module";
import { compactGate } from "./gate.mjs";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama, LlamaChatSession } = await import(require.resolve("node-llama-cpp"));

const [arm, tempS, seedS, out] = process.argv.slice(2);
const CAPTURE = "<workspace>/rnd/kiln/exp-01-inram-moe-reader/capture/lantern52.jsonl";
const MODEL = "<workspace>/shared-models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf";

const OLD_RULE = "cite a source you used by its number, like [1] or [2].";
const NEW_RULE =
  "end every sentence that uses the context with the number of the source it comes from, like [1], and state its facts with that source's own words.";
const EXEMPLAR =
  "\n\nExample of the answer style:\nContext:\n[1] Monsoon\nA monsoon is a seasonal change in the direction of the prevailing winds of a region, which causes wet and dry seasons.\n" +
  "[2] Desert\nA desert is a region that receives very little precipitation.\nQuestion: What is a monsoon?\n" +
  "Answer: A monsoon is a seasonal change in the direction of a region's prevailing winds [1]. It causes wet and dry seasons [1].";

function variant(system) {
  if (arm === "A0") return system;
  if (!system.includes(OLD_RULE)) throw new Error("rule sentence not found");
  let s = system.replace(OLD_RULE, NEW_RULE);
  if (arm === "A2") {
    const i = s.indexOf("\n\nContext:\n");
    if (i < 0) throw new Error("no Context section");
    s = s.slice(0, i) + EXEMPLAR + s.slice(i);
  }
  return s;
}

const rows = fs.readFileSync(CAPTURE, "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((r) => r.promptSources?.length);
const llama = await getLlama();
const model = await llama.loadModel({ modelPath: MODEL });
const context = await model.createContext({ contextSize: 4096 });
const w = fs.createWriteStream(out);
for (const r of rows) {
  const msgs = r.kilnCaptured[0].messages;
  const system = variant(msgs.find((m) => m.role === "system").content);
  const user = msgs.find((m) => m.role === "user").content;
  const seq = context.getSequence();
  const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: system });
  const t0 = Date.now();
  const raw = await session.prompt(user, { temperature: Number(tempS), seed: Number(seedS), maxTokens: 512 });
  const ms = Date.now() - t0;
  session.dispose();
  seq.dispose();
  const g = compactGate(raw, r.promptSources);
  const answer = g.declined ? "The passages found don't support this answer." : g.text;
  w.write(JSON.stringify({ queryId: r.queryId, category: r.category, arm, temp: Number(tempS), seed: Number(seedS), raw, gate: g.code, codes: g.codes, rawHasCite: g.rawHasCite, declined: g.declined, answer, ms }) + "\n");
  process.stdout.write(`${r.queryId} ${g.code}\n`);
}
w.end();
await context.dispose();
await model.dispose();
