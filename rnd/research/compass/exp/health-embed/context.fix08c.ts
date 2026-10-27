/**
 * Sentence-level context selection. Two uses:
 *
 * 1. Instant tier: pick the single best source sentence for a question and
 *    show it in <1s with no LLM (selectInstant).
 * 2. Context compression: prefill is the hidden cost of RAG on a phone CPU
 *    (~70 tok/s for a 1.5B, so 4 chunks x 500 tokens is ~30s before the first
 *    word). compressContext keeps only the sentences that match the question,
 *    up to a work budget (~1.2k by default), in document order.
 *
 * Pure and deterministic: lexical scoring (IDF-weighted query-term coverage),
 * no embeddings, so it runs in milliseconds in JS. When the knowledge layer
 * returns pre-scored sentences (src/rag passages), those scores can be fed in
 * instead; this module is the fallback over plain RetrievedChunks.
 */
import type { RetrievedChunk } from "../rag/retrieve.types";

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

/** Minimum confidence for the instant snippet to stand as the final answer to a lookup. */
export const INSTANT_FINAL_CONFIDENCE = 0.75;
/** Below this, the snippet is not worth showing even as a preview. */
export const INSTANT_MIN_CONFIDENCE = 0.34;

export interface InstantSnippet {
  text: string;
  /** 0-based index into the chunks passed in (= sources[sourceIndex]). */
  sourceIndex: number;
  confidence: number;
}

/**
 * Best single source sentence for the question, with the sentence after it
 * when the best one is very short (a bare "It is the capital." needs its
 * neighbor). Null when nothing clears INSTANT_MIN_CONFIDENCE.
 */
export function selectInstant(query: string, chunks: RetrievedChunk[]): InstantSnippet | null {
  const scored = scoreSentences(query, chunks);
  let best: ScoredSentence | null = null;
  for (const s of scored) {
    // Near-ties go to the denser (shorter) sentence: "X is the capital of Y."
    // beats a long sentence that mentions the same words in passing. Exact
    // ties keep the earlier chunk (better retrieval rank).
    if (!best || s.score > best.score + 0.01 || (Math.abs(s.score - best.score) <= 0.01 && s.text.length < best.text.length)) best = s;
  }
  if (!best || best.score < INSTANT_MIN_CONFIDENCE) return null;
  let text = best.text;
  if (text.length < 80) {
    const next = scored.find((s) => s.chunkIndex === best!.chunkIndex && s.position === best!.position + 1);
    if (next) text = `${text} ${next.text}`;
  }
  return { text, sourceIndex: best.chunkIndex, confidence: best.score };
}

/**
 * Why a confident instant snippet still must not stand as the whole answer,
 * or null when it may. One sentence answers a single fact; it does not
 * answer a list ("Which signature algorithms are quantum resistant?"), a
 * two-part question ("What is EIP-4844 and what does it add?"), or define a
 * term it only mentions ("What is ML-DSA?" -> "EIP-8051 specifies only
 * ML-DSA-44..."). A sentence opening with a pronoun ("It initially
 * focuses...") needs the text before it.
 */
const POINTER = /\b(can be found|is available (at|in|from)|see (the|also|below|above)|for more (information|details)|refer to|repository|see https?:|https?:\/\/)/i;

export function instantFinalBlock(
  query: string,
  snippet: string,
  matchQuery: string = query
): "anaphora" | "list" | "compound" | "not-definition" | "health" | "pointer" | "title-only" | null {
  const q = query.trim().replace(/[?!.\s]+$/, "");
  // One sentence is never a complete first-aid answer.
  if (isHealthQuestion(q)) return "health";
  if (/^(it|its|this|that|these|those|they|their|he|she|his|her|such|both)\b/i.test(snippet.trim())) return "anaphora";
  if (/\b(and|or)\s+(what|how|why|which|who|when|where)\b/i.test(q)) return "compound";
  if (/^(which|what)\b.*\b(are|were)\b/i.test(q)) return "list";
  // "What is X?" for a short term X: the sentence must say what X is.
  const term = q.match(/^(?:what|who)\s+(?:is|was)\s+(?:an?\s+)?(.+)$/i)?.[1];
  if (term && term.split(/\s+/).length <= 3 && !/^the\b/i.test(term)) {
    const esc = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const defines = new RegExp(`(^|[^\\w-])${esc}(?![\\w-])[^.]{0,60}?\\b(is|are|was|were|refers to|stands for|means)\\b`, "i");
    if (!defines.test(snippet)) return "not-definition";
  }
  // A sentence that points elsewhere answers nothing (Sextant cry-020: "Full specification of the beacon
  // chain can be found in the ethereum/consensus-specs repository").
  if (POINTER.test(snippet)) return "pointer";
  // The sentence itself must cover the question past its identifiers: a named title ("EIP-3675") scores
  // every sentence of its page, so the score alone let a content-free sentence be final.
  const rest = matchQuery.replace(/\b(EIP|ERC|BIP|RFC)[-\s]?\d{1,5}\b/gi, " ");
  if (tokenizeTerms(rest).length && termCoverage(rest, snippet) < 0.5) return "title-only";
  return null;
}

/**
 * Share of the question's distinct content words found in `text` (0..1).
 * An absolute measure: relative scores alone let an off-topic page win when
 * nothing on-topic was retrieved ("Dean Lee", a nuclear physicist, for "Which
 * signature algorithms are quantum resistant?", with no crypto pack).
 */
export function termCoverage(query: string, text: string): number {
  const q = [...new Set(tokenizeTerms(query))];
  if (!q.length) return 1;
  const t = new Set(tokenizeTerms(text));
  return q.filter((x) => t.has(x)).length / q.length;
}

/** Below this, a snippet is not shown as "from the source", and the sources count as weak. */
export const MIN_TERM_COVERAGE = 0.75;
/** A source whose title names a question word must still cover this much of the question. */
const TITLE_MIN_COVERAGE = 0.5;

/** Best coverage of the question by any single source (title + body). 0 without sources. */
export function sourceCoverage(query: string, chunks: RetrievedChunk[]): number {
  return chunks.reduce((best, c) => Math.max(best, termCoverage(query, `${c.title} ${c.body}`)), 0);
}

/** Health, first aid and emergencies: the answer may only state what the sources say. */
const HEALTH =
  /\b(first aid|nose ?bleeds?|bleed(ing)?|burns?|scald(ed|s)?|bites?|stings?|snake|venom|poison(ing|ed)?|overdose|cpr|resuscitat\w*|chok(e|ing)|heimlich|fractur\w*|broken (bone|arm|leg)|sprain\w*|concussion|seizures?|stroke|heart attack|cardiac|allerg\w*|anaphyla\w*|epipen|asthma|hypotherm\w*|heat ?stroke|frostbite|drown\w*|unconscious|faint\w*|wounds?|fever|dehydrat\w*|symptoms?|dosage|medicine|medication|injur\w*|emergency|shiver\w*|evacuat\w*|contaminated|safe to drink|purify\w*|drinking water|evacua\w*|[áa]gua (pot[áa]vel|contaminada|fervente)|primeiros socorros|sangra\w*|queimadura\w*|picada\w*|mordida\w*|cobra|veneno|envenena\w*|engasg\w*|fratura\w*|desmai\w*|convuls\w*|infarto|avc|alergi\w*|febre|ferida\w*|ferimento\w*|afogamento|rcp|reanima\w*|emerg[eê]ncia|sintomas?|rem[eé]dio)\b/i;

// Portuguese terms starting or ending with an accented letter: JS \b doesn't see "á" as a letter.
const HEALTH_PT = /(^|[^\p{L}])([áa]gua (pot[áa]vel|contaminada|fervente|quente)|queimadura|picad[ao]|tremend\w*|tremores?|calafrios?|hipotermia|sangramento|engasg\w*|afogamento|desmai\w*|convuls\p{L}*|emerg[êe]ncia)(?![\p{L}])/iu;

// Disasters are safety questions when the question is what to do (Iris, E-1: "What should I
// do during an earthquake?"), not when it asks history ("What caused the 1906 earthquake?").
const DISASTER =
  /(^|[^\p{L}])(earthquakes?|tsunamis?|floods?|flooding|hurricanes?|tornado(es)?|cyclones?|typhoons?|wildfires?|bush ?fires?|house fires?|kitchen fires?|on fire|caught fire|fires? (breaks?|broke) out|fire alarm|smoke inhalation|landslides?|avalanches?|volcan\p{L}*|eruption|terremotos?|sismos?|tsunamis?|enchentes?|inunda\p{L}*|alagamentos?|furac[ãa]o|tornados?|inc[êe]ndios?|deslizamentos?|avalanches?)(?![\p{L}])/iu;
export const ACTION_INTENT =
  /\b(what (should|do|can|must) (i|we|you|one) do|what to do|how (do|should|can) (i|we|you) (stay|keep|survive|protect|prepare|get|treat|stop|help|make|purify|care)|how to (treat|stop|help|survive|make|purify)|first aid|stay safe|survive|protect (myself|yourself|ourselves)|prepare for|during|after (it|the)|before (it|the)|right now|evacuat\w*)\b|o que (eu )?(fa[çc]o|fazer|devo fazer)|como (agir|me proteger|sobreviver|se proteger|deixo|tornar|fa[çc]o|estancar|parar|tratar|cuidar|socorrer|aliviar)|durante|depois (de|do|da|que)|antes (de|do|da)|segur[ao] para/i;

// An injury DESCRIBED without the condition's name ("spilled boiling water on his arm",
// "derramou água fervendo no braço", "got bitten", "está sangrando"): health when the
// question asks what to do (gate ee1f2b7: 20/20 free answers, one said "medicinal oil").
const INJURY_DESCRIBED =
  /(^|[^\p{L}])(spill\p{L}*|splash\p{L}*|scald\p{L}*|burn\p{L}*|boiling|blister\p{L}*|bit|bitten|stung|sting\p{L}*|bleed\p{L}*|faint\p{L}*|passed out|chok\p{L}*|cut (my|his|her|their|him|herself|himself|myself)|fell (off|down|from)|broke (my|his|her|their)|twist\p{L}*|sprain\p{L}*|swallow\p{L}*|electrocut\p{L}*|collaps\p{L}*|desabou|derram\p{L}*|escald\p{L}*|queim\p{L}*|fervend\p{L}*|fervent\p{L}*|bolha\p{L}*|mord\p{L}*|picou|picad\p{L}*|sangr\p{L}*|desmai\p{L}*|engasg\p{L}*|cortou|caiu d\p{L}*|bateu a cabe[çc]a|torceu|quebrou|engoliu|choque el[ée]trico)(?![\p{L}])/iu;

