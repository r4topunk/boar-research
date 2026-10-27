// exp-09 LOCAL COPY of boar-app 611a4b92 src/routing/o2WeakSupport.ts with namedEntities / titleCovers / norm exported
// (no logic change), for the offline subject-check hypothesis. Not app code.
/**
 * O2 "off-subject" early decline (exp-03; rule rnd/lantern/o2-weak-support-spec.md, reference
 * rnd/lantern/tools/o2_reference.py, ported function by function). A numeric / superlative / comparative / list
 * question whose passages are all about something else (Kantō region for "Japan's population", Moose for "the
 * tallest animal") is declined before prefill on the compact tier: the small model otherwise states a number or a
 * ranking the passages don't hold. No model and no asset: regexes, title normalization and one scan of the text.
 *
 * Fails open: no subject extracted, or a Portuguese question whose subject the lexicon can't name in English, keeps
 * the answer. No geographic containment: "Kantō region" does not cover "Japan". No alias table yet (no redirects
 * lookup in src/rag), so "USA" vs "United States" refuses: tracked in the A/B as `o2:no-alias-table`.
 */

/** Off until the blind iPhone A/B (exp-03 README §5) passes; EXPO_PUBLIC_O2_COMPACT=1 turns it on in a build. */
export const O2_COMPACT = process.env.EXPO_PUBLIC_O2_COMPACT === "1";

let override: boolean | undefined;
/** An evaluation run's arm (src/eval/answerEval.ts, eval builds only); undefined goes back to the build flag. */
export function setO2Override(on: boolean | undefined): void {
  override = on;
}
export function o2Enabled(): boolean {
  return override ?? O2_COMPACT;
}

export type O2Kind = "list" | "superlative" | "comparative" | "numeric";
export type O2Passage = { title: string; text?: string | null };
export type O2Decision = {
  inScope: boolean;
  kind?: O2Kind;
  action: "keep" | "refuse";
  reason: string;
  /** What the question is about, for the decline message (named subjects only). */
  questionSubject?: string;
  /** The first passage's title without its source label. */
  passageSubject?: string;
};

// Python's Unicode \w and \b: JS's are ASCII-only, and Portuguese questions have accents ("população", "países").
const W = "[\\p{L}\\p{N}_]";
const NW = "[^\\p{L}\\p{N}_]";
const B = `(?:(?<=${W})(?!${W})|(?<!${W})(?=${W}))`;
/** A reference pattern with Python's \w, \W and \b (outside character classes), Unicode-aware. */
const rx = (src: string, flags = "") => new RegExp(src.replace(/\\b/g, B).replace(/\\W/g, NW).replace(/\\w/g, W), `${flags}u`);
const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\/]/g, "\\$&");

// ---- §3.1 scope -------------------------------------------------------------------------------------------------
const SUPERL_EN =
  "(most|least|largest|biggest|smallest|tallest|highest|lowest|heaviest|lightest|longest|shortest|oldest|" +
  "youngest|deepest|fastest|richest|poorest|densest|hottest|coldest|busiest)";
const SUPERL_PT = "(?:o|a|os|as) (?:\\w+ )?(?:mais|menos) \\w+ d[oa]s? \\w+|(?:o|a|os|as) (?:mais|menos) \\w+|(?:o|a|os|as) (?:maior|menor)(?:es)?";
const COMPAR_EN =
  "(larger|bigger|smaller|taller|shorter|heavier|lighter|older|younger|longer|more populous|more densely|" + "more|fewer|less|exceed\\w*|outnumber\\w*)";
const COMPAR_PT =
  "mais \\w+(?: \\w+)? (?:que|do que)|maior(?:es)? (?:que|do que)|menor(?:es)? (?:que|do que)|ultrapass\\w*|" +
  "mais (?:pesad|alt|populos|grand|long|antig)\\w*";
const NUMERIC =
  "(how (many|much|far|long|tall|high|big|old|heavy|often|deep|wide)|population|populated|height|" +
  "weigh\\w*|distance|area of|density|number of|what year|which year|when did|when was|how fast|" +
  "quant[oa]s?|população|altura|distância|peso|em que ano|quando)";
