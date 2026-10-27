/**
 * CT-1 (Prism): a [n] must point at a source that supports its sentence. The
 * models answer from memory and still cite [1] ("Earth's axial tilt causes
 * the seasons [1]" with [1] = Walipini, a greenhouse). A citation stays only
 * when the source contains at least half of the sentence's key words; one
 * pointing past the sources is always dropped. Pure.
 */
import type { RetrievedChunk } from "../rag/retrieve.types";
import { tokenizeTerms } from "./context.ts";

/** Share of a cited sentence's key words the source must contain. */
export const CITATION_MIN_SUPPORT = 0.5;
/** Sentences with fewer key words than this are too short to judge: the citation stays. */
const MIN_KEY_TERMS = 2;

const same = (a: string, b: string) => {
  if (a === b) return true;
  const [short, long] = a.length <= b.length ? [a, b] : [b, a];
  return short.length >= 5 && long.startsWith(short) && long.length - short.length <= 3;
};

/** tokenizeTerms without a final "e", so "cause" meets "caused"/"causes" ("caus") and "radiate" meets "radiation". */
const terms = (text: string) => tokenizeTerms(text).map((t) => (t.length > 4 && t.endsWith("e") ? t.slice(0, -1) : t));

/**
 * Words an English paraphrase adds around a claim without adding one ("gases like carbon dioxide", "due to",
 * "on the other hand"); as key words they made a faithful paraphrase of a short source fall under the bar
 * (iPhone 13, 28/09: the 1.5B's monsoon and the 4B's greenhouse answers lost their [1]). Word fragments
 * ("re-radiate") too.
 */
const FILLER = new Set(
  (
    "like due often especially typically usually generally mainly primarily commonly both whereas while although though " +
    "however therefore thus hence hand per etc even still yet instead rather within throughout through across among " +
    "upon onto toward towards via around re"
  ).split(" ")
);
const keyTerms = (text: string) => [...new Set(terms(text.replace(/\[\d+\]/g, " ")))].filter((t) => !FILLER.has(t));

/** The sentence a citation at `at` belongs to: back past "." and spaces right before it, then to the previous sentence end. */
function sentenceBefore(text: string, at: number): string {
  let j = at;
  while (j > 0 && /[\s\]\d[]/.test(text[j - 1]) && !/[.!?\n]/.test(text[j - 1])) j--;
  if (j > 0 && /[.!?]/.test(text[j - 1])) j--;
  let start = j;
  while (start > 0 && !/[.!?\n]/.test(text[start - 1])) start--;
  return text.slice(start, j);
}

export function citationSupport(sentence: string, source: RetrievedChunk): number {
  const key = keyTerms(sentence);
  if (key.length < MIN_KEY_TERMS) return 1;
  const have = terms(`${source.title} ${source.body}`);
  return key.filter((k) => have.some((h) => same(h, k))).length / key.length;
}

export interface CheckedCitations {
  text: string;
  /** Source numbers removed, in order of appearance. */
  removed: number[];
}

/**
 * What a citation that closes its paragraph ("A. B. [1]", "A. B [1].") vouches for: the whole paragraph
 * since the previous citation, judged as one claim at the bar for adding a citation (ATTRIBUTION_MIN_SUPPORT):
 * a bigger claim, a higher bar. The 1.5B writes one [1] after a whole explanation; judging only its last
 * sentence ("This cycle keeps Earth warm, essential for life.") dropped it. At the lower bar, loose word
 * overlap passed ("The United States has 50 states. The element with atomic number 50 is tin." with
 * Avogadro: 0.5). Null for a citation inside a paragraph, or one that closes a single sentence.
 */
function paragraphBefore(text: string, at: number, end: number): string | null {
  if (!/^[\s.!?]*(\n|$)/.test(text.slice(end))) return null;
  let start = at;
  while (start > 0 && text[start - 1] !== "\n" && text[start - 1] !== "]") start--;
  const span = text.slice(start, at);
  return (span.match(/[.!?](\s|$)/g) ?? []).length > 1 || /[.!?]\s+\S/.test(span.trim()) ? span : null;
}

