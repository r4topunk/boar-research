import { registerHooks } from "node:module";
import { pathToFileURL } from "node:url";
const AD = "<workspace>/boar-eval/adapters/desktop-node";
const shim = (f: string) => pathToFileURL(`${AD}/runner/app-shims/${f}`).href;
const SH: Record<string, string> = { "expo-sqlite": shim("expo-sqlite.mjs"), "expo-file-system": shim("expo-file-system.mjs"), "expo-file-system/legacy": shim("expo-file-system.mjs"), "llama.rn": shim("llama-rn.mjs"), "react-native": shim("react-native.mjs"), "ram-monitor": shim("ram-monitor.mjs") };
(registerHooks as any)({ resolve: (s: string, c: any, n: any) => (SH[s] ? { url: SH[s], shortCircuit: true } : n(s, c)) });
const T = process.argv[2]; const PACK = process.argv[3]; const qs = process.argv.slice(4);
const SQ: any = await import("expo-sqlite");
const { decompress } = await import(`${T}/node_modules/fzstd/lib/index.js`);
const W: any = await import(`${T}/src/rag/wikiPack.ts`);
const sl = PACK.lastIndexOf("/");
const db = await SQ.openDatabaseAsync(PACK.slice(sl + 1), { useNewConnection: true }, PACK.slice(0, sl));
const wp = await W.WikiPack.open(db, decompress);
for (const q of qs) {
  const hits = await wp.search(q, { k: 4 });
  console.log(`== ${q}`); for (const h of hits) console.log(`   ${h.via} ${h.source} ${h.title} | ${h.section?.slice(0, 50)} act=${h.action}`);
}
process.exit(0);