// Symptoms and illnesses named without a HEALTH word (exp-08b, R&D: "headache and nausea at
// 4,000 m" missed the health path, found no on-topic source and was answered from the model's
// memory). Health on their own, like HEALTH.
const SYMPTOMS =
  /(^|[^\p{L}])(headaches?|migraines?|nause\p{L}*|vomit\p{L}*|throwing up|diarrh\p{L}*|dizz\p{L}*|vertigo|chest pains?|short(ness)? of breath|(can't|cannot|trouble|difficulty|hard to) breath\p{L}*|numbness|slurr\p{L}*|altitude sickness|mountain sickness|heat exhaustion|sunstroke|sunburn\p{L}*|frostbit\p{L}*|rabies|dengue|malaria|cholera|typhoid|yellow fever|zika|chikungunya|tetanus|leptospirosis|dor de cabe[çc]a|enxaqueca|n[áa]use\p{L}*|enjo[oô]\p{L}*|v[ôo]mit\p{L}*|diarr?eia|tontura|falta de ar|dor no peito|mal de altitude|mal da montanha|insola[çc][ãa]o|intoxica\p{L}*|ferroad\p{L}*|mal[áa]ria|c[óo]lera|febre amarela|t[ée]tano|leptospirose)(?![\p{L}])/iu;

// Hazards (an animal, a gas) are health only with an injury or a what-to-do question: "stung by a
// jellyfish… should I…" is, "Are there jellyfish in Lake Tahoe?" is not (CodeRabbit, exp-08c).
const HAZARDS =
  /(^|[^\p{L}])(jellyfish|box jellyfish|scorpions?|carbon monoxide|[áa]guas?-vivas?|escorpi[ãa]o|escorpi[õo]es|mon[óo]xido de carbono)(?![\p{L}])/iu;

// A described injury or a disaster asked as a yes/no decision ("got stung… Should I pour vinegar
// on it?", "Should I stand in a doorway?", "devo colocar gelo?") is as much a what-to-do question
// as ACTION_INTENT. Only with INJURY_DESCRIBED or DISASTER: "Should I take the bus?" alone is not health.
const DECISION_INTENT =
  /(^|[^\p{L}])(should (i|we|you|he|she|they)|do (i|we) (need|have) to|is it (ok|okay|safe|fine|bad) to|can (i|we) (give|put|use|apply|pour|take|move)|devo|devemos|posso|podemos|[ée] seguro)(?![\p{L}])/iu;

export function isHealthQuestion(query: string): boolean {
  return (
    HEALTH.test(query) ||
    HEALTH_PT.test(query) ||
    SYMPTOMS.test(query) ||
    (HAZARDS.test(query) && (INJURY_DESCRIBED.test(query) || ACTION_INTENT.test(query) || DECISION_INTENT.test(query))) ||
    (DISASTER.test(query) && (ACTION_INTENT.test(query) || DECISION_INTENT.test(query))) ||
    (INJURY_DESCRIBED.test(query) && (ACTION_INTENT.test(query) || DECISION_INTENT.test(query))) ||
    // Health for the content, translation for the form (Sextant lng-009, gate 52a2310: the 4B wrote "Je suis
    // allergique au peanut" for a phrase the traveller shows a waiter): a phrase to translate that carries
    // health content stays on the health path, and without a source it declines.
    (PHRASE_ASK.test(query) && PHRASE_HEALTH_CONTENT.test(query))
  );
}

/**
 * The chat's emergency-services line (Quill, src/ui/chat/safetyNote.ts b48657b, EQ-1): a broad,
 * deliberately generous word list ("a note too many costs a line, one too few can cost more").
 * Kept here so engine and UI use one classifier: isSafetyQuery = isHealthQuestion (which also
 * switches the answer to the source's own text, so it is stricter) OR these words.
 */
// Disasters get the line only with a what-to-do word (Quill 31c1ee8): "Why do earthquakes
// happen near plate boundaries?" is science, not an emergency.
const DISASTER_NOTE_STEMS = [
  "earthquake", "flood", "wildfire", "hurricane", "tornado", "tsunami", "disaster", "landslide", "avalanche",
  "lightning", "blizzard", "volcan", "terremoto", "sismo", "enchente", "inunda", "queimada", "furacão",
  "furacao", "desastre", "deslizamento", "vulcão", "vulcao",
];
const DISASTER_NOTE_WORDS = ["fire", "fires", "raio", "raios"];
const NOTE_INTENT =
  /\b(what should|what to do|what do i do|how do i|how to|during|survive|stay safe|safe|prepare|protect|escape|help|trapped|caught in|in case of|hit by|there is|there's)\b|o que fazer|o que devo|como agir|como me proteger|como sobreviver|durante|sobreviv|preparar|proteger|escapar|ajuda|preso|em caso de|tem uma?\b|est[áa] pegando/i;
const SAFETY_NOTE_STEMS = [
  "evacuat", "gas leak", "carbon monoxide", "survival", "evacua", "vazamento de gás", "vazamento de gas",
  "monóxido", "perdido", "incêndio", "incendio",
  "first aid", "emergency", "bleed", "blood", "nosebleed", "burn", "wound", "injur", "fractur",
  "broken bone", "sprain", "resuscitat", "chok", "poison", "overdose", "allerg", "anaphyla", "faint",
  "unconscious", "seizure", "heart attack", "stroke", "chest pain", "breath", "drown", "hypotherm",
  "heatstroke", "heat stroke", "dehydrat", "fever", "concussion", "symptom", "medicine", "medication",
  "primeiros socorros", "emergência", "emergencia", "sangr", "hemorrag", "queimad", "ferid", "ferimento",
  "fratur", "osso quebrado", "entors", "reanima", "engasg", "envenen", "intoxica", "picada",
  "mordida", "alergi", "desmai", "inconsciente", "convuls", "infarto", "derrame", "dor no peito", "respira",
  "afog", "hipotermia", "insolação", "insolacao", "desidrat", "febre", "concussão", "sintoma", "remédio",
  "remedio", "medicamento",
];
/** Whole words only ("pain" must not match "painting", "raio" not "raio-x"). */
const SAFETY_NOTE_WORDS = ["pain", "dor", "dose", "cut", "shock", "choque", "bite", "sting", "cpr", "rcp", "avc", "dores", "cuts", "bites", "stings"];
const escRe = (w: string) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const wordList = (stems: string[], words: string[]) =>
  new RegExp(`(^|[^\\p{L}])(?:(?:${stems.map(escRe).join("|")})|(?:${words.map(escRe).join("|")})(?![\\p{L}-]))`, "iu");
const SAFETY_NOTE = wordList(SAFETY_NOTE_STEMS, SAFETY_NOTE_WORDS);
const DISASTER_NOTE = wordList(DISASTER_NOTE_STEMS, DISASTER_NOTE_WORDS);

/** One classifier for the emergency-services line, shared by the engine (done.safety) and the chat. */
export function isSafetyQuery(query: string): boolean {
  return isHealthQuestion(query) || SAFETY_NOTE.test(query) || (DISASTER_NOTE.test(query) && NOTE_INTENT.test(query));
}

/**
 * The health topic of a question, as search terms: what the health detector
 * matched ("bitten", "earthquake", "safe to drink") plus the article names it
 * maps to (canonical EN / PT dictionary: "snakebite", "hypothermia").
 */
// Words that name no condition: in a title they match anything ("Just Stop Oil", "Tree snake",
// "California Department of Water Resources", gate ee1f2b7).
const GENERIC_TOPIC = new Set(tokenizeTerms("water stop treat treatment child children nose safe drink drinking prevent help make first aid snake arm hand hot cold"));

export function healthTopicTerms(query: string, articleTerms: string | null): Set<string> {
  // With article terms (the dictionary / canonical names), they ARE the topic: the story's own
  // words ("cobra", "parar") are not. Otherwise, what the health detector matched.
  const source = articleTerms
    ? articleTerms
    : [
        ...(query.match(new RegExp(HEALTH.source, "gi")) ?? []),
        ...(query.match(new RegExp(HEALTH_PT.source, "giu")) ?? []),
        ...(query.match(new RegExp(DISASTER.source, "giu")) ?? []),
      ].join(" ");
  const terms = new Set(tokenizeTerms(source).filter((t) => !GENERIC_TOPIC.has(t)));
  // "snakebite snake bite": the parts only count together (via COMPOUNDS), never alone ("Dog bite").
  for (const [compound, parts] of Object.entries(COMPOUNDS)) if (terms.has(compound)) parts.forEach((p) => terms.delete(p));
  // Drinking water: the condition is contamination / purification, not "water".
  if (/\b(drink|flood|contaminat|potavel|purif)/i.test(source)) ["contaminat", "purification", "purify", "disinfect", "boil", "flood"].forEach((t) => terms.add(t));
  return terms;
}

/**
 * A health source must BE about the topic: its title names it. Word overlap
 * in the text is not enough: with "snakebite" as the query, a plant used
 * against snakebites ("Renealmia cernua") covered it fully (gate 715ffdd).
 */
/** Sources written for laypeople (first-aid book, travel health, Ready.gov/CDC): preferred for what to do. */
const LAY_SOURCE = /^(Wikibooks|Wikivoyage|US government):/;

// Technical specifications are never first-aid sources ("EIP-7775: BURN opcode" for a burn).
const NON_HEALTH_SOURCE = /^(Ethereum EIPs\/ERCs|Ethereum specs|ethereum\.org|Bitcoin BIPs):/;

// Disasters (gate 2329dc0): an article about one event ("The 1513 Marash earthquake", "1952
// Kamchatka earthquake") names the topic but tells nobody what to do. For them, only a
// generic title counts ("Earthquake safety", "Earthquakes (Ready.gov)"), or a pack action section.
const DISASTER_TOPIC = /^(earthquak|flood|tsunami|fire|wildfire|hurricane|tornado|cyclone|typhoon|landslide|avalanche|volcan|eruption|blizzard|storm)/;
const SAFETY_TITLE_WORDS = new Set(
  tokenizeTerms("safety safe preparedness prepare preparing survival survive response emergency emergencies guide tips what do during after before protect yourself staying")
);

/** "Earthquake safety", "Earthquakes (Ready.gov)": the topic word plus safety words only, no year or place. */
function genericDisasterTitle(title: string, topic: Set<string>): boolean {
  const bare = title.replace(/^[^:]{1,30}:\s*/, "").replace(/\([^)]*\)/g, " ");
  const words = tokenizeTerms(bare);
  const inTopic = (w: string) => [...topic].some((t) => sameTerm(w, t));
  return words.some(inTopic) && words.every((w) => inTopic(w) || SAFETY_TITLE_WORDS.has(w));
}

export function onHealthTopic(topic: Set<string>, chunk: RetrievedChunk): boolean {
  if (NON_HEALTH_SOURCE.test(chunk.title)) return false;
  const action = (chunk as { action?: boolean }).action;
  // Drinking water after a flood is about the water (contamination, boiling), not the disaster itself.
  const waterSafety = [...topic].some((t) => /^(contaminat|purif|disinfect|boil)/.test(t));
  if (!waterSafety && [...topic].some((t) => DISASTER_TOPIC.test(t))) {
    if (genericDisasterTitle(chunk.title, topic)) return true;
    return action === true && titleNames(`${sectionHeading(chunk)} ${chunk.body}`, topic);
  }
  // The article title names the condition; or the section heading does ("Stay healthy" ›
  // "... > Water contamination") and the pack didn't mark it as background
  // ("Hog Butchering and Smoking › SCALDING" is not about scalds on people).
  if (titleNames(chunk.title, topic)) return true;
  // An article about another compound condition is off topic even when its text names the
  // question's word: "Nosebleed › Treatment" says "bleeding", but a cut on the arm is not a nosebleed.
  if (Object.keys(COMPOUNDS).some((c) => !topic.has(c) && new RegExp(`\\b${c}s?\\b`, "i").test(chunk.title))) return false;
  if ((action !== false || LAY_SOURCE.test(chunk.title)) && titleNames(sectionHeading(chunk), topic)) return true;
  // A pack's action section counts only when its text names the condition too
  // ("Oral rehydration therapy › Treatment" is an action section, not about burns). So does a
  // lay first-aid source whose text names it (Army FM 21-76 "Before you start treating a
  // snakebite...", Wikibooks "Outdoor Survival/First Aid › Insect and animal bite").
  return (action === true || LAY_SOURCE.test(chunk.title)) && titleNames(chunk.body, topic);
}

/** Next to the question (small models follow instructions there, s32): health answers stay inside the sources. */
export const HEALTH_GROUNDING_INSTRUCTION =
  "This is a health or first-aid question. State only what the numbered sources say, and cite the source of each step. " +
  "Do not add steps or facts from memory. If the sources do not cover something, say so and advise calling the local emergency number.";

/**
 * A source is on topic when its title shares a content word with the question
 * ("Post-quantum cryptography", "Nosebleed") or its text covers most of the
 * question's words. "Dean Lee" (a nuclear physicist) for "Which signature
 * algorithms are quantum resistant?" is neither.
 */
/** Same word despite the tiny stemmer ("earthquakes" -> "earthquak", "earthquake" stays). */
function sameTerm(a: string, b: string): boolean {
  // A stemmer quirk differs by a short suffix ("earthquak"/"earthquake", "contaminat"/"contamination");
  // a longer one is another word ("snake" is not "snakebite").
  if (a === b) return true;
  const [short, long] = a.length <= b.length ? [a, b] : [b, a];
  return short.length >= 5 && long.startsWith(short) && long.length - short.length <= 3;
}

/**
 * Conditions written as one word or two ("snakebite" / "snake bite", Wikibooks'
 * "Animal bites > Snakes"): the compound matches a title with both parts.
 */
const COMPOUNDS: Record<string, [string, string]> = {
  snakebite: ["snake", "bite"],
  nosebleed: ["nose", "bleed"],
  heatstroke: ["heat", "stroke"],
  frostbite: ["frost", "bite"],
};

function titleNames(title: string, terms: Iterable<string>): boolean {
  const t = tokenizeTerms(title);
  const has = (q: string) => t.some((x) => sameTerm(x, q));
  for (const q of terms) {
    if (has(q)) return true;
    // Parts on the raw words: the tiny stemmer turns "bites" into "bit".
    const parts = COMPOUNDS[q];
    if (parts && parts.every((p) => new RegExp(`\\b${p}(s|es)?\\b`, "i").test(title))) return true;
  }
  return false;
}

/** A pack chunk's section path ("During your trip > ... > Water contamination"), or "". */
function sectionHeading(chunk: RetrievedChunk): string {
  const colon = chunk.body.indexOf(":");
  return colon > 0 && colon <= 120 ? chunk.body.slice(0, colon) : "";
}

/**
 * A source for a PT question matched by the lexicon's English article names (PT-1): its title, or
 * its section heading, is one of the names. A multi-word name counts inside a longer title
 * ("Greenhouse effect" in "Runaway greenhouse effect"); a one-word name must be the whole title
 * ("Season", never "Hurricane Season Preparedness Digital Toolkit"). Text alone never counts.
 */
function titledByLexicon(names: string[], chunk: RetrievedChunk): boolean {
  const clean = (s: string) => s.replace(/^(Wikibooks|Wikivoyage|US government|Appropedia):\s*/, "").replace(/\s*\([^)]*\)\s*$/, "").trim().toLowerCase();
  // A heading under a "… by country" list is an item of that list, not the page's subject (Sextant trv-009:
  // "Triage systems by country > Portugal" for "É esperado dar gorjeta em restaurantes em Portugal?").
  const path = sectionHeading(chunk).split(">").map(clean);
  const listItem = (k: number) => k > 0 && /\bby (country|countries|region|state|city|nation|continent)\b|\b(other countries|around the world|worldwide)\b/.test(path[k - 1]);
  const heads = [clean(chunk.title), ...path.filter((_, k) => !listItem(k))];
  return names.some((n) => {
    const name = clean(n);
    if (!name.includes(" ")) return heads.some((h) => h === name || h === `${name}s`);
    // A multi-word name opens the title or heading ("Greenhouse effect", "Chiang Mai"): at its end it
    // is a place in another subject's title ("Consulate-General of China, Chiang Mai", ea21e82 v2-pt).
    const re = new RegExp(`^${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(?![\\p{L}])`, "iu");
    return heads.some((h) => re.test(h));
  });
}

export function namedByLexicon(names: string[], chunk: RetrievedChunk): boolean {
  if (titledByLexicon(names, chunk)) return true;
  // Two or more names (PT suggestion "Por que existem estações do ano na Terra?" -> Season, Earth): a
  // passage whose first sentence names them all ("The Earth's axis is tilted ... this causes the seasons")
  // is on topic too. Never with one name: "season" opens "Prepare before hurricane season starts".
  if (names.length < 2) return false;
  const colon = chunk.body.indexOf(":");
  const text = colon > 0 && colon <= 120 ? chunk.body.slice(colon + 1) : chunk.body;
  const lead = new Set(tokenizeTerms(splitSentences(text.trim())[0] ?? ""));
  return names.every((n) => tokenizeTerms(n.replace(/\s*\([^)]*\)\s*$/, "")).some((t) => lead.has(t)));
}

