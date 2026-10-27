// Offline replay: Kiln exp-01 captured app prompts (lantern52, 40 rows with sources) on Qwen3-4B-Instruct-2507 Q4_K_M,
// persona arms. P0 = succinct (as captured, 0cfd4a77 text); P1 = the app's existing "detailed" persona;
// P2 = "complete paragraph" (new wording, one paragraph of 4-6 sentences covering every part asked).
// Usage: node run.mjs <P0|P1|P2> <temperature> <seed> <out.jsonl>
import fs from "node:fs";
import { createRequire } from "node:module";
const require = createRequire("<workspace>/boar-app/package.json");
const { getLlama, LlamaChatSession } = await import(require.resolve("node-llama-cpp"));
const [arm, tempS, seedS, out] = process.argv.slice(2);
const CAPTURE = "<workspace>/rnd/kiln/exp-01-inram-moe-reader/capture/lantern52.jsonl";
const MODEL = "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf";
const SUCC_SYS = "You are Boar, a concise offline research assistant. Answer in 2-3 short, direct sentences or a brief paragraph, no preamble. Do not default to a bulleted list or a single takeaway sentence followed by three bullet points — use bullets only when the content is genuinely a list of distinct items.";
const SUCC_STYLE = "Keep it short: 2-3 sentences. No lists unless the question asks for one.";
const ARMS = {
  P1: {
    sys: "You are Boar, an analytical research partner. Provide thorough, structured explanations with comparisons and evidence.",
    style: "Be thorough: 3-5 paragraphs that cover the key points in depth, with reasons, comparisons and examples. Don't repeat yourself.",
  },
  P2: {
    sys: "You are Boar, an offline research assistant. Answer in one complete paragraph of 4-6 sentences, no preamble: give the direct answer first, then the key facts, reasons or numbers behind it, and cover every part the question asks about (both sides of a comparison). Use bullets only when the content is genuinely a list of distinct items.",
    style: "One paragraph, 4-6 sentences: direct answer first, then the key facts and reasons; cover every part of the question.",
  },
};
const rows = fs.readFileSync(CAPTURE, "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((r) => r.promptSources?.length);
const llama = await getLlama();
const model = await llama.loadModel({ modelPath: MODEL });
const context = await model.createContext({ contextSize: 4096 });
const w = fs.createWriteStream(out);
for (const r of rows) {
  const msgs = r.kilnCaptured[0].messages;
  let system = msgs.find((m) => m.role === "system").content;
  let user = msgs.find((m) => m.role === "user").content;
  if (arm !== "P0") {
    if (!system.startsWith(SUCC_SYS) || !user.includes(SUCC_STYLE)) throw new Error("persona text not found in " + r.queryId);
    system = ARMS[arm].sys + system.slice(SUCC_SYS.length);
    user = user.replace(SUCC_STYLE, ARMS[arm].style);
  }
  const seq = context.getSequence();
  const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: system });
  const t0 = Date.now();
  const raw = await session.prompt(user, { temperature: Number(tempS), seed: Number(seedS), maxTokens: 512 });
  const ms = Date.now() - t0;
  session.dispose(); seq.dispose();
  w.write(JSON.stringify({ queryId: r.queryId, category: r.category, arm, temp: Number(tempS), seed: Number(seedS), answer: raw.trim(), declined: false, ms, outTokens: model.tokenize(raw).length, words: raw.trim().split(/\s+/).length }) + "\n");
}
w.end(); await context.dispose(); await model.dispose();
