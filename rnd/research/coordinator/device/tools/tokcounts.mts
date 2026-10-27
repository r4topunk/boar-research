// A15-LATENCY-BUDGET helper: token counts of the fixed prompt parts of cut 4 (Qwen3-4B tokenizer, vocab only; light).
// usage: tsx tokcounts.mts <engine-tree-root> <out.json>      (root = wt/instsubj, read-only)
import { writeFileSync } from "node:fs";
import { join } from "node:path";
const [root, out] = process.argv.slice(2);
const { getLlama } = await import(join(root, "node_modules/node-llama-cpp/dist/index.js"));
const pure: any = await import(join(root, "src/rag/pure.ts"));
const pers: any = await import(join(root, "src/constants/personalities.ts"));
const gate: any = await import(join(root, "src/routing/routeGate.ts"));
const p = pers.getPersonality(pers.DEFAULT_PERSONALITY_ID);
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf", vocabOnly: true });
const tok = (s: string) => model.tokenize(s, true).length; // special tokens parsed (ChatML markers = 1 token each)
const chatml = (sys: string, user: string) => `<|im_start|>system\n${sys}<|im_end|>\n<|im_start|>user\n${user}<|im_end|>\n<|im_start|>assistant\n`;

// Gate: fixed part = system message (+ template head); new part = user message + template tail.
const gateSys = gate.ROUTE_GATE_SYSTEM as string;
const gateFixed = tok(`<|im_start|>system\n${gateSys}<|im_end|>\n`);
const gateQ = (q: string) => tok(chatml(gateSys, q)) - gateFixed;
// Answer: cacheable prefix = ChatML head + answerPromptPrefix(system); the rest is sources + question.
const ap = pure.answerPromptPrefix(p.systemPrompt);
const ansPrefix = tok(`<|im_start|>system\n${ap.system}`);
const instrOnly = tok(`<|im_start|>system\n${p.systemPrompt.trim()}`); // shared head when the prompt has no sources (no CONTEXT_INSTRUCTION)
const GI = (pure as any).__groundingInstruction; // not exported: rebuild the no-source system head from answerPromptPrefix pieces
const CI = " Use the context below when relevant, and cite a source you used by its number, like [1] or [2]. If the context doesn't cover the question, say so and answer from general knowledge.";
const noSrcSystem = ap.system.replace(CI, ""); // assembleChatMessages with no chunks: instruction + " " + GROUNDING (no CONTEXT_INSTRUCTION)
const noSrcPrefix = tok(`<|im_start|>system\n${noSrcSystem}<|im_end|>\n`);
const sampleQs = ["What is the capital of France?", "What is John Stuart Mill's harm principle in On Liberty, and what are the main objections to it?"];
const res = { gateFixedTokens: gateFixed, gateUserTokens: sampleQs.map(gateQ), answerPrefixTokens: ansPrefix, answerInstructionOnlyTokens: instrOnly, answerNoSourceSystemTokens: noSrcPrefix, contextInstructionPresent: ap.system.includes(CI), templateOverheadPerMsg: tok(chatml("", "")) };
writeFileSync(out, JSON.stringify(res, null, 1));
console.log(JSON.stringify(res));
