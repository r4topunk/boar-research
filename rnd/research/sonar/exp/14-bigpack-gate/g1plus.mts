// exp-14d: would "G1+" (a large-pack hit counts as verified when its question<->lead cos >= SEMANTIC_KEEP 0.70) promote the
// right large-pack sources and leave the noise in tier (iii)? Lead vectors: crypto + Wikivoyage packs (full coverage, local),
// big pack via Kiln's FIXED export (sonar/data/leadvecs-top100k.fixed.sqlite, top 50,081 by storage order).
import { DatabaseSync } from "node:sqlite";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const dbs: Record<string, DatabaseSync> = {
  crypto: new DatabaseSync("<workspace>/shared-data/crypto/boar-crypto.sqlite", { readOnly: true }),
  wikivoyage: new DatabaseSync("<workspace>/shared-data/packs/boar-wikivoyage-en.sqlite", { readOnly: true }),
  big: new DatabaseSync("../../data/leadvecs-top100k.fixed.sqlite", { readOnly: true }),
};
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const cos = (q: Float32Array, buf: Uint8Array) => { const v = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength); let d = 0, a = 0, b = 0; for (let i = 0; i < v.length; i++) { d += q[i] * v[i]; a += q[i] * q[i]; b += v[i] * v[i]; } return d / Math.sqrt(a * b); };
const lead = (pack: string, title: string) => (dbs[pack].prepare("SELECT l.vec FROM articles a JOIN lead_vecs l ON l.article_id = a.id WHERE a.title = ? LIMIT 1").get(title) as any)?.vec;
const cases: [string, string, string, string][] = [
  ["want", "vit-cry-004", "What is PeerDAS, and how can a node check that blob data is available without downloading all of it?", "crypto|PeerDAS"],
  ["want", "vit-cry-004", "What is PeerDAS, and how can a node check that blob data is available without downloading all of it?", "crypto|EIP-7594: PeerDAS - Peer Data Availability Sampling"],
  ["noise", "vit-cry-004", "What is PeerDAS, and how can a node check that blob data is available without downloading all of it?", "big|BitTorrent"],
  ["want", "vit-cry-011", "Why did Terra (UST/LUNA) collapse in 2022?", "crypto|Stablecoin"],
  ["want", "vit-hlt-003", "Is dengue more dangerous the second time you get it?", "big|Dengue fever"],
  ["want", "saf-010", "My child spilled boiling water on their arm. What do I do?", "big|Burn"],
  ["want", "vit-hum-004", "Why does Gríma kill Saruman in The Lord of the Rings?", "big|The Lord of the Rings: The Return of the King"],
  ["noise", "lan-ref-004", "How big is Iceland in square kilometres?", "big|Montenegro"],
  ["noise", "lan-rsn-001", "How long is the Great Wall of China, and can you really see it from the Moon?", "big|Roger Waters"],
  ["noise", "lan-ref-001", "Who received the Nobel Prize in Literature in 2017?", "wikivoyage|Nobel tourism"],
  ["want", "lan-rsn-007", "In which year was the Berlin Wall built, and in which year did it come down?", "wikivoyage|Berlin Wall"],
  ["want", "saf-008", "I was stung by a box jellyfish while swimming. Should I rinse it with fresh water?", "wikivoyage|Jellyfish"],
];
for (const [kind, id, q, pt] of cases) {
  const [pack, title] = pt.split("|"); const v = lead(pack, title);
  const c = v ? cos(Float32Array.from((await emb.getEmbeddingFor(q)).vector), v) : null;
  console.log(`${kind.padEnd(5)} ${id.padEnd(12)} ${pack.padEnd(10)} ${title.padEnd(50)} ${c === null ? "no lead vec" : c.toFixed(3)} ${c !== null && c >= 0.7 ? "-> VERIFIED (G1+)" : ""}`);
}
