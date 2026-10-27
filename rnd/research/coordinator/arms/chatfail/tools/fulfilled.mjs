// CHATFAIL S1 detectors (frozen by sha256 in fulfilled.sha256 before the first generation; any change = a new freeze).
// Criterion: arms/chatfail/CHATFAIL-S1-criterion.md (sha c8fde243...). Calibrated on CHAT-FU-v1 TURN TEXTS only, never on answers.
//   refusal(answer)  -> boolean   engine decline detector (DeepResearch.kt REFUSAL, ported as in arms/honestprompt/tools/score_a2.py A_RE, ^-anchored)
//                                 OR the criterion's phrase list anywhere in the answer.
//   fulfilled({expected_intent, turnText, answer, prevAnswer}) -> { ok, kind, why }
//     code      : a fenced code block (``` with at least one following non-empty line; an unclosed fence counts: the 512-token cap can cut it)
//                 or >= 3 lines that look like code (keyword / assignment / call statement / line ending in { } ;).
//     format    : kind from the turn text -> table (>= 2 markdown rows with pipes) | numbered (>= 2 "1." / "1)" lines) | list (>= 2 bullet,
//                 number or checkbox lines) | shorter (answer <= 50 % of the previous answer's characters; also "summarize it in two lines")
//                 | simple ("like I'm five": not a refusal, <= 90 words). Any format answer that is a refusal is not fulfilled.
//     translate : target language from the turn text (pt | es | de); stop-word ratio of the target >= 0.12 and > the English ratio; not a refusal.
const norm = (t) => String(t ?? "").replace(/[‘’]/g, "'").trim();

// --- refusal ---------------------------------------------------------------------------------------------------------------------
export const REFUSAL_ENGINE = /^(i'?m sorry|i am sorry|sorry|i (cannot|can't|can ?not|am unable|'m unable|don't have|do not have)|as an ai|unfortunately|desculp|lamento|infelizmente|não (posso|consigo|tenho)|nao (posso|consigo|tenho))/i;
export const REFUSAL_PHRASES = [/\bi can't\b/i, /\bi cannot\b/i, /\bi'm unable\b/i, /\bi am unable\b/i, /\bnot able to\b/i, /\bi don't have the ability\b/i, /\bi do not have the ability\b/i];
export function refusal(answer) {
  const t = norm(answer);
  return REFUSAL_ENGINE.test(t) || REFUSAL_PHRASES.some((re) => re.test(t));
}

// --- code ------------------------------------------------------------------------------------------------------------------------
const CODE_LINE = [
  /^\s*(?:def|class|import|from|function|const|let|var|return|if|elif|else|for|while|try|catch|contract|pragma|public|private|external|internal|struct|mapping|event|modifier|uint\d*|int\d*|address|bool|string|print|console\.log|require|emit|#include|using|namespace|fn|pub|use|select|insert)\b.*[\w)\]}"';:{]\s*$/i,
  /^\s*[A-Za-z_][\w.\[\]]*\s*(?::=|[-+*\/%]?=)\s*\S/, // assignment
  /^\s*[A-Za-z_][\w.]*\(.*\)\s*;?\s*$/, // call statement
  /[{};]\s*$/, // ends with a brace or semicolon
  /^\s*(?:\/\/|#)\s*\S/, // comment line
  /^\s*[})\]]+[;,]?\s*$/, // closer
];
export function codeLikeLines(answer) {
  return norm(answer).split("\n").filter((l) => l.trim() && CODE_LINE.some((re) => re.test(l)));
}
export function hasCode(answer) {
  const t = norm(answer);
  const m = t.match(/```[^\n]*\n([\s\S]*)/);
  if (m && m[1].split("\n").some((l) => l.trim() && !l.trim().startsWith("```"))) return true;
  return codeLikeLines(t).length >= 3;
}

// --- format ----------------------------------------------------------------------------------------------------------------------
export function formatKind(turnText) {
  const t = norm(turnText).toLowerCase();
  if (/\btable\b/.test(t)) return "table";
  if (/\bnumbered\b/.test(t)) return "numbered";
  if (/\b(bullet|checklist|list)\b/.test(t)) return "list";
  if (/\b(shorter|two lines|summari[sz]e)\b/.test(t)) return "shorter";
  if (/\b(five|5)\b/.test(t)) return "simple";
  return "other";
}
const lines = (a) => norm(a).split("\n");
export const tableRows = (a) => lines(a).filter((l) => (l.match(/\|/g) || []).length >= 2).length;
export const numberedLines = (a) => lines(a).filter((l) => /^\s*\d+[.)]\s+\S/.test(l)).length;
export const listLines = (a) => lines(a).filter((l) => /^\s*(?:[-*•]|\d+[.)]|\[[ xX]\]|- \[[ xX]\])\s+\S/.test(l)).length;
const words = (a) => norm(a).split(/\s+/).filter(Boolean).length;

