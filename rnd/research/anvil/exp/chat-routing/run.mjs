// Chat routing prototype (Anvil, 2026-10-02 night): A = native tool call, A-logit = p(<tool_call>) at the first answer token,
// B = Jev-style label gate (one prefill, next-token probs for SEARCH vs ANSWER). Desktop CPU, node-llama-cpp 3.21.1, greedy.
//   node run.mjs MODEL.gguf TAG   -> runs-<TAG>.jsonl
import fs from "node:fs";
import { getLlama, readGgufFileInfo } from "<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js";
import { Template } from "<workspace>/boar-app/node_modules/@huggingface/jinja/dist/index.js";

const [modelPath, tag] = process.argv.slice(2);
const B_ONLY = process.env.B_ONLY === "1";
let SYSB;
const items = fs.readFileSync(process.env.ITEMS || "items.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l));

const SYS_A = `You are BOAR, an offline assistant running on the user's phone. You have a search tool over the offline library (encyclopedia, travel guides, medical and practical guides).
Call search when the user's message needs facts, explanations, places, health, safety or travel information. Do not call it for greetings, thanks, small talk, questions about yourself, arithmetic, or rewriting/translating text that is already in the conversation; answer those directly and briefly.
When you call search, write a short self-contained query in the language of the library content you expect (resolve follow-ups using the conversation).`;
const TOOLS = [{ type: "function", function: { name: "search", description: "Search the offline library. Returns passages with sources.",
  parameters: { type: "object", properties: { query: { type: "string", description: "Self-contained search query" } }, required: ["query"] } } }];
const SYS_B = `You are BOAR's router. Decide whether answering the user's last message needs a search in the offline library (facts, explanations, places, health, safety, travel): SEARCH. Or whether it can be answered directly without sources (greetings, thanks, small talk, questions about the assistant, arithmetic, rewriting or translating text already in the conversation): ANSWER.
Reply with exactly one word: SEARCH or ANSWER.`;
const SYS_B4_EX = `\n\nExamples:\n"oi!" -> ANSWER\n"good evening" -> ANSWER\n"obrigado!" -> ANSWER\n"who made you?" -> ANSWER\n"what is 12 times 7?" -> ANSWER\n"make that shorter" -> ANSWER\n"lol" -> ANSWER\n"capital da Austrália" -> SEARCH\n"how tall is the Eiffel Tower?" -> SEARCH\n"como chegar em Ouro Preto de ônibus?" -> SEARCH\n"is it safe to swim after eating?" -> SEARCH\n"what is a rollup?" -> SEARCH\n"e quanto custa?" (after a travel answer) -> SEARCH`;
const SYS_B3 = `You are BOAR's router. BOAR answers questions about the world only from its offline library, never from memory.
SEARCH: the last message asks for any fact, explanation, advice, place, route, rule, health, safety or travel information, even if you think you know the answer.
ANSWER: the last message is a greeting, thanks, small talk, a question about BOAR itself, arithmetic, or a request to rewrite or translate text already in the conversation.
Reply with exactly one word: SEARCH or ANSWER.`;

SYSB = process.env.B4 === "1" ? SYS_B3.replace("\nReply with", SYS_B4_EX + "\n\nReply with") : process.env.B3 === "1" ? SYS_B3 : SYS_B;
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath, gpuLayers: 0 });
const ctx = await model.createContext({ contextSize: 4096, threads: 4, batchSize: 512 });
const seq = ctx.getSequence();
const info = await readGgufFileInfo(modelPath);
const tmpl = new Template(info.metadata.tokenizer.chat_template);
const render = (messages, tools) => tmpl.render({ messages, tools, add_generation_prompt: true, bos_token: "", eos_token: "" });
const tok = (s) => model.tokenize(s, true);
const detok = (ts) => model.detokenize(ts, true);
const msgsB = (it) => ((B_ONLY || process.env.FOLD === "1") && it.history ? [{ role: "system", content: SYSB }, { role: "user", content: "Conversation so far:\n" + it.history.map(([r, c]) => `${r}: ${c}`).join("\n") + "\n\nLast message: " + it.msg }] : msgs(SYSB, it));
const msgs = (sys, it) => [{ role: "system", content: sys }, ...(it.history || []).map(([role, content]) => ({ role, content })), { role: "user", content: it.msg }];

