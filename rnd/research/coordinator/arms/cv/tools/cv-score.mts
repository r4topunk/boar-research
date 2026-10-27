// cv-score: verdict accuracy of cut 3 vs cut 3 + CV on the DEV probe items, against a gold key. Verdict only, no judge.
// usage: tsx cv-score.mts --key key.jsonl --cut3 cv-dev-cut3-s44/traces.jsonl --cv cv-dev-cv-s44/traces.jsonl [--tree <workspace>/wt/cv] [--detail out.jsonl]
//
// KEY FORMAT (one JSON object per line; the scorer never looks at any other field):
//   { "id": "vgq-007", "answer": "gold" }              which-question: the correct winner, as a name (or an "accept": [...] list of spellings)
//   { "id": "vgq-013", "answer": "yes" }               yes/no question: "yes" or "no"
//   optional "options": ["gold", "lead"]               the two candidates of a which-question when the router can't name them
// Items not in the key are not scored. Items with a key line but no parseable verdict in an answer count as wrong and are listed
// as `unknown`.
//
// VERDICT EXTRACTION
//   Both arms: the app's uncited preface ("This answer is not from an offline source ...") is stripped first.
//   CV answers (reason code `answer:computed-verdict`): the verdict line = the first line of the text.
//     yes/no: starts with "Yes" / "No".   which: "<winner> is|has|came|gets|holds ... than <loser>." -> the text before the verb.
//   Cut 3 answers (and a CV-arm answer where CV abstained: the criterion counts those as cut 3's answer, so the cut 3 trace's
//   answer is used for that item): FIRST-SENTENCE HEURISTIC, because verdictGuard.ts keeps its verdict reading private.
//     yes/no: the first sentence starts with Yes/No/Correct/Incorrect/True/False (after markdown and "Answer:"), else it is
//             "unknown" (a leading restatement of facts is not guessed).
//     which:  of the two candidate names (the router's entities, or the key's "options"), the one that appears first in the first
//             sentence is the winner; if the sentence has a "smaller-end" word (less, fewer, smaller, shorter, lighter, slower,
//             lower, colder, younger, closer) while the question asks for the larger end (or the reverse), the other name is the
//             winner. Neither name in the first sentence -> unknown.
//   A name matches case-insensitively on its non-generic words (the, of, river, lake, mount ...), as in the engine.
import fs from "node:fs";

const arg = (k: string, d?: string) => {
  const i = process.argv.indexOf(k);
  return i >= 0 ? process.argv[i + 1] : d;
};
const need = (k: string) => arg(k) ?? (console.error(`missing ${k}`), process.exit(2));
const tree = arg("--tree", "<workspace>/wt/cv")!;
const { routeVerdict, sameName } = await import(`${tree}/src/routing/computedVerdict.ts`);
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));

interface KeyRow { id: string; answer: string; accept?: string[]; options?: [string, string] }
const key: KeyRow[] = jl(need("--key"));
const t3 = new Map<string, any>(jl(need("--cut3")).map((t: any) => [t.itemId, t]));
const tcv = new Map<string, any>(jl(need("--cv")).map((t: any) => [t.itemId, t]));

