// cv-timing: desktop timing of cut 3 vs cut 3 + CV from the two L0 trace files (desktop numbers, never phone numbers).
// usage: tsx cv-timing.mts <cut3 traces.jsonl> <cv traces.jsonl> [--out cv-timing.txt]
import fs from "node:fs";
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const a = new Map<string, any>(jl(process.argv[2]).map((t: any) => [t.itemId, t]));
const b = new Map<string, any>(jl(process.argv[3]).map((t: any) => [t.itemId, t]));
const med = (x: number[]) => { const s = [...x].sort((p, q) => p - q); return s.length ? (s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2) : NaN; };
const isCV = (t: any) => (t.route?.reasonCodes ?? []).includes("answer:computed-verdict");
const ms = (t: any) => Number(t.timing?.totalMs);
const ids = [...a.keys()].filter((i) => b.has(i));
const cvIds = ids.filter((i) => isCV(b.get(i)));
const other = ids.filter((i) => !isCV(b.get(i)));
const out: string[] = [];
const say = (s: string) => { out.push(s); console.log(s); };
const row = (name: string, set: string[]) => {
  const d = set.map((i) => ms(b.get(i)) - ms(a.get(i)));
  say(`${name.padEnd(34)} n=${String(set.length).padStart(3)}  cut3 median ${(med(set.map((i) => ms(a.get(i)))) / 1000).toFixed(2)} s  CV median ${(med(set.map((i) => ms(b.get(i)))) / 1000).toFixed(2)} s  paired diff median ${(med(d) / 1000).toFixed(2)} s  mean ${(d.reduce((x, y) => x + y, 0) / Math.max(1, d.length) / 1000).toFixed(2)} s`);
};
say("CV desktop timing (Mac mini, node-llama-cpp, 4 threads; totalMs per answer; cut 3 = cut 3 arm, CV = cut 3 + CV arm; same seed 44)");
row("all items", ids);
row("items CV answered", cvIds);
row("items the normal path answered", other);
say(`criterion: median added time on the 4B path <= +2 s (paired diff median on the items CV answered: ${(med(cvIds.map((i) => ms(b.get(i)) - ms(a.get(i)))) / 1000).toFixed(2)} s)`);
const gen = (t: any) => (t.events ?? []).filter((e: any) => e.kind === "generation").length;
say(`model calls per CV answer (median): ${med(cvIds.map((i) => gen(b.get(i))))}; cut 3 on the same items: ${med(cvIds.map((i) => gen(a.get(i))))}`);
fs.writeFileSync(process.argv.includes("--out") ? process.argv[process.argv.indexOf("--out") + 1] : "cv-timing.txt", out.join("\n") + "\n");