/** Years a question names ("the 1906 earthquake", "the 1970 World Cup"). */
function yearsIn(text: string): string[] {
  return text.match(/(?<![\d.,])(1[0-9]{3}|20[0-9]{2})(?![\d.,]?\d)/g) ?? [];
}

/** Proper nouns a question names: capitalized words after the first ("Who is Vitalik Buterin?"), as terms. */
function properNounTerms(query: string): string[] {
  const words = query.match(/[\p{L}][\p{L}\p{N}'’-]*/gu) ?? [];
  return words
    .slice(1)
    .filter((w) => /^\p{Lu}/u.test(w) && w !== "I")
    .flatMap((w) => tokenizeTerms(w));
}

/**
 * A pair of consecutive question terms appears, consecutive, in the title or the first sentence, as the
 * subject: not as a place ("… in Chiang Mai", the title's ", Chiang Mai" qualifier: the Chinese consulate
 * is not about visiting Chiang Mai).
 */
function sharesQuestionPair(query: string, chunk: RetrievedChunk): boolean {
  const qt = tokenizeTerms(query);
  const pairs = qt.slice(1).map((t, i) => [qt[i], t] as const).filter(([a, b]) => a !== b);
  if (!pairs.length) return false;
  const colon = chunk.body.indexOf(":");
  const text = colon > 0 && colon <= 120 ? chunk.body.slice(colon + 1) : chunk.body;
  const PLACE = new Set(["in", "at", "near", "to", "into", "from", "em", "no", "na", "perto"]);
  const has = (raw: string) => {
    const words = (raw.toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "").match(/[a-z0-9]+/g) ?? []).map((w) => ({ w, t: tokenizeTerms(w)[0] }));
    return pairs.some(([a, b]) =>
      words.some((x, i) => i + 1 < words.length && !!x.t && !!words[i + 1].t && sameTerm(x.t, a) && sameTerm(words[i + 1].t!, b) && !(i > 0 && PLACE.has(words[i - 1].w)))
    );
  };
  // The title before its ", Place" qualifier ("Vienna, Georgia"; "Consulate-General of China, Chiang Mai").
  return has(chunk.title.split(/,\s+/)[0]) || has(splitSentences(text.trim())[0] ?? "");
}

/** The title's first word is a question term ("Plate" of "Plate tectonics"). */
function leadsTitle(title: string, q: Set<string>): boolean {
  const first = tokenizeTerms(title)[0];
  return !!first && [...q].some((t) => sameTerm(first, t));
}

/** A title's first segment, past a source label: "Scary Stories" for "Scary Stories: Dark Web", "Water" for "Wikivoyage: Water". */
function mainTitle(title: string): string {
  return title.replace(/^(Wikipedia|Wikibooks|Wikivoyage|US government|Appropedia|ethereum\.org|Ethereum EIPs\/ERCs|Ethereum specs|Bitcoin BIPs):\s*/, "").split(/:\s+/)[0];
}

/** Every word of one title segment is a question term ("Monsoon"; "Ethereum EIPs/ERCs: EIP-4844: …" by its "EIP-4844" part). */
function titleSegmentNamed(title: string, q: Set<string>): boolean {
  return title.split(/:\s+/).some((seg) => {
    const st = tokenizeTerms(seg.replace(/\s*\([^)]*\)\s*$/, ""));
    return st.length > 0 && st.every((t) => q.has(t));
  });
}

export function onTopic(query: string, chunk: RetrievedChunk): boolean {
  const q = new Set(tokenizeTerms(query));
  const text = `${chunk.title} ${chunk.body}`;
  // A year or a proper noun in the question must be in the source (Sextant, gate a9f156c:
  // "1513 Marash earthquake" for the 1906 one, a cricketer for the 1970 World Cup).
  if (!yearsIn(query).every((y) => yearsIn(text).includes(y))) return false;
  const proper = properNounTerms(query);
  if (proper.length) {
    const words = new Set(tokenizeTerms(text));
    if (!proper.some((p) => words.has(p))) return false;
  }
  // The article the question names ("Monsoon" for "What causes the monsoon?": every word of a title
  // segment is in the question) is on topic even when this passage doesn't repeat the question's
  // other words (Prism RF-1: the suggested question lost its source to the coverage rule below).
  if (titleSegmentNamed(chunk.title, q)) return true;
  // Two consecutive question terms ("Roman Empire") in the title or the passage's first sentence
  // (Sextant cmp-009: "Fall of the Western Roman Empire", and "The Byzantine Empire, also known as
  // the Eastern Roman Empire, ..." for "How did government in the Roman Republic differ from the
  // Roman Empire?"). "Scary Stories: Dark Web" has no "dark matter".
  if (sharesQuestionPair(query, chunk)) return true;
  // The title's acronym ("Maximal extractable value (MEV)") named by the question ("O que é MEV…?").
  const acronym = /\(([A-Z][A-Z0-9-]{1,9})\)\s*$/.exec(chunk.title)?.[1];
  if (acronym && q.has(tokenizeTerms(acronym)[0] ?? "")) return true;
  // The article's own title OPENS with a question word ("Plate tectonics" for "…near plate boundaries?",
  // Sextant RF-1): on topic. Its first segment only, past a source label ("Wikivoyage: …"), and its first
  // word only: any word let in the s32 noise ("United States Northern Command" for the northern lights,
  // "Black Down and Sampford Common" for the commons, "Autonomy South"; gate ea21e82). A subtitle word
  // ("Scary Stories: Dark Web") or a section heading needs the coverage below.
  if (leadsTitle(mainTitle(chunk.title), q)) return true;
  // A subtitle or the section heading names a question word, and the source covers the question.
  if (titleNames(chunk.title, q) || titleNames(sectionHeading(chunk), q)) {
    return termCoverage(query, text) >= (q.size < MIN_TERMS_FOR_COVERAGE ? 1 : TITLE_MIN_COVERAGE);
  }
  // With one or two content words, any page that mentions them somewhere "covers" the
  // question (Walipini, an earth-sheltered greenhouse, for "Why do we have seasons on
  // Earth?"). Then the passage must open with them: "Canberra is the capital city of
  // Australia", "The Earth's axis is tilted ... this causes the seasons".
  if (q.size < MIN_TERMS_FOR_COVERAGE) {
    const colon = chunk.body.indexOf(":");
    const text = colon > 0 && colon <= 80 ? chunk.body.slice(colon + 1) : chunk.body;
    const first = new Set(tokenizeTerms(splitSentences(text.trim())[0] ?? ""));
    return q.size > 0 && [...q].every((t) => first.has(t));
  }
  return termCoverage(query, `${chunk.title} ${chunk.body}`) >= MIN_TERM_COVERAGE;
}