const PREFACE = /^\s*This answer is not from an offline source[^\n]*\n+/i;
const textOf = (t: any): string => String(t?.answer?.text ?? "").replace(PREFACE, "").trim();
const isCV = (t: any) => (t?.route?.reasonCodes ?? []).includes("answer:computed-verdict");
const firstSentence = (s: string) => {
  const line = s.replace(/^[*_#>\s]+/, "").replace(/^answer\s*:\s*/i, "").split(/\n/)[0];
  const m = line.match(/^(.+?[.!?])(?:\s|$)/);
  return (m ? m[1] : line).trim();
};
const SMALL_END = /\b(?:less|fewer|smaller|shorter|lighter|slower|lower|colder|younger|closer|cooler|shallower|narrower)\b/i;
const BIG_END = /\b(?:more|larger|bigger|taller|longer|heavier|faster|higher|hotter|older|farther|further|denser|deeper|wider|greater)\b/i;

function yesNo(sentence: string): "yes" | "no" | "unknown" {
  const m = sentence.replace(/^[*_"'\s]+/, "").match(/^(yes|no|correct|incorrect|true|false)\b/i);
  if (!m) return "unknown";
  return /^(yes|correct|true)$/i.test(m[1]) ? "yes" : "no";
}
function whichWinner(sentence: string, options: [string, string], askedBigEnd: boolean): string | "unknown" {
  const lower = sentence.toLowerCase();
  const pos = options.map((o) => {
    const words = o.toLowerCase().replace(/[^a-z0-9 ]/g, " ").split(/\s+/).filter((w) => w && !["the", "of", "a", "an"].includes(w));
    const idx = words.map((w) => lower.search(new RegExp(`\\b${w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`))).filter((i) => i >= 0);
    return idx.length ? Math.min(...idx) : -1;
  });
  if (pos[0] < 0 && pos[1] < 0) return "unknown";
  let first = pos[1] < 0 || (pos[0] >= 0 && pos[0] <= pos[1]) ? 0 : 1;
  const flips = askedBigEnd ? SMALL_END.test(sentence) && !BIG_END.test(sentence) : BIG_END.test(sentence) && !SMALL_END.test(sentence);
  if (flips && pos[0] >= 0 && pos[1] >= 0) first = 1 - first;
  return options[first];
}
function cvWinner(verdictLine: string): string {
  const m = verdictLine.match(/^(.+?)\s+(?:is|are|has|have|came|gets|holds|was)\b/i);
  return m ? m[1] : "unknown";
}

function extract(k: KeyRow, t: any): string {
  const s = textOf(t);
  if (!s) return "unknown";
  const yn = /^(yes|no)$/i.test(k.answer);
  if (isCV(t)) {
    const line = s.split("\n")[0];
    return yn ? yesNo(line) : cvWinner(line);
  }
  const sentence = firstSentence(s);
  if (yn) return yesNo(sentence);
  const plan = routeVerdict(t.question ?? "");
  const options: [string, string] | undefined = k.options ?? (plan?.kind === "compare" ? [plan.a.name, plan.b.name] : undefined);
  if (!options) return "unknown";
  return whichWinner(sentence, options, (plan?.kind === "compare" ? plan.dir : "max") === "max");
}
function correct(k: KeyRow, got: string): boolean {
  if (got === "unknown") return false;
  if (/^(yes|no)$/i.test(k.answer)) return got.toLowerCase() === k.answer.toLowerCase();
  return [k.answer, ...(k.accept ?? [])].some((a) => sameName(a, got));
}

let n = 0, ok3 = 0, okCv = 0, wrongWhereRight = 0, rightWhereWrong = 0, abst = 0, unk3 = 0, unkCv = 0, cvAnswered = 0;
const badIds: string[] = [], goodIds: string[] = [], absIds: string[] = [];
const detail: any[] = [];
for (const k of key) {
  const a = t3.get(k.id), b = tcv.get(k.id);
  if (!a || !b) { console.error(`no trace for ${k.id}`); continue; }
  n++;
  const g3 = extract(k, a);
  const routed = !!routeVerdict(b.question ?? a.question ?? "");
  const cvUsed = isCV(b);
  if (cvUsed) cvAnswered++;
  if (routed && !cvUsed) { abst++; absIds.push(k.id); }
  // the criterion: an abstained or unparsed item counts as cut 3's answer
  const gcv = cvUsed ? extract(k, b) : g3;
  if (g3 === "unknown") unk3++;
  if (gcv === "unknown") unkCv++;
  const r3 = correct(k, g3), rc = correct(k, gcv);
  if (r3) ok3++;
  if (rc) okCv++;
  if (r3 && !rc) { wrongWhereRight++; badIds.push(k.id); }
  if (!r3 && rc) { rightWhereWrong++; goodIds.push(k.id); }
  detail.push({ id: k.id, key: k.answer, cut3: g3, cv: gcv, cvAnswered: cvUsed, routed });
}
const pct = (x: number) => (n ? (100 * x / n).toFixed(1) : "n/a");
console.log(`scored ${n} items`);
console.log(`cut 3        : ${ok3}/${n} = ${pct(ok3)} %  (unknown verdicts counted wrong: ${unk3})`);
console.log(`cut 3 + CV   : ${okCv}/${n} = ${pct(okCv)} %  (unknown: ${unkCv}; CV answered ${cvAnswered}, routed but abstained ${abst})`);
console.log(`delta        : ${n ? (100 * (okCv - ok3) / n).toFixed(1) : "n/a"} percentage points (bar >= +10)`);
console.log(`wrong where cut 3 right : ${wrongWhereRight}${badIds.length ? "  " + badIds.join(" ") : ""}  (bar <= 2)`);
console.log(`right where cut 3 wrong : ${rightWhereWrong}${goodIds.length ? "  " + goodIds.join(" ") : ""}`);
console.log(`CV abstained (routed, normal path answered): ${abst}${absIds.length ? "  " + absIds.join(" ") : ""}`);
const out = arg("--detail");
if (out) fs.writeFileSync(out, detail.map((d) => JSON.stringify(d)).join("\n") + "\n");
