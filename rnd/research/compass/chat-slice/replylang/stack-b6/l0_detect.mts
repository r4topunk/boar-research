// L0 (mechanism only, no model): replyLanguage() from the arm vs the expected reply language.
// (1) chat-slice v0 (dev): 64 items, last user turn + history; expected = REPLY_LANG override else item lang.
// (2) bench v0.1 public (60 EN) + safety track (12 EN): must stay null/"en" (no line → prompt unchanged).
// Usage: tsx l0_detect.mts <engine tree> <slice.v0.jsonl> <bench dir>
import { readFileSync } from "node:fs";
const [tree, slicePath, bench] = process.argv.slice(2);
const ctx = await import(`${tree}/src/routing/context.ts`); const { replyLanguage, isPortugueseQuestion } = ctx;
const OVERRIDE: Record<string, string> = { "cs-037": "pt" };
const lines = (p: string) => readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
let ok = 0, none = 0; const bad: string[] = []; const base = { ok: 0 };
for (const it of slicePath.split(",").flatMap(lines)) {
  const turns = it.turns; const q = turns[turns.length - 1].text;
  const got = replyLanguage(q, { turns: turns.slice(0, -1) }) ?? "none";
  const want = it.reply_lang ?? OVERRIDE[it.id] ?? it.lang;
  const old = isPortugueseQuestion(q) ? "pt" : "none";               // main: PT line only, last turn only
  base.ok += (old === want) || (want === "en" && old === "none") ? 1 : 0;
  const good = got === want || (want === "en" && got === "none");
  ok += good ? 1 : 0; none += got === "none" ? 1 : 0;
  if (!good) bad.push(`${it.id}(${want}→${got}: ${JSON.stringify(q).slice(0, 40)})`);
}
console.log(`chat-slice: line language right ${ok}/${slicePath.split(",").flatMap(lines).length} (main ${base.ok}); no evidence ${none}`);
console.log("  misses:", bad.join(" "));
let flips = 0; const fl: string[] = [];
for (const f of ["questions.public.jsonl", "safety/track.v0.3.jsonl"]) for (const q of lines(`${bench}/${f}`)) {
  const got = replyLanguage(q.question, null); const old = isPortugueseQuestion(q.question) ? "pt" : null;
  if ((got ?? "en") !== (old ?? "en") && !(got === "en" && old === null)) { flips++; fl.push(`${q.id}:${old}→${got}`); }
}
console.log(`bench v0.1 (72 EN): language-line changes vs main ${flips}`, fl.join(" "));