export function checkCitations(answer: string, sources: RetrievedChunk[]): CheckedCitations {
  const removed: number[] = [];
  const text = answer.replace(/\s?\[(\d+)\]/g, (whole, num: string, at: number) => {
    const n = Number(num);
    const source = sources[n - 1];
    const bracket = at + whole.indexOf("[");
    const paragraph = source ? paragraphBefore(answer, bracket, at + whole.length) : null;
    const keep =
      !!source &&
      (citationSupport(sentenceBefore(answer, bracket), source) >= CITATION_MIN_SUPPORT ||
        (paragraph !== null && citationSupport(paragraph, source) >= ATTRIBUTION_MIN_SUPPORT));
    if (keep) return whole;
    removed.push(n);
    return "";
  });
  return { text: removed.length ? text.replace(/[ \t]+([.,;:!?])/g, "$1").replace(/[ \t]{2,}/g, " ") : answer, removed };
}

export interface AttributedCitations {
  text: string;
  /** Source numbers added, in order of appearance. */
  added: number[];
}

/**
 * Share of a sentence's key words a source must contain for a [n] to be ADDED. Higher than the bar to
 * keep one (CITATION_MIN_SUPPORT): on gate 9ef80f9's real uncited answers, 0.5 would have cited the
 * Post-quantum cryptography article for "…signature algorithms include those based on elliptic curve
 * cryptography (ECC)" (wrong; 0.67), while the monsoon (0.84), greenhouse (0.86) and OQS (1.0) sentences
 * clear 0.75.
 */
export const ATTRIBUTION_MIN_SUPPORT = 0.75;

/**
 * The honest inverse of checkCitations (Boar, gate 9ef80f9: the 4B answered the monsoon from the Monsoon
 * source and the 1.5B the greenhouse effect from its article, without a [n]): a sentence without a
 * citation gets the [n] of the source that supports it, by the same measure at a higher bar. A sentence
 * too short to judge never gets one (checkCitations keeps those; adding needs real support).
 */
export function attributeCitations(answer: string, sources: RetrievedChunk[]): AttributedCitations {
  const added: number[] = [];
  if (!sources.length) return { text: answer, added };
  const text = answer.replace(/[^.!?\n]+[.!?]*/g, (sentence: string, at: number) => {
    if (/\[\d+\]/.test(sentence)) return sentence;
    // A citation right after the sentence's punctuation ("… Zone. [1]") is its own (Prism CIT-2: "[1]. [1]").
    if (/^\s*\[\d+\]/.test(answer.slice(at + sentence.length))) return sentence;
    if (keyTerms(sentence).length < MIN_KEY_TERMS) return sentence;
    // A heading or a bold title line ("## Greenhouse effect", "**Causes:**") names a topic, it claims nothing.
    if (/^\s*(#{1,6}\s|\*\*[^*]+\*\*\s*:?\s*$)/.test(sentence)) return sentence;
    let best = -1;
    let bestSupport = 0;
    sources.forEach((source, i) => {
      const support = citationSupport(sentence, source);
      if (support >= ATTRIBUTION_MIN_SUPPORT && support > bestSupport) {
        best = i;
        bestSupport = support;
      }
    });
    if (best < 0) return sentence;
    added.push(best + 1);
    const m = /^(.*?)(\s*)([.!?]*)(\s*)$/s.exec(sentence)!;
    return `${m[1]} [${best + 1}]${m[3]}${m[4]}`;
  });
  return { text: dedupeCitations(text), added };
}

/** The same [n] twice around one sentence end ("… Zone [1]. [1]", "… [1] [1].") is shown once (Prism CIT-2). */
export function dedupeCitations(text: string): string {
  return text.replace(/\[(\d+)\][ \t]*([.!?]?)[ \t]*\[\1\]/g, "[$1]$2");
}
