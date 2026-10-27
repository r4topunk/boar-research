// CF trigger scorer (criterion arms/cf/CF-criterion.md, L0 bar 2): scores arms/cf/trigger-set/items.jsonl ONCE against the frozen CF trigger.
// Lines: {"id", "text", "expect": "country"|"none"}. The engineer never opens that folder.
// Bars: recall >= 90% on expect=country, false fires <= 2 per 100 expect=none items (scaled: <= floor(n/50), min 2 when n >= 100).
// usage: tsx cf-trigger-score.mts <engine tree with CF (cf-on-cut3 applied)> [items.jsonl (default arms/cf/trigger-set/items.jsonl)]
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
const tree = process.argv[2];
if (!tree) { console.error("usage: tsx cf-trigger-score.mts <tree> [items.jsonl]"); process.exit(1); }
const R = path.join(tree, "src/routing");
const FROZEN: Record<string, string> = {
  "countryFacts.ts": "bbcbc8827643f149285e77a5743bba9a3c2f8278d6781fae8c60ee46ce493b61",
  "countryFacts.v1.json": "5503bdd133bd0c38a09cfb8aa21d3dc29335a650aae82a701d5c3b32d091b774",
};
for (const [f, h] of Object.entries(FROZEN)) {
  const got = crypto.createHash("sha256").update(fs.readFileSync(path.join(R, f))).digest("hex");
  if (got !== h) { console.error(`FROZEN MISMATCH ${f}: ${got} != ${h}`); process.exit(2); }
}
const M: any = await import(path.join(R, "countryFacts.ts"));
const countryFacts = M.countryFacts ?? M.default?.countryFacts;
const file = process.argv[3] ?? path.join(path.dirname(new URL(import.meta.url).pathname), "..", "trigger-set", "items.jsonl");
const items = fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const fires = (d: any) => !!countryFacts(d.text);
const pos = items.filter((d: any) => d.expect === "country");
const neg = items.filter((d: any) => d.expect === "none");
const hit = pos.filter(fires);
const ff = neg.filter(fires);
const recallOk = pos.length > 0 && hit.length / pos.length >= 0.9;
const ffMax = Math.max(neg.length >= 100 ? 2 : 0, Math.floor((neg.length * 2) / 100));
const ffOk = ff.length <= ffMax;
console.log(`CF trigger on ${file} (${items.length} items), trigger sha256s verified`);
console.log(`  recall ${hit.length}/${pos.length} (${pos.length ? ((100 * hit.length) / pos.length).toFixed(0) : "-"} %, bar >= 90 %) ${recallOk ? "PASS" : "FAIL"}`);
console.log(`  missed: ${pos.filter((d: any) => !fires(d)).map((d: any) => d.id).join(" ") || "-"}`);
console.log(`  false fires ${ff.length}/${neg.length} (bar <= ${ffMax}) ${ffOk ? "PASS" : "FAIL"}`);
console.log(`  false-fire ids: ${ff.map((d: any) => d.id).join(" ") || "-"}`);
console.log(`CF trigger ${recallOk && ffOk ? "PASS" : "FAIL"} (dev-pool bar is separate: 0 fires except labelled true country-slot messages)`);
