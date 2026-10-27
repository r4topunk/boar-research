/**
 * "Why"/"what causes" questions (RF-1): within the article a question lands on, the passage that also has the
 * question's OTHER words ("earthquake", "boundary" for Plate tectonics) explains more than the article's lead.
 * Pure: shared by format-1 (packs.ts) and format-2 (wikiPack.ts) passage choice.
 */
import { countMatchedTerms, type LexicalTerm } from "./pure.ts";

/** Questions asking for a cause or a mechanism, in English or Portuguese. */
export const EXPLAIN_INTENT =
  /\b(why|what (?:causes?|makes|drives|triggers|produces)|how (?:does|do|did|is|are|can)|reason|por ?que|o que (?:causa|faz|provoca|gera)|como (?:funciona|acontece|se forma|ocorre))\b/i;

/** The question's terms that aren't in the title: what a passage must add beyond naming the subject. */
export function termsBeyondTitle(terms: LexicalTerm[], title: string): LexicalTerm[] {
  return terms.filter((t) => countMatchedTerms(title, [t]) === 0);
}

/**
 * Reorders the chunks of each title among the positions that title already holds, most of the question's other
 * terms first (ties keep their order). Other titles don't move. A chunk takes the score of the position it moves
 * to, so a later sort by score (the fusion in retrieve()) keeps the order.
 */
export function explainingFirst<T extends { title: string; body: string; score?: number }>(items: T[], terms: LexicalTerm[]): T[] {
  const out = [...items];
  const byTitle = new Map<string, number[]>();
  items.forEach((c, i) => byTitle.set(c.title, [...(byTitle.get(c.title) ?? []), i]));
  for (const [title, slots] of byTitle) {
    if (slots.length < 2) continue;
    const beyond = termsBeyondTitle(terms, title);
    if (!beyond.length) continue;
    const ranked = slots
      .map((i, order) => ({ c: items[i], order, n: countMatchedTerms(items[i].body, beyond) }))
      .sort((a, b) => b.n - a.n || a.order - b.order);
    slots.forEach((slot, k) => {
      const c = ranked[k].c;
      out[slot] = items[slot].score === undefined ? c : { ...c, score: items[slot].score };
    });
  }
  return out;
}
