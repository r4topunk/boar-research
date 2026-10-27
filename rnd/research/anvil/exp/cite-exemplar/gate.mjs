// Port of boar-app 0cfd4a77 src/routing/citations.ts (+ tokenizeTerms from context.ts) and of the
// compact-model citation gate in src/routing/answer.ts (lines ~1188-1290), for offline replay only.
// Not covered: health route, wrong-script, false-quantum-claim, topic guard ("uncited-on-topic" path).
const STOPWORDS = new Set(
  (
    "a an the and or but if then else of to in on at by for with from as is are was were be been being " +
    "do does did doing have has had having it its this that these those there here what which who whom whose " +
    "when where why how can could should would will shall may might must i you he she we they me him her us them " +
    "my your his our their not no yes so than too very just about into over under between vs versus also " +
    "tell explain describe give me please much many more most some any all each other such only own same " +
    "o a os as um uma de do da dos das em no na nos nas por para com que qual quais quem como quando onde porque é"
  ).split(/\s+/)
);
function stem(t) {
  if (t.length > 5 && t.endsWith("ies")) return t.slice(0, -3) + "y";
  if (t.length > 4 && (t.endsWith("es") || t.endsWith("ed"))) return t.slice(0, -2);
  if (t.length > 3 && t.endsWith("s") && !t.endsWith("ss")) return t.slice(0, -1);
  if (t.length > 5 && t.endsWith("ing")) return t.slice(0, -3);
  return t;
}
export function tokenizeTerms(text) {
  return (text.toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "").match(/[a-z0-9]+/g) ?? [])
    .filter((t) => t.length > 1 && !STOPWORDS.has(t))
    .map(stem);
}
export const CITATION_MIN_SUPPORT = 0.5;
export const ATTRIBUTION_MIN_SUPPORT = 0.75;
const MIN_KEY_TERMS = 2;
const same = (a, b) => {
  if (a === b) return true;
  const [short, long] = a.length <= b.length ? [a, b] : [b, a];
  return short.length >= 5 && long.startsWith(short) && long.length - short.length <= 3;
};
const terms = (text) => tokenizeTerms(text).map((t) => (t.length > 4 && t.endsWith("e") ? t.slice(0, -1) : t));
const FILLER = new Set(
  (
    "like due often especially typically usually generally mainly primarily commonly both whereas while although though " +
    "however therefore thus hence hand per etc even still yet instead rather within throughout through across among " +
    "upon onto toward towards via around re"
  ).split(" ")
);
const keyTerms = (text) => [...new Set(terms(text.replace(/\[\d+\]/g, " ")))].filter((t) => !FILLER.has(t));
function sentenceBefore(text, at) {
  let j = at;
  while (j > 0 && /[\s\]\d[]/.test(text[j - 1]) && !/[.!?\n]/.test(text[j - 1])) j--;
  if (j > 0 && /[.!?]/.test(text[j - 1])) j--;
  let start = j;
  while (start > 0 && !/[.!?\n]/.test(text[start - 1])) start--;
  return text.slice(start, j);
}
export function citationSupport(sentence, source) {
  const key = keyTerms(sentence);
  if (key.length < MIN_KEY_TERMS) return 1;
  const have = terms(`${source.title} ${source.body}`);
  return key.filter((k) => have.some((h) => same(h, k))).length / key.length;
}
function paragraphBefore(text, at, end) {
  if (!/^[\s.!?]*(\n|$)/.test(text.slice(end))) return null;
  let start = at;
  while (start > 0 && text[start - 1] !== "\n" && text[start - 1] !== "]") start--;
  const span = text.slice(start, at);
  return (span.match(/[.!?](\s|$)/g) ?? []).length > 1 || /[.!?]\s+\S/.test(span.trim()) ? span : null;
}
export function checkCitations(answer, sources) {
  const removed = [];
  const text = answer.replace(/\s?\[(\d+)\]/g, (whole, num, at) => {
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
export function dedupeCitations(text) {
  return text.replace(/\[(\d+)\][ \t]*([.!?]?)[ \t]*\[\1\]/g, "[$1]$2");
}
export function attributeCitations(answer, sources) {
  const added = [];
  if (!sources.length) return { text: answer, added };
  const text = answer.replace(/[^.!?\n]+[.!?]*/g, (sentence, at) => {
    if (/\[\d+\]/.test(sentence)) return sentence;
    if (/^\s*\[\d+\]/.test(answer.slice(at + sentence.length))) return sentence;
    if (keyTerms(sentence).length < MIN_KEY_TERMS) return sentence;
    if (/^\s*(#{1,6}\s|\*\*[^*]+\*\*\s*:?\s*$)/.test(sentence)) return sentence;
    let best = -1, bestSupport = 0;
    sources.forEach((source, i) => {
      const support = citationSupport(sentence, source);
      if (support >= ATTRIBUTION_MIN_SUPPORT && support > bestSupport) { best = i; bestSupport = support; }
    });
    if (best < 0) return sentence;
    added.push(best + 1);
    const m = /^(.*?)(\s*)([.!?]*)(\s*)$/s.exec(sentence);
    return `${m[1]} [${best + 1}]${m[3]}${m[4]}`;
  });
  return { text: dedupeCitations(text), added };
}
/** Compact-model gate (sources present, not health, not multipass, answerAnyway off). */
export function compactGate(raw, sources) {
  let text = raw;
  const codes = [];
  let allRemoved = false;
  const rawHasCite = /\[\d+\]/.test(text);
  if (rawHasCite) {
    const c = checkCitations(text, sources);
    if (c.removed.length) { codes.push(`citations:removed-${c.removed.join("-")}`); text = c.text; allRemoved = !/\[\d+\]/.test(text); }
  }
  const a = attributeCitations(text, sources);
  if (a.added.length) { codes.push(`citations:added-${a.added.join("-")}`); text = a.text; }
  if (allRemoved && !/\[\d+\]/.test(text)) return { declined: true, code: "all-citations-removed", text, codes, rawHasCite };
  if (sources.length && text.trim() && !/\[\d+\]/.test(text)) return { declined: true, code: "uncited-with-sources", text, codes, rawHasCite };
  return { declined: false, code: "answered", text, codes, rawHasCite };
}
