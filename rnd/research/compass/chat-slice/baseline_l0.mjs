// L0 baseline: main's own single-turn search decision on the chat slice (engine files copied from upstream/main, see engine/COMMIT).
// Decision = smallTalkReply(query) -> no search; else classifyTask(query) -> isRetrievalIrrelevant -> no search; else search.
// Ignores history (main's single-turn rule only). Usage: node baseline_l0.mjs slice.v0.jsonl > decisions.main.jsonl
import fs from "node:fs";
import { smallTalkReply } from "./engine/smallTalk.ts";
import { classifyTask, isRetrievalIrrelevant } from "./engine/classify.ts";
const pt = (q) => /[ãõçáéíóúâêô]|\b(oi|ola|boa|bom|voce|vc|que|como|qual|quem|por que|e o|e a)\b/i.test(q);
for (const line of fs.readFileSync(process.argv[2], "utf8").trim().split("\n")) {
  const it = JSON.parse(line); const q = it.turns.at(-1).text;
  const st = smallTalkReply(q, pt(q), new Date());
  const task = st ? "small-talk" : classifyTask(q);
  const search = !st && !isRetrievalIrrelevant(task);
  console.log(JSON.stringify({ id: it.id, search, why: st ? `small-talk-${st.kind}` : `task:${task}` }));
}