const RX_SUPERL = rx(`\\b(${SUPERL_EN}|${SUPERL_PT})\\b`, "i");
const RX_SUPERL_EN = rx(`\\b${SUPERL_EN}\\b`, "i");
const RX_COMPAR = rx(`\\b(${COMPAR_EN}|${COMPAR_PT})\\b`, "i");
const RX_NUMERIC = rx(`\\b${NUMERIC}\\b`, "i");
const RX_TWO_SIDED = rx("\\b(or|than|ou|que|vs\\.?|versus)\\b", "i");
const NOT_PLURAL = new Set(["is", "was", "has", "does", "this", "its", "pais", "mais"]);
/** "which countries…", "quais países…". */
const RX_LISTQ = rx("^\\s*(?:which|what|quais|que)\\s+(\\w{3,}(?:s|es))\\b", "i");
/** Causal/explanatory ("why did Terra collapse in 2022?"): out of scope. */
const RX_WHY = rx("^\\s*(why|how did|how does|how do|explain|por que|porque|como)\\b", "i");

function listNoun(q: string): string | null {
  const m = RX_LISTQ.exec(q);
  return m && !NOT_PLURAL.has(m[1].toLowerCase()) ? m[1] : null;
}

/** Which kind of question O2 judges, or null when it's out of scope. The order of the steps is the spec's. */
export function o2Kind(q: string): O2Kind | null {
  if (RX_WHY.test(q)) return null;
  const twoSided = RX_TWO_SIDED.test(q);
  const sup = RX_SUPERL.test(q);
  const comp = RX_COMPAR.test(q);
  if (listNoun(q) && (sup || comp)) return "list";
  if (sup && !(comp && twoSided && !RX_SUPERL_EN.test(q))) return "superlative";
  if (comp && twoSided) return "comparative";
  if (RX_NUMERIC.test(q)) return "numeric";
  return null;
}

// ---- §3.2 subjects ----------------------------------------------------------------------------------------------
const QWORDS = new Set(
  (
    "what which who how is are was were did does do could can tell when where why i if my with and qual quais quem " +
    "como quando onde quanto quantos quantas o a os as the in"
  ).split(" ")
);
const JOIN = new Set(["of", "the", "de", "da", "do", "dos", "das"]);
const ATTR = new Set(
  (
    "population populations larger bigger heavier taller smaller more densely populated weigh weighs be is are an a " +
    "the which populacao mais pesados pesadas altos altas sao e"
  ).split(" ")
);

