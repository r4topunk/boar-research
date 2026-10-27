#!/usr/bin/env node
// Content hash of an engine tree: sha256 over "<sha256(file)>  <relpath>\n" for every file under
// src/ assets/ locales/ modules/ + package.json + tsconfig.json, sorted by path. Same file set as boar-eval's
// desktop-node setup.sh archives, so a desktop tree (be-<sha8>-<arm>) and BOAR Bench's engine/ of the same spec
// print the same hash. Ignores node_modules, build outputs and runner dirs (be/, .cache/).
//   node scripts/tree-hash.mjs <tree dir>
import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync, existsSync } from "node:fs";
import { join, relative } from "node:path";

const root = process.argv[2];
if (!root || !existsSync(root)) { console.error("usage: tree-hash.mjs <tree dir>"); process.exit(2); }
const SKIP = new Set(["node_modules", "build", ".gradle", ".cxx", ".expo"]);
const files = [];
const walk = (d) => {
  for (const name of readdirSync(d)) {
    if (SKIP.has(name)) continue;
    const p = join(d, name);
    const s = statSync(p);
    if (s.isDirectory()) walk(p);
    else if (s.isFile()) files.push(relative(root, p).split("\\").join("/"));
  }
};
for (const top of ["src", "assets", "locales", "modules"]) if (existsSync(join(root, top))) walk(join(root, top));
for (const f of ["package.json", "tsconfig.json"]) if (existsSync(join(root, f))) files.push(f);
files.sort();
const h = createHash("sha256");
for (const f of files) h.update(`${createHash("sha256").update(readFileSync(join(root, f))).digest("hex")}  ${f}\n`);
console.log(h.digest("hex"));
