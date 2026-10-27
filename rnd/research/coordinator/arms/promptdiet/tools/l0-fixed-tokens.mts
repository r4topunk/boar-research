// L0 (PROMPTDIET): mean fixed-prompt tokens on the 4B answer path, with the 4B tokenizer (vocab only).
// usage: tsx l0-fixed-tokens.mts <tree-root> <out.json>
// For every v0.1 EN trace that generated (promptTokens > 0) it builds assembleChatMessages exactly as answer.ts does
// (default persona, same query, same number of passages, same titles) with EMPTY passage bodies, so the passages
// are identical and zero-cost in both arms. Fixed tokens = tokens(system) + tokens(user), template overhead excluded
// (same in both arms). Items with no kept passage get NO_SOURCE_INSTRUCTION in the style reminder, as answer.ts does.
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const [root, out] = process.argv.slice(2);
const { getLlama } = await import(join(root, "node_modules/node-llama-cpp/dist/index.js"));
const pure: any = await import(join(root, "src/rag/pure.ts"));
const pers: any = await import(join(root, "src/constants/personalities.ts"));
const ctxm: any = await import(join(root, "src/routing/context.ts"));
const p = pers.getPersonality(pers.DEFAULT_PERSONALITY_ID);
const llama = await getLlama({ gpu: false });
const model = await llama.loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf", vocabOnly: true });
const tok = (s: string) => model.tokenize(s, false, "trimLeadingSpace").length;

const dir = "<workspace>/boar-eval/runs/kiln/cut3-confirm";
const rows: any[] = [];
for (const seed of ["s44", "s45"]) {
  for (const l of readFileSync(`${dir}/cut3-v01-${seed}.traces.jsonl`, "utf8").split("\n").filter(Boolean)) {
    const t = JSON.parse(l);
    if (!(t.timing?.promptTokens > 0)) continue;
    const titles: string[] = (t.retrieval?.kept ?? []).map((k: any) => k.title);
    const chunks = titles.map((title, i) => ({ chunkId: String(i), title, body: "", source: "" }));
    const style = [p.styleReminder, titles.length ? undefined : ctxm.NO_SOURCE_INSTRUCTION].filter(Boolean).join("\n") || undefined;
    const msgs = pure.assembleChatMessages(t.question, chunks, p.systemPrompt, undefined, style);
    const sys = tok(msgs[0].content), usr = tok(msgs[msgs.length - 1].content);
    rows.push({ seed, id: t.itemId, n: titles.length, sys, usr, fixed: sys + usr - tok(t.question), real: t.timing.promptTokens });
  }
}
const mean = (k: string) => rows.reduce((a, r) => a + r[k], 0) / rows.length;
const res = { items: rows.length, meanFixed: mean("fixed"), meanSys: mean("sys"), meanRealPromptTokensOld: mean("real"), rows };
writeFileSync(out, JSON.stringify(res, null, 1));
console.log(JSON.stringify({ ...res, rows: undefined }));
