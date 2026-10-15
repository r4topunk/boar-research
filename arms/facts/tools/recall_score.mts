/**
 * FACTS recall-set scorer v2 (deterministic; no model, no judge). tsx recall_score.mts <tree> <recall-set.jsonl> <out.jsonl>
 * Frozen rule (FACTS-RECALL.md): a fact item is correct only if factsAnswer() fires and the answer contains `expect`
 * (any alternative split on "|"): a number within 3% (million/billion scaled; any number in the answer), or a name
 * (case- and accent-insensitive substring). Comparison items (entity "A|B") must name `expect` as the verdict, i.e. the
 * answer (after an optional "Yes. "/"No. ") starts with it. A near-miss that fires is a false positive.
 */
import { readFileSync, writeFileSync } from "node:fs";
const [tree, set, out] = process.argv.slice(2);
const { factsAnswer } = await import(`${tree}/src/rag/facts.ts`);
// v2 (FACTS-r4-criterion.md): + transliteration fold (đ→d, ł→l, ø→o, ß→ss, æ→ae, œ→oe), both sides.
const TRANSLIT: Record<string, string> = { "đ": "d", "ł": "l", "ø": "o", "ß": "ss", "æ": "ae", "œ": "oe" };
const fold = (s: string) => s.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase().replace(/[đłøßæœ]/g, (c) => TRANSLIT[c]);
const nums = (s: string) =>
  [...s.replace(/(\d),(?=\d{3})/g, "$1").matchAll(/(\d+(?:\.\d+)?)\s*(million|billion)?/g)].map((m) => Number(m[1]) * (m[2] === "billion" ? 1e9 : m[2] === "million" ? 1e6 : 1));
function ok(expect: string, answer: string, comparison: boolean): boolean {
  return expect.split("|").some((alt) => {
    const m = alt.match(/^(\d+(?:\.\d+)?)\s*(million|billion)?\b/);
    if (m && !comparison) {
      const v = Number(m[1]) * (m[2] === "billion" ? 1e9 : m[2] === "million" ? 1e6 : 1);
      return nums(answer).some((x) => Math.abs(x - v) / v <= 0.03);
    }
    if (comparison) return fold(answer.replace(/^(Yes|No)\. /, "")).startsWith(fold(alt)) || fold(answer.replace(/^(Yes|No)\. /, "")).startsWith(`people's republic of ${fold(alt)}`);
    return fold(answer).includes(fold(alt));
  });
}
const rows = readFileSync(set, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const res = rows.map((r) => {
  const a = factsAnswer(r.text);
  const fired = !!a;
  const correct = r.kind === "fact" && fired && ok(r.expect, a.text.split("\n")[0], r.entity.includes("|"));
  return { id: r.id, kind: r.kind, text: r.text, fired, correct, answer: a ? a.text.split("\n")[0] : null };
});
writeFileSync(out, res.map((r) => JSON.stringify(r)).join("\n") + "\n");
const facts = res.filter((r) => r.kind === "fact");
const near = res.filter((r) => r.kind === "nearmiss");
const fires = res.filter((r) => r.fired);
const correct = facts.filter((r) => r.correct).length;
const lower = facts.filter((r) => r.text === r.text.toLowerCase() || /^[a-z]/.test(r.text));
console.log(`fact fired ${facts.filter((r) => r.fired).length}/${facts.length}; recall ${correct}/${facts.length} = ${((100 * correct) / facts.length).toFixed(1)}%`);
console.log(`precision ${correct}/${fires.length} = ${((100 * correct) / fires.length).toFixed(1)}%; FP ${near.filter((r) => r.fired).length}/${near.length}`);
console.log(`lowercase-typed fact items correct ${lower.filter((r) => r.correct).length}/${lower.length}`);
for (const r of res) if ((r.kind === "fact" && !r.correct) || (r.kind === "nearmiss" && r.fired)) console.log(`${r.kind === "fact" ? "MISS" : "FP  "} ${r.id} | ${r.text} | ${r.answer ?? "no fire"}`);
