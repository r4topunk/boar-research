// vg-apply: apply the verdict guard offline to stored answers, exactly as the engine hook does.
// usage: tsx vg-apply.mts <traces.jsonl> [--tree <engine tree> | --branch <git branch/commit>] [--jsonl out.jsonl] [--all]
//   default tree: <workspace>/wt/cut3-dev as checked out (coord/final = VG v3; warns if verdictGuard.ts isn't v3)
//   --branch coord/vg4 (or coord/final, a commit): exports src/ of that ref from the boar-app repo via `git archive` into a
//   temp dir and uses it, whatever wt/cut3-dev has checked out. VG v4 = coord/vg4 (verdictGuard.ts sha256 25d73a8b…).
// Per item it prints: itemId, flagged yes/no (or skip:<reason>), and for flagged items the kind, before and after.
// Engine parity: EN only (the engine also skips PT/ES), model answers only (health, cards, calculators, places, instant
// final, current-event and small-talk routes are skipped), and the app's uncited preface is stripped before the check and
// put back after (the hook runs before the preface is added). Input lines: protocol traces (itemId, question,
// answer.text, route.reasonCodes) or plain {id, question, answer}. --all also prints unflagged items in full.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import os from "node:os";
import { execSync } from "node:child_process";

const args = process.argv.slice(2);
const file = args.find((a) => !a.startsWith("--") && !["--tree", "--jsonl", "--branch"].includes(args[args.indexOf(a) - 1] ?? ""));
if (!file) {
  console.error("usage: tsx vg-apply.mts <traces.jsonl> [--tree <engine tree>] [--jsonl out.jsonl] [--all]");
  process.exit(1);
}
const opt = (k: string) => (args.includes(k) ? args[args.indexOf(k) + 1] : undefined);
const DEFAULT_TREE = "<workspace>/wt/cut3-dev";
let tree = opt("--tree") ?? DEFAULT_TREE;
const branch = opt("--branch");
if (branch) {
  if (!/^[\w./-]+$/.test(branch)) { console.error(`bad --branch ${branch}`); process.exit(1); }
  tree = fs.mkdtempSync(path.join(os.tmpdir(), "vg-apply-"));
  execSync(`git -C ${DEFAULT_TREE} archive ${branch} src | tar -x -C ${tree}`);
  fs.symlinkSync("<workspace>/boar-app/node_modules", path.join(tree, "node_modules"));
}
const KNOWN: Record<string, string> = { "6f589e630421fbc921652aaef283e3236837bf11548d545609e6c34bb7b397f1": "VG v3", "25d73a8b41161a743078a583ff80f91f6008f70346b198adb3e761f85024937f": "VG v4" };
const vgPath = path.join(tree, "src/routing/verdictGuard.ts");
const sha = crypto.createHash("sha256").update(fs.readFileSync(vgPath)).digest("hex");
const V3 = "6f589e630421fbc921652aaef283e3236837bf11548d545609e6c34bb7b397f1";
if (!opt("--tree") && !branch && sha !== V3) console.error(`warning: ${vgPath} sha256 ${sha.slice(0, 8)}… is not VG v3 (${V3.slice(0, 8)}…); check out coord/final or pass --branch`);
const { verdictGuard } = await import(vgPath);
const { isPortugueseQuestion, isSpanishQuestion } = await import(path.join(tree, "src/routing/context.ts"));

const PREFACE = "This answer is not from an offline source on this phone; check it before relying on it.";
const NOT_MODEL = /answer:|grounding:health|instant:final|places|calculator|grounding:current-event|small-talk|safety-fact/;
const rows = fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const out: any[] = [];
let flagged = 0, checked = 0;
for (const r of rows) {
  const id = r.itemId ?? r.id ?? "?";
  const question: string = r.question ?? r.item?.question ?? "";
  const text: string = r.answer?.text ?? (typeof r.answer === "string" ? r.answer : "");
  const codes: string[] = r.route?.reasonCodes ?? [];
  let skip: string | null = null;
  if (!text) skip = "no-answer";
  else if (codes.length && NOT_MODEL.test(codes.join(" "))) skip = "not-model-route";
  else if (isPortugueseQuestion(question) || isSpanishQuestion(question)) skip = "not-en";
  let res: { kind: string; text: string } | null = null;
  let after = text;
  if (!skip) {
    checked++;
    let body = text, pre = "";
    if (body.startsWith(PREFACE)) { pre = PREFACE + "\n\n"; body = body.slice(PREFACE.length).replace(/^\s+/, ""); }
    res = verdictGuard(question, body);
    if (res) { flagged++; after = pre + res.text; }
  }
  const rec = { itemId: id, flagged: !!res, skip, kind: res?.kind ?? null, question, before: text, after };
  out.push(rec);
  if (res) console.log(`${id}\tflagged=yes\t${res.kind}\n  Q: ${question}\n  BEFORE: ${text.replace(/\n+/g, " / ")}\n  AFTER:  ${after.replace(/\n+/g, " / ")}`);
  else console.log(`${id}\tflagged=no${skip ? `\tskip:${skip}` : ""}${args.includes("--all") && !skip ? `\n  ANSWER: ${text.replace(/\n+/g, " / ")}` : ""}`);
}
console.log(`\n${path.basename(file)}: ${rows.length} items, ${checked} checked (EN model answers), ${flagged} flagged; verdictGuard.ts sha256 ${sha.slice(0, 16)}… (${KNOWN[sha] ?? "unknown version"}${branch ? `, --branch ${branch}` : ""})`);
const j = opt("--jsonl");
if (j) fs.writeFileSync(j, out.map((o) => JSON.stringify(o)).join("\n") + "\n");
