/**
 * Sends the model only the sentences that answer the question: scores every sentence of the
 * retrieved passages against the question (IDF-weighted term coverage), keeps the best ones up
 * to a work budget, opens each kept passage with its first sentence (it names the subject), and
 * drops passages far less relevant than the best one. Prompt prefill is the phone's bottleneck,
 * so a few hundred tokens instead of four full passages bring the first word much sooner.
 *
 * Ported from the new UI's engine (rato-new-ui, src/routing/context.ts), sentence selection only.
 * Pure: tested without React Native.
 */
import type { RetrievedChunk } from "./src/rag/retrieve.types.ts";

export interface ScoredSentence {
  chunkIndex: number;
  /** Position inside the chunk, for restoring document order. */
  position: number;
  text: string;
  /** 0..1, absolute: share of the question's (IDF-weighted) terms this sentence covers. */
  score: number;
}

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

export function tokenizeTerms(text: string): string[] {
  return (text.toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "").match(/[a-z0-9]+/g) ?? [])
    .filter((t) => t.length > 1 && !STOPWORDS.has(t))
    .map(stem);
}

/** Tiny suffix stripper: enough to match "revolutions"/"revolution", "caused"/"causes". */
function stem(t: string): string {
  if (t.length > 5 && t.endsWith("ies")) return t.slice(0, -3) + "y";
  if (t.length > 4 && (t.endsWith("es") || t.endsWith("ed"))) return t.slice(0, -2);
  if (t.length > 3 && t.endsWith("s") && !t.endsWith("ss")) return t.slice(0, -1);
  if (t.length > 5 && t.endsWith("ing")) return t.slice(0, -3);
  return t;
}

/**
 * Joins soft line wraps ("commonly known \nas Dilithium") while keeping real
 * line breaks: blank lines, list items ("RSA\nDSA\nECDSA") and markdown
 * headings. A single newline is a wrap when the next line starts in lower
 * case or the previous one ends mid-phrase (space, comma, hyphen, "(").
 */
function unwrapLines(text: string): string {
  return text
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/([^\n])\n(?!\n)(?=[a-z(])|([ ,(\-–])\n(?!\n)/g, (_m, a, b) => `${a ?? b}${a ? " " : ""}`)
    .replace(/ {2,}/g, " ");
}

/**
 * Splits on sentence ends while keeping abbreviations and decimals intact
 * ("U.S.", "3.5", "e.g.") — good enough for encyclopedia prose. Remaining
 * newlines (list items, headings) are boundaries too.
 */
export function splitSentences(text: string): string[] {
  text = unwrapLines(text);
  const out: string[] = [];
  // Candidate boundary: terminal punctuation (optionally closing quote/paren),
  // whitespace, then something that can open a sentence. Newlines always split.
  const re = /[.!?]+["')\]]*\s+(?=["'(\[]?[A-Z0-9])|\n+/g;
  let start = 0;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text))) {
    const end = m.index + m[0].trimEnd().length;
    const candidate = text.slice(start, end);
    // Not a boundary after a single capital ("U.S.") or a known abbreviation ("e.g.").
    if (m[0][0] === "." && /(?:\b[A-Z]|\b(?:e\.g|i\.e|etc|vs|Mr|Mrs|Dr|St|No|approx|c|ca))\.$/.test(candidate.trimEnd())) continue;
    if (candidate.trim()) out.push(candidate.trim());
    start = m.index + m[0].length;
  }
  if (text.slice(start).trim()) out.push(text.slice(start).trim());
  return out;
}

/** Scores every sentence of every chunk against the question. */
export function scoreSentences(query: string, chunks: RetrievedChunk[]): ScoredSentence[] {
  const qTerms = [...new Set(tokenizeTerms(query))];
  const all: { chunkIndex: number; position: number; text: string; terms: Set<string> }[] = [];
  chunks.forEach((c, chunkIndex) => {
    splitSentences(c.body).forEach((text, position) => {
      all.push({ chunkIndex, position, text, terms: new Set(tokenizeTerms(text)) });
    });
  });
  if (qTerms.length === 0) return all.map((s) => ({ chunkIndex: s.chunkIndex, position: s.position, text: s.text, score: 0 }));

  // IDF over the candidate sentences: a term every sentence has says little.
  const n = all.length;
  const idf = new Map<string, number>();
  for (const t of qTerms) {
    const df = all.reduce((acc, s) => acc + (s.terms.has(t) ? 1 : 0), 0);
    idf.set(t, Math.log(1 + (n + 1) / (df + 0.5)));
  }
  const totalWeight = qTerms.reduce((acc, t) => acc + idf.get(t)!, 0);

  // An article the question names ("EIP-4844: Shard Blob Transactions" for
  // "What is EIP-4844?") rarely repeats its name in the body: a title
  // segment whose words are all in the question counts for every sentence.
  const named = chunks.map((c) => {
    const terms = new Set<string>();
    for (const seg of c.title.split(/:\s+/)) {
      const st = tokenizeTerms(seg);
      if (st.length && st.every((t) => qTerms.includes(t))) st.forEach((t) => terms.add(t));
    }
    return terms;
  });

  return all.map((s) => {
    let covered = 0;
    for (const t of qTerms) if (s.terms.has(t) || named[s.chunkIndex].has(t)) covered += idf.get(t)!;
    // A sentence that also names the article title is on-topic even when it
    // uses a pronoun for the subject: small bonus, capped at 1.
    const titleTerms = tokenizeTerms(chunks[s.chunkIndex].title);
    const titleHit = titleTerms.some((t) => qTerms.includes(t)) ? 0.1 : 0;
    const score = Math.min(1, covered / totalWeight + (covered > 0 ? titleHit : 0));
    return { chunkIndex: s.chunkIndex, position: s.position, text: s.text, score };
  });
}