const TOOL_TOK = tok("<tool_call>");
if (TOOL_TOK.length !== 1) throw new Error("<tool_call> is not one token: " + TOOL_TOK);
const S = tok("SEARCH")[0], A = tok("ANSWER")[0];
if (S === A) throw new Error("label first tokens collide");
const EOG = new Set([...tok("<|im_end|>"), model.tokens.eos].filter((t) => t != null));

const common = (a, b) => { let i = 0; while (i < a.length && i < b.length && a[i] === b[i]) i++; return i; };
// static (cacheable) prefix = tokens shared by two prompts that differ only in the user message
const prefixA = common(tok(render(msgs(SYS_A, { msg: "x" }), TOOLS)), tok(render(msgs(SYS_A, { msg: "y" }), TOOLS)));
const prefixB = common(tok(render(msgs(SYSB, { msg: "x" }))), tok(render(msgs(SYSB, { msg: "y" }))));

async function firstProbs(tokens) {
  await seq.clearHistory();
  const input = tokens.map((t, i) => (i === tokens.length - 1 ? [t, { generateNext: { probabilities: true, token: true, options: { temperature: 0 } } }] : t));
  const t0 = performance.now();
  const out = await seq.controlledEvaluate(input);
  const ms = performance.now() - t0;
  const next = out[tokens.length - 1].next;
  return { ms, probs: next.probabilities, token: next.token };
}

const out = fs.createWriteStream(`runs-${tag}.jsonl`);
// warm-up
await firstProbs(tok(render(msgs(SYS_B, { msg: "hello" }))));
for (const it of items) {
  // ---- B: label gate
  const pb = tok(render(msgsB(it)));
  const b = await firstProbs(pb);
  const pS = b.probs.get(S) ?? 0, pA = b.probs.get(A) ?? 0;
  const bScore = pS / (pS + pA || 1);
  if (B_ONLY) { out.write(JSON.stringify({ id: it.id, label: it.label, kind: it.kind, tag, B: { decision: bScore >= 0.5 ? "SEARCH" : "ANSWER", score: +bScore.toFixed(4), pLabels: +(pS + pA).toFixed(4), promptTokens: pb.length, staticPrefix: prefixB, prefillMs: Math.round(b.ms) } }) + "\n"); console.log(it.id, it.label, bScore.toFixed(3), (pS + pA).toFixed(3)); continue; }
  // ---- A: tool-calling chat; A-logit = p(<tool_call>) at the first assistant token; then greedy continue
  const pa = tok(render(msgs(SYS_A, it), TOOLS));
  const a = await firstProbs(pa);
  const pTool = a.probs.get(TOOL_TOK[0]) ?? 0;
  const gen = [a.token];
  const t1 = performance.now();
  if (!EOG.has(a.token)) {
    for await (const t of seq.evaluate([a.token], { temperature: 0 })) {
      if (EOG.has(t) || gen.length >= 96) break;
      gen.push(t);
      if (detok(gen).includes("</tool_call>")) break;
    }
  }
  const decodeMs = performance.now() - t1;
  const text = detok(gen);
  let call = null, formatOk = null;
  if (text.includes("<tool_call>")) {
    const m = text.match(/<tool_call>\s*([\s\S]*?)\s*<\/tool_call>/);
    try { const j = JSON.parse(m[1]); formatOk = j.name === "search" && typeof j.arguments?.query === "string" && j.arguments.query.length > 0; call = j; }
    catch { formatOk = false; }
  }
  const looksLikeCallInText = !text.includes("<tool_call>") && /"name"\s*:\s*"search"|search\(/.test(text);
  const row = {
    id: it.id, label: it.label, kind: it.kind, tag,
    B: { decision: bScore >= 0.5 ? "SEARCH" : "ANSWER", score: +bScore.toFixed(4), pLabels: +(pS + pA).toFixed(4), promptTokens: pb.length, staticPrefix: prefixB, prefillMs: Math.round(b.ms) },
    A: { decision: text.includes("<tool_call>") || looksLikeCallInText ? "SEARCH" : "ANSWER", pTool: +pTool.toFixed(4), formatOk, looksLikeCallInText,
         query: call?.arguments?.query ?? null, promptTokens: pa.length, staticPrefix: prefixA, prefillMs: Math.round(a.ms),
         genTokens: gen.length, decodeMs: Math.round(decodeMs), text: text.slice(0, 200) },
  };
  out.write(JSON.stringify(row) + "\n");
  console.log(it.id, it.label, "B", row.B.decision, row.B.score, "| A", row.A.decision, row.A.pTool, row.A.query ?? text.slice(0, 50).replace(/\n/g, " "));
}
out.end();
await ctx.dispose(); await model.dispose();
