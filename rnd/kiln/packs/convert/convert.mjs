#!/usr/bin/env node
// Converts open corpora into build-wiki-pack.mjs input: <out>/<name>.jsonl + manifest.json + convert-info.json.
//   node convert.mjs <format> <input> --out <dir> [--source <code>] [--limit N] [format options]
// Formats: stackexchange, medlineplus, pdf, factbook (see README.md).
// --source overrides the row source code (e.g. map a new code to an existing one for a builder dry run
// before the builder's SOURCE map knows it); the row keeps its real family in "source_family".
import { parseArgs } from "node:util";
import { writeOutput } from "./lib/common.mjs";

const FORMATS = {
  stackexchange: () => import("./formats/stackexchange.mjs"),
  medlineplus: () => import("./formats/medlineplus.mjs"),
  pdf: () => import("./formats/pdf.mjs"),
  factbook: () => import("./formats/factbook.mjs"),
};

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    out: { type: "string" },
    source: { type: "string" },
    limit: { type: "string" },
    "id-base": { type: "string" },
    // stackexchange
    "site-host": { type: "string" },
    "min-score": { type: "string" },
    "max-answers": { type: "string" },
    "keep-unanswered": { type: "boolean" },
    // medlineplus
    lang: { type: "string" },
    // pdf
    manual: { type: "string" },
    "doc-title": { type: "string" },
    date: { type: "string" },
    url: { type: "string" },
    "min-chars": { type: "string" },
    // factbook
    snapshot: { type: "string" },
    help: { type: "boolean" },
  },
});
const [format, input, ...extra] = positionals;
if (values.help || !FORMATS[format] || !input || !values.out) {
  const usages = await Promise.all(Object.values(FORMATS).map(async (f) => `  node convert.mjs ${(await f()).usage}`));
  console.log(`usage: node convert.mjs <format> <input> --out DIR [--source CODE] [--limit N]\n${usages.join("\n")}`);
  process.exit(values.help ? 0 : 1);
}
const mod = await FORMATS[format]();
const opts = { ...values, limit: values.limit ? Number(values.limit) : 0, _extra: extra };
const { name, docs, info } = await mod.convert(input, opts);
if (values.source) {
  for (const d of docs) {
    d.source_family = d.source;
    d.source = values.source;
  }
  info.params.sourceOverride = values.source;
}
const summary = await writeOutput(values.out, name, docs, info);
console.log(JSON.stringify({ out: values.out, name, count: summary.count, sources: summary.sources, licenses: summary.licenses, stats: summary.stats }, null, 1));
