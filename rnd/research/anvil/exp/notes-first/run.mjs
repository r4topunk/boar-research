// Offline replay: Kiln exp-01 captured app prompts (lantern52, 40 rows with sources; built for Qwen3-4B by app 3bb0a3f)
// on Qwen3-4B-Instruct-2507 Q4_K_M. Arms: N0 = as captured; N1 = capped "notes first" (Chain-of-Note style):
// the model writes ≤ 3 short notes quoting the sources, then "Answer:"; only the text after "Answer:" is scored.
// Usage: node run.mjs <N0|N1> <temperature> <seed> <out.jsonl>
import fs from "node:fs";
import { createRequire } from "node:module";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama, LlamaChatSession } = await import(require.resolve("node-llama-cpp"));

const [arm, tempS, seedS, out] = process.argv.slice(2);
const CAPTURE = "<workspace>/rnd/kiln/exp-01-inram-moe-reader/capture/lantern52.jsonl";
const MODEL = "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf";
const NOTES =
  "\n\nBefore answering, write a line starting with \"Notes:\" with at most 3 short notes (under 40 words in total): " +
  "for each source that matters, what it says about the question, with its number like [1]; write \"Notes: none relevant\" if no source covers it. " +
  "Then write \"Answer:\" and the answer.";

const rows = fs.readFileSync(CAPTURE, "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((r) => r.promptSources?.length);
const llama = await getLlama();
const model = await llama.loadModel({ modelPath: MODEL });
const context = await model.createContext({ contextSize: 4096 });
const w = fs.createWriteStream(out);
for (const r of rows) {
  const msgs = r.kilnCaptured[0].messages;
  let system = msgs.find((m) => m.role === "system").content;
  if (arm === "N1") {
    const i = system.indexOf("\n\nContext:\n");
    system = (i < 0 ? system + NOTES : system.slice(0, i) + NOTES + system.slice(i));
  }
  const user = msgs.find((m) => m.role === "user").content;
  const seq = context.getSequence();
  const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: system });
  const t0 = Date.now();
  let firstAnswerMs = null, buf = "";
  const raw = await session.prompt(user, {
    temperature: Number(tempS), seed: Number(seedS), maxTokens: 512,
    onTextChunk: (t) => { buf += t; if (firstAnswerMs === null && (arm === "N0" ? buf.length > 0 : /Answer:/i.test(buf))) firstAnswerMs = Date.now() - t0; },
  });
  const ms = Date.now() - t0;
  session.dispose(); seq.dispose();
  const m = /Answer:\s*([\s\S]*)$/i.exec(raw);
  const answer = arm === "N1" ? (m ? m[1].trim() : raw.trim()) : raw.trim();
  const notes = arm === "N1" ? (m ? raw.slice(0, m.index).trim() : "") : "";
  const outTokens = model.tokenize(raw).length;
  const noteTokens = notes ? model.tokenize(notes).length : 0;
  w.write(JSON.stringify({ queryId: r.queryId, category: r.category, arm, temp: Number(tempS), seed: Number(seedS), raw, notes, answer, declined: false, ms, firstAnswerMs, outTokens, noteTokens, parsed: arm === "N0" || !!m }) + "\n");
}
w.end();
await context.dispose();
await model.dispose();
