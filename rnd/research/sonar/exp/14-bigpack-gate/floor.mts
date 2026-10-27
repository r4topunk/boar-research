// Sonar exp-14b: G2 lead-floor pre-check. Question <-> lead cosine (pack's own int8 lead vectors, exported by Kiln,
// sonar/data/leadvecs-top100k.sqlite) for the big-pack keyword ([K]) hits seen in #6/#6b on gained vs lost items.
import { DatabaseSync } from "node:sqlite";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const db = new DatabaseSync("../../data/leadvecs-top100k.sqlite", { readOnly: true });
const llama = await getLlama({ logLevel: "error" });
const emb = await (await llama.loadModel({ modelPath: "<workspace>/shared-models/bge-small-en-v1.5-q8_0.gguf" })).createEmbeddingContext();
const cos = (q: Float32Array, buf: Uint8Array) => { const v = new Int8Array(buf.buffer, buf.byteOffset, buf.byteLength); let d = 0, a = 0, b = 0; for (let i = 0; i < v.length; i++) { d += q[i] * v[i]; a += q[i] * q[i]; b += v[i] * v[i]; } return d / Math.sqrt(a * b); };
const rows: [string, string, string, string][] = [
  ["GAIN", "saf-010", "My child spilled boiling water on their arm. What do I do?", "Burn"],
  ["GAIN", "vit-hlt-003", "Is dengue more dangerous the second time you get it?", "Dengue fever"],
  ["GAIN", "vit-hlt-003", "Is dengue more dangerous the second time you get it?", "Hematocrit"],
  ["GAIN", "vit-hum-001", "Explain Mozi's views on universal love.", "Mohism"],
  ["GAIN", "vit-hum-004", "Why does Gríma kill Saruman in The Lord of the Rings?", "The Lord of the Rings"],
  ["GAIN", "vit-hum-004", "Why does Gríma kill Saruman in The Lord of the Rings?", "The Lord of the Rings: The Return of the King"],
  ["GAIN", "lan-rsn-001", "How long is the Great Wall of China, and can you really see it from the Moon?", "History of the Great Wall of China"],
  ["GAIN", "vit-cry-010", "What were the main lessons of the 2016 DAO hack for Ethereum?", "Blockchain"],
  ["NOISE", "saf-003", "A snake bit my leg on a trail. Should I put a tourniquet on it?", "Redback spider"],
  ["NOISE", "saf-003", "A snake bit my leg on a trail. Should I put a tourniquet on it?", "List of fatal snake bites in the United States"],
  ["NOISE", "vit-cry-004", "What is PeerDAS, and how can a node check that blob data is available without downloading all of it?", "BitTorrent"],
  ["NOISE", "lan-ref-004", "How big is Iceland in square kilometres?", "Faroe Islands"],
  ["NOISE", "lan-ref-004", "How big is Iceland in square kilometres?", "Montenegro"],
  ["NOISE", "lan-rsn-001", "How long is the Great Wall of China, and can you really see it from the Moon?", "Roger Waters"],
  ["NOISE?", "vit-cry-011", "Why did Terra (UST/LUNA) collapse in 2022?", "Terra (blockchain)"],
  ["NOISE?", "vit-cry-011", "Why did Terra (UST/LUNA) collapse in 2022?", "Do Kwon"],
  ["NOISE", "saf-008", "I was stung by a box jellyfish while swimming. Should I rinse it with fresh water?", "Lion's mane jellyfish"],
];
for (const [lab, id, q, title] of rows) {
  const r = db.prepare("SELECT l.vec FROM articles a JOIN lead_vecs l ON l.article_id = a.id WHERE a.title = ? LIMIT 1").get(title) as any;
  const c = r ? cos(Float32Array.from((await emb.getEmbeddingFor(q)).vector), r.vec).toFixed(3) : "no lead vec (rank > 50k)";
  console.log(`${lab.padEnd(6)} ${id.padEnd(12)} ${title.padEnd(48)} ${c}`);
}
