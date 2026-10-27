import { registerHooks } from "node:module";
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
const AD = "<workspace>/boar-eval/adapters/desktop-node";
const LNM = "<workspace>/wt/eval/eval/node_modules";
const shim = (f: string) => pathToFileURL(`${AD}/runner/app-shims/${f}`).href;
const SH: Record<string, string> = { "expo-sqlite": shim("expo-sqlite.mjs"), "expo-file-system": shim("expo-file-system.mjs"), "expo-file-system/legacy": shim("expo-file-system.mjs"), "llama.rn": shim("llama-rn.mjs"), "react-native": shim("react-native.mjs"), "ram-monitor": shim("ram-monitor.mjs") };
const fb = pathToFileURL(`${LNM}/_r_.js`).href;
(registerHooks as any)({ resolve: (s: string, c: any, n: any) => { if (SH[s]) return { url: SH[s], shortCircuit: true }; try { return n(s, c); } catch (e) { if (/^[./]/.test(s) || s.startsWith("node:")) throw e; return n(s, { ...c, parentURL: fb }); } } });
const T = process.argv[2]; const PACK = process.argv[3]; const qfile = process.argv[4]; const ids = process.argv[5]?.split(",");
const SQ: any = await import("expo-sqlite");
const { decompress } = await import(`${T}/node_modules/fzstd/lib/index.js`);
const W: any = await import(`${T}/src/rag/wikiPack.ts`);
const p = PACK; const sl = p.lastIndexOf("/");
const db = await SQ.openDatabaseAsync(p.slice(sl + 1), { useNewConnection: true }, p.slice(0, sl));
const wp = await W.WikiPack.open(db, decompress);
const Q = readFileSync(qfile, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)).filter((q) => !ids || ids.some((i) => q.id.endsWith(i)));
for (const q of Q) {
  const gold = q.selftest?.source?.title?.replace(/ \(Ready\.gov\)$/, "").toLowerCase();
  const stems = await wp.stems(q.question);
  const cands = await wp.bm25Candidates(stems);
  const rows: string[] = []; let gr = -1;
  for (let i = 0; i < cands.length; i++) {
    const h = await (wp as any).materialize(cands[i]);
    const cov = W.coverage(`${h.title} ${h.text}`, stems);
    if (gold && h.title.toLowerCase().includes(gold) && gr < 0) gr = i;
    if (i < 8 || (gold && h.title.toLowerCase().includes(gold))) rows.push(`   ${i} ${h.source} ${h.title} | ${h.section?.slice(0, 40)} cov=${cov.toFixed(2)} act=${h.action}`);
  }
  console.log(`== ${q.id} ${q.question}\n  stems ${stems.map((s: any) => `${s.stem}:${s.idf.toFixed(1)}`).join(" ")}\n  gold ${gold} rank ${gr}/${cands.length}`);
  console.log(rows.join("\n"));
}
process.exit(0);
