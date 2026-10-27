// Card picker prototype (Anvil, dev only): one 4B forward over a cached card-list prompt (CP1.txt), next-token probs over 30
// single-token codes; pick = argmax code, NONE if its share of code mass < 0.5. Baseline = engine conversationCondition (regex).
// npx tsx cp.mts <tree> <out.jsonl>   items: Compass emergency-dev emergencies (gold `cond`).
import fs from "node:fs";
const [tree, outPath] = process.argv.slice(2);
const D = "<workspace>/rnd/research/anvil/exp/card-picker";
const K = await import(`${tree}/src/routing/conditionCards.ts`);
const sys = fs.readFileSync(`${D}/${process.env.P ?? "CP1"}.txt`, "utf8").trim();
const CODES = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z AA BB CC DD".split(" ");
const KEYS = ["altitude","anaphylaxis","animalbite","battery","beesting","bleeding","burn","choking","chokinginfant","co","drowning","earthquake","electric","eyechem","frostbite","headinjury","heartattack","heatexhaustion","heatstroke","hypoglycemia","hypothermia","jellyfish","marinepuncture","nosebleed","scorpion","seizure","stroke","tick","tsunami","NONE"];
const { getLlama } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf", gpuLayers: 0 });
const ctx = await model.createContext({ contextSize: 4096, threads: 4 });
const seq = ctx.getSequence();
const codeTok = CODES.map((c) => (model.tokenize(c) as number[])[0]);
if (new Set(codeTok).size !== CODES.length) throw new Error("code tokens not unique");
const clip = (t: string) => (t.length > 280 ? `${t.slice(0, 280).trimEnd()}…` : t);
const items = fs.readFileSync("<workspace>/rnd/research/compass/exp/emergency-dev/dev.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((r: any) => r.emergency);
let prev: number[] = [];
const out: any[] = [];
for (const it of items) {
  const turns = it.turns.map((t: any) => [t.role, t.text]); let k = turns.length - 1; while (turns[k][0] !== "user") k--;
  const msg = turns[k][1], hist = turns.slice(0, k).slice(-6);
  const user = hist.length ? `Conversation so far:\n${hist.map(([r, t]: any) => `${r}: ${clip(t)}`).join("\n")}\n\nLast message: ${msg}` : msg;
  const tokens: number[] = model.tokenize(`<|im_start|>system\n${sys}<|im_end|>\n<|im_start|>user\n${user}<|im_end|>\n<|im_start|>assistant\n`, true) as any;
  let j = 0; while (j < prev.length && j < tokens.length - 1 && prev[j] === tokens[j]) j++;
  if (seq.nextTokenIndex > j) await seq.eraseContextTokenRanges([{ start: j, end: seq.nextTokenIndex }]);
  const rest = tokens.slice(j);
  const t0 = performance.now();
  const o = await seq.controlledEvaluate(rest.map((t, i) => (i === rest.length - 1 ? [t, { generateNext: { probabilities: true, options: { temperature: 0 } } }] : t)) as any);
  const ms = performance.now() - t0; prev = tokens;
  const pr: Map<number, number> = (o as any)[rest.length - 1].next.probabilities;
  const ps = codeTok.map((t) => pr.get(t) ?? 0), mass = ps.reduce((a, b) => a + b, 0);
  const top = ps.indexOf(Math.max(...ps)), share = mass > 0 ? ps[top] / mass : 0;
  const pick = mass > 0 && share >= 0.5 ? KEYS[top] : "NONE";
  const userTurns = turns.filter((t: any) => t[0] === "user").map((t: any) => t[1]);
  const rc = K.conversationCondition(msg, userTurns.slice(0, -1)).condition;
  out.push({ id: it.id, gold: it.cond, sev: it.sev, multi: hist.length > 0, pick, raw: KEYS[top], share, mass, regex: rc && rc !== "MULTI" ? rc : "NONE", regexRaw: rc, newTok: rest.length, ms: Math.round(ms) });
}
fs.writeFileSync(outPath, out.map((x) => JSON.stringify(x)).join("\n") + "\n");
const isKey = (g: string) => KEYS.includes(g) && g !== "NONE";
const ok = (p: string, g: string) => p === g || (g === "other:febrile-seizure" && p === "seizure");
for (const f of ["pick", "raw", "regex"]) {
  const r = out.filter((x) => x.gold !== "other:snakebite");
  const cardItems = r.filter((x) => isKey(x.gold)), other = r.filter((x) => !isKey(x.gold));
  const right = cardItems.filter((x) => ok(x[f], x.gold)).length;
  const wrong = r.filter((x) => x[f] !== "NONE" && !ok(x[f], x.gold)).length;
  const noneOnCard = cardItems.filter((x) => x[f] === "NONE").length;
  console.log(`${f.padEnd(5)} right card ${right}/${cardItems.length} · NONE on a card condition ${noneOnCard} · WRONG card ${wrong}/${r.length} (of which on 'other' conditions ${other.filter((x) => x[f] !== "NONE" && !ok(x[f], x.gold)).length}/${other.length})`);
}
