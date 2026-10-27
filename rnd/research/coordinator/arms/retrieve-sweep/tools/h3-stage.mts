// H3 stage attribution (0 LLM): re-run the live compressContext (src/routing/context.ts of rs-H3) on each replay row's rawFull
// (substantive chunks), switch off vs on, at a given work budget, and print per item the compressed output (chunk ids + bodies).
// usage: tsx h3-stage.ts <replay.jsonl> <budget|task> > out.jsonl
import { readFileSync } from "node:fs";
const T = "<workspace>/kiln-local/rs-H3";
const { compressContext, isSubstantive } = await import(`${T}/src/routing/context.ts`);
const rows = readFileSync(process.argv[2], "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const budgetArg = process.argv[3]; // a number, or "task": lookup 450 / other 700 (FAST_CONTEXT_TOKENS)
for (const r of rows) {
  const raw = r.rawFull.filter((c: any) => isSubstantive(c));
  const mk = (on: boolean) => {
    if (on) process.env.RS_COMPRESS_HEAD = "1"; else delete process.env.RS_COMPRESS_HEAD;
    const o = compressContext(r.question ?? r.query, raw, { tokenBudget: budgetArg === "task" ? (r.task === "lookup" ? 450 : 700) : Number(budgetArg) });
    return { ids: o.chunks.map((c: any) => c.chunkId), bodies: o.chunks.map((c: any) => c.body), titles: o.chunks.map((c: any) => c.title), before: o.tokensBefore, after: o.tokensAfter, flag: !!o.headProtected };
  };
  console.log(JSON.stringify({ id: r.id, off: mk(false), on: mk(true), nraw: raw.length }));
}