/** Rough token count (~4 chars/token for English BPE) when no tokenizer is at hand. */
export const approxTokens = (s: string) => Math.ceil(s.length / 4);

/** A chunk whose best sentence scores under this share of the best chunk's is dropped. */
export let RELATIVE_RELEVANCE_FLOOR = 0.5;
export function setFloor(x: number) { RELATIVE_RELEVANCE_FLOOR = x; }

export interface CompressOptions {
  /** work budget for all selected sentences together. Default 1200. */
  tokenBudget?: number;
  maxSentencesPerChunk?: number;
  /** Real tokenizer when available (llama.rn tokenize); approxTokens otherwise. */
  countTokens?: (s: string) => number;
  /**
   * Chunks that always get a place, first, whatever their relative relevance: the page of an identifier the
   * question names ("EIP-7251"; Sextant dddd8a8: the Ethereum articles out-scored it and the 4B said the EIP
   * doesn't exist).
   */
  pinned?: ReadonlySet<string>;
}

export interface CompressedContext {
  /**
   * The kept chunks, most relevant first (the order defines [n] numbering,
   * so the model reads and cites the best source as [1]), bodies cut to the
   * selected sentences. Chunks with nothing relevant, or far less relevant
   * than the best one, are dropped.
   */
  chunks: RetrievedChunk[];
  /** Index into the input array for each output chunk. */
  keptIndices: number[];
  tokensBefore: number;
  tokensAfter: number;
}

/**
 * Keeps the best sentences across all chunks until the work budget is
 * spent. Each kept chunk always opens with its first sentence (it usually
 * names the subject, so later sentences' pronouns resolve), and sentences
 * are restored to document order. A chunk whose sentences all score 0 is
 * dropped — unless nothing scores at all, in which case the first sentences
 * of the top chunks are kept so the model still sees its best sources.
 */
/** Tokens the best passage's other sentences may add after the ranked pick (prefill is the phone's bottleneck). */
const FILL_MAX_TOKENS = 60;


