// SC L0 (criterion arms/sc-L0-criterion.md). usage: tsx sc-l0.mts <engine-tree> <baseline-cut2-tree> [heldout.jsonl]
import fs from "node:fs";
import path from "node:path";
const [tree, base, heldout] = process.argv.slice(2);
const W = await import(path.join(tree, "src/routing/waterSafety.ts"));
const S1 = await import(path.join(tree, "src/routing/firstAidCards.ts"));
const S0 = await import(path.join(base, "src/routing/firstAidCards.ts"));
const C1 = await import(path.join(tree, "src/routing/conditionCards.ts"));
const C0 = await import(path.join(base, "src/routing/conditionCards.ts"));
const B = "<workspace>";
const A = path.join(B, "rnd/research/coordinator/arms");
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const userTurns = (d: any): string[] => (d.turns ?? []).map((t: any) => (typeof t === "string" ? t : t.role === "user" ? t.text : null)).filter(Boolean);
const lastUser = (d: any) => userTurns(d).at(-1) ?? d.text ?? d.question ?? d.query ?? "";
const fire = (q: string) => W.isWaterSafetyQuestion(q);
const out: string[] = [];

// S1
const v01 = jl(`${B}/boar-eval/bench/v0.1/questions.public.jsonl`).filter((q: any) => q.lang === "en");
const d5 = v01.find((q: any) => q.id === "dng-005");
const probes = jl(`${A}/probes/water-safety.probes.jsonl`);
const pos = probes.filter((p: any) => p.expect === "pos"), neg = probes.filter((p: any) => p.expect === "neg");
const posHit = pos.filter((p: any) => fire(p.text));
out.push(`S1 dng-005 ${fire(d5.question) ? "fires" : "NO FIRE"}; dev paraphrases ${posHit.length}/${pos.length} (misses: ${pos.filter((p: any) => !fire(p.text)).map((p: any) => p.id).join(", ") || "none"})`);
const s1 = fire(d5.question) && posHit.length >= 10;

// S2
const E = `${B}/rnd/research/sonar/exp/30-learned-detector/data/`;
const chat: string[] = [];
for (const f of ["slice.v0.jsonl", "v1-fresh/slice.v1.jsonl", "v2-fresh/slice.v2.jsonl"]) for (const d of jl(`${B}/rnd/research/compass/chat-slice/${f}`)) if (d.lang === "en") chat.push(lastUser(d));
const co = (f: string) => jl(`${B}/rnd/research/compass/exp/co-hazard/${f}`).map(lastUser);
const pools: [string, string[]][] = [
  ["aligned-en", jl(E + "aligned-en.jsonl").map(lastUser)],
  ["terse-live-en", jl(E + "terse-live.jsonl").filter((d: any) => d.lang === "en").map(lastUser)],
  ["compass-dev-en", jl(`${B}/rnd/research/compass/exp/emergency-dev/dev.jsonl`).filter((d: any) => (d.lang ?? "en") === "en").map(lastUser)],
  ["co-lookalike-dev", co("lookalike.dev.jsonl")],
  ["co-lookalike-heldout", co("lookalike.heldout.jsonl")],
  ["co-lookalike-heldout3", co("lookalike.heldout3.jsonl")],
  ["chat-slice-en", chat],
  ["v0.1-en minus dng-005", v01.filter((q: any) => q.id !== "dng-005").map((q: any) => q.question)],
];
let poolFires: string[] = [], poolN = 0;
for (const [name, qs] of pools) {
  const f = qs.filter((q) => q && fire(q));
  poolN += qs.length;
  poolFires.push(...f.map((q) => `${name}: ${q.slice(0, 140)}`));
  out.push(`  ${name}: ${f.length}/${qs.length}`);
}
const negFires = neg.filter((p: any) => fire(p.text));
out.push(`S2 pools ${poolFires.length}/${poolN}${poolFires.length ? "\n    " + poolFires.join("\n    ") : ""}; dev hard negatives ${negFires.length}/${neg.length} ${negFires.map((p: any) => p.id).join(" ")}`);
const s2 = poolFires.length === 0 && negFires.length <= 1;

// S3: emergency-dev emergencies the water card would take.
const ed = jl(`${B}/rnd/research/compass/exp/emergency-dev/dev.jsonl`);
const emerg = ed.filter((d: any) => d.emergency === 1);
const taken = emerg.filter((d: any) => fire(lastUser(d)));
out.push(`S3 emergency-dev emergencies (${emerg.length}): water card fires ${taken.length}${taken.map((d: any) => `\n    ${d.id}: ${lastUser(d).slice(0, 140)}`).join("")}`);
const s3 = taken.length === 0;

// S4: snakebite trigger before/after on every pool message (card fast path and condition detection).
const all = [...pools.flatMap(([, q]) => q), ...ed.map(lastUser), ...probes.map((p: any) => p.text)].filter(Boolean);
let diff = 0, snakeFires = 0;
for (const q of all) {
  const a = S0.isSnakebiteFirstAid(q), b = S1.isSnakebiteFirstAid(q);
  const ca = C0.conversationCondition ? C0.conversationCondition(q, []).condition : null;
  const cb = C1.conversationCondition ? C1.conversationCondition(q, []).condition : null;
  if (a !== b || ca !== cb) diff++;
  if (b) snakeFires++;
}
out.push(`S4 snakebite trigger diff ${diff}/${all.length} (fast-path fires ${snakeFires})`);
const s4 = diff === 0;

// S5
let s5: boolean | null = null;
if (heldout) {
  const H = jl(heldout);
  const hp = H.filter((p: any) => p.expect === "pos"), hn = H.filter((p: any) => p.expect === "neg");
  const hr = hp.filter((p: any) => fire(p.text)).length, hf = hn.filter((p: any) => fire(p.text));
  s5 = hr / hp.length >= 0.8 && hf.length <= 1;
  out.push(`S5 held-out: recall ${hr}/${hp.length} (${((100 * hr) / hp.length).toFixed(0)} %), misses ${hp.filter((p: any) => !fire(p.text)).map((p: any) => p.id).join(" ")}; false fires ${hf.length}/${hn.length} ${hf.map((p: any) => `${p.id}: ${p.text}`).join(" | ")}`);
}
out.push(`\nS1 ${s1 ? "PASS" : "FAIL"} · S2 ${s2 ? "PASS" : "FAIL"} · S3 ${s3 ? "PASS" : "FAIL"} · S4 ${s4 ? "PASS" : "FAIL"} · S5 ${s5 === null ? "pending" : s5 ? "PASS" : "FAIL"} · S6 pending (reviewer)`);
console.log(out.join("\n"));
