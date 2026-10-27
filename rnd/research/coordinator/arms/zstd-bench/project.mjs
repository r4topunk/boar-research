// Projection of Pixel pack-search p50 (PARTIME serial 3947 ms, block phase 73.2 %, PA lower/upper bound 2534/2892 ms, T_8GB p50 7.57 s).
import fs from "node:fs";
const r = n => JSON.parse(fs.readFileSync(`aggregates/bench-${n}.json`))["decompress+utf8"].median_ms;
const base = r("fzstd");
const libs = { "fzstd (today)": base, "bokuweb-wasm": r("bokuweb-wasm"), "zstddec (wasm)": r("zstddec"), "node-zlib-zstd (native bound)": r("node-zlib-zstd") };
const SERIAL = 3947, BLOCK = 0.732 * SERIAL, PA_LB = 2534, PA_UB = 2892, T8 = 7.57;
const out = { phone_ms_per_block: 16.0, macbook_fzstd_ms: base, phone_over_mac: 16.0 / base, rows: [] };
for (const [name, ms] of Object.entries(libs)) for (const f of [1.0, 0.6]) for (const cache of [1, 0.506]) {
  const rr = ms / base, blk = BLOCK * cache * (1 - f * (1 - rr)), saved = BLOCK - blk;
  const serial = SERIAL - saved, pa = [Math.max(1063, PA_LB - saved), Math.max(1063, PA_UB - saved)];
  out.rows.push({ lib: name, decompress_share_f: f, blockcache64: cache < 1, serial_ms: Math.round(serial), promise_all_ms: pa.map(Math.round), t8gb_serial_s: +(T8 - saved / 1000).toFixed(2), t8gb_promiseall_s: pa.map(p => +(T8 - (SERIAL - p) / 1000).toFixed(2)) });
}
fs.writeFileSync("aggregates/projection.json", JSON.stringify(out, null, 1));
for (const x of out.rows) console.log(x.lib.padEnd(30), "f", x.decompress_share_f, x.blockcache64 ? "BC64" : "    ", "serial", x.serial_ms, "PA", x.promise_all_ms.join("-"), "T8", x.t8gb_serial_s, x.t8gb_promiseall_s.join("-"));
