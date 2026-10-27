import { DatabaseSync } from "node:sqlite";
import zlib from "node:zlib";
import { WikiPack } from "./src/rag/wikiPack.ts";
import { onTopic } from "./src/routing/context.ts";
const dec = (d: Uint8Array) => new Uint8Array(zlib.zstdDecompressSync(Buffer.from(d)));
const raw = new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true });
const db = { getAllAsync: async (s: string, p: any[]) => raw.prepare(s).all(...p), getFirstAsync: async (s: string, p: any[]) => raw.prepare(s).get(...p) ?? null, execAsync: async (s: string) => { raw.exec(s); }, runAsync: async (s: string, p: any[]) => raw.prepare(s).run(...p) };
const pack = await WikiPack.open(db as any, dec);
const cases: [string, string, string][] = [
  ["lan-exp-003", "Give me the essentials on Kenya: its location, capital, official languages and year of independence.", "Nairobi"],
  ["vit-hlt-001", "My friend just got stung by a jellyfish while swimming in Thailand. Should I pour vinegar or fresh water on it?", "Darwin"],
  ["vit-hlt-001", "My friend just got stung by a jellyfish while swimming in Thailand. Should I pour vinegar or fresh water on it?", "Langkawi"],
];
for (const [id, q, art] of cases) {
  const { hits } = await pack.searchDetailed(q, { k: 4 });
  const h = hits.find((x) => x.title === art); if (!h) { console.log(id, art, "not in replay hits"); continue; }
  const c: any = { chunkId: "x", docId: "x", title: `Wikivoyage: ${h.title}`, body: h.section ? `${h.section}: ${h.text}` : h.text, score: 1, matchType: "lexical" };
  const proper = (q.match(/[\p{L}][\p{L}\p{N}'’-]*/gu) ?? []).slice(1).filter((w) => /^\p{Lu}/u.test(w) && w !== "I");
  const qNoProper = q.replace(new RegExp(`\\b(${proper.join("|")})\\b`, "g"), (m) => m.toLowerCase());
  console.log(`${id} ${art}: onTopic=${onTopic(q, c)} | proper nouns ${JSON.stringify(proper)} present in passage: ${proper.map((p) => c.body.includes(p) || c.title.includes(p))} | onTopic with proper nouns lower-cased (rule off): ${onTopic(qNoProper, c)}`);
}
