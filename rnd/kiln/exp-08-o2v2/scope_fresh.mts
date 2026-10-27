// exp-08 diagnostic (not part of the frozen verdict): O2 scope (o2Kind) of the new fresh items.
import { readFileSync } from "node:fs";
import { o2Kind } from "../src/routing/o2WeakSupport.ts";
const qs = readFileSync(new URL("./o2v2c-fresh.jsonl", import.meta.url), "utf8").trim().split("\n").map((l) => JSON.parse(l));
for (const q of qs) console.log(JSON.stringify({ id: q.id, type: q.o2_type, lang: q.lang, kind: o2Kind(q.question), q: q.question }));
