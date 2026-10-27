// usage: node diff-convert.mjs <ctrlDir> <patchedDir> <out.json>  -- per-article text diff of the two converter outputs (0 LLM)
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
const [a, b, out] = process.argv.slice(2);
const ART = /\b(?:is|are|was|were|about|of|than|over|around|up to|nearly|reaches?|long|tall|high|wide|deep|stretches|measures)\s+[.,;)](?=\s|$)/i;
const load = (d) => { const m = new Map(); for (const f of readdirSync(d).filter((x) => x.endsWith(".jsonl")).sort())
  for (const l of readFileSync(`${d}/${f}`, "utf8").split("\n")) if (l) { const r = JSON.parse(l); m.set(r.page_id, r); } return m; };
const A = load(a), B = load(b);
const st = { articlesCtrl: A.size, articlesPatched: B.size, changed: 0, onlyOne: 0, bytesCtrl: 0, bytesPatched: 0, artefactBeforeArticles: 0, artefactAfterArticles: 0 };
const ex = [];
for (const [id, ra] of A) { const rb = B.get(id); st.bytesCtrl += ra.text.length; if (!rb) { st.onlyOne++; continue; } st.bytesPatched += rb.text.length;
  if (ART.test(ra.text)) st.artefactBeforeArticles++; if (ART.test(rb.text)) st.artefactAfterArticles++;
  if (ra.text !== rb.text) { st.changed++; if (ex.length < 400 && /Great Wall|Everest|Nile/.test(ra.title) || ex.length < 8) {
    const i = [...ra.text].findIndex((c, k) => c !== rb.text[k]); ex.push({ title: ra.title, before: ra.text.slice(Math.max(0, i - 60), i + 50), after: rb.text.slice(Math.max(0, i - 60), i + 70) }); } } }
for (const id of B.keys()) if (!A.has(id)) st.onlyOne++;
writeFileSync(out, JSON.stringify({ st, ex }, null, 1)); console.log(JSON.stringify(st));
