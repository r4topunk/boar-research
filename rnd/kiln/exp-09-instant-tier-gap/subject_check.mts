// exp-09 hypothesis H1 (offline, pure, no model): before serving an instant/extractive answer, require that its source is
// ABOUT the question's subject ("passage subject = question subject"), not just mentions it.
//   subject terms: EN -> named entities of the question (O2's extractor); PT -> the app lexicon's English names;
//                  health -> the app's health topic terms (healthTopicTerms).
//   source: the cited source of the instant answer (final instant / health extractive) or, for a preview the model
//           replaced, every instant source (block only if none is about the subject).
//   H1-title: a source title covers a subject term (O2 titleCovers: no part-of, "South Holland" != "Netherlands").
//   H1-title+section: title OR section heading covers it (health pages put the condition in the section).
//   No subject extracted -> fail open (keep).
// Usage (tree root on the mini): tsx kiln/subject_check.mts kiln/runs/<run>.jsonl > out.jsonl
import { readFileSync } from "node:fs";
import { namedEntities, titleCovers } from "./subject_lib.ts";
import { healthTopicTerms, isHealthQuestion } from "../src/routing/context.ts";
import { englishNamesIn } from "../src/rag/ptLexicon.ts";
import * as PLA from "../src/rag/ptLexiconAsset.ts";

const rows = readFileSync(process.argv[2], "utf8").trim().split("\n").map((l) => JSON.parse(l));
const lex = (PLA as any).ptLexicon();
const LANG = new Map(readFileSync(new URL("./questions.exp09.jsonl", import.meta.url), "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((q: any) => [q.id, q.lang]));
for (const r of rows) {
  const codes: string[] = r.reasonCodes ?? [];
  const served = r.tier === "instant" ? (codes.includes("grounding:health-extractive") ? "health-extractive" : codes.includes("instant:final") ? "instant-final" : "instant-other")
    : r.instantText ? "preview-replaced" : null;
  if (!served) continue;
  const q: string = r.question;
  const health = isHealthQuestion(q);
  const pt = LANG.get(r.id) === "pt" || /-pt$/.test(r.id);
  let terms: string[] = health ? [...healthTopicTerms(q, null)] : pt ? englishNamesIn(q, lex) : namedEntities(q);
  terms = terms.filter((t) => t && t.length > 2);
  const cited: string[] = r.citedTitles?.length ? r.citedTitles : [];
  const srcTitles: string[] = served === "preview-replaced" || !cited.length ? (r.instantSources ?? []) : cited;
  const srcSections: string[] = (r.shownSources ?? []).filter((s: any) => srcTitles.includes(s.title)).map((s: any) => s.section ?? "").filter(Boolean);
  const coverT = terms.some((t) => srcTitles.some((ti) => titleCovers(t, ti)));
  const coverS = coverT || terms.some((t) => srcSections.some((se) => titleCovers(t, se)));
  console.log(JSON.stringify({ id: r.id, served, health, pt, terms, srcTitles, srcSections,
    h1_title: !terms.length ? "keep(no-subject)" : coverT ? "keep" : "block",
    h1_title_section: !terms.length ? "keep(no-subject)" : coverS ? "keep" : "block" }));
}
