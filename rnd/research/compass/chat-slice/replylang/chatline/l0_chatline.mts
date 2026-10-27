// L0 (no model) for idea (b): where would the chat-only line fire? Uses B6-alone traces (plan.retrieve = false ⇔ a
// "retrieve:skipped" reason code; health answers always retrieve) and the arm's replyLanguage/isPortugueseQuery.
// Usage: tsx l0_chatline.mts <engine tree>
import { readFileSync, existsSync } from "node:fs";
const tree = process.argv[2];
const { replyLanguage, isPortugueseQuery } = await import(`${tree}/src/routing/context.ts`);
const R = "<workspace>/rnd/research/compass/chat-slice", K = "<workspace>/boar-eval/runs/kiln";
const L = (p: string) => readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const { execSync } = await import("node:child_process");
const langOf = (t: string) => execSync(`python3 -c "import sys,json; sys.path.insert(0,'${R}'); from score_l0 import lang_of; print(lang_of(json.load(sys.stdin)))"`, { input: JSON.stringify(t) }).toString().trim();
const runs: [string, string, string][] = [["v0", `${R}/slice.v0.jsonl`, `${K}/b6replylang/v0-4b-b6gate`], ["v1", `${R}/v1-fresh/slice.v1.jsonl`, `${R}/v1-fresh/runs/stack-4b-b6gate`], ["v2", `${R}/v2-fresh/slice.v2.jsonl`, `${R}/v2-fresh/runs/b6gate`]];
let fire = 0, fireWrongLang = 0, total = 0; const byLang: Record<string, number> = {};
for (const [sl, slice, run] of runs) {
  const T = Object.fromEntries(L(`${run}/traces.jsonl`).map((t: any) => [t.itemId, t]));
  for (const it of L(slice)) {
    total++; const t = T[it.id]; const skipped = (t.route.reasonCodes as string[]).some((c) => c.startsWith("retrieve:skipped"));
    if (!skipped) continue;
    const q = it.turns[it.turns.length - 1].text; const pt = isPortugueseQuery(q);
    const lang = replyLanguage(q, { turns: it.turns.slice(0, -1) }) ?? (pt ? "pt" : null);
    if (lang !== "pt" && lang !== "es") continue;
    fire++; byLang[lang] = (byLang[lang] ?? 0) + 1;
    const want = it.reply_lang ?? (it.id === "cs-037" ? "pt" : it.lang);
    if (langOf(t.answer.text) !== want) fireWrongLang++;
  }
}
console.log(`chat-slice v0+v1+v2 (4B B6-alone traces): line fires on ${fire}/${total} items ${JSON.stringify(byLang)}; of those, B6 alone answered in the wrong language on ${fireWrongLang}`);
// v0.1 guard: any v0.1 item with retrieval skipped in B6 traces?
let v01 = 0, v01skip = 0;
for (const f of [`${K}/l1/b6gate-outofkit-quality-s42/traces.jsonl`]) if (existsSync(f)) for (const t of L(f)) { v01++; if ((t.route.reasonCodes as string[]).some((c) => c.startsWith("retrieve:skipped"))) v01skip++; }
console.log(`v0.1 (B6 outofkit L1 traces): ${v01skip}/${v01} items skip retrieval (the line can only fire there)`);
