/**
 * CITEFIX (2026-10-21): model-agnostic citation normaliser. Maps source references whose target is unambiguous to
 * the engine's [n] form BEFORE CT-1 (checkCitations) and the compact release/decline rules run, so a model that
 * cites in another notation is judged on its support, not on its notation. It never adds a reference where the
 * model wrote none, and maps only numbers 1..sourceCount. Pure; no imports, so it runs under plain node too.
 *
 *   [1, 3] / [1,2,6] / [1; 2]          -> [1][3] / [1][2][6] / [1][2]   (bracket list of source numbers)
 *   [Source 2] / [source 1, 3] / [Passage 2] / [Doc 2] / [Document 2] -> [2] / [1][3]
 *   (Source 2) / (Passage 2)             -> [2]
 *   【2】                                -> [2]
 *   [^2] (footnote marker, not a "[^2]:" definition) -> [2]
 *
 * Not mapped (ambiguous): superscripts (km², 10⁻⁴³), bare "(1)" (enumerations), "^100", titles, ranges ("[1-3]",
 * also regex classes), any list with a number outside 1..sourceCount or a repeated number, anything inside `code`.
 */
const NAMED = "(?:source|passage|doc(?:ument)?)";
const NUMS = "\\d{1,2}(?:\\s*[,;]\\s*\\d{1,2})*";
const FORMS: RegExp[] = [
  new RegExp(`\\[\\s*${NAMED}s?\\s*#?\\s*(${NUMS})\\s*\\]`, "gi"),
  new RegExp(`\\(\\s*${NAMED}s?\\s*#?\\s*(${NUMS})\\s*\\)`, "gi"),
  /【\s*(\d{1,2})\s*】/g,
  /\[\^(\d{1,2})\](?!:)/g,
  // A bare bracket list needs at least two numbers ("[1]" is already the engine's form) and must not follow "=", "(", a
  // word character or "]" directly (code arrays: "x = [1, 2]", "f([1, 2])", "arr[1, 2]").
  /(?<![\w\]])(?<![=(]\s?)\[(\d{1,2}(?:\s*[,;]\s*\d{1,2})+)\]/g,
];

export function normalizeCitations(text: string, sourceCount: number): { text: string; mapped: number } {
  if (sourceCount <= 0 || !/[\[(【]/.test(text)) return { text, mapped: 0 };
  let mapped = 0;
  // Leave fenced and inline code alone: split on code spans, map only the prose parts.
  const parts = text.split(/(```[\s\S]*?```|`[^`\n]*`)/g);
  const out = parts.map((part, i) => {
    if (i % 2 === 1) return part;
    let p = part;
    for (const re of FORMS) {
      p = p.replace(re, (whole: string, list: string) => {
        const ns = list.split(/\s*[,;]\s*/).map(Number);
        if (ns.some((n) => !Number.isInteger(n) || n < 1 || n > sourceCount) || new Set(ns).size !== ns.length) return whole;
        mapped++;
        return ns.map((n) => `[${n}]`).join("");
      });
    }
    return p;
  });
  return mapped ? { text: out.join(""), mapped } : { text, mapped: 0 };
}
