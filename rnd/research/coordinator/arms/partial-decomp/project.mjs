// Projection of decompression-time saving per pack search (aunion73-a, 59 pack searches). usage: node project.mjs <aggdir>
import fs from "node:fs"; const d = process.argv[2];
const R = JSON.parse(fs.readFileSync(d + "/replay-sim.json")), P = JSON.parse(fs.readFileSync(d + "/repack-sim.json")), B = JSON.parse(fs.readFileSync(d + "/bench-stop.json"));
const meanKB = R.sim[16].baseline.decoded_MB_full * 1000 / R.sim[16].baseline.misses; // KB per decompression (shipped layout)
const out = { searches: R.searches, mean_decoded_KB_per_decompression: meanKB, phone_ms_per_MB: { f1: 12.5 / (meanKB / 1000), f06: 0.6 * 12.5 / (meanKB / 1000) }, desktop_ms_per_MB_fzstd: B.all.ms_per_decoded_MB_full, rows: {} };
const row = (name, C, MB) => { const base = R.sim[C].baseline.decoded_MB_full; const saved = base - MB; out.rows[name + "@" + C] = { decoded_MB: MB, saved_pct: 100 * saved / base, desktop_ms_per_search_saved: saved * B.all.ms_per_decoded_MB_full / R.searches, phone_ms_per_search_saved_f06: saved * out.phone_ms_per_MB.f06 / R.searches, phone_ms_per_search_saved_f1: saved * out.phone_ms_per_MB.f1 / R.searches, baseline_phone_decode_ms_per_search_f1: base * out.phone_ms_per_MB.f1 / R.searches }; };
for (const C of [16, 64]) {
  const m = R.sim[C].modes;
  row("fzstd_stream_stop_resume", C, m.stream_stop_resume.decoded_MB); row("fzstd_stream_stop_restart", C, m.stream_stop_restart.decoded_MB);
  row("midblock_stop_resume(hypothetical native)", C, m.exact_resume.decoded_MB); row("midblock_stop_restart(hypothetical native)", C, m.exact_restart.decoded_MB);
  for (const N of [16, 32]) row("repack_" + N + "KB(equal cache bytes vs 64KB-slot layout)", C, P.sim[C][N].decoded_MB);
}
fs.writeFileSync(d + "/projection.json", JSON.stringify(out, null, 1)); console.log(JSON.stringify(out, null, 1));
