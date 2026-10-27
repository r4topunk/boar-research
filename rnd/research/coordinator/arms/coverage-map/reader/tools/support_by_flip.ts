// RD2 0-LLM diagnostic (post-hoc, not adopted): for each bar-0.6 flip, the best on-topic numeric-guard-passing citationSupport per claim sentence, to show what a higher bar would have done.
import { readFileSync } from "node:fs";
import { citationSupport, groundUncited } from "<workspace>/kiln-local/rs-RD2/src/routing/citations";
const C = "<workspace>/rnd/research/coordinator/arms/coverage-map";
const rd = (f: string) => readFileSync(f, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const T = new Map(rd(C + "/sefix/ans-traces/f1b-main-s42.traces.jsonl").map((t: any) => [t.itemId, t]));
const R = new Map(rd(C + "/sefix/replays/main.v3-extra.jsonl").map((r: any) => [r.id, r]));
const W = "Not found in this phone's offline library. From the model's memory, may be wrong:";
const ids = ["st-qa-money-se-003","lan-exp-002","vit-hum-006","vit-cry-001","vit-cry-002","vit-cry-005","vit-cry-009","lan-cmp-004","st-qa-cooking-se-010","st-qa-cooking-se-012","st-qa-cooking-se-019","st-qa-money-se-015","st-qa-money-se-018"];
for (const id of ids) {
  const t: any = T.get(id), rp: any = R.get(id); const raw: string = t.answer.text; const body = raw.startsWith(W) ? raw.slice(W.length).replace(/^\n/, "") : raw;
  const src = rp.keptFull.map((c: any) => ({ chunkId: c.chunkId, docId: c.docId, title: c.title, body: c.body, score: 1, matchType: "lexical" }));
  const bars = [0.6, 0.67, 0.75, 0.8, 0.9].map((b) => `${b}:${groundUncited(body, src, t.question, b).added.length ? "cite" : "-"}`).join(" ");
  const sents = body.match(/(?:[^.!?\n]|(?<=\d)\.(?=\d))+[.!?]*/g) ?? [];
  const mx = sents.map((s: string) => Math.max(0, ...src.map((c: any) => citationSupport(s, c)))).map((x: number) => x.toFixed(2)).join("/");
  console.log(id, "maxSupport per sentence", mx, "|", bars);
}