/** Questions with fewer content words than this need a source whose title names one of them. */
export const MIN_TERMS_FOR_COVERAGE = 3;

/**
 * Next to the question when a knowledge question found no offline source at
 * all: the model may answer, but says so and only states what it is sure of
 * (the post-quantum question without a pack: the 1.5B otherwise named
 * "Rainbow" and "McEliece" as signature standards; the compact model now
 * declines instead, see answer.ts).
 */
/** Opens a knowledge answer that cites none of its sources (Boar, gate ea5978c): the reader must not take it as the library's. */
export function uncitedPreface(pt: boolean): string {
  return pt
    ? "Esta resposta não vem de uma fonte offline deste celular; confira antes de confiar nela."
    : "This answer is not from an offline source on this phone; check it before relying on it.";
}

export const NO_SOURCE_INSTRUCTION =
  // The app's own line is the one notice (gate cd1478a: asked to say it, the 4B translated it under "Responda em
  // português" and the notice came out twice). The model isn't asked to say it, only told why.
  "No source in the offline library covers this question; the app already tells the reader. Do not mention sources or the library. " +
  // s32 (ee1f2b7): "Only state what you are sure of" made the 4B drop list items (the Danube without
  // Moldova). The compact model no longer answers from memory unasked (6e5e9b7), so ask for a full answer.
  "Answer completely; if you are unsure of a specific detail, say which one.";

