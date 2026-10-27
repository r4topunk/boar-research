// PICK + VERIFY-as-continuation (Anvil, dev only): pick forward (CP1) on the cached prefix, then append the picked code as the
// assistant turn + a short user check turn (V2c) on the SAME KV — the message is never prefilled twice. Keep iff p(YES) >= 0.5.
// npx tsx cpv.mts <tree> <out.jsonl>   [P=CP1]
import fs from "node:fs";
const [tree, outPath] = process.argv.slice(2);
const D = "<workspace>/rnd/research/anvil/exp/card-picker";
const K = await import(`${tree}/src/routing/conditionCards.ts`);
const sys = fs.readFileSync(`${D}/${process.env.P ?? "CP1"}.txt`, "utf8").trim();
const check = fs.readFileSync(`${D}/V2c.txt`, "utf8").trim();
const CODES = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z AA BB CC DD".split(" ");
const KEYS = ["altitude","anaphylaxis","animalbite","battery","beesting","bleeding","burn","choking","chokinginfant","co","drowning","earthquake","electric","eyechem","frostbite","headinjury","heartattack","heatexhaustion","heatstroke","hypoglycemia","hypothermia","jellyfish","marinepuncture","nosebleed","scorpion","seizure","stroke","tick","tsunami","NONE"];
const TITLE: Record<string, string> = {};
for (const l of fs.readFileSync(`${D}/CP1.txt`, "utf8").split("\n")) { const m = l.match(/^([A-Z]{1,2}) (.+)$/); if (m) TITLE[m[1]] = m[2]; }
const { getLlama } = await import("<workspace>/boar-app/node_modules/node-llama-cpp/dist/index.js");
const model = await (await getLlama({ gpu: false })).loadModel({ modelPath: "<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf", gpuLayers: 0 });
const ctx = await model.createContext({ contextSize: 4096, threads: 4 });
const seq = ctx.getSequence();
const codeTok = CODES.map((c) => (model.tokenize(c) as number[])[0]);
const [yT, nT] = ["YES", "NO"].map((w) => (model.tokenize(w) as number[])[0]);
const clip = (t: string) => (t.length > 280 ? `${t.slice(0, 280).trimEnd()}…` : t);
const items = fs.readFileSync("<workspace>/rnd/research/compass/exp/emergency-dev/dev.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((r: any) => r.emergency);
const fwd = async (toks: number[]) => {
  const o = await seq.controlledEvaluate(toks.map((t, i) => (i === toks.length - 1 ? [t, { generateNext: { probabilities: true, options: { temperature: 0 } } }] : t)) as any);
  return (o as any)[toks.length - 1].next.probabilities as Map<number, number>;
};
let prev: number[] = [];
const out: any[] = [];
for (const it of items) {
  const turns = it.turns.map((t: any) => [t.role, t.text]); let k = turns.length - 1; while (turns[k][0] !== "user") k--;
  const msg = turns[k][1], hist = turns.slice(0, k).slice(-6);
  const user = hist.length ? `Conversation so far:\n${hist.map(([r, t]: any) => `${r}: ${clip(t)}`).join("\n")}\n\nLast message: ${msg}` : msg;
  const tokens: number[] = model.tokenize(`<|im_start|>system\n${sys}<|im_end|>\n<|im_start|>user\n${user}<|im_end|>\n<|im_start|>assistant\n`, true) as any;
  let j = 0; while (j < prev.length && j < tokens.length - 1 && prev[j] === tokens[j]) j++;
  if (seq.nextTokenIndex > j) await seq.eraseContextTokenRanges([{ start: j, end: seq.nextTokenIndex }]);
  const pr = await fwd(tokens.slice(j));
  prev = tokens;
  const ps = codeTok.map((t) => pr.get(t) ?? 0), top = ps.indexOf(Math.max(...ps)), pick = KEYS[top];
  let verified = "NONE", pYes: number | null = null, vTok = 0;
  if (pick !== "NONE") {
    const cont: number[] = model.tokenize(`${CODES[top]}<|im_end|>\n<|im_start|>user\n${check.replace("{TITLE}", TITLE[CODES[top]])}<|im_end|>\n<|im_start|>assistant\n`, true) as any;
    vTok = cont.length;
    const pv = await fwd(cont);
    prev = [...tokens, ...cont]; // the next item erases after its common prefix with this
    const y = pv.get(yT) ?? 0, n = pv.get(nT) ?? 0; pYes = y + n > 0 ? y / (y + n) : 0;
    if (pYes >= 0.5) verified = pick;
  }
  const userTurns = turns.filter((t: any) => t[0] === "user").map((t: any) => t[1]);
  const rc = K.conversationCondition(msg, userTurns.slice(0, -1)).condition;
  out.push({ id: it.id, gold: it.cond, sev: it.sev, pick, verified, pYes, vTok, regex: rc && rc !== "MULTI" ? rc : "NONE" });
}
fs.writeFileSync(outPath, out.map((x) => JSON.stringify(x)).join("\n") + "\n");
const ok = (p: string, g: string) => p === g || (g === "other:febrile-seizure" && p === "seizure") || (g === "other:magnet-ingestion" && p === "battery");
const rows = out.filter((x) => x.gold !== "other:snakebite");
for (const f of ["pick", "verified", "regex"]) {
  const right = rows.filter((x) => KEYS.includes(x.gold) && ok(x[f], x.gold)).length, wrong = rows.filter((x) => x[f] !== "NONE" && !ok(x[f], x.gold)).length;
  console.log(`${f.padEnd(9)} right ${right}/103 · wrong ${wrong}/177`);
}
const vt = rows.filter((x) => x.vTok).map((x) => x.vTok).sort((a, b) => a - b);
console.log(`verify-continuation new tokens p50 ${vt[Math.floor(vt.length / 2)]} max ${vt[vt.length - 1]}`);
