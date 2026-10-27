// L0 replay of the ARM tree (rnd/research/forge/arms/tree) with perf flags baked in at bundle time; otherwise as main.ts.
// L0 replay entry: BOAR's retrieve() + compressContext() over the recorded g75 workload, with SQLite and the embedder
// replaced by recorded results. Runs under the Hermes V1 CLI (no JIT) and under Node for comparison.
// Stages: zstd (fzstd), utf8 (TextDecoder.decode: Expo's JS polyfill on Hermes, as in the app), sqlReplay + embedReplay
// (harness lookups, not phone work), js (everything else inside retrieve), compress (compressContext).
import { now, T, N } from "./clock";
import { TextDecoder as ExpoTextDecoder } from "../app/node_modules/expo/src/winter/TextDecoder";
declare const globalThis: any;
declare const print: any;
const out = typeof print === "function" ? print : (s: string) => console.log(s);
const RAW = globalThis.__REC_RAW;

// --- decode the recording (outside every timer)
const B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
const LUT = new Uint8Array(128); for (let i = 0; i < 64; i++) LUT[B64.charCodeAt(i)] = i;
function b64(s: string): Uint8Array {
  let n = (s.length * 3) >> 2; if (s.endsWith("==")) n -= 2; else if (s.endsWith("=")) n -= 1;
  const o = new Uint8Array(n); let j = 0;
  for (let i = 0; i < s.length; i += 4) {
    const a = LUT[s.charCodeAt(i)], b = LUT[s.charCodeAt(i + 1)], c = LUT[s.charCodeAt(i + 2)], d = LUT[s.charCodeAt(i + 3)];
    const v = (a << 18) | (b << 12) | (c << 6) | d;
    if (j < n) o[j++] = (v >> 16) & 255; if (j < n) o[j++] = (v >> 8) & 255; if (j < n) o[j++] = v & 255;
  }
  return o;
}
const dec = (x: any): any => x && typeof x === "object" ? (x.$b64 !== undefined ? b64(x.$b64) : Array.isArray(x) ? x.map(dec) : Object.fromEntries(Object.entries(x).map(([k, v]) => [k, dec(v)]))) : x;
const store: Record<string, any> = {};
for (const h of Object.keys(RAW.store)) store[h] = dec(RAW.store[h]);
const q = new Map<string, any[]>();
for (const w of RAW.work) for (const c of w.calls) { const k = `${c.db}|${c.m}|${c.sql}|${JSON.stringify(c.p)}`; let a = q.get(k); if (!a) q.set(k, (a = [])); a.push(store[c.h]); }
globalThis.__REPLAY = { q, last: new Map(), embeds: RAW.embeds };

// --- TextDecoder: Hermes V1 has none, so the app runs Expo's JS polyfill (expo/src/winter/runtime.native.ts). POLY=1 forces it on Node.
const force = typeof process !== "undefined" && (process as any).env && (process as any).env.POLY === "1";
if (typeof globalThis.TextDecoder === "undefined" || force) globalThis.TextDecoder = ExpoTextDecoder;
const TD = globalThis.TextDecoder;
const origDecode = TD.prototype.decode;
TD.prototype.decode = function (this: any, ...a: any[]) { const t = now(); try { return origDecode.apply(this, a); } finally { T.utf8 = (T.utf8 ?? 0) + now() - t; N.utf8 = (N.utf8 ?? 0) + 1; N.utf8Bytes = (N.utf8Bytes ?? 0) + (a[0]?.byteLength ?? 0); } };

declare const __FORGE_FLAGS__: string;
async function main() {
  const { setPerfFlags, parsePerfFlags } = await import("../../../arms/tree/src/rag/perfFlags");
  setPerfFlags(parsePerfFlags(__FORGE_FLAGS__));
  const { retrieve } = await import("../../../arms/tree/src/rag/retrieve");
  const { compressContext } = await import("../../../arms/tree/src/rag/compress");
  const { embeddingEngine } = await import("../../../arms/tree/src/rag/embed");
  await embeddingEngine.load("embedding.gguf");
  const rows: any[] = [];
  let mismatch = 0;
  for (const w of RAW.work) {
    for (const k of Object.keys(T)) T[k] = 0;
    for (const k of Object.keys(N)) N[k] = 0;
    const t0 = now();
    const raw: any[] = await retrieve(w.q, w.k);
    const tRet = now() - t0;
    const t1 = now();
    const comp = compressContext(w.q, raw, { tokenBudget: 320 });
    const tComp = now() - t1;
    const ids = raw.map((c) => c.chunkId), cids = comp.chunks.map((c: any) => c.chunkId);
    const same = JSON.stringify(ids) === JSON.stringify(w.rawIds) && JSON.stringify(cids) === JSON.stringify(w.compIds);
    if (!same) mismatch++;
    const zstd = T.zstd ?? 0, utf8 = T.utf8 ?? 0, sqlR = T.sqlReplay ?? 0, embR = T.embedReplay ?? 0;
    rows.push({ id: w.id, total: tRet, zstd, utf8, sqlReplay: sqlR, embedReplay: embR, js: tRet - zstd - utf8 - sqlR - embR, compress: tComp,
      nZstd: N.zstd ?? 0, utf8Bytes: N.utf8Bytes ?? 0, sqlCalls: N.sqlCalls ?? 0, sqlMiss: N.sqlMiss ?? 0, same, nodeMs: w.ms });
  }
  out(JSON.stringify({ misses: (globalThis.__MISSES ?? []).slice(0, 8), flags: __FORGE_FLAGS__, engine: typeof print === "function" ? "hermes" : "node", poly: TD === ExpoTextDecoder, mismatch, rows }));
}
main().catch((e) => out("ERROR " + (e && e.stack || e)));
