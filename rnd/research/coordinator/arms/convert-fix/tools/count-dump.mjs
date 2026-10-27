// usage: node count-dump.mjs <dump.xml.bz2> <libdir> <out.json>
// 0 LLM. Counts ns-0 non-redirect pages with {{convert|cvt, total convert templates, and keeps 400 sample template strings.
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
const [dump, libdir, out] = process.argv.slice(2);
const { parseDumpPage } = await import(`${libdir}/wiki-pack-lib.mjs`);
const child = spawn("bzcat", [dump], { stdio: ["ignore", "pipe", "inherit"] });
child.stdout.setEncoding("utf8");
const RX = /\{\{\s*(?:convert|cvt)\s*\|[^{}]*\}\}/gi;
const st = { ns0Pages: 0, articles: 0, articlesWithConvert: 0, convertTemplates: 0, otherUnitTemplates: {} };
const samples = []; const seen = new Set();
let buf = "";
for await (const piece of child.stdout) {
  buf += piece; let end;
  while ((end = buf.indexOf("</page>")) >= 0) {
    const start = buf.indexOf("<page>");
    const p = parseDumpPage(buf.slice(start, end)); buf = buf.slice(end + 7);
    if (p.ns !== "0") continue; st.ns0Pages++;
    if (p.redirect) continue; st.articles++;
    const m = p.text.match(RX);
    if (m) { st.articlesWithConvert++; st.convertTemplates += m.length;
      for (const s of m) { const k = s.toLowerCase().replace(/[0-9.,]+/g, "N"); if (!seen.has(k) && samples.length < 400) { seen.add(k); samples.push({ title: p.title, tpl: s }); } } }
  }
}
writeFileSync(out, JSON.stringify({ st, samples }, null, 1));
console.log(JSON.stringify(st));
