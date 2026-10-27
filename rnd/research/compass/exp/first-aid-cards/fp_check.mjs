import { readFileSync } from "node:fs";
import { PROPOSED } from "./triggers.proposed.mjs";
const L = (p) => readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const qs = [...L("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl").map((q) => [q.id, q.question]),
  ...L("<workspace>/boar-eval/bench/v0.1/safety/track.v0.3.jsonl").map((q) => [q.id, q.question]),
  ...[...L("../../chat-slice/slice.v0.jsonl"), ...L("../../chat-slice/v1-fresh/slice.v1.jsonl"), ...L("../../chat-slice/v2-fresh/slice.v2.jsonl")].map((q) => [q.id, q.turns.filter((t) => t.role === "user").map((t) => t.text).join(" / ")])];
for (const [id, q] of qs) {
  const hits = Object.keys(PROPOSED).filter((k) => PROPOSED[k].test(q));
  if (hits.length) console.log(id, hits.join("+"), "|", q.slice(0, 90));
}
