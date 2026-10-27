// SFT4B renderer core: the cut-7 engine's OWN functions build the 4B's prompt (no re-implementation).
// Tree: kiln-local/be-0cfd4a77-cut7 (imported read-only). Run with that tree's tsx:
//   <tree>/be/node_modules/tsx/dist/cli.mjs render_core.mts < in.jsonl > out.jsonl
// Input line: {id, question, chunks: [...], budget?, keep?}
//   chunk = {chunkId, packTitle, source: int (pack articles.source), text (article text), start, end}  (format-2 pack hit)
//        or {chunkId, title, body}                                                                    (already a RetrievedChunk)
//   keep  = optional list of chunkIds allowed after compression (replay of a trace's kept set; order = compression order)
//   order = optional list of chunkIds: the kept sources re-ordered to this list (v3; absent = compression order)
// Pipeline = answer.ts fast path: packHitToChunk shape (title label, "section: text" body) -> isSubstantive ->
//   compressContext(question, raw, {tokenBudget}) -> [keep filter] -> assembleChatMessages(question, sources, persona, -, styleReminder).
// Output line: {id, messages, kept: [chunkId], tokensBefore, tokensAfter}
import { createInterface } from "node:readline";
const T = "<workspace>/kiln-local/be-0cfd4a77-cut7";
const { compressContext, isSubstantive } = await import(`${T}/src/routing/context.ts`);
const { assembleChatMessages } = await import(`${T}/src/rag/pure.ts`);
const { sectionAt } = await import(`${T}/src/rag/wikiPack.ts`);
const { PERSONALITIES } = await import(`${T}/src/constants/personalities.ts`);
const P = PERSONALITIES.find((p: any) => p.id === "succinct");

// wikiPack.ts SOURCES (cut 7): indexes >= 9 (stackexchange, medlineplus, factbook, simplewiki) fall back to "enwiki".
const SOURCES = ["enwiki", "enwikivoyage", "enwikibooks", "appropedia", "usgov", "eips", "ethspecs", "ethereumorg", "bips"];
const LABEL: Record<string, string> = { enwiki: "Wikipedia", enwikivoyage: "Wikivoyage", enwikibooks: "Wikibooks", appropedia: "Appropedia",
  usgov: "US government", eips: "Ethereum EIPs/ERCs", ethspecs: "Ethereum specs", ethereumorg: "ethereum.org", bips: "Bitcoin BIPs" };

function toChunk(c: any) {
  if (c.body !== undefined) return { chunkId: c.chunkId, title: c.title, body: c.body, source: c.sourceLine ?? "" };
  const src = SOURCES[c.source] ?? "enwiki";
  const section = sectionAt(c.text, c.start);
  const text = c.text.slice(c.start, c.end).trim();
  return { chunkId: c.chunkId, title: src === "enwiki" ? c.packTitle : `${LABEL[src] ?? "Source"}: ${c.packTitle}`,
    body: section ? `${section}: ${text}` : text, source: "" };
}

const rl = createInterface({ input: process.stdin, crlfDelay: Infinity });
for await (const line of rl) {
  if (!line.trim()) continue;
  const r = JSON.parse(line);
  const raw = r.chunks.map(toChunk).filter(isSubstantive);
  const comp = compressContext(r.question, raw, { tokenBudget: r.budget ?? 1200, pinned: new Set() });
  let sources = comp.chunks;
  if (r.keep) sources = sources.filter((c: any) => r.keep.includes(c.chunkId));
  // v3 (SFT4B data v3): optional `order` = chunkIds in the order to show them (gold position randomised); absent = engine order.
  if (r.order) sources = r.order.map((id: string) => sources.find((c: any) => c.chunkId === id)).filter(Boolean);
  const messages = assembleChatMessages(r.question, sources, P.systemPrompt, undefined, P.styleReminder);
  process.stdout.write(JSON.stringify({ id: r.id, messages, kept: sources.map((c: any) => c.chunkId), raw_n: raw.length,
    tokensBefore: comp.tokensBefore, tokensAfter: comp.tokensAfter }) + "\n");
}
