// Sonar exp-27: cross-encoder gate on the answer prompt's passages (runner-side, no engine change).
// The engine puts passages at the end of the system message: "...\n\nContext:\n[1] Title\nbody\n\n[2] Title\nbody".
// Rule (one knob): passage [1] (the engine's first) is always kept; passages [2..4] (<= 3 pairs) are scored against the
// question with bge-reranker-v2-m3 and dropped when score < tau. Remaining passages keep their numbers, so the engine's
// citation post-processing still maps [n] to the same source.
export interface Passage { n: number; text: string }
const MARK = "\n\nContext:\n";

export function splitContext(system: string): { head: string; passages: Passage[] } | null {
  const at = system.indexOf(MARK);
  if (at < 0) return null;
  const body = system.slice(at + MARK.length);
  const starts = [...body.matchAll(/(?:^|\n\n)\[(\d+)\] /g)].map((m) => ({ n: Number(m[1]), at: m.index! + (m[0].startsWith("\n\n") ? 2 : 0) }));
  if (!starts.length || starts[0].at !== 0) return null;
  const passages = starts.map((s, i) => ({ n: s.n, text: body.slice(s.at, i + 1 < starts.length ? starts[i + 1].at - 2 : body.length) }));
  return { head: system.slice(0, at + MARK.length), passages };
}

export function joinContext(head: string, passages: Passage[]): string {
  return head + passages.map((p) => p.text).join("\n\n");
}

/** The question the user typed: the last user message without the engine's "(Response style: …)" suffix. */
export function questionOf(user: string): string {
  return user.split("\n\n(Response style:")[0].trim();
}

/** Passage text without its "[n] " marker, as the reranker sees it (title line + body). */
export const doc = (p: Passage) => p.text.replace(/^\[\d+\] /, "").slice(0, 2400);

export async function gate(messages: { role: string; content: string }[], rank: (q: string, d: string) => Promise<number>, tau: number, maxPairs = 3) {
  const si = messages.findIndex((m) => m.role === "system");
  const user = [...messages].reverse().find((m) => m.role === "user");
  const split = si >= 0 ? splitContext(messages[si].content) : null;
  if (!split || !user || split.passages.length < 2) return { messages, info: null };
  const q = questionOf(user.content);
  const scored: { n: number; score: number | null; kept: boolean }[] = [{ n: split.passages[0].n, score: null, kept: true }];
  const kept: Passage[] = [split.passages[0]];
  for (const [i, p] of split.passages.slice(1).entries()) {
    if (i >= maxPairs) { kept.push(p); scored.push({ n: p.n, score: null, kept: true }); continue; }
    const s = await rank(q, doc(p));
    const keep = s >= tau;
    if (keep) kept.push(p);
    scored.push({ n: p.n, score: Math.round(s * 1000) / 1000, kept: keep });
  }
  const out = messages.map((m, i) => (i === si ? { ...m, content: joinContext(split.head, kept) } : m));
  return { messages: out, info: { question: q, scored, dropped: scored.filter((x) => !x.kept).map((x) => x.n) } };
}
