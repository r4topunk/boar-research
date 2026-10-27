// Stage clock shared by the replay shims: performance.now() where it exists (Node), Date.now() under the Hermes CLI
// (ms ticks; summed over many intervals the error averages out).
declare const globalThis: any;
export const now: () => number = typeof performance !== "undefined" && performance.now ? () => performance.now() : () => Date.now();
export const T: Record<string, number> = (globalThis.__T ??= {});
export const N: Record<string, number> = (globalThis.__N ??= {});
export function timed<R>(key: string, f: () => R): R {
  const t = now();
  try { return f(); } finally { T[key] = (T[key] ?? 0) + now() - t; N[key] = (N[key] ?? 0) + 1; }
}