export function norm(s: string | null | undefined): string {
  const ascii = (s ?? "")
    .normalize("NFKD")
    .replace(/[^\x00-\x7f]/g, "")
    .toLowerCase();
  return ascii
    .replace(/'s\b|’s\b/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function stem(w: string): string {
  for (const suf of ["ies", "es", "s"]) {
    if (w.endsWith(suf) && w.length > suf.length + 2) return w.slice(0, -suf.length) + (suf === "ies" ? "y" : "");
  }
  return w;
}

const isUpper = (t: string) => {
  const c = t.slice(0, 1);
  return c !== "" && c === c.toUpperCase() && c !== c.toLowerCase();
};

/** Quoted spans, capitalized spans (not sentence-initial) and codes like EIP-7251 / ERC-20. */
export function namedEntities(q: string): string[] {
  const ents: string[] = [];
  for (const m of q.matchAll(/(?<![\p{L}\p{N}_])['"‘“]([^'"’”]{3,40})['"’”]/gu)) ents.push(m[1]);
  const toks = q.match(/[\p{L}\p{N}_\-’']+|[^\p{L}\p{N}_\s]/gu) ?? [];
  let cur: string[] = [];
  let sentStart = true;
  toks.forEach((t, i) => {
    const code = /^[A-Z]{2,}-?\d+[A-Za-z]*$/.test(t);
    const next = toks[i + 1];
    const cap =
      (isUpper(t) && !sentStart) || code || (isUpper(t) && sentStart && !QWORDS.has(norm(t)) && next !== undefined && isUpper(next));
    if (cap && !QWORDS.has(norm(t))) cur.push(t);
    else if (cur.length && JOIN.has(t.toLowerCase()) && next !== undefined && isUpper(next)) cur.push(t);
    else if (cur.length) {
      ents.push(cur.join(" "));
      cur = [];
    }
    sentStart = t === "." || t === "?" || t === "!";
    if (i === 0) sentStart = false;
  });
  if (cur.length) ents.push(cur.join(" "));
  return [...new Set(ents)].filter((e) => norm(e) && !QWORDS.has(norm(e)));
}

function comparisonSides(q: string): string[] {
  const ents = namedEntities(q);
  if (ents.length >= 2) return ents.slice(0, 2);
  const ql = q.toLowerCase().replace(/[?!.,]/g, " ");
  const m = rx("\\b(?:or|than|ou|que|do que|vs|versus)\\b").exec(ql);
  if (!m) return ents;
  const parts = [ql.slice(0, m.index), ql.slice(m.index + m[0].length)];
  const words = (s: string) => norm(s).split(" ").filter(Boolean);
  const left = words(parts[0])
    .filter((w) => !ATTR.has(w) && !QWORDS.has(w) && w !== "which")
    .slice(-2);
  const right = words(parts[1])
    .filter((w) => !ATTR.has(w) && !QWORDS.has(w))
    .slice(0, 3)
    .filter((w) => !/^(?:\w+er|\w+est)$/.test(w) || w === "deer")
    .slice(0, 2);
  return [left, right].filter((x) => x.length).map((x) => x.join(" "));
}

function superlativeClass(q: string): string | null {
  const m = rx(`\\b${SUPERL_EN}\\s+(?:\\w+ed\\s+|\\w+ous\\s+|living\\s+|land\\s+|known\\s+)?(\\w+)`, "i").exec(q);
  if (m && !ATTR.has(norm(m[2])) && !["in", "of", "world", "r0"].includes(norm(m[2]))) return m[2];
  // PT: "o animal mais alto".
  const p = rx("\\b(\\w+) (?:mais|menos) \\w+", "i").exec(q);
  if (p && !QWORDS.has(norm(p[1])) && !ATTR.has(norm(p[1]))) return p[1];
  return listNoun(q);
}

type Subjects = { mode: "any" | "all" | "class"; terms: string[] };

function subjectsOf(q: string, kind: O2Kind): Subjects {
  if (kind === "comparative") return { mode: "all", terms: comparisonSides(q) };
  if (kind === "list") {
    const noun = listNoun(q);
    return { mode: "class", terms: noun ? [noun] : [] };
  }
  let ents = namedEntities(q).filter((e) => !/^(R0|R₀)$/u.test(e));
  if (kind === "superlative" && !ents.length) {
    const c = superlativeClass(q);
    return { mode: "class", terms: c ? [c] : [] };
  }
  if (!ents.length && /\bworld\b|\bmundo\b/i.test(q)) ents = ["world"];
  if (
    kind === "numeric" &&
    ents.length >= 2 &&
    rx("\\bfrom\\b.+\\bto\\b|\\bbetween\\b|\\bde\\b.+\\ba\\b|\\bentre\\b", "i").test(q) &&
    !/^(EIP|ERC)/.test(namedEntities(q)[0])
  ) {
    return { mode: "all", terms: ents.slice(0, 2) };
  }
  return { mode: "any", terms: ents };
}

// ---- §3.3/3.4 matching ------------------------------------------------------------------------------------------
/** The app's source labels (src/rag/packs.ts SOURCE_LABEL) in front of a non-Wikipedia title. */
const PREFIX = /^(Wikivoyage|Wikibooks|Appropedia|US government|Ethereum EIPs\/ERCs|ethereum\.org|Ethereum specs|Bitcoin BIPs)[^:]*:\s*/;

const words = (s: string) => s.split(" ").filter(Boolean);

/**
 * Aboutness: the passage's title contains the subject (token subsequence after normalization and plural stemming).
 * Part-of relations are NOT coverage: "Kantō region" does not cover "Japan".
 */
export function titleCovers(term: string, title: string): boolean {
  const t = words(norm(title.replace(PREFIX, ""))).map(stem);
  const s = words(norm(term))
    .filter((w) => !["the", "a", "an"].includes(w))
    .map(stem);
  if (!s.length || !t.length) return false;
  const contains = (hay: string[], needle: string[]) => {
    for (let i = 0; i + needle.length <= hay.length; i++) if (needle.every((w, j) => hay[i + j] === w)) return true;
    return false;
  };
  return contains(t, s) || contains(s, t);
}

const NARROW = rx(
  "\\b(in|of) (the )?(north|south|east|west|central)?\\s*([A-Z][\\p{L}\\p{N}_-]+|arab world|the americas|region|genus|family|deer family)\\b"
);
const sentences = (text: string) => text.split(/(?<=[.!?])\s+/);

/**
 * The passage states "<dim> <class>" ("the tallest living animal", "most populous country") unqualified: not
 * "one of the …", no narrower scope ("… in North America", "… of deer", "… in the Arab world").
 */
function assertsSuperlative(text: string | null | undefined, cls: string | undefined, dims: string[] | null): boolean {
  if (!text || !cls || !dims) return false;
  const c = stem(norm(cls));
  const r = rx(`\\b(?:${dims.map(esc).join("|")})\\b(?:\\W+\\w+){0,2}?\\W+${esc(c)}\\w*`, "gi");
  for (const sent of sentences(text)) {
    for (const m of sent.matchAll(r)) {
      const start = m.index ?? 0;
      const end = start + m[0].length;
      const before = sent.slice(Math.max(0, start - 20), start).toLowerCase();
      // "one of the most…", "the eleventh most populous country".
      if (before.includes("one of") || /(second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|\d+(st|nd|rd|th))[- ]*$/.test(before)) continue;
      if (NARROW.test(sent.slice(end, end + 60)) || rx("\\bof\\s+(?:the\\s+)?\\w+\\s*$").test(sent.slice(start, end))) continue;
      return true;
    }
  }
  return false;
}

function classLevelTitle(cls: string, title: string): boolean {
  const t = norm(title.replace(PREFIX, ""));
  const c = stem(norm(cls));
  return (
    stem(t) === c ||
    new RegExp(`^list of\\b.*\\b${esc(c)}`).test(t) ||
    new RegExp(`\\b${esc(c)}\\w* by (population|height|area|size|weight)\\b`).test(t) ||
    ["world population", "largest organisms", "list of largest animals"].includes(t)
  );
}

const SUP_DIMS: Array<[RegExp, string[]]> = [
  [/populous|populated|population|popula/i, ["most populous", "most populated", "largest population"]],
  [/tall|height|alt[oa]/i, ["tallest"]],
  [/heav|weigh|pesad/i, ["heaviest", "largest"]],
  [/big|large|size|grand|maior/i, ["largest", "biggest"]],
  [/dens/i, ["most densely", "densest", "highest population density"]],
  [/long|comprid/i, ["longest"]],
  [/high|elev/i, ["highest", "tallest"]],
  [/old|antig/i, ["oldest"]],
];

function dimsFor(q: string): string[] | null {
  for (const [pat, d] of SUP_DIMS) if (pat.test(q)) return d;
  return null;
}

/** "<side> is/are the [world's] <dim> …" in a passage about that side, not "one of the …", no narrower scope. */
function dominates(text: string | null | undefined, side: string, dims: string[] | null): boolean {
  if (!text || !dims || !norm(side)) return false;
  const sd = stem(words(norm(side)).at(-1)!);
  const r = rx(
    `\\b${esc(sd)}\\w*\\b[^.]{0,40}?\\b(?:is|are|was|were)\\s+(?:the\\s+)?(?:world's\\s+)?(?:${dims.map(esc).join("|")})\\b`,
    "i"
  );
  for (const sent of sentences(text)) {
    const m = r.exec(sent);
    if (!m) continue;
    const end = m.index + m[0].length;
    if (!sent.slice(Math.max(0, m.index - 5), end).toLowerCase().includes("one of") && !NARROW.test(sent.slice(end, end + 120))) return true;
  }
  return false;
}

/** "Japan's" -> "Japan", for the message. */
const display = (s: string) => s.replace(/['’]s$/u, "");

export type O2Options = {
  /** A Portuguese question: its subjects are the lexicon's English names (src/rag/ptLexicon.ts englishNamesIn). */
  pt?: boolean;
  englishNames?: string[];
};

/**
 * Keep or refuse, from the question and the passages going into the prompt (`title` as the app shows it, label
 * included; `text` the chunk body).
 */
export function o2Decide(question: string, passages: O2Passage[], opts: O2Options = {}): O2Decision {
  const kind = o2Kind(question);
  if (!kind) return { inScope: false, action: "keep", reason: "out of scope" };
  // No passages: the app's no-source gate decides.
  if (!passages.length) return { inScope: false, kind, action: "keep", reason: "no passages in the prompt" };
  const titles = passages.map((p) => p.title);
  const passageSubject = titles[0].replace(PREFIX, "");
  let subj = subjectsOf(question, kind);
  if (opts.pt) {
    // A PT subject is only matched through the lexicon's English names; nothing mapped -> keep (spec §3.2).
    const names = opts.englishNames ?? [];
    if (!names.length) return { inScope: true, kind, action: "keep", reason: "o2:pt-unmapped (fail-open)" };
    subj = kind === "comparative" && names.length >= 2 ? { mode: "all", terms: names.slice(0, 2) } : { mode: "any", terms: names };
  }
  const base = { inScope: true, kind, passageSubject };
  const { terms } = subj;
  if (subj.mode === "any") {
    if (!terms.length) return { ...base, action: "keep", reason: "no subject extracted (fail-open)" };
    const ok = terms.some((t) => titles.some((ti) => titleCovers(t, ti)));
    return ok
      ? { ...base, action: "keep", reason: "subject covered" }
      : { ...base, action: "refuse", reason: `no passage is about ${terms.join(", ")} (o2:no-alias-table)`, questionSubject: display(terms[0]) };
  }
  if (subj.mode === "all") {
    const missing = terms.filter((t) => !titles.some((ti) => titleCovers(t, ti)));
    if (!missing.length) return { ...base, action: "keep", reason: "all sides covered" };
    const dims = dimsFor(question);
    const covered = terms.filter((t) => !missing.includes(t));
    for (const p of passages) {
      for (const c of covered) {
        if (titleCovers(c, p.title) && dominates(p.text, c, dims)) {
          return { ...base, action: "keep", reason: `side ${missing.join(", ")} uncovered, but "${p.title}" states ${c} is the ${dims?.[0] ?? "superlative"}` };
        }
      }
    }
    return { ...base, action: "refuse", reason: `side ${missing.join(", ")} not covered by any passage (o2:no-alias-table)`, questionSubject: display(missing[0]) };
  }
  // Class mode: a superlative over a class, or a list question.
  const cls = terms[0];
  if (cls && titles.some((ti) => classLevelTitle(cls, ti))) return { ...base, action: "keep", reason: "class/list-level passage" };
  if (passages.some((p) => assertsSuperlative(p.text, cls, dimsFor(question)))) {
    return { ...base, action: "keep", reason: "a passage states the superlative over the class, unqualified" };
  }
  return { ...base, action: "refuse", reason: `no passage is class-level for "${cls ?? "?"}" or states the superlative unqualified` };
}

/** The decline, saying why when both subjects are known (spec §1); else the existing weak-source line. */
export function o2Message(pt: boolean, d: Pick<O2Decision, "questionSubject" | "passageSubject">): string {
  if (d.questionSubject && d.passageSubject) {
    return pt
      ? `Os trechos encontrados falam de ${d.passageSubject}, não de ${d.questionSubject}.`
      : `The passages found are about ${d.passageSubject}, not ${d.questionSubject}.`;
  }
  return pt ? "Os trechos encontrados não sustentam esta resposta." : "The passages found don't support this answer.";
}
