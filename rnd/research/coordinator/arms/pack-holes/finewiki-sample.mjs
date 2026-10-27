// usage: node finewiki-sample.mjs <shard.parquet> <boar-app dir (for hyparquet)> <every Nth row> > rows.jsonl
// Emits {p: title, base: text, wl: text} so holes-eval.py can score FineWiki's rendered text the same way (wl = base).
import { createRequire } from "node:module";
const [shard, appdir, every = "10"] = process.argv.slice(2);
const require = createRequire(`${appdir}/package.json`);
const { asyncBufferFromFile, parquetMetadataAsync, parquetReadObjects } = await import(require.resolve("hyparquet"));
const { compressors } = await import(require.resolve("hyparquet-compressors"));
const file = await asyncBufferFromFile(shard);
const md = await parquetMetadataAsync(file);
let n = 0, rg0 = 0;
for (const rg of md.row_groups) {
  const rows = await parquetReadObjects({ file, compressors, columns: ["title", "text", "infoboxes"], rowStart: rg0, rowEnd: rg0 + Number(rg.num_rows) });
  rg0 += Number(rg.num_rows);
  for (const r of rows) { if (n++ % Number(every)) continue; if (!r.text) continue; process.stdout.write(JSON.stringify({ p: r.title, base: r.text, wl: r.text }) + "\n"); }
}
console.error("rows", n);
