// exp-14c: G2 floor pre-check with the CORRECTED mapping hypothesis (vector at sorted position i belongs to article id i+1).
import { DatabaseSync } from "node:sqlite";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const ex = new DatabaseSync("../../data/leadvecs-top100k.sqlite", { readOnly: true });
const vecs = (ex.prepare("SELECT vec FROM lead_vecs ORDER BY article_id").all() as any[]).map((r) => r.vec);
const idOf = (t: string) => (ex.prepare("SELECT id FROM articles WHERE title = ?").get(t) as any)?.id;
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const cos = (q: Float32Array, buf: Uint8Array) => { const v = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength); let d = 0, a = 0, b = 0; for (let i = 0; i < v.length; i++) { d += q[i] * v[i]; a += q[i] * q[i]; b += v[i] * v[i]; } return d / Math.sqrt(a * b); };
// validation: title embedding vs corrected lead for a few known titles
for (const t of ["Dengue fever", "Iceland", "Burn", "BitTorrent", "Redback spider"]) {
  const id = idOf(t); const v = id && id <= vecs.length ? vecs[id - 1] : null;
  console.log(`check "${t}" id ${id}: title-emb vs corrected lead ${v ? cos(Float32Array.from((await emb.getEmbeddingFor(t)).vector), v).toFixed(3) : "n/a"}`);
}
const rows: [string, string, string][] = [
  ["GAIN", "My child spilled boiling water on their arm. What do I do?", "Burn"],
  ["GAIN", "Is dengue more dangerous the second time you get it?", "Dengue fever"],
  ["GAIN", "Why does Gríma kill Saruman in The Lord of the Rings?", "The Lord of the Rings"],
  ["GAIN", "Why does Gríma kill Saruman in The Lord of the Rings?", "The Lord of the Rings: The Return of the King"],
  ["GAIN", "What were the main lessons of the 2016 DAO hack for Ethereum?", "Blockchain"],
  ["NOISE", "A snake bit my leg on a trail. Should I put a tourniquet on it?", "Redback spider"],
  ["NOISE", "What is PeerDAS, and how can a node check that blob data is available without downloading all of it?", "BitTorrent"],
  ["NOISE", "How big is Iceland in square kilometres?", "Faroe Islands"],
  ["NOISE", "How big is Iceland in square kilometres?", "Montenegro"],
  ["NOISE", "How long is the Great Wall of China, and can you really see it from the Moon?", "Roger Waters"],
  ["NOISE", "I was stung by a box jellyfish while swimming. Should I rinse it with fresh water?", "Lion's mane jellyfish"],
];
for (const [lab, q, t] of rows) {
  const id = idOf(t); const v = id && id <= vecs.length ? vecs[id - 1] : null;
  console.log(`${lab.padEnd(6)} ${t.padEnd(48)} ${v ? cos(Float32Array.from((await emb.getEmbeddingFor(q)).vector), v).toFixed(3) : `no corrected vector (id ${id} > ${vecs.length})`}`);
}