// A model's own "not from an offline source" opening, EN and PT, as the gates saw it: "This answer is not from an
// offline source.", "Esta resposta não está em um banco de dados offline.", "Essa resposta não está em uma fonte
// offline.", "Esta resposta não vem de uma fonte offline.", "I don't have a source for this."
const MODEL_DISCLAIMER =
  /^\s*(?:(?:this|the) (?:answer|response|information) (?:is|was) not (?:from|in|based on|drawn from)(?: an?| any| the)? (?:offline )?(?:source|database|library|data)\b|(?:esta|essa) (?:resposta|informa[çc][ãa]o) n[ãa]o (?:vem|est[áa]|[ée]|foi tirada|se baseia)(?: baseada)?(?: em| de| d[aeo]| n[ao])?(?: uma?| nenhuma| um)? ?(?:fonte|banco de dados|base de dados|acervo|biblioteca)(?: offline)?|i (?:don'?t|do not) have (?:a|an|any) (?:offline |reliable )?source\b|n[ãa]o tenho (?:uma? |nenhuma )?fonte\b)[^.!?\n]*[.!?]?\s*/i;

/** The answer without the model's own "not from an offline source" opening (and a copy of the app's line). */
export function stripModelDisclaimer(text: string, pt: boolean): string {
  let out = text.trimStart();
  const app = uncitedPreface(pt);
  for (let i = 0; i < 3; i++) {
    const before = out;
    if (out.startsWith(app)) out = out.slice(app.length).trimStart();
    out = out.replace(MODEL_DISCLAIMER, "").trimStart();
    if (out === before) break;
  }
  return out;
}

// A reference list the model wrote itself (CT-A: "[1] Monsoon, Wikipedia, acessado em 1 de fevereiro de 2023" at the end of a
// PT answer from the Rápido). The app's [n] are the only citations; the model's are invented. A header line ("Fontes:",
// "References", "**Bibliografia**") starts a list; an entry is "[n] …" or "1. …" with a reference mark (Wikipedia, "acessado
// em", "retrieved on", a URL). A header needs a colon or nothing after the word: "Sources of vitamin C: oranges" is content.
const REF_HEADER =
  /^\s*(?:#{1,6}\s*)?[*_]*(?:fontes?|sources?|refer[êe]ncias?(?: bibliogr[áa]ficas)?|references?|bibliografia|bibliography|works cited|obras citadas|cita[çc][õo]es|citations)[*_]*(?:\s*:[*_]*\s*(.*))?\s*$/i;
const REF_ENTRY = /^\s*(?:[-*•]\s*)?(?:\[\d+\]|\d+[.)])\s*\S/;
const REF_MARK =
  /\bwikip[ée]dia\b|\bacessad[oa] em\b|\baccessed(?: on)?\b|\bretrieved (?:on|from)\b|\brecuperad[oa] em\b|\bconsultad[oa] em\b|\bdispon[íi]vel em\b|\bavailable (?:at|from)\b|https?:\/\/|\bwww\./i;
const REF_DATE_LINE = /^\s*(?:retrieved (?:on|from)|accessed on|acessad[oa] em|consultad[oa] em|recuperad[oa] em)\b/i;
const REF_INLINE_TAIL = /\s*\[\d+\]\s+[^\n[\]]{1,150}?,\s*(?:wikip[ée]dia|acessad[oa] em|accessed on|retrieved on)\b[^\n]*$/i;

/**
 * The answer without the model's own reference or bibliography lines ("Fonte(s):", "Referências", "[n] <Title>,
 * Wikipedia, acessado em…", "Retrieved on…"): the citation comes only from the app's [n]. A "Fontes: [1][2]" line with
 * nothing but markers keeps them, on the line before it, so the answer still cites what it cited.
 */
export function stripModelReferences(text: string): string {
  const out: string[] = [];
  let inRefs = false;
  const lastKept = () => {
    for (let i = out.length - 1; i >= 0; i--) if (out[i].trim()) return i;
    return -1;
  };
  for (const line of text.split("\n")) {
    const header = REF_HEADER.exec(line);
    if (header) {
      const rest = (header[1] ?? "").trim();
      const markers = rest.match(/\[\d+\]/g) ?? [];
      const k = lastKept();
      if (markers.length && !rest.replace(/\[\d+\]|[\s,;.]/g, "") && k >= 0) out[k] = `${out[k].trimEnd()} ${markers.join("")}`;
      inRefs = true;
      continue;
    }
    if (inRefs && (!line.trim() || REF_ENTRY.test(line) || REF_MARK.test(line))) continue;
    inRefs = false;
    if ((REF_ENTRY.test(line) && REF_MARK.test(line)) || REF_DATE_LINE.test(line)) continue;
    out.push(line.replace(REF_INLINE_TAIL, ""));
  }
  return out.join("\n").trimEnd();
}

/** When the offline library was built (Wikipedia and the packs' dumps). Update with the packs. */
export const LIBRARY_SNAPSHOT = { en: "September 2026", pt: "setembro de 2026" };

// A current-time word AND an event/news intent: "Who won the football match yesterday?", "latest
// news", "placar do jogo de hoje". Either alone is not enough: "What happened in the 1906
// earthquake?" has no current-time word; "Why is the sky blue today?" asks for no event.
const CURRENT_TIME =
  /\b(yesterday|today|tonight|this (morning|afternoon|evening|week|weekend|month|year)|last (night|week|weekend)|right now|at the moment|currently|latest|breaking|live|so far this)\b|(^|[^\p{L}])(ontem|hoje|hoje [àa] noite|agora|neste momento|nesta semana|esta semana|essa semana|semana passada|[úu]ltim[oa]s?|ao vivo|atualmente)(?![\p{L}])/iu;
const EVENT_INTENT =
  /\b(who won|who (is )?winning|won|win|beat|score|scores|result|results|match|game|election|news|headlines?|what happened|happening|price|stock|weather|forecast|standings?|goals?)\b|(^|[^\p{L}])(quem ganhou|quem venceu|ganhou|venceu|placar|resultado|jogo|partida|elei[çc][ãa]o|not[íi]cias?|manchetes?|aconteceu|cota[çc][ãa]o|pre[çc]o|previs[ãa]o do tempo|gols?)(?![\p{L}])/iu;

// "What happened today in history?" asks about the past (Prism): the library answers it.
const HISTORY_FRAME = /\b(in history|on this day|this day in|historically)\b|(^|[^\p{L}])(na hist[óo]ria|neste dia|nesse dia|num dia como hoje)(?![\p{L}])/iu;

/** Whether a question is about the present ("today", "hoje", "right now"): the model needs the date (Prism TD-1). */
export function mentionsNow(query: string): boolean {
  return CURRENT_TIME.test(query);
}

/** The device's date for the prompt, in the question's language: "Today is Sunday, 27 September 2026." */
export function todayLine(date: Date, pt: boolean): string {
  const text = date.toLocaleDateString(pt ? "pt-BR" : "en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  return pt ? `Hoje é ${text} (data deste aparelho).` : `Today is ${text} (this device's date).`;
}

const TODAY_IN_HISTORY =
  /\b(today|this day)\b[^?.!]{0,30}\bin history\b|\bon this day\b|\bthis day in history\b|(^|[^\p{L}])(hoje na hist[óo]ria|neste dia na hist[óo]ria|num dia como hoje|hoje[^?.!]{0,30}na hist[óo]ria)(?![\p{L}])/iu;

/** "What happened today in history?": a question about the device's calendar date (Boar/Piston R3). */
export function isTodayInHistory(query: string): boolean {
  return TODAY_IN_HISTORY.test(query);
}

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

/**
 * The date as the sources write it: search words ("September 27") and the on-topic test. Only the date's
 * own article ("September 27": events, births, deaths) is on topic: a text that merely mentions the date
 * ("Recorded September 27, 2011", a Ready.gov webinar) was quoted as what happened today (E2E, corpus + pack v3).
 */
export function historyDate(date: Date): { search: string; isDateArticle: (title: string) => boolean } {
  const month = MONTHS[date.getMonth()];
  const day = date.getDate();
  const title = new RegExp(`^(\\w[\\w .]*:\\s*)?(${month} ${day}|${day} ${month})$`, "i");
  return { search: `${month} ${day}`, isDateArticle: (t) => title.test(t.trim()) };
}

const TEMPERATURE =
  /(-?\d+(?:[.,]\d+)?)\s*(?:°|º|degrees?|graus?)?\s*(c|celsius|centigrade|f|fahrenheit)\b[^?]*?\b(?:in|to|into|em|para)\s+(?:degrees?\s+|graus?\s+)?(celsius|centigrade|fahrenheit|c|f)\b/i;

/**
 * "What is 30 °C in Fahrenheit?" (a suggested question, Prism RF-1): arithmetic, not knowledge. Answered
 * exactly, with the formula, instead of by a model (the compact one miscounts) or not at all.
 */
export function temperatureConversion(query: string, pt: boolean): string | null {
  const m = TEMPERATURE.exec(query);
  if (!m) return null;
  const value = Number(m[1].replace(",", "."));
  const from = m[2][0].toLowerCase() === "f" ? "F" : "C";
  const to = m[3][0].toLowerCase() === "f" ? "F" : "C";
  if (from === to || !Number.isFinite(value)) return null;
  const result = from === "C" ? (value * 9) / 5 + 32 : ((value - 32) * 5) / 9;
  const fmt = (n: number) => (Math.round(n * 10) / 10).toLocaleString(pt ? "pt-BR" : "en-US");
  const formula = from === "C" ? "°F = °C × 9/5 + 32" : "°C = (°F − 32) × 5/9";
  return pt
    ? `${fmt(value)} °${from} = ${fmt(result)} °${to} (${formula}).`
    : `${fmt(value)} °${from} = ${fmt(result)} °${to} (${formula}).`;
}

export function isCurrentEventQuery(query: string): boolean {
  return CURRENT_TIME.test(query) && EVENT_INTENT.test(query) && !HISTORY_FRAME.test(query);
}

export function currentEventAnswer(pt: boolean): string {
  return pt
    ? `Estou offline, e o meu acervo é uma cópia de ${LIBRARY_SNAPSHOT.pt}: não tenho notícias, resultados nem preços recentes.`
    : `I'm offline, and my library is a snapshot from ${LIBRARY_SNAPSHOT.en}: I don't have news, results or prices since then.`;
}

/** Portuguese questions over mostly English sources can't be matched word for word; the guard skips them. */
const PT_WORDS = /^(o|a|os|as|um|uma|de|do|da|dos|das|em|no|na|nos|nas|que|para|com|por|pelo|pela|se|mais|como|mas|foi|sao|nao|ao|aos|e|ou|entre|sobre|tambem|ela|ele|seu|sua|isso|esta|este)$/;
const EN_WORDS = /^(the|a|an|of|in|on|and|or|to|is|are|was|were|for|with|by|from|that|this|it|as|at|be|which|its)$/;

/** The language a passage reads in, by its function words: "pt", "en", or null when unclear. */
export function passageLanguage(text: string): "pt" | "en" | null {
  const words = text.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").match(/[a-z]+/g) ?? [];
  const pt = words.filter((w) => PT_WORDS.test(w)).length;
  const en = words.filter((w) => EN_WORDS.test(w)).length;
  if (pt + en < 2) return null;
  return pt > en ? "pt" : en > pt ? "en" : null;
}

/**
 * The lead of a source's words shown to a reader of another language (Quill/Sextant q8: "O que é uma
 * monção?" got the English Monsoon lead with no word that it is in English). The engine reads the
 * passage, not the UI's language: imported documents may be PT. Null when the languages match.
 */
export function sourceLanguageLead(questionPt: boolean, passage: string): string | null {
  const lang = passageLanguage(passage);
  if (questionPt && lang === "en") return "Da fonte offline (em inglês):";
  if (!questionPt && lang === "pt") return "From the offline source (in Portuguese):";
  return null;
}

/**
 * Whether a passage carries content: not an EIP's metadata header ("Status: Final Type: … Created: …"), a
 * code/hex-only block, a copyright notice or a two-word stub ("Hard fork: Spurious Dragon"). Sextant cry-012:
 * the three pinned EIP-155 passages were exactly those, and the model filled in "a nonce field".
 */
export function isSubstantive(chunk: RetrievedChunk): boolean {
  const colon = chunk.body.indexOf(":");
  const heading = colon > 0 && colon <= 120 ? chunk.body.slice(0, colon) : "";
  const text = (heading ? chunk.body.slice(colon + 1) : chunk.body).trim();
  if (/^(status|type|created|requires|author|category|discussions-to)\s*:/i.test(chunk.body.trim()) && /\bcreated\s*:/i.test(chunk.body)) return false;
  if (/^copyright\b/i.test(heading) || /^copyright and related rights waived/i.test(text)) return false;
  const prose = text.replace(/```[\s\S]*?```/g, " ").replace(/\b0x[0-9a-f]+\b/gi, " ");
  const words = prose.match(/\p{L}{2,}/gu) ?? [];
  return words.length >= 3;
}

const IDENTIFIER = /\b(EIP|ERC|BIP|RFC)[-\s]?(\d{1,5})\b/gi;

/**
 * Whether a sentence names the subject the question and its source share (the question's terms in the source's
 * title): "Greenhouse effect" for "O que causa o efeito estufa?" (Sextant q7: the instant snippet was "Surface
 * heating can happen from an internal heat source … host star", a sentence of the Greenhouse effect article that
 * scored only through its title). No shared subject (Canberra for "capital of Australia"): no constraint.
 */
export function sentenceNamesSubject(matchQuery: string, title: string, sentence: string): boolean {
  const q = new Set(tokenizeTerms(matchQuery));
  const shared = tokenizeTerms(mainTitle(title)).filter((t) => [...q].some((x) => sameTerm(x, t)));
  if (!shared.length) return true;
  // An identifier's page ("EIP-4844: Shard Blob Transactions") is also named by its title's name: "Shard Blob
  // Transactions scale data-availability of Ethereum…" is about EIP-4844 (Sextant cry-004-pt, gate a11d730).
  const named = identifiersIn(title).length
    ? tokenizeTerms(title.replace(/^(Wikipedia|Wikibooks|Wikivoyage|US government|Appropedia|ethereum\.org|Ethereum EIPs\/ERCs|Ethereum specs|Bitcoin BIPs):\s*/, "")).filter((t) => t.length >= 4 && !/^\d+$/.test(t))
    : [];
  const subject = [...shared, ...named];
  const words = tokenizeTerms(sentence);
  return subject.some((t) => words.some((w) => sameTerm(w, t)));
}

/** Standard identifiers a question names ("EIP-7251", "ERC 4337"), normalized as "EIP-7251". */
export function identifiersIn(text: string): string[] {
  return [...new Set([...text.matchAll(IDENTIFIER)].map((m) => `${m[1].toUpperCase()}-${m[2]}`))];
}

/** Whether a source's title carries one of these identifiers ("Ethereum EIPs/ERCs: EIP-7251: Increase …"). */
export function titleHasIdentifier(title: string, ids: string[]): boolean {
  const own = identifiersIn(title);
  return ids.some((id) => own.includes(id));
}

/** A Portuguese question: its interrogatives (PT_QUESTION) or, failing those, its function words ("É esperado dar
 * gorjeta em restaurantes em Portugal?" has neither "como" nor "o que", and was answered in English, trv-009). */
const PT_ONLY = /(?<![\p{L}])(é|são|não|em|uma|umas|dos|das|nos|nas|pelo|pela|com|sem|isso|isto|está|estão|também|você|vocês|meu|minha|seus|suas|dar|fazer|que|para|da|lá|alguns|algumas)(?![\p{L}])/giu;
export function isPortugueseQuestion(query: string): boolean {
  if (PT_QUESTION.test(query)) return true;
  // Words English doesn't use ("do", "a", "no" are both): two, or one plus an accent in a lowercase word.
  const strong = query.match(PT_ONLY)?.length ?? 0;
  const accent = /(^|[^\p{L}])[a-zà-ÿ]*[ãõçâêôáéíóú]/u.test(query);
  return strong >= 2 || (strong >= 1 && accent);
}

/** Next to a PT question: answer in Portuguese even with English sources (the sources' language pulls the model). */
// And the citation, with an example (gate 1724fd5: with the language line alone the models stopped writing [n]).
export const PT_ANSWER_LANGUAGE =
  "Responda em português do Brasil, mesmo que as fontes estejam em inglês, e cite cada afirmação com o número da fonte, como [1].";
// Without sources, the language only (gate 19bb043: "cite [n]" with nothing to cite made the 4B write its own
// "not from an offline source" line after the app's, and a weaker answer).
export const PT_ANSWER_LANGUAGE_NO_SOURCES = "Responda em português do Brasil.";

export const PT_QUESTION = /\b(como|o que|quando|onde|qual|quais|por que|porque|devo|fazer|posso|existe|quem|quanto)\b/i;

/** Longest health excerpt shown as the answer (about 120 words). */
export const HEALTH_EXTRACT_MAX_CHARS = 700;

// What to DO, not what it is: a treatment / first-aid / "during" section, with instructions.
const ACTION_SECTION = /^(treatment|first aid|management|what to do|during|immediate|self[- ]care|emergency care|response|stay safe|how to|signs and treatment)/i;
const ACTION_WORD = /\b(apply|applying|pinch|lean|press|pressure|call|cool|drop|cover|hold|boil|move|remove|keep|seek|get|stay|avoid|do not|don't)\b/gi;
const HEDGE = /\b(controversial|traditionally|historically|history|studies|evidence is)\b/i;
// Sections that describe, not instruct.
const DESCRIPTIVE_SECTION = /^(cause|causes|mechanics|mechanism|pathophysiology|epidemiology|history|etymology|society|research|classification|prognosis|injection|diagnosis)\b/i;
/** Under this, the chosen source gives no steps: say so before quoting it. */
export const HEALTH_ACTION_MIN_SCORE = 0.5;

/** Which source to quote for a health question: the most instructive on-topic one (index into `sources`). */
/**
 * The core procedure per condition (Ready.gov, NHS, CDC), as the words a passage that
 * gives it contains, EN and PT. Among action sources, the one with the core procedure is
 * quoted, and the excerpt starts at it (safety-008: "Drop, Cover and Hold" over "Do not run").
 */
const CORE_PROCEDURE: Array<[RegExp, RegExp]> = [
  [/^earthquak|^terremot|^sismo/, /\bdrop\b[^.]{0,40}\bcover\b|\bhold on\b|drop,? cover|abaixe|proteja-se|segure-se/i],
  [/^burn|^scald|^queimad/, /\b(cool|cold|lukewarm)\b[^.]{0,30}\b(running )?water\b|[áa]gua (corrente|fria)/i],
  // "Direct pressure" and the soft part of the nose too: the PT suggestion quoted "Nasal packing" (a
  // clinic's procedure) over the first aid (RF-1 harness, pt4: "Emergency bleeding control › Epistaxis").
  [/^nosebleed|^nose|^sangram/, /\bpinch\w*|\blean\w* forward|\btilt\w*[^.]{0,20}forward|\bdirect pressure\b|\bsoft (fleshy )?part of the nose\b|inclin\w*[^.]{0,20}frente|apert/i],
  // After nosebleed: a nosebleed's topic has no "bleed" (the compound's parts are dropped).
  [/^bleed|^sangr|^hemorrag/, /\b(direct|firm|steady)\b[^.]{0,20}\bpressure\b|\b(apply|put|press)\w*\b[^.]{0,30}\b(pressure|firmly)\b|press[ãa]o (direta|firme)/i],
  [/^hypotherm|^hipoterm/, /\bshelter\b|\bwarm\w*|\bremove\b[^.]{0,30}\bwet\b|\bcold environment\b|abrigo|aquec/i],
  // Not "immobilization" (pressure immobilization is contested for vipers, Sextant dng-001) nor "antivenom"
  // (a hospital's): the practical steps: keep still and calm, call emergency, get to a hospital.
  [/^snakebite|^snake/, /\b(keep|stay)\b[^.]{0,20}\b(still|calm)\b|\bhospital\b|\bemergency\b|\bcall\b[^.]{0,20}\b(help|911|112|ambulance)\b/i],
  // Near "water": "Clean and disinfect everything that got wet" is about surfaces (safety-005, Appropedia Floods).
  [/^contaminat|^purif|^boil|^water/, /\b(boil|disinfect|purif|treat)\w*\b[^.]{0,40}\bwater\b|\bwater\b[^.]{0,40}\b(boil|disinfect|purif)\w*|\bbleach\b[^.]{0,40}\bwater\b|\bwater\b[^.]{0,40}\bbleach\b|ferv/i],
  [/^chok|^engasg/, /\bback blows?\b|\babdominal thrusts?\b|\bheimlich\b/i],
  [/^flood|^enchent/, /\bhigher ground\b|\bavoid\b[^.]{0,20}\bflood ?water|\bdo not (walk|drive)\b[^.]{0,30}\bwater\b/i],
  [/^fire|^incendi/, /\bget out\b|\bstay low\b|\bcrawl\b|\bstop,? drop,? and roll\b/i],
];

/** The core-procedure pattern for a health topic, or null. */
export function coreProcedure(topic: Iterable<string>): RegExp | null {
  for (const [topicRe, procedure] of CORE_PROCEDURE) if ([...topic].some((t) => topicRe.test(t))) return procedure;
  return null;
}

export function healthSourceIndex(sources: RetrievedChunk[], procedure: RegExp | null = null): number {
  return healthSourceOrder(sources, procedure)[0] ?? 0;
}

/** Candidate sources for a health excerpt, best first (the same scoring as healthSourceIndex). */
export function healthSourceOrder(sources: RetrievedChunk[], procedure: RegExp | null = null): number[] {
  const scored: Array<[number, number]> = [];
  // The packs mark action sections (RetrievedChunk.action, Bramble b4becc5): when any is marked,
  // only those are candidates ("Quality by country" never beats "Water contamination").
  const flag = (c: RetrievedChunk) => (c as { action?: boolean }).action;
  const anyAction = sources.some((c) => flag(c) === true);
  sources.forEach((c, i) => {
    if (anyAction && flag(c) !== true && !LAY_SOURCE.test(c.title)) return;
    // Laypeople's first-aid text beats a clinical Treatment section ("Active external rewarming involves...").
    // Lay first-aid text that gives steps beats a clinical Treatment section.
    // Appropedia's how-to action sections are lay text too (EQ-2, pack v3: without it Wikivoyage's
    // "If you are outdoors" beat "Drop, cover, and hold on!"); scoring only, not the topic rule.
    const steps = healthActionScore(c) >= HEALTH_ACTION_MIN_SCORE;
    const lay = LAY_SOURCE.test(c.title) ? (steps ? 6 : 2) : /^Appropedia:/.test(c.title) && flag(c) === true && steps ? 6 : 0;
    // The official source (Ready.gov) wins a tie between texts that give the core procedure.
    const official = /^US government:/.test(c.title) && procedure?.test(c.body) ? 1 : 0;
    const score = healthActionScore(c) + (flag(c) === true ? 3 : 0) + lay + official + (procedure?.test(c.body) ? 8 : 0) - i * 0.05;
    scored.push([i, score]);
  });
  return scored.sort((a, b) => b[1] - a[1]).map(([i]) => i);
}

/** How much a source tells what to do: an instructions section, action words, minus description and hedging. */
export function healthActionScore(c: RetrievedChunk): number {
  // Pack chunks start with "Section > Subsection: "; anything else has no section.
  const colon = c.body.indexOf(":");
  const section = colon > 0 && colon <= 80 ? c.body.slice(0, colon) : "";
  return (
    (ACTION_SECTION.test(section) ? 2 : 0) +
    Math.min(2, (c.body.match(ACTION_WORD)?.length ?? 0) * 0.25) -
    (HEDGE.test(c.body) ? 1 : 0) -
    (DESCRIPTIVE_SECTION.test(section) ? 1.5 : 0) -
    // A caption or a heading alone ("Image") is not an answer.
    (c.body.length - section.length < 40 ? 3 : 0)
  );
}

/**
 * A health answer taken word for word from one source (its full text, not
 * the compressed one), cut at a sentence end and cited by its number.
 */
/** Always under a health or disaster answer, whatever the excerpt says (Boar, safety-008). */
export function emergencyLine(pt: boolean): string {
  return pt
    ? "Em uma emergência, ligue para o serviço de emergência local (192 SAMU, 193 Bombeiros no Brasil, 112 na Europa, 911 nos EUA)."
    : "In an emergency, call your local emergency number (911 in the US, 112 in Europe).";
}

// Burns (Boar, decision A): the excerpt stops before any line about ointments, creams, oils,
// butter or aloe: the core procedure is cooling with running water; the rest stays in the source.
const BURN_REMEDY = /\b(ointments?|creams?|lotions?|oils?|butter|aloe( vera)?|petroleum jelly|egg white|toothpaste)\b|pomada|\bcreme\b|[óo]leo|manteiga|babosa|pasta de dente/i;
/** A child or boiling water: the excerpt keeps the source's "seek medical care" line if it has one. */
const SEEK_CARE = /\b(seek|get) (medical|emergency) (care|attention|help|treatment)|\b(require|requires|need|needs) (immediate |urgent )?medical (attention|care)|\bsee a (doctor|healthcare)|\bcall (911|112|999|your doctor|a doctor)|\bemergency (room|department)|procure (atendimento|um m[ée]dico)/i;
const HIGH_RISK_BURN = /\b(child|children|kid|baby|infant|toddler|son|daughter|boiling)\b|crian[çc]a|beb[êe]|filh[oa]|fervend|fervent/i;

export interface ExcerptRules {
  /** Core procedure: the excerpt starts at it when the steps before it don't fit. */
  procedure?: RegExp | null;
  /** Stop before the first sentence that matches (burn remedies). */
  cutAt?: RegExp | null;
  /** Cut inside that sentence, at its last list item or clause before the match (a list is one "sentence"). */
  cutInside?: boolean;
  /** Append the source's sentence that matches, if the excerpt lacks it (seek care). */
  mustInclude?: RegExp | null;
}

/** Excerpt rules for a health question and its topic terms. */
// Making water safe to drink: the excerpt stops at drinking something else instead ("Consider drinking tea, soft
// drinks or bottled juices… Milk… Coffee and alcoholic drinks… Never drink sea water", Wikivoyage Water › Buy;
// Sextant dng-005: generic travel advice after the steps).
const WATER_ASIDE = /\b(tea|soft drinks?|juices?|milk|yog(h)?urt|dairy|coffee|alcohol\w*|sea ?water)\b/i;

export function excerptRules(query: string, topic: Iterable<string>): ExcerptRules {
  const burn = [...topic].some((t) => /^(burn|scald|queimad)/.test(t));
  const water = [...topic].some((t) => /^(contaminat|purif|disinfect|boil)/.test(t));
  return {
    procedure: coreProcedure(topic),
    cutAt: burn ? BURN_REMEDY : water ? WATER_ASIDE : null,
    cutInside: water && !burn,
    mustInclude: burn && HIGH_RISK_BURN.test(query) ? SEEK_CARE : null,
  };
}

// The situation a question is about, when the quoted source doesn't address it (Sextant dng-005: a flood question
// answered with Wikivoyage's general "Water › Buy" travel section).
const SITUATIONS: Array<[RegExp, RegExp, string, string]> = [
  [/\bflood\w*|enchente\w*|inunda[çc]\w*|alagamento/i, /\bflood\w*/i, "enchente", "flood"],
];

/**
 * When the question names a situation (a flood) that the quoted source never mentions, the excerpt is
 * general advice: say so, after the lead, instead of passing it off as advice for that situation.
 */
export function situationNote(query: string, source: RetrievedChunk, pt: boolean): string | null {
  for (const [asks, mentions, ptName, enName] of SITUATIONS) {
    if (asks.test(query) && !mentions.test(`${source.title} ${source.body}`)) {
      return pt
        ? `O acervo offline não tem orientação específica para ${ptName}; o trecho abaixo é uma orientação geral sobre o assunto.`
        : `The offline library has no guidance specific to a ${enName}; the passage below is general advice on the subject.`;
    }
  }
  return null;
}

/**
 * The "seek care" sentence a high-risk case needs (a child, boiling water) when the quoted source lacks it: from
 * another on-topic source, with its own [n], before the emergency line (Sextant dng-003: the Ready.gov "How to Treat
 * Minor Burns" excerpt never says when to get help; the article's opening chunk does: "…require immediate medical
 * attention"). Nothing found: unchanged (the emergency line stays).
 */
export function withSeekCare(text: string, sources: RetrievedChunk[], primary: number, rules: ExcerptRules): string {
  if (!rules.mustInclude || rules.mustInclude.test(text)) return text;
  for (let k = 0; k < sources.length; k++) {
    if (k === primary) continue;
    const sentence = splitSentences(sources[k].body).find((x) => rules.mustInclude!.test(x) && !rules.cutAt?.test(x));
    if (!sentence) continue;
    const cut = text.indexOf("\n\n");
    const [head, tail] = cut >= 0 ? [text.slice(0, cut), text.slice(cut)] : [text, ""];
    return `${head}\n\n${sentence.replace(/^[-•]\s*/, "")} [${k + 1}]${tail}`;
  }
  return text;
}

const AFTER_ASK = /\bafter (it|the \w+) (stops|ends|is over|passes)\b|\b(and|what about|what to do) after\b|\bafterwards\b|depois que (parar|passar|acabar|terminar)|\be depois\b|o que fazer depois|\bap[óo]s (parar|passar|o tremor|a enchente)/i;
const AFTER_SECTION = /(^|>\s*)(after|recover\w*|depois|ap[óo]s)\b/i;

/**
 * "…o que eu faço, e o que fazer depois que parar?" (Sextant dng-004-pt): the excerpt covered only "during".
 * When the question also asks about afterwards, an on-topic source's "After …" section is quoted too, with its
 * own [n]; without one, the answer says the source covers only the first part. Other questions: unchanged.
 */
export function withAfterPart(
  query: string,
  text: string,
  sources: RetrievedChunk[],
  primary: number,
  pt: boolean,
  rules: ExcerptRules
): string {
  if (!AFTER_ASK.test(query)) return text;
  const cut = text.indexOf("\n\n");
  const [head, tail] = cut >= 0 ? [text.slice(0, cut), text.slice(cut)] : [text, ""];
  const j = sources.findIndex((c, k) => k !== primary && AFTER_SECTION.test(sectionHeading(c)));
  if (j >= 0) {
    // The "After" section from its start ("Check yourself for injuries. Expect aftershocks. …"), by sentences.
    let quote = "";
    for (const sentence of splitSentences(sources[j].body)) {
      if (quote && quote.length + sentence.length + 1 > HEALTH_EXTRACT_MAX_CHARS) break;
      quote = quote ? `${quote} ${sentence}` : sentence;
    }
    if (quote) return `${head}\n\n${quote} [${j + 1}]${tail}`;
  }
  const note = pt
    ? "A fonte citada cobre o que fazer durante; não encontrei no acervo offline o que fazer depois."
    : "The cited source covers what to do during it; I didn't find what to do afterwards in the offline library.";
  return `${head}\n\n${note}${tail}`;
}

const IMPERATIVE = /^(boil|use|drink|avoid|keep|call|apply|remove|cover|hold|drop|get|stay|move|put|wash|clean|rinse|cool|press|pinch|lean|sit|lie|seek|go|find|filter|add|let|store|treat|do not|don't|never)\b/i;

/** How many list items or sentences of a text start with an instruction ("Boil the water…", "Do not …"). */
export function imperativeSteps(text: string): number {
  return text
    .split(/(?:^|\s)[-•]\s+|(?<=[.!?])\s+/)
    .map((x) => x.replace(/^[^:]{0,80}:\s*/, "").trim())
    .filter((x) => IMPERATIVE.test(x)).length;
}

export function healthExtract(source: RetrievedChunk, sourceNumber: number, pt: boolean, rulesOrProcedure: ExcerptRules | RegExp | null = null): string {
  const rules: ExcerptRules = rulesOrProcedure instanceof RegExp || rulesOrProcedure === null ? { procedure: rulesOrProcedure } : rulesOrProcedure;
  const procedure = rules.procedure ?? null;
  // Steps first: start at the first sentence that tells what to do, keeping the section heading
  // ("Treatment > First aid: Snakebite first aid recommendations vary..." opens with background).
  const colon = source.body.indexOf(":");
  const heading = colon > 0 && colon <= 120 ? source.body.slice(0, colon) : "";
  const sentences = splitSentences(heading ? source.body.slice(colon + 1).replace(/^[:\s]+/, "") : source.body);
  // Start at the first step; jump to the core procedure ("Drop, Cover and Hold...") only when it
  // wouldn't fit from there (a list's earlier steps, "Remove clothing and jewelry", are kept).
  const core = procedure ? sentences.findIndex((x) => procedure.test(x)) : -1;
  const action = sentences.findIndex((x) => new RegExp(ACTION_WORD.source, "i").test(x));
  const firstAction = action >= 0 ? action : 0;
  const reach = (from: number, to: number) => sentences.slice(from, to + 1).join(" ").length + heading.length + 2;
  const picked = core >= 0 && (core < firstAction || reach(firstAction, core) > HEALTH_EXTRACT_MAX_CHARS) ? core : firstAction;
  // A numbered list's marker splits off as its own "sentence" ("- 1.", then "Drop (or Lock): ..."): keep it,
  // or the list starts at 2 (Ready.gov, pack v3; the chat renders "1. … 2. … 3." as a list).
  const start = picked > 0 && /^[-•*]?\s*\d+[.)]$/.test(sentences[picked - 1].trim()) ? picked - 1 : picked;
  let text = heading ? `${heading}:` : "";
  for (const s of sentences.slice(start)) {
    const hit = rules.cutAt ? rules.cutAt.exec(s) : null;
    if (hit) {
      if (rules.cutInside) {
        // "- Boil … - Use iodine tablets … - Use a survival straw (…) Consider drinking tea…": keep what comes
        // before the last item/clause boundary preceding the aside.
        const before = s.slice(0, hit.index);
        const boundary = Math.max(before.lastIndexOf(" - "), before.lastIndexOf(") ") + 1, before.lastIndexOf("; "));
        const kept = boundary > 0 ? before.slice(0, boundary).trim() : "";
        if (kept.split(/\s+/).length >= 3) text = text ? `${text} ${kept}` : kept;
      }
      break;
    }
    if (text.length > heading.length + 1 && text.length + s.length + 1 > HEALTH_EXTRACT_MAX_CHARS) break;
    text = text ? `${text} ${s}` : s;
  }
  if (rules.mustInclude && !rules.mustInclude.test(text)) {
    const care = sentences.find((x) => rules.mustInclude!.test(x) && !rules.cutAt?.test(x));
    if (care) text = `${text} ${care}`;
  }
  // Steps = an instructions-like source AND at least one sentence that tells what to do
  // (a heading plus an image caption, "During an Earthquake: Image", is not an answer).
  // Or the quoted text itself gives two or more instructions ("- Boil the water before drinking - Use iodine
  // tablets": Sextant dng-005-pt said "the source doesn't give the steps" over them, from a travel page).
  const steps =
    (healthActionScore(source) >= HEALTH_ACTION_MIN_SCORE || imperativeSteps(text) >= 2) &&
    splitSentences(text).some((s) => new RegExp(ACTION_WORD.source, "i").test(s));
  const lead = steps
    ? pt
      ? "Da fonte offline (em inglês):"
      : "From the offline source:"
    : pt
      ? "A fonte offline não traz os passos de socorro para isso. Em uma emergência, ligue para o serviço de emergência local (192 SAMU, 193 Bombeiros). O que a fonte diz (em inglês):"
      : "The offline source doesn't give first-aid steps for this. In an emergency, call your local emergency number. What the source says:";
  // The emergency line closes every health answer; the "no steps" lead already says it.
  return steps ? `${lead}\n${text} [${sourceNumber}]\n\n${emergencyLine(pt)}` : `${lead}\n${text} [${sourceNumber}]`;
}

// First-aid instructions the sources call wrong (NHS, CDC, Ready.gov), as a model might phrase them.
const RISKY_HEALTH: Array<[string, RegExp]> = [
  ["blow-nose", /\bblow\w*\b[^.]{0,20}\bnose\b/i],
  ["head-back", /\b(tilt|lean|put|tip|throw)\w*\b[^.]{0,25}\bhead\b[^.]{0,10}\bback(wards?)?\b/i],
  ["lie-down-nosebleed", /\b(lie|lay)\b[^.]{0,10}\b(down|flat)\b[^.]{0,40}\bnose/i],
  ["tourniquet", /\btourniquet|torniquete|garrote|constricting band|faixa de constri/i],
  ["suck-venom", /\bsuck\w*[^.]{0,30}venom|chup\w*[^.]{0,30}veneno/i],
  ["cut-wound", /\b(cut|slice|incise|incision)\w*\b[^.]{0,30}\b(bite|wound|fang)/i],
  ["ice", /\b(apply|use|put)\w*\b[^.]{0,20}\bice\b|\bice[- ](pack|cold)|\bgelo\b/i],
  ["butter-toothpaste", /\bbutter\b|toothpaste|manteiga|pasta de dente/i],
  ["burn-cream", /\b(cream|ointment|lotion)s?\b[^.]{0,30}\bburn|\bburn\w*\b[^.]{0,40}\b(cream|ointment|lotion)|pomada/i],
  ["doorway", /\bdoorway|batente|v[ãa]o da porta/i],
  ["run-outside-quake", /\b(run|rush)\w* (outside|outdoors)/i],
];
// Known-false technical claims, as a model might phrase them (gate 394bf31, crypto-named-001 seed 5: "Quantum-
// resistant signature algorithms include those based on elliptic curve cryptography (ECC)"; the NSA passage in
// the prompt says elliptic curves are what quantum computing threatens). Shor's algorithm breaks RSA, ECC, DSA and
// Diffie-Hellman: none of them is quantum resistant.
const CLASSICAL_PK = /\b(rsa|ecc|ecdsa|eddsa|ed25519|secp256k1|elliptic[- ]curves?|diffie[- ]hellman|dsa)\b|curvas? el[íi]pticas?/i;
const QUANTUM_SAFE = /\bquantum[- ](resistant|safe|secure|proof)\b|\b(resistant|secure|safe|immune)\s+(to|against)\s+(a\s+)?quantum\b|resistentes? (a|contra) (computadores |ataques )?qu[âa]nticos?|seguros? contra (computadores |ataques )?qu[âa]nticos?/i;
// Negation or contrast in the sentence ("RSA is widely used, while lattice schemes are quantum resistant").
const CLAIM_NEGATED = /\b(not|no|none|never|isn't|aren't|vulnerable|broken|break|breaks|breaking|breakable|threat\w*|migrat\w*|shor|unlike|instead of|rather than|replac\w*|weak\w*|insecure|while|whereas|but|however|compared|versus|vs)\b|n[ãa]o\b|nenhum\w*|\bnem\b|vulner[áa]ve|quebr|enquanto|mas\b|diferente/i;

// Languages with their own script: what a question asks for, and the Unicode script its words must be in.
const LANGUAGE_SCRIPTS: Array<[RegExp, RegExp]> = [
  [/\bthai\b|tailand[êe]s/i, /\p{Script=Thai}/u],
  [/\bjapanese\b|japon[êe]s/i, /[\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Han}]/u],
  [/\bkorean\b|coreano/i, /\p{Script=Hangul}/u],
  [/\b(chinese|mandarin|cantonese)\b|chin[êe]s|mandarim/i, /\p{Script=Han}/u],
  [/\barabic\b|[áa]rabe/i, /\p{Script=Arabic}/u],
  [/\brussian\b|\brusso\b/i, /\p{Script=Cyrillic}/u],
  [/\bgreek\b|\bgrego\b/i, /\p{Script=Greek}/u],
  [/\bhebrew\b|hebraico/i, /\p{Script=Hebrew}/u],
  [/\bhindi\b/i, /\p{Script=Devanagari}/u],
  [/\bkhmer\b|cambojano|khmer/i, /\p{Script=Khmer}/u],
  [/\b(lao|laotian)\b|laosiano/i, /\p{Script=Lao}/u],
];
const NON_LATIN_LETTER = /[^\p{Script=Latin}\p{Script=Common}\p{Script=Inherited}\s\d]/u;

/**
 * Sentences of an answer whose non-Latin words are in the wrong script for the language the question asks about
 * (Sextant trv-007-pt, gate 39a2508: "Obrigado em tailandês é 'សួស្តី'" — Khmer, not Thai). Only the script is
 * checked: a wrong word in the right script isn't caught. No language with its own script asked: none.
 */
export function wrongScriptSentences(query: string, answer: string): string[] {
  const expected = LANGUAGE_SCRIPTS.filter(([asks]) => asks.test(query)).map(([, script]) => script);
  if (!expected.length) return [];
  return splitSentences(answer).filter((sentence) =>
    [...sentence].some((ch) => NON_LATIN_LETTER.test(ch) && !expected.some((script) => script.test(ch)))
  );
}

const LANGUAGE_NAMES =
  "thai|japanese|korean|chinese|mandarin|cantonese|arabic|russian|greek|hebrew|hindi|khmer|lao|vietnamese|indonesian|malay|turkish|spanish|french|german|italian|portuguese|tailand[êe]s|japon[êe]s|coreano|chin[êe]s|mandarim|[áa]rabe|russo|grego|hebraico|vietnamita|indon[ée]sio|turco|espanhol|franc[êe]s|alem[ãa]o|italiano|portugu[êe]s";
// Health content in a phrase to translate: allergy, medicine, illness, symptom, blood, medical emergency.
const PHRASE_HEALTH_CONTENT =
  /(?<![\p{L}])(al[ée]rg\p{L}*|allerg\p{L}*|anaphyla\p{L}*|epipen|insulin\p{L}*|diabet\p{L}*|epilep\p{L}*|asthma|asma|medicine|medication|pills?|rem[ée]dios?|medicamentos?|rem[ée]dio|disease|illness|sick|doen[çc]a|doente|symptoms?|sintomas?|pain|hurts?|dor(es)?|d[óo]i|blood|sangue|sangr\p{L}*|bleed\p{L}*|doctor|m[ée]dic[oa]|hospital|ambulance|ambul[âa]ncia|pregnant|gr[áa]vida|heart|cora[çc][ãa]o|emergency|emerg[êe]ncia)(?![\p{L}])/iu;
const PHRASE_ASK = new RegExp(
  `\\b(how (do|would|can|should) (i|you|we) say|how to say|how do (you|i) greet|what('s| is| are) [^?]{1,40} in (${LANGUAGE_NAMES})|translate)\\b|(?<![\\p{L}])(como (se )?diz|como (eu )?(falo|digo|cumprimento)|como se fala|como se escreve|como [ée] [^?]{1,40} em (${LANGUAGE_NAMES}))(?![\\p{L}])`,
  "iu"
);

/**
 * "Como se diz obrigado em tailandês, e muda se eu for homem ou mulher?" (Sextant trv-007, 91b17a2): with no
 * phrasebook in the library, every model answer (the old control's too) said it doesn't change with gender (it
 * does: khop khun khrap / kha), one in Khmer script. A phrase or translation question with no source is declined
 * by both models instead of being answered from memory.
 */
export function isPhraseQuestion(query: string): boolean {
  // Narrowed to what the models invent: whether a phrase changes with the speaker's gender (politeness particles).
  // Every phrase question would also decline lng-001/006/009/010 on s32 (4B refusals, limit 2/32).
  return PHRASE_ASK.test(query) && GENDER_ASK.test(query);
}
const GENDER_ASK = /\b(man or (a )?woman|men and women|male|female|gender|by sex)\b|(?<![\p{L}])(homem ou (uma )?mulher|homens e mulheres|g[êe]nero|sexo|masculino|feminino)(?![\p{L}])/iu;

/** Sentences of an answer that call classical public-key crypto (RSA, ECC, DSA, DH) quantum resistant. */
export function falseQuantumClaims(answer: string): string[] {
  return splitSentences(answer).filter((s) => CLASSICAL_PK.test(s) && QUANTUM_SAFE.test(s) && !CLAIM_NEGATED.test(s));
}

// A passage that presents a procedure as disputed is not first-aid guidance to quote (Sextant dng-001:
// "…by pressure immobilization is desirable … whether this trade-off is desirable remains a point of controversy").
const CONTESTED = /\bcontrovers\w*|\bdebated\b|\bdisputed\b|\btrade-?off\b|\bconflicting (evidence|advice|recommendations)\b|\bno consensus\b|\bpoint of contention\b|recommendations vary/i;

/** Whether a health excerpt may be shown: no disputed procedure, no known-dangerous instruction. */
export function safeHealthExcerpt(text: string): boolean {
  return !CONTESTED.test(text) && riskyHealthInstruction(text) === null;
}

/** No safe first-aid text in the library: the emergency number and "get care", no steps from memory. */
export function noSafeStepsAnswer(pt: boolean): string {
  return pt
    ? "Não encontrei no acervo offline instruções de primeiros socorros seguras para isso. Ligue agora para o serviço de emergência (192 SAMU ou 193 Bombeiros no Brasil, 112 na Europa, 911 nos EUA) e procure atendimento médico o quanto antes."
    : "I didn't find safe first-aid instructions for this in the offline library. Call your local emergency number now (911 in the US, 112 in Europe) and get medical care as soon as possible.";
}

const NEGATED = /\b(do not|don't|dont|never|avoid|not|no|instead of|rather than|without)\b|n[ãa]o\b|nunca|evite/i;

// Exertion advice in a text about hypothermia (Lantern safety 2026-09-30, dng-002): Wikivoyage "Cold weather" led
// with "Keeping on walking even when tired is important" for a confused, slurring partner. Confusion and slurred
// speech mean at least moderate hypothermia, where the person is kept horizontal and handled gently (WMS 2019);
// exercise is allowed only in mild hypothermia, so a sentence that says "mild" stays.
const HYPOTHERMIA_CONTEXT = /\bhypotherm|hipoterm|\bfrostbite|congelamento/i;
// Walking, moving on or exercising, as advice ("keep walking", "get them to walk") or as a direct instruction
// ("walk to shelter", "start walking", PT "caminhe", "ande", "continue andando").
const EXERTION = new RegExp(
  [
    String.raw`\b(keep\w*|continu\w*|stay\w*)\b[^.]{0,20}\b(walk|mov|hik|exercis|march)\w*`,
    String.raw`\b(get|make|help|encourag)\w*\b[^.]{0,40}\b(walk|rise)\w*`,
    String.raw`\b(walk\w*|hik(e|es|ed|ing)|jog\w*|march(es|ed|ing)?)\b`,
    String.raw`\bexercis\w*|\bphysical activity`,
    String.raw`(?<![\p{L}])(caminh\p{L}*|and(e|em|ar|ando|a)|mexa|se mexer|exercit\p{L}*|exerc[ií]cios?|atividade f[ií]sica)(?![\p{L}])`,
    String.raw`mant\p{L}* [^.]{0,20}em movimento`,
  ].join("|"),
  "giu"
);
const MILD = /\bmild\b|\bleve\b/i;
// Negation of the exertion itself: in its clause, right before it. English and Portuguese apart, so the Portuguese
// preposition "no"/"na" ("caminhando no frio") never counts; "not only … but also" doesn't negate either.
const EXERTION_NEGATED_EN = /\b(not|don't|dont|do not|never|avoid\w*|cannot|can't|without|instead of|rather than)\b/i;
const EXERTION_NEGATED_PT = /(?<![\p{L}])(n[ãa]o|nunca|evit\p{L}*|sem|em vez de)(?![\p{L}])/iu;
const CLAUSE_BREAK = /[,;:—()]|\b(and|but|then|so)\b|(?<![\p{L}])(e|mas|ent[ãa]o)(?![\p{L}])/giu;

/** Whether the exertion at `index` is negated in its own clause ("do not keep walking", "não continue caminhando"). */
function exertionNegated(sentence: string, index: number): boolean {
  const before = sentence.slice(0, index);
  let from = 0;
  for (const m of before.matchAll(CLAUSE_BREAK)) from = (m.index ?? 0) + m[0].length;
  const clause = before.slice(Math.max(from, index - 40)).replace(/\bnot only\b|n[ãa]o s[óo]\b|n[ãa]o apenas\b/giu, "");
  return EXERTION_NEGATED_EN.test(clause) || EXERTION_NEGATED_PT.test(clause);
}

/** The first known-dangerous instruction in a generated health answer (not negated in its sentence), or null. */
export function riskyHealthInstruction(answer: string): string | null {
  const cold = HYPOTHERMIA_CONTEXT.test(answer);
  for (const sentence of splitSentences(answer)) {
    for (const [id, re] of RISKY_HEALTH) if (re.test(sentence) && !NEGATED.test(sentence)) return id;
    if (!cold || MILD.test(sentence)) continue;
    for (const m of sentence.matchAll(EXERTION)) if (!exertionNegated(sentence, m.index ?? 0)) return "exertion-hypothermia";
  }
  return null;
}

/** Health question without a good source: fixed text, no model. */
export function noHealthSourceAnswer(pt: boolean): string {
  return pt
    ? "Não tenho uma fonte offline confiável sobre isso, então não vou arriscar orientações de saúde de memória. Em uma emergência, ligue para o serviço de emergência local (192 SAMU ou 193 Bombeiros no Brasil, 112 na Europa, 911 nos EUA)."
    : "I don't have a reliable offline source on this, so I won't give health advice from memory. In an emergency, call your local emergency number (911 in the US, 112 in Europe).";
}

/** A chunk whose best sentence scores under this share of the best chunk's is dropped. */
export const RELATIVE_RELEVANCE_FLOOR = 0.5;

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

/** The shown relevance of an article the question names: the UI's 'high' band (Quill: >= 0.75). */
const NAMED_ARTICLE_RELEVANCE = 0.75;

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
      if (used + titleCost + cost(s) > budget) continue;
      used += titleCost;
      const first = scored.find((x) => x.chunkIndex === s.chunkIndex && x.position === 0);
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
  const qTerms = [...new Set(tokenizeTerms(query))];
  const shownRelevance = (ci: number) => {
    const best = scored.filter((x) => x.chunkIndex === ci).sort((a, b) => b.score - a.score)[0];
    const have = new Set([...tokenizeTerms(chunks[ci].title), ...tokenizeTerms(best?.text ?? "")]);
    const share = qTerms.length ? qTerms.filter((t) => have.has(t)).length / qTerms.length : 0;
    // The article the question names ("Monsoon" for "What causes the monsoon?") never reads as weak.
    const named = chunks[ci].title.split(/:\s+/).some((seg) => {
      const st = tokenizeTerms(seg.replace(/\s*\([^)]*\)\s*$/, ""));
      return st.length > 0 && st.every((t) => qTerms.includes(t));
    });
    return named ? Math.max(share, NAMED_ARTICLE_RELEVANCE) : share;
  };
  const out = keptIndices.map((ci) => {
    const positions = [...picked.get(ci)!].sort((a, b) => a - b);
    const body = positions
      .map((p) => scored.find((s) => s.chunkIndex === ci && s.position === p)!.text)
      .join(" ");
    // relevance (0..1), what the UI shows: the share of the question's words the title and the best
    // sentence cover, unweighted. The ranking's IDF weights are relative to the candidates: the topic
    // word itself ("monsoon"), in every sentence, weighed almost nothing, and the exact article read
    // "Low" (Prism BAND-1; on Sextant's sets the gold sources' median went 0.58 -> 0.75). None when
    // nothing matched at all.
    return { ...chunks[ci], body, ...(anyMatch ? { relevance: shownRelevance(ci) } : {}) };
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
