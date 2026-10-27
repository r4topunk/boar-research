// FineWiki enwiki (HF HuggingFaceFW/finewiki @ 8bd13e72) -> page_id<TAB>title for all 15 shards,
// reading only the page_id and title column chunks over HTTP range requests.
import { asyncBufferFromUrl, cachedAsyncBuffer, parquetMetadataAsync, parquetReadObjects } from "hyparquet";
import { compressors } from "hyparquet-compressors";
import { createWriteStream } from "node:fs";
const REV = "8bd13e72e6a002407649b3e898535f42ceb1aeb9";
const [outDir, ...which] = process.argv.slice(2);
let total = 0, bytes = 0;
for (const s of which.map(Number)) {
  const out = createWriteStream(`${outDir}/fw-${String(s).padStart(2, "0")}.tsv.part`);
  const url = `https://huggingface.co/datasets/HuggingFaceFW/finewiki/resolve/${REV}/data/enwiki/000_${String(s).padStart(5, "0")}.parquet`;
  const retry = async (f) => { for (let k = 0; ; k++) { try { return await f(); } catch (e) { if (k >= 30) throw e; console.log(`retry ${k} ${e.message}`); await new Promise((r) => setTimeout(r, 30000)); } } };
  const raw = await retry(() => asyncBufferFromUrl({ url }));
  const counted = { byteLength: raw.byteLength, slice: async (a, b) => { const r = await retry(() => raw.slice(a, b)); bytes += r.byteLength; return r; } };
  const file = cachedAsyncBuffer(counted);
  const md = await parquetMetadataAsync(file);
  let row = 0;
  for (const rg of md.row_groups) {
    const n = Number(rg.num_rows);
    const rows = await parquetReadObjects({ file, metadata: md, compressors, rowStart: row, rowEnd: row + n, columns: ["page_id", "title"] });
    row += n;
    for (const r of rows) out.write(`${r.page_id}\t${String(r.title).replace(/[\t\n]/g, " ")}\n`);
    total += rows.length;
  }
  await new Promise((r) => out.end(r)); (await import("node:fs")).renameSync(`${outDir}/fw-${String(s).padStart(2, "0")}.tsv.part`, `${outDir}/fw-${String(s).padStart(2, "0")}.tsv`);
  console.log(`shard ${s}: rows ${md.num_rows}, total ${total}, fetched ${(bytes / 1e6).toFixed(1)} MB`);
}
console.log("DONE", total, (bytes / 1e6).toFixed(1), "MB");
