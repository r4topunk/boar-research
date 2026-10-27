// VG v4 question gate on Sonar's 1,328 EN dev messages: does any v4-only check (threshold, superlative, either-way compare)
// fire when the message is paired with answers built to trip it? (No stored answers exist for these messages.)
import fs from "node:fs";
const V = (await import(process.argv[2] + "/src/routing/verdictGuard.ts")).verdictGuard;
const B = "<workspace>", E = `${B}/rnd/research/sonar/exp/30-learned-detector/data/`;
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const last = (d: any) => { const t = d.turns.at(-1); return typeof t === "string" ? t : d.turns.filter((x: any) => x.role === "user").at(-1).text; };
const qs = [...jl(E + "aligned-en.jsonl"), ...jl(E + "terse-live.jsonl").filter((d: any) => d.lang === "en"), ...jl(`${B}/rnd/research/compass/exp/emergency-dev/dev.jsonl`).filter((d: any) => (d.lang ?? "en") === "en")].map(last);
const PROBES = [
  "Yes, it is. It is about 10 m.", "No, it is not. It is about 99,999 m.", "Yes. It has about 5 million people.", "No, it isn't. It is about 99,999 km.",
  "No, it is not the largest. It is the largest in the world.", "Yes, it is. It has fewer people than India.", "No. It is the largest.",
];
const hits = qs.filter((q) => PROBES.some((p) => V(q, p)));
console.log(`v4 question gate on ${qs.length} EN dev messages: ${hits.length}${hits.length ? "\n  " + hits.join("\n  ") : ""}`);
