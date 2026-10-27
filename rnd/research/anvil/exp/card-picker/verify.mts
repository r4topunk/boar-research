// Verify step (Anvil, dev only): for each picker pick != NONE, one 4B forward "does card X fit?" -> p(YES)/(p(YES)+p(NO)) >= 0.5 keeps it.
// npx tsx verify.mts <picks.jsonl> <out.jsonl>
import fs from "node:fs";
const [inPath, outPath] = process.argv.slice(2);
const D = "<workspace>/rnd/research/anvil/exp/card-picker";
const sys = fs.readFileSync(`${D}/V1.txt`, "utf8").trim();
const TITLE: Record<string, string> = {};
for (const l of fs.readFileSync(`${D}/CP1.txt`, "utf8").split("\n")) { const m = l.match(/^([A-Z]{1,2}) (.+)$/); if (m) TITLE[m[1]] = m[2]; }
const CODES = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z AA BB CC".split(" ");
const KEYS = ["altitude","anaphylaxis","animalbite","battery","beesting","bleeding","burn","choking","chokinginfant","co","drowning","earthquake","electric","eyechem","frostbite","headinjury","heartattack","heatexhaustion","heatstroke","hypoglycemia","hypothermia","jellyfish","marinepuncture","nosebleed","scorpion","seizure","stroke","tick","tsunami"];
const title = (k: string) => TITLE[CODES[KEYS.indexOf(k)]];
const { getLlama } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf", gpuLayers: 0 });
const ctx = await model.createContext({ contextSize: 4096, threads: 4 });
const seq = ctx.getSequence();
const [yT, nT] = ["YES", "NO"].map((w) => (model.tokenize(w) as number[])[0]);
const items = new Map(fs.readFileSync("<workspace>/rnd/research/compass/exp/emergency-dev/dev.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((r: any) => [r.id, r]));
const clip = (t: string) => (t.length > 280 ? `${t.slice(0, 280).trimEnd()}…` : t);
let prev: number[] = [];
const out: any[] = [];
for (const r of fs.readFileSync(inPath, "utf8").trim().split("\n").map((l) => JSON.parse(l))) {
  if (r.pick === "NONE") { out.push({ ...r, verified: "NONE", pYes: null }); continue; }
  const it: any = items.get(r.id);
  const turns = it.turns.map((t: any) => [t.role, t.text]); let k = turns.length - 1; while (turns[k][0] !== "user") k--;
  const hist = turns.slice(0, k).slice(-6);
  const conv = hist.length ? `Conversation so far:\n${hist.map(([a, t]: any) => `${a}: ${clip(t)}`).join("\n")}\n\nLast message: ${turns[k][1]}` : `Message: ${turns[k][1]}`;
  const user = `${conv}\n\nCard: ${title(r.pick)}`;
  const tokens: number[] = model.tokenize(`<|im_start|>system\n${sys}<|im_end|>\n<|im_start|>user\n${user}<|im_end|>\n<|im_start|>assistant\n`, true) as any;
  let j = 0; while (j < prev.length && j < tokens.length - 1 && prev[j] === tokens[j]) j++;
  if (seq.nextTokenIndex > j) await seq.eraseContextTokenRanges([{ start: j, end: seq.nextTokenIndex }]);
  const rest = tokens.slice(j);
  const o = await seq.controlledEvaluate(rest.map((t, i) => (i === rest.length - 1 ? [t, { generateNext: { probabilities: true, options: { temperature: 0 } } }] : t)) as any);
  prev = tokens;
  const pr: Map<number, number> = (o as any)[rest.length - 1].next.probabilities;
  const pY = pr.get(yT) ?? 0, pN = pr.get(nT) ?? 0, pYes = pY + pN > 0 ? pY / (pY + pN) : 0;
  out.push({ ...r, verified: pYes >= 0.5 ? r.pick : "NONE", pYes, vTok: rest.length });
}
fs.writeFileSync(outPath, out.map((x) => JSON.stringify(x)).join("\n") + "\n");
const ok = (p: string, g: string) => p === g || (g === "other:febrile-seizure" && p === "seizure") || (g === "other:magnet-ingestion" && p === "battery");
const rows = out.filter((x) => x.gold !== "other:snakebite");
for (const f of ["pick", "verified", "regex"]) {
  const right = rows.filter((x) => KEYS.includes(x.gold) && ok(x[f], x.gold)).length, wrong = rows.filter((x) => x[f] !== "NONE" && !ok(x[f], x.gold)).length;
  console.log(`${f.padEnd(9)} right ${right}/103 · wrong ${wrong}/177`);
}
