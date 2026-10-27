// Sonar exp-30: learned emergency detector, the part that runs in JS (Forge: the head must live in JS; the
// pooled vector comes from llama.rn/llama.cpp `embedding()` with pooling mean). Pure: no I/O.
export const DETECTOR_MAX_PREV = 3;
export const DETECTOR_MAX_CHARS = 2000;
/** Content-work budget: 126 + <bos>/<eos> = the 128 the model was trained with (Forge review: longer inputs differ). */
export const DETECTOR_MAX_TOKENS = 126;
/** Frozen 2026-10-03 before any blind run (see confirm-health11.md). */
export const DETECTOR_THRESHOLD = 0.2;
/** Gated lexical floor (v3 L1): the broad health regex still routes to the health path when the detector gives at least
 *  this much evidence, so a generic health how-to ("como trata queimadura de água-viva? vou pra Maragogi…", p 0.028) is
 *  never answered from memory; figurative/trivia score ~0. Compass dev: +1 strict false fire, +3 how-to (tolerated). */
export const DETECTOR_FLOOR = 0.01;
const CONTROL = /<(?:bos|eos|unk|pad|mask|start_of_turn|end_of_turn)>/gi; // typed literals parse as special tokens
const norm = (u: string) => u.replace(CONTROL, " ").replace(/\s+/g, " ").trim();
// Left cut to MAX_CHARS code points (as Python str slicing), then no leading space: llama.cpp would emit "▁▁word", HF "▁word".
const cut = (t: string) => { const cp = Array.from(t); return (cp.length > DETECTOR_MAX_CHARS ? cp.slice(-DETECTOR_MAX_CHARS).join("") : t).trimStart(); };

/**
 * The detector's input, the same algorithm as training (common2.py detector_text): up to 3 earlier user turns + the
 * message, " | "-joined (never "\n": an added token HF and llama.cpp tokenize differently after); drop the oldest turns
 * until <= 126 tokens, then the message's leading words (fewest that fit, binary search). `countTokens` = llama.rn
 * `tokenize()` on the detector context (no BOS/EOS), or llama-server /tokenize on the desktop.
 */
export async function detectorText(userTurns: string[], query: string, countTokens: (t: string) => Promise<number>): Promise<string> {
  let prev = userTurns.map(norm).filter(Boolean).slice(-DETECTOR_MAX_PREV);
  const msg = norm(query);
  let t = cut([...prev, msg].join(" | "));
  while ((await countTokens(t)) > DETECTOR_MAX_TOKENS && prev.length) {
    prev = prev.slice(1);
    t = cut([...prev, msg].join(" | "));
  }
  if ((await countTokens(t)) <= DETECTOR_MAX_TOKENS) return t;
  const words = t.split(" ");
  let lo = 1, hi = words.length - 1;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if ((await countTokens(words.slice(mid).join(" "))) <= DETECTOR_MAX_TOKENS) hi = mid;
    else lo = mid + 1;
  }
  return words.slice(lo).join(" ").trimStart();
}

export type MmbertHead = { kind: "mmbert-cls"; dim: number; eps: number; dense: number[]; norm: number[]; cls_w: number[]; cls_b: number[] };
export type E5Head = { kind: "e5-linear"; w: number[]; b: number };
export type DetectorHead = MmbertHead | E5Head;

// erf, Abramowitz & Stegun 7.1.26 (|error| < 1.5e-7): exact-GELU as in HF's GELUActivation.
function erf(x: number): number {
  const s = Math.sign(x), a = Math.abs(x), t = 1 / (1 + 0.3275911 * a);
  const y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-a * a);
  return s * y;
}

/** ModernBERT classification head on the mean-pooled, NOT normalized vector. Returns P(emergency). */
export function mmbertProbability(h: MmbertHead, pooled: ArrayLike<number>): number {
  // Forge: llama.rn caches n_embd in a function-local static from the FIRST embedding context; a wrong length must
  // fail (caller falls back to the lexical predicate), never score garbage.
  if (pooled.length !== h.dim) throw new Error(`detector: embedding length ${pooled.length} != ${h.dim}`);
  const d = h.dim, z = new Float64Array(d);
  for (let i = 0; i < d; i++) {
    let acc = 0;
    for (let j = 0; j < d; j++) acc += h.dense[i * d + j] * pooled[j];
    z[i] = 0.5 * acc * (1 + erf(acc / Math.SQRT2));
  }
  let mean = 0;
  for (let i = 0; i < d; i++) mean += z[i];
  mean /= d;
  let v = 0;
  for (let i = 0; i < d; i++) v += (z[i] - mean) ** 2;
  const inv = 1 / Math.sqrt(v / d + h.eps);
  const l = [h.cls_b[0], h.cls_b[1]];
  for (let i = 0; i < d; i++) {
    const n = (z[i] - mean) * inv * h.norm[i];
    l[0] += h.cls_w[i] * n;
    l[1] += h.cls_w[d + i] * n;
  }
  return 1 / (1 + Math.exp(l[0] - l[1]));
}

/** e5-small linear head on [emb('query: '+message) ⊕ emb('query: '+detectorText)], both L2-normalized. */
export function e5Probability(h: E5Head, embQuery: ArrayLike<number>, embText: ArrayLike<number>): number {
  let z = h.b;
  const n = embQuery.length;
  for (let i = 0; i < n; i++) z += h.w[i] * embQuery[i] + h.w[n + i] * embText[i];
  return 1 / (1 + Math.exp(-z));
}

/** health13 learned card picker: a linear head (33 classes = the cards + snakebite + NONE) on the SAME raw mean-pooled vector
 *  the detector reads, so it costs one 384x33 matvec. Returns the top class and its softmax probability. */
export type CardHead = { kind: "card-linear"; classes: string[]; W: number[][]; b: number[] };
export function cardTop(h: CardHead, pooled: ArrayLike<number>): { key: string; p: number } {
  if (pooled.length !== h.W[0].length) throw new Error(`card picker: embedding length ${pooled.length} != ${h.W[0].length}`);
  const z = h.W.map((w, k) => { let a = h.b[k]; for (let i = 0; i < w.length; i++) a += w[i] * pooled[i]; return a; });
  const m = Math.max(...z); const e = z.map((v) => Math.exp(v - m)); const sum = e.reduce((a, b) => a + b, 0);
  let k = 0; for (let i = 1; i < e.length; i++) if (e[i] > e[k]) k = i;
  return { key: h.classes[k], p: e[k] / sum };
}

