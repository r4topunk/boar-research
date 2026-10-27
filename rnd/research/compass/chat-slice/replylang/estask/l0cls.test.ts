import { readFileSync, writeFileSync } from "node:fs";
import { it } from "vitest";
import { classifyTask as now } from "../src/routing/classify";
import { classifyTask as old } from "./classifyOld";
it("l0", () => {
  const sets: Record<string, string> = { "chat-v0": "<workspace>/rnd/research/compass/chat-slice/slice.v0.jsonl", "chat-v1": "<workspace>/rnd/research/compass/chat-slice/v1-fresh/slice.v1.jsonl", "chat-v2": "<workspace>/rnd/research/compass/chat-slice/v2-fresh/slice.v2.jsonl", "emerg-dev": "<workspace>/rnd/research/compass/exp/emergency-dev/dev.jsonl", "v01-public": "<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "v01-safety": "<workspace>/boar-eval/bench/v0.1/safety/track.v0.3.jsonl" };
  const out: string[] = [];
  for (const [name, f] of Object.entries(sets)) {
    const rows = readFileSync(f, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
    const byLang: Record<string, [number, number]> = {}; const ch: string[] = [];
    for (const r of rows) {
      const q: string = r.turns ? r.turns[r.turns.length - 1].text : r.question;
      const lang: string = r.lang ?? "?";
      const a = old(q), b = now(q);
      byLang[lang] ??= [0, 0]; byLang[lang][1]++;
      if (a !== b) { byLang[lang][0]++; ch.push(`   ${r.id} ${lang} ${a}->${b} | ${q.slice(0, 80)}`); }
    }
    out.push(`== ${name}: ` + Object.entries(byLang).map(([l, [c, n]]) => `${l} ${c}/${n}`).join(", "), ...ch);
  }
  writeFileSync("l0tmp/out.txt", out.join("\n"));
});
