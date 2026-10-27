/**
 * Pure, native-module-free RAG helpers, kept separate from db.ts/embed.ts
 * (which pull in expo-sqlite/llama.rn) so they're unit-testable under plain
 * Node/vitest without an RN runtime.
 */
import type { RetrievedChunk } from "./retrieve.types";

export function cosineSimilarity(a: Float32Array, b: Float32Array): number {
  let dot = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  if (normA === 0 || normB === 0) return 0;
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

/**
 * Cosine similarity against an int8-quantized vector as stored in a knowledge
 * pack (raw bytes). The per-vector scale cancels out of the cosine, so it's
 * not needed here.
 */
export function cosineSimilarityInt8(query: Float32Array, bytes: Uint8Array): number {
  const v = new Int8Array(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  let dot = 0;
  let normQ = 0;
  let normV = 0;
  for (let i = 0; i < v.length; i++) {
    dot += query[i] * v[i];
    normQ += query[i] * query[i];
    normV += v[i] * v[i];
  }
  if (normQ === 0 || normV === 0) return 0;
  return dot / (Math.sqrt(normQ) * Math.sqrt(normV));
}

// bge-small-en-v1.5 cosine floor for a semantic hit to count as relevant.
// Without one, brute-force top-K always returns K chunks even when nothing
// on the device is about the question, and they get fed to the model as
// context. Measured on 2026-09-26 (eval/retrieval/questions.v1, 160
// questions against Wikipedia article leads; docs/KNOWLEDGE_PACKS.md):
// question → right article: p5 0.573, median 0.776; question → random
// article: median 0.380, p95 0.483, p99 0.530. The old floor of 0.45 let
// 13% of random articles through, which is how "Which signature algorithms
// are quantum resistant?" got answered from the RSA article when no
// post-quantum text was installed. 0.55 keeps 98% of right articles and
// 0.6% of random ones.
export const MIN_SEMANTIC_SIMILARITY = 0.55;

/**
 * Chunks given to the model for a chat answer. Each chunk adds prompt
 * processing before the first token (the main wait on a phone). In the
 * 2026-09-24 device benchmark every expected article was retrieved at rank
 * 1 or 2, and ranks 3-6 were mostly unrelated, so 4 keeps a margin for
 * three-topic questions. Deep Research keeps the default 6 per sub-question.
 */
export const ANSWER_CONTEXT_CHUNKS = 4;

/**
 * Excludes chunks whose raw score is below a minimum confidence floor.
 * Applied to a SINGLE source's raw scores, before fuseRetrievalResults's
 * max-relative normalization — normalizing first would make a floor
 * meaningless, since that normalization rescales each result set so its
 * own best match always looks "confident" (~1.0) relative to itself,
 * regardless of how weak that best match actually is in absolute terms.
 */
export function filterByMinScore<T extends { score: number }>(chunks: T[], minScore: number): T[] {
  return chunks.filter((c) => c.score >= minScore);
}

// Question framing and instruction words: they say what kind of answer is
// wanted, not what it's about, so matching on them only pulls in noise.
// Includes "work"/"mean"/"happen" because of "how does X work", "what
// does X mean", "why did X happen". English only, matching the corpus.
const LEXICAL_STOPWORDS = new Set([
  "a", "about", "after", "all", "also", "am", "an", "and", "any", "are", "as", "at",
  "be", "because", "been", "before", "being", "best", "better", "between", "both", "but", "by",
  "can", "could", "compare", "comparison", "describe", "detail", "details", "did",
  "difference", "differences", "do", "does", "doing", "during", "each", "explain",
  "for", "from", "give", "had", "has", "have", "having", "he", "her", "here", "him",
  "his", "how", "i", "if", "in", "into", "is", "it", "its", "just", "know", "like",
  "me", "mean", "means", "meant", "more", "most", "much", "my", "no", "not", "of",
  "on", "or", "other", "our", "overview", "please", "same", "she", "should", "show",
  "so", "some", "something", "such", "summarize", "summary", "tell", "than", "that",
  "the", "their", "them", "then", "there", "these", "they", "thing", "things", "this",
  "those", "through", "to", "too", "under", "up", "us", "very", "versus", "vs", "want",
  "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "whose",
  "why", "will", "with", "work", "works", "would", "you", "your", "happen", "happened",
  "happens", "cause", "caused", "causes",
]);

const MAX_LEXICAL_TERMS = 12;

export interface LexicalTerm {
  /**
   * Exact word forms that count as this term: the query word, plus its
   * singular when it looks plural ("vaccines" → "vaccine"), because the FTS
   * index has no stemmer.
   */
  forms: string[];
}

export interface LexicalQuery {
  /** FTS5 MATCH expression: every quoted form OR-ed together, BM25-ranked by FTS5 itself. */
  match: string;
  terms: LexicalTerm[];
}

// "-es" is ambiguous ("viruses" → "virus" but "cases" → "case"), so both
// candidates are kept; a form that isn't a real word simply never matches.
function singularsOf(token: string): string[] {
  if (token.length < 4 || !token.endsWith("s") || /(ss|is|us)$/.test(token)) return [];
  if (token.endsWith("ies")) return [`${token.slice(0, -3)}y`];
  if (/(s|x|z|o|ch|sh)es$/.test(token)) return [token.slice(0, -1), token.slice(0, -2)];
  return [token.slice(0, -1)];
}

function tokenize(text: string): string[] {
  return text
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .split(/[^\p{L}\p{N}]+/u)
    .filter((t) => t.length > 0);
}

/**
 * Turns a natural-language question into an FTS5 query of its content
 * words, OR-ed so a document doesn't have to contain the question verbatim.
 * Returns null when nothing meaningful is left ("tell me something"), so
 * the caller skips lexical search instead of matching on filler words.
 * Every term is double-quoted, so FTS5 operators typed by the user are
 * treated as plain text.
 */
export function buildLexicalQuery(query: string): LexicalQuery | null {
  const seen = new Set<string>();
  const terms: LexicalTerm[] = [];
  for (const token of tokenize(query)) {
    if (token.length < 2 || LEXICAL_STOPWORDS.has(token)) continue;
    const forms = [token, ...singularsOf(token)];
    if (forms.some((f) => seen.has(f))) continue;
    forms.forEach((f) => seen.add(f));
    terms.push({ forms });
    if (terms.length >= MAX_LEXICAL_TERMS) break;
  }
  if (terms.length === 0) return null;
  const match = terms.flatMap((t) => t.forms.map((f) => `"${f}"`)).join(" OR ");
  return { match, terms };
}

/**
 * How many content terms a lexical hit must contain. OR-matching alone
 * would accept a document that shares one incidental word with the
 * question ("black" → "Black Sea" for "black holes"), so short queries
 * need every term and longer ones a strict majority. Half was too little:
 * for "Which signature algorithms are quantum resistant?" a nuclear
 * physicist's bio (quantum Monte Carlo *algorithms*) matched 2 of 4 terms and
 * became the only source when the corpus had nothing on the topic.
 */
export function requiredTermMatches(termCount: number): number {
  return termCount <= 2 ? termCount : Math.floor(termCount / 2) + 1;
}

export function countMatchedTerms(text: string, terms: LexicalTerm[]): number {
  const tokens = new Set(tokenize(text));
  return terms.filter((term) => term.forms.some((f) => tokens.has(f))).length;
}

/**
 * The lexical relevance gate: keeps only BM25 hits covering enough of the
 * query's content terms, in their original BM25 order.
 */
export function filterByTermCoverage<T extends { title: string; body: string }>(
  hits: T[],
  terms: LexicalTerm[]
): T[] {
  const required = requiredTermMatches(terms.length);
  return hits.filter((h) => countMatchedTerms(`${h.title} ${h.body}`, terms) >= required);
}

/**
 * Weighted-sum fusion of two already-scored, already-relevance-filtered
 * result sets into one ranked list. Each source is normalized to its own
 * max score before weighting so lexical (BM25, unbounded) and semantic
 * (cosine, bounded [-1,1]) scores combine meaningfully despite being on
 * completely different scales.
 *
 * This is a RELATIVE re-ranking step, not a second relevance gate — it has
 * no way to tell a genuinely strong match from "the best of a bad lot",
 * since normalizing to each set's own max erases that distinction by
 * construction. Absolute relevance must be decided by filterByMinScore
 * (or an equivalent gate, like lexicalSearch's filterByTermCoverage) on
 * the INPUTS, before this runs — see retrieve.ts.
 */
export function fuseRetrievalResults(
  lexical: RetrievedChunk[],
  semantic: RetrievedChunk[],
  topK: number,
  weights: { lexical: number; semantic: number } = { lexical: 0.5, semantic: 0.5 }
): RetrievedChunk[] {
  const byId = new Map<string, RetrievedChunk>();
  const normalize = (chunks: RetrievedChunk[], weight: number) => {
    if (chunks.length === 0) return;
    const max = Math.max(...chunks.map((c) => c.score), 1e-9);
    for (const c of chunks) {
      const norm = (c.score / max) * weight;
      const existing = byId.get(c.chunkId);
      if (existing) {
        existing.score += norm;
        existing.matchType = "hybrid";
        if (c.similarity !== undefined) existing.similarity = Math.max(existing.similarity ?? -1, c.similarity);
      } else {
        byId.set(c.chunkId, { ...c, score: norm });
      }
    }
  };

  normalize(lexical, weights.lexical);
  normalize(semantic, weights.semantic);

  // At most MAX_CHUNKS_PER_ARTICLE per title, so one article's chunks can't crowd out a
  // second topic (knowledge packs store up to 3 chunks per article).
  const perTitle = new Map<string, number>();
  const out: RetrievedChunk[] = [];
  for (const c of Array.from(byId.values()).sort((a, b) => b.score - a.score)) {
    const key = c.title.trim().toLowerCase();
    const n = perTitle.get(key) ?? 0;
    if (n >= MAX_CHUNKS_PER_ARTICLE) continue;
    perTitle.set(key, n + 1);
    out.push(c);
    if (out.length >= topK) break;
  }
  return out;
}

export const MAX_CHUNKS_PER_ARTICLE = 2;

/**
 * Relevance gate on fused results (retrieve.ts), on the real cosine similarity rather than the
 * fused score, which is only relative. Measured with bge-small over the Vital Articles pack
 * (scripts/rag-calibrate.mjs): the right sources for the evaluation questions scored 0.73-0.86,
 * while noise like "can you help me?" matched at 0.54-0.57.
 *
 * Nothing below ANSWER_MIN_SIMILARITY is sent to the model. There's deliberately no cut relative
 * to the best chunk: a comparison's second topic scores lower than its first, and a window of
 * 0.06 below the best dropped it (French vs Industrial Revolution, immune system vs vaccine, in
 * the on-phone evaluation of 2026-09-28).
 *
 * Chunks with no similarity (a keyword-only hit) are dropped: a word in common isn't enough.
 * Questions that share only a word with an article ("whats your name?" and Name at 0.69) are
 * kept out earlier, by classifyTask's "conversation" type.
 */
export const ANSWER_MIN_SIMILARITY = 0.7;

export function gateByRelevance<T extends { similarity?: number }>(
  chunks: T[],
  minSimilarity = ANSWER_MIN_SIMILARITY
): T[] {
  return chunks.filter((c) => c.similarity !== undefined && c.similarity >= minSimilarity);
}

export interface ConversationTurn {
  role: "user" | "assistant";
  text: string;
}

export interface ConversationHistory {
  /** Condensed summary of older turns (see src/services/summarize.ts). */
  summary?: string | null;
  /** Recent turns kept verbatim, oldest first. */
  turns?: ConversationTurn[];
}

/**
 * `systemPrompt` sets the assistant's tone/style/length (see
 * src/constants/personalities.ts) — the citation instruction is always
 * appended on top so RAG citations keep working regardless of persona.
 *
 * `history` layers in prior conversation: a condensed summary of older
 * turns (once a chat exceeds the configured turn threshold — see
 * src/services/summarize.ts) plus the last few turns kept verbatim, so the
 * assistant doesn't lose context on the 7th+ message in a long chat.
 */
export function assemblePrompt(
  userQuery: string,
  chunks: RetrievedChunk[],
  systemPrompt?: string,
  history?: ConversationHistory,
  styleReminder?: string
): string {
  const instruction = instructionOf(systemPrompt);

  const summarySection =
    history?.summary && history.summary.trim().length > 0
      ? `Summary of earlier conversation:\n${history.summary.trim()}\n\n`
      : "";

  const turnsSection =
    history?.turns && history.turns.length > 0
      ? `Recent conversation:\n${history.turns
          .map((t) => `${t.role === "user" ? "User" : "Assistant"}: ${t.text}`)
          .join("\n")}\n\n`
      : "";

  // With zero retrieved chunks (a greeting/calculate/translate/code task
  // per isRetrievalIrrelevant, or a "chat"-type query retrieve() genuinely
  // found nothing relevant for), the whole context/citation framing is
  // omitted entirely rather than left as an empty "Context:\n\n" section —
  // an empty-but-present section still tells the model there's supposed to
  // be something there and to "cite a source you used by its number", which is exactly the
  // kind of dangling framing that nudges a small model toward inventing
  // content to fill it instead of just answering conversationally.
  const hasContext = chunks.length > 0;
  const contextInstruction = hasContext ? CONTEXT_INSTRUCTION : "";
  const contextSection = hasContext
    ? `Context:\n${chunks.map((c, i) => `[${i + 1}] ${c.title}\n${c.body}`).join("\n\n")}\n\n`
    : "";

  return `${instruction}${contextInstruction} ${GROUNDING_INSTRUCTION}\n\n` +
    `${summarySection}${turnsSection}` +
    `${contextSection}` +
    `Question: ${userQuery}${styleSection(styleReminder)}\n\nAnswer:`;
}

const instructionOf = (systemPrompt: string | undefined) =>
  systemPrompt && systemPrompt.trim().length > 0 ? systemPrompt.trim() : "You are an offline research assistant.";

const CONTEXT_INSTRUCTION =
  " Use the context below when relevant, and cite a source you used by its number, like [1] or [2]. " +
  "If the context doesn't cover the question, say so and answer from general knowledge.";

/**
 * The fixed start of every answer prompt that has sources, for a given tone: persona, source rules and
 * GROUNDING_INSTRUCTION, before the summary, the sources and the question. `system` opens
 * assembleChatMessages' system message, `prompt` opens assemblePrompt's text. LlamaEngine keeps it prefilled
 * in the KV cache (setAnswerPrefix), so a question only pays for what follows it: on the iPhone 13 this is
 * ~225 of a ~400-token prompt, ~2 s of CPU prefill.
 */
export function answerPromptPrefix(systemPrompt?: string): { system: string; prompt: string } {
  const head = `${instructionOf(systemPrompt)}${CONTEXT_INSTRUCTION} ${GROUNDING_INSTRUCTION}`;
  return { system: head, prompt: `${head}\n\n` };
}

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

/**
 * Same inputs and content as assemblePrompt, structured as a role-separated
 * messages array instead of one hand-built string — for models that need
 * their own real chat/instruction template applied (see
 * ModelCapabilities.usesChatTemplate, src/routing/types.ts) rather than the
 * app's generic "Question: ...\n\nAnswer:" completion shape. The caller
 * (executor.ts) passes this to LlamaEngine.generate()'s `messages` param,
 * which hands it to llama.rn/llama.cpp's own jinja chat-template engine —
 * this function never guesses at a specific template's literal syntax
 * (ChatML, Phi's format, etc.), it only decides message content/roles.
 *
 * Deliberately NOT used by assemblePrompt's callers by default — see that
 * function's own doc comment on why switching everything to a chat
 * template is a bigger, separate change than this fix attempts.
 */
export function assembleChatMessages(
  userQuery: string,
  chunks: RetrievedChunk[],
  systemPrompt?: string,
  history?: ConversationHistory,
  styleReminder?: string
): ChatMessage[] {
  const instruction = instructionOf(systemPrompt);

  const hasContext = chunks.length > 0;
  const contextInstruction = hasContext ? CONTEXT_INSTRUCTION : "";
  const contextSection = hasContext
    ? `\n\nContext:\n${chunks.map((c, i) => `[${i + 1}] ${c.title}\n${c.body}`).join("\n\n")}`
    : "";
  const summarySection =
    history?.summary && history.summary.trim().length > 0
      ? `\n\nSummary of earlier conversation:\n${history.summary.trim()}`
      : "";

  const systemMessage: ChatMessage = {
    role: "system",
    content:
      `${instruction}${contextInstruction} ${GROUNDING_INSTRUCTION}${summarySection}${contextSection}`,
  };

  const historyMessages: ChatMessage[] = (history?.turns ?? []).map((t) => ({
    role: t.role,
    content: t.text,
  }));

  return [systemMessage, ...historyMessages, { role: "user", content: userQuery + styleSection(styleReminder) }];
}

/**
 * Universal capability/tone boundary, appended for every request regardless
 * of persona or content — not a hardcoded response to any specific phrase.
 *
 * Root cause of the "wake up" -> "morning alarm set / room temperature
 * adjusted" hallucination: this prompt hand-builds a generic "Question: ...
 * Answer:" completion shape rather than a model's actual fine-tuned chat
 * template. Off that template, a small model given a short, ambiguous,
 * command-shaped fragment with no explicit "you're a chat assistant with
 * no real-world abilities" framing tends to free-associate into a
 * narrative completion (the classic sci-fi/smart-home assistant pattern,
 * or — as later real-device testing found with Qwen specifically — a
 * rambling multi-question FAQ ramble) instead of a real conversational
 * reply. `assembleChatMessages` (below) now gives models flagged
 * `usesChatTemplate` (currently just Qwen2.5-1.5B-Instruct) their own real
 * template via llama.rn's jinja support — but switching every model
 * (including Phi) and every caller (including Deep Research's per-stage
 * prompts, researchSubQuestion in orchestrator.ts) over is a bigger,
 * separate, deliberately not-yet-made decision. This instruction stays as
 * the universal, always-applied floor regardless of which prompt-building
 * path is used. It's a no-op for genuine questions (Deep Research's
 * decomposed sub-questions are always real questions, never action
 * requests), so it doesn't change that path's behavior in practice.
 */
/**
 * The tone's style reminder, appended to the current question (see
 * Personality.styleReminder). Only this turn carries it: history keeps the
 * user's own words, and retrieval searches the question alone.
 */
function styleSection(styleReminder: string | undefined): string {
  const s = styleReminder?.trim();
  return s ? `\n\n(Response style: ${s})` : "";
}

const GROUNDING_INSTRUCTION =
  // "You are Boar" alone made a 1.5B model answer "Boar is a water mammal" (Sextant, 2026-09-26).
  'You are BOAR, an offline AI research app running on this phone; "Boar" is the app\'s name, never the animal, so never describe yourself as one. ' +
  "You have no ability to control real-world devices or take physical actions — no alarms, " +
  "lights, thermostats, timers, or any other device or system. You can only respond with text. " +
  "Treat greetings and casual small talk conversationally and briefly, not as a command or task. " +
  "Never claim to have done something (set, adjusted, turned on/off, scheduled, etc.) that you " +
  "don't actually have the ability to do.";