// --- translate -------------------------------------------------------------------------------------------------------------------
const STOP = {
  en: "the and of to is are that it in for with as on was this be by or not from can you your which they have has will would".split(" "),
  pt: "de que e o os as um uma não para com em é do da dos das na por mais se como foi são ao ele ela mas ou você pelo pela seu sua isso esta este também já muito".split(" "),
  es: "de que y el los las un una para con en es del por más se como fue son al él ella pero o usted su sus esto esta este también ya muy lo".split(" "),
  de: "der die das und ist nicht ein eine zu den mit von auf für sich dem des im auch es sind wird wie oder aber nach bei aus nur noch".split(" "),
};
export function targetLang(turnText) {
  const t = norm(turnText).toLowerCase();
  if (/portugu|\bpt\b/.test(t)) return "pt";
  if (/spanish|espa[nñ]ol/.test(t)) return "es";
  if (/german|deutsch/.test(t)) return "de";
  return null;
}
export function stopRatio(answer, lang) {
  const toks = norm(answer).toLowerCase().split(/[^\p{L}]+/u).filter(Boolean);
  if (!toks.length) return 0;
  const set = new Set(STOP[lang]);
  return toks.filter((w) => set.has(w)).length / toks.length;
}

// --- fulfilled -------------------------------------------------------------------------------------------------------------------
export function fulfilled({ expected_intent, turnText, answer, prevAnswer }) {
  const a = norm(answer);
  if (!a) return { ok: false, kind: expected_intent, why: "empty" };
  if (expected_intent === "code") return { ok: hasCode(a), kind: "code", why: hasCode(a) ? "code" : "no-code" };
  if (expected_intent === "translate") {
    const lang = targetLang(turnText), r = refusal(a);
    if (!lang) return { ok: false, kind: "translate", why: "no-target-lang" };
    const tr = stopRatio(a, lang), en = stopRatio(a, "en");
    const ok = !r && tr >= 0.12 && tr > en;
    return { ok, kind: "translate:" + lang, why: r ? "refusal" : ok ? "target-lang" : `ratio ${tr.toFixed(2)} vs en ${en.toFixed(2)}` };
  }
  if (expected_intent === "format") {
    const kind = formatKind(turnText);
    if (refusal(a)) return { ok: false, kind, why: "refusal" };
    let ok = false;
    if (kind === "table") ok = tableRows(a) >= 2;
    else if (kind === "numbered") ok = numberedLines(a) >= 2;
    else if (kind === "list") ok = listLines(a) >= 2;
    else if (kind === "shorter") ok = prevAnswer != null && norm(prevAnswer).length > 0 ? a.length <= 0.5 * norm(prevAnswer).length : a.length <= 300;
    else if (kind === "simple") ok = words(a) <= 90;
    return { ok, kind, why: ok ? "shape" : "shape-missing" };
  }
  return { ok: false, kind: expected_intent, why: "not-a-capability-turn" };
}
