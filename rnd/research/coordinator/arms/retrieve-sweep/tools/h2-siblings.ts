// H2 sibling scan (0 LLM, no retrieval): which dev queries get a different health topic under RS_HEALTH_TOPIC_FB.
// usage: tsx tools/h2-siblings.ts <tree> -> JSON lines on stdout
import * as fs from "node:fs";
const B = "<workspace>";
const tree = process.argv[2];
(async () => {
const ctx: any = await import(`${tree}/src/routing/context.ts`);
const cc: any = await import(`${tree}/src/routing/conditionCards.ts`);
const fb: any = await import(`${tree}/src/routing/healthTopicFallback.ts`);
const rd = (f: string) => fs.readFileSync(f, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const sets: Record<string, any[]> = { v01: rd(`${B}/boar-eval/bench/v0.1/questions.public.jsonl`) };
for (const d of fs.readdirSync(`${B}/boar-eval/bench/selftest`)) { const f = `${B}/boar-eval/bench/selftest/${d}/questions.jsonl`; if (fs.existsSync(f)) sets[`st:${d}`] = rd(f); }
sets.qform = rd(`${B}/rnd/research/coordinator/arms/qform/items/qform.questions.jsonl`);
const seen = new Set<string>();
for (const [set, qs] of Object.entries(sets)) for (const q of qs) {
  const text: string = q.question ?? q.query; const key = q.id + "|" + text; if (seen.has(key)) continue; seen.add(key);
  const lex = ctx.isHealthQuestion(text), cardEm = cc.isCardEmergency(text), card = cc.regexCondition(text);
  const ven = new RegExp(ctx.VENOMOUS.source, "iu").test(text);
  const out: any = { set, id: q.id, q: text, lex, cardEm, card, ven };
  const snap = process.env.RS_HEALTH_TOPIC_FB; 
  delete process.env.RS_HEALTH_TOPIC_FB; out.base = [...ctx.healthTopicTerms(text, null)].sort();
  process.env.RS_HEALTH_TOPIC_FB = "1"; out.fb1 = [...fb.healthTopicFallback(text, null)].sort();
  process.env.RS_HEALTH_TOPIC_FB = "2"; out.fb2 = [...fb.healthTopicFallback(text, null)].sort();
  if (snap === undefined) delete process.env.RS_HEALTH_TOPIC_FB; else process.env.RS_HEALTH_TOPIC_FB = snap;
  if (out.base.join() !== out.fb1.join() || lex || cardEm || ven || card) console.log(JSON.stringify(out));
}
})();
