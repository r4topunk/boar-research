// VG v4 L0 helper: run v3 and v4 on the DEV probe traces; print fires/differences.
import fs from "node:fs";
import path from "node:path";
const [t3, t4] = process.argv.slice(2);
const V3 = (await import(path.join(t3, "src/routing/verdictGuard.ts"))).verdictGuard;
const V4 = (await import(path.join(t4, "src/routing/verdictGuard.ts"))).verdictGuard;
const kinds = new Map(fs.readFileSync("<workspace>/rnd/research/coordinator/arms/vg-probe-q/items.jsonl", "utf8").split("\n").filter(Boolean).map((l) => { const d = JSON.parse(l); return [d.id, d.kind]; }));
const PREFACE = "This answer is not from an offline source on this phone; check it before relying on it.";
const NOT_MODEL = /answer:|grounding:health|instant:final|places|calculator|grounding:current-event|small-talk|safety-fact/;
for (const l of fs.readFileSync("<workspace>/boar-eval/runs/kiln/vg-probe-cut2-s44/traces.jsonl", "utf8").split("\n").filter(Boolean)) {
  const r = JSON.parse(l); const text = r.answer?.text ?? "";
  if (!text || NOT_MODEL.test((r.route?.reasonCodes ?? []).join(" "))) continue;
  let body = text; if (body.startsWith(PREFACE)) body = body.slice(PREFACE.length).replace(/^\s+/, "");
  const a = V3(r.question, body), b = V4(r.question, body);
  if (a || b) console.log(`${r.itemId} [${kinds.get(r.itemId)}] v3=${a?.kind ?? "-"} v4=${b?.kind ?? "-"}${a && b && a.text !== b.text ? " TEXT-DIFF" : ""}\n  Q: ${r.question}\n  AFTER: ${(b ?? a)!.text.replace(/\n+/g, " / ")}`);
}
