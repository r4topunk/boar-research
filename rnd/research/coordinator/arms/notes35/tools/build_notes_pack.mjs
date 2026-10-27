#!/usr/bin/env node
// NOTES35 pack builder: notes.jsonl -> a format-2 knowledge pack (the format of the curated kit packs boar-crypto and
// boar-wikivoyage-en), built by the claim tree's OWN builder (wt/cut7/scripts/build-wiki-pack.mjs, unchanged), so the
// chunking (chunkArticle 1000/1500 chars), contentless FTS5 (porter unicode61), zstd blocks, df table, int8 lead
// embeddings (bge-small-en-v1.5 q8_0 via node-llama-cpp, quantizeInt8) and meta are byte-for-byte the engine's.
//
//   node build_notes_pack.mjs --notes notes.jsonl --out /path/boar-notes35.sqlite [--name "..."] [--builder-tree wt/cut7]
//
// Each note = one article: title = topic, text = "# <topic>\n\n<note>", articles.source = 0 ("enwiki": the only code that
// keeps the plain title in the engine's chunk and resolves through titlesInQuestion; the engine has no "notes35" code),
// article_meta.url = https://notes35.boar.invalid/<topic> and article_meta.license = "NOTES35 generated note (<model>)"
// (the "notes35" source tag; meta.sources = {"notes35": …} from the manifest). The file must be named boar-notes35.sqlite
// for the adapter's kit (config.kit [{id:"boar-notes35", sha256}] -> <id>.sqlite in BOAR_EVAL_PACK_DIRS).
// Writes <out>, <out>.json (builder summary + notes35 provenance) and a work dir <out>.work/ (shard + manifest).
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";

const HERE = dirname(fileURLToPath(import.meta.url));
const BOAR = resolve(HERE, "../../../../../..");
const { values: o } = parseArgs({
  options: {
    notes: { type: "string" },
    out: { type: "string" },
    name: { type: "string", default: "NOTES35 encyclopedic notes" },
    "builder-tree": { type: "string", default: join(BOAR, "wt/cut7") },
    "embed-threads": { type: "string", default: "4" },
    embedding: { type: "string", default: join(BOAR, "shared-models/bge-small-en-v1.5-q8_0.gguf") },
  },
});
if (!o.notes || !o.out) {
  console.error("usage: build_notes_pack.mjs --notes notes.jsonl --out boar-notes35.sqlite [--name NAME] [--builder-tree wt/cut7]");
  process.exit(1);
}
const out = resolve(o.out);
const tree = resolve(o["builder-tree"]);
const builder = join(tree, "scripts/build-wiki-pack.mjs");
const sha = (b) => createHash("sha256").update(b).digest("hex");
if (basename(out) !== "boar-notes35.sqlite") console.error(`note: the adapter's kit id is the file name; ${basename(out)} != boar-notes35.sqlite`);

const notes = readFileSync(o.notes, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const seen = new Set();
const rows = [];
const manifest = [];
for (const n of notes) {
  if (seen.has(n.title) || !n.note?.trim()) continue;
  seen.add(n.title);
  // Paragraphs separated by blank lines (chunkArticle splits on "\n\n"); no "#" lines inside a note.
  const body = n.note.replace(/\r/g, "").split(/\n\s*\n/).map((p) => p.replace(/\s+/g, " ").trim()).filter((p) => p && !/^#/.test(p)).join("\n\n");
  const url = `https://notes35.boar.invalid/${n.title}`;
  const license = `NOTES35 generated note (${n.model})`;
  rows.push({ page_id: rows.length + 1, title: n.title, text: `# ${n.title}\n\n${body}`, source: "enwiki", url, license, views: 0 });
  manifest.push({ source: "notes35", title: n.title, url, license });
}
const work = `${out}.work`;
mkdirSync(work, { recursive: true });
mkdirSync(dirname(out), { recursive: true });
const shard = join(work, "notes35.shard.jsonl");
const manifestFile = join(work, "notes35.manifest.json");
writeFileSync(shard, rows.map((r) => JSON.stringify(r)).join("\n") + "\n");
writeFileSync(manifestFile, JSON.stringify(manifest));
console.error(`notes: ${notes.length} rows, ${rows.length} articles -> ${builder}`);

const r = spawnSync(process.execPath, [builder, "--out", out, "--shards", shard, "--manifest", manifestFile, "--name", o.name,
  "--embed-threads", o["embed-threads"]], { stdio: ["ignore", "inherit", "inherit"], env: { ...process.env, BOAR_EMBEDDING_GGUF: o.embedding } });
if (r.status !== 0) { console.error(`builder exit ${r.status}`); process.exit(1); }

const summary = JSON.parse(readFileSync(`${out}.json`, "utf8"));
const treeCommit = spawnSync("git", ["-C", tree, "rev-parse", "HEAD"], { encoding: "utf8" }).stdout.trim();
Object.assign(summary, {
  id: "boar-notes35",
  notes35: {
    notesFile: resolve(o.notes), notesSha256: sha(readFileSync(o.notes)), notes: notes.length, models: [...new Set(notes.map((n) => n.model))],
    promptSha256: [...new Set(notes.map((n) => n.promptSha256))], builder: `${builder} @ ${treeCommit}`, builderSha256: sha(readFileSync(builder)),
    sourceCode: "enwiki (0) + article_meta url https://notes35.boar.invalid/<title>", embedding: o.embedding,
  },
});
writeFileSync(`${out}.json`, `${JSON.stringify(summary, null, 2)}\n`);
console.log(JSON.stringify({ file: out, sizeBytes: summary.sizeBytes, sha256: summary.sha256, articles: summary.articles, chunks: summary.chunks, indexed: summary.indexed }));
console.log(`kit entry: ${JSON.stringify({ id: "boar-notes35", sha256: summary.sha256 })}`);