export function compressContext(query: string, chunks: RetrievedChunk[], opts: CompressOptions = {}): CompressedContext {
  const budget = opts.tokenBudget ?? 1200;
  const perChunk = opts.maxSentencesPerChunk ?? 4;
  const count = opts.countTokens ?? approxTokens;
  const tokensBefore = chunks.reduce((acc, c) => acc + count(`${c.title}\n${c.body}`), 0);

  const scored = scoreSentences(query, chunks);
  const anyMatch = scored.some((s) => s.score > 0);
  // Per-chunk relevance = its best sentence. A chunk under half the best
  // chunk's relevance is a distractor ("RSA" for a post-quantum question):
  // dropped so the budget goes to the sources that answer.
  const chunkBest = chunks.map((_, ci) => Math.max(0, ...scored.filter((s) => s.chunkIndex === ci).map((s) => s.score)));
  const topBest = Math.max(0, ...chunkBest);
  const pinnedIdx = new Set(chunks.map((c, i) => (opts.pinned?.has(c.chunkId) ? i : -1)).filter((i) => i >= 0));
  const relevant = (ci: number) => pinnedIdx.has(ci) || !anyMatch || chunkBest[ci] >= RELATIVE_RELEVANCE_FLOOR * topBest;
  // Rank: matching sentences by score (ties → retrieval rank, then position);
  // with no match at all, fall back to each chunk's opening sentence.
  const ranked = (anyMatch ? scored.filter((s) => s.score > 0 && relevant(s.chunkIndex)) : scored.filter((s) => s.position === 0)).sort(
    (a, b) => b.score - a.score || a.chunkIndex - b.chunkIndex || a.position - b.position
  );
  // Pinned chunks first: their opening sentence (and best ones) before anything else competes for the budget.
  if (pinnedIdx.size) {
    const opening = scored.filter((s) => pinnedIdx.has(s.chunkIndex) && s.position === 0);
    const pinnedRanked = [...opening, ...ranked.filter((s) => pinnedIdx.has(s.chunkIndex) && s.position !== 0)];
    ranked.splice(0, ranked.length, ...pinnedRanked, ...ranked.filter((s) => !pinnedIdx.has(s.chunkIndex)));
  }

  const picked = new Map<number, Set<number>>();
  let used = 0;
  const cost = (s: ScoredSentence) => count(s.text) + 1;
  const tryAdd = (s: ScoredSentence): boolean => {
    const set = picked.get(s.chunkIndex) ?? new Set<number>();
    if (set.has(s.position)) return true;
    const c = cost(s);
    if (used + c > budget) return false;
    set.add(s.position);
    picked.set(s.chunkIndex, set);
    used += c;
    return true;
  };

  for (const s of ranked) {
    const set = picked.get(s.chunkIndex);
    if (set && set.size >= perChunk) continue;
    // Opening a new chunk: its title line and first sentence come first.
    if (!set) {
      const titleCost = count(chunks[s.chunkIndex].title) + 1;
      const first = scored.find((x) => x.chunkIndex === s.chunkIndex && x.position === 0);
      // The opening sentence goes in first, so it must fit together with the one that matched:
      // otherwise the passage would be kept without the sentence that answers.
      const firstCost = first && first !== s ? cost(first) : 0;
      if (used + titleCost + firstCost + cost(s) > budget) continue;
      used += titleCost;
      if (first && first !== s && !tryAdd(first)) {
        used -= titleCost;
        continue;
      }
    }
    tryAdd(s);
  }

  // Budget left: the best passage's other sentences, in order, up to perChunk (Boar/Sextant RF-1: the
  // Plate tectonics passage reached the prompt with 2 of its 4 sentences, the ones naming a question
  // word, and lost "The processes that result in plates and shape Earth's crust are called tectonics").
  // Only the MOST relevant chosen passage (Boar: prefill is the phone's bottleneck; filling every
  // chosen passage cost +14% context on the suggestions): a distractor never enters this way.
  // At most FILL_MAX_TOKENS: on s32 the fill took long passages' long sentences (+20% context, Sextant).
  const top = [...picked.keys()].sort((a, b) => chunkBest[b] - chunkBest[a] || a - b)[0];
  if (top !== undefined) {
    const fillEnd = Math.min(budget, used + FILL_MAX_TOKENS);
    for (const s of scored.filter((x) => x.chunkIndex === top).sort((a, b) => a.position - b.position)) {
      if (picked.get(top)!.size >= perChunk) break;
      if (picked.get(top)!.has(s.position)) continue;
      if (used + cost(s) > fillEnd) continue;
      tryAdd(s);
    }
  }

  const keptIndices = [...picked.keys()].sort((a, b) => Number(pinnedIdx.has(b)) - Number(pinnedIdx.has(a)) || chunkBest[b] - chunkBest[a] || a - b);
  const out = keptIndices.map((ci) => {
    const positions = [...picked.get(ci)!].sort((a, b) => a - b);
    const body = positions
      .map((p) => scored.find((s) => s.chunkIndex === ci && s.position === p)!.text)
      .join(" ");
    return { ...chunks[ci], body };
  });
  const tokensAfter = out.reduce((acc, c) => acc + count(`${c.title}\n${c.body}`), 0);
  return { chunks: out, keptIndices, tokensBefore, tokensAfter };
}

/**
 * Global, deduplicated source list for multi-retrieval answers: the same
 * chunk retrieved by two sub-questions gets one number. Returns the merged
 * list and, per input list, the global 0-based index of each of its chunks.
 */
export function mergeSources(lists: RetrievedChunk[][]): { sources: RetrievedChunk[]; indexMaps: number[][] } {
  const sources: RetrievedChunk[] = [];
  const byId = new Map<string, number>();
  const indexMaps = lists.map((list) =>
    list.map((c) => {
      const key = c.chunkId;
      let idx = byId.get(key);
      if (idx === undefined) {
        idx = sources.length;
        sources.push(c);
        byId.set(key, idx);
      }
      return idx;
    })
  );
  return { sources, indexMaps };
}

/**
 * Context budget for a normal (fast) answer, in tokens: a lookup ("what is X?") needs a few
 * sentences, other questions a little more. Deep research keeps its full passages.
 */
export const FAST_CONTEXT_TOKENS = { lookup: 450, other: 700 } as const;

/** The passages a fast answer sends: their best sentences within the task's budget. */
export function compressForAnswer(query: string, chunks: RetrievedChunk[], taskType: string): CompressedContext {
  if (chunks.length === 0) return { chunks, keptIndices: [], tokensBefore: 0, tokensAfter: 0 };
  const tokenBudget = taskType === "lookup" ? FAST_CONTEXT_TOKENS.lookup : FAST_CONTEXT_TOKENS.other;
  return compressContext(query, chunks, { tokenBudget });
}
