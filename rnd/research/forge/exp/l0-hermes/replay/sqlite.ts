// expo-sqlite replay: answers each call with the result the Node recorder logged for the same (db, method, sql, params).
// FIFO per key, the last result is reused once a queue is drained (repeat passes). Unrecorded calls (db migrations at
// getDb) get empty results and are counted in __N.sqlMiss. Time spent here is reported as "sql-replay" (not phone work).
import { now, T, N } from "./clock";
declare const globalThis: any;
const R = globalThis.__REPLAY as { q: Map<string, any[]>; last: Map<string, any> };
function answer(db: string, m: string, sql: string, p: any[]) {
  const t = now();
  const key = `${db}|${m}|${sql}|${JSON.stringify(p)}`;
  const q = R.q.get(key);
  let r: any;
  if (q && q.length) { r = q.shift(); R.last.set(key, r); }
  else if (R.last.has(key)) r = R.last.get(key);
  else { N.sqlMiss = (N.sqlMiss ?? 0) + 1; ((globalThis as any).__MISSES ??= []).push(key.slice(0, 160)); r = m === "all" ? [] : m === "first" ? null : m === "run" ? { changes: 0, lastInsertRowId: 0 } : null; }
  T.sqlReplay = (T.sqlReplay ?? 0) + now() - t; N.sqlCalls = (N.sqlCalls ?? 0) + 1;
  return r;
}
const params = (p: any[]) => (p.length === 0 ? [] : p.length > 1 ? p : Array.isArray(p[0]) ? p[0] : p[0] === undefined ? [] : [p[0]]);
function wrap(key: string): any {
  const api: any = {
    async execAsync(sql: string) { answer(key, "exec", sql, []); },
    async getAllAsync(sql: string, ...p: any[]) { return answer(key, "all", sql, params(p)); },
    async getFirstAsync(sql: string, ...p: any[]) { return answer(key, "first", sql, params(p)); },
    async runAsync(sql: string, ...p: any[]) { return answer(key, "run", sql, params(p)); },
    async withTransactionAsync(work: any) { await work(); },
    async withExclusiveTransactionAsync(work: any) { await work(api); },
    async prepareAsync() { return { async executeAsync() { return { changes: 0, lastInsertRowId: 0, async getAllAsync() { return []; } }; }, async finalizeAsync() {} }; },
    async closeAsync() {},
    closeSync() {},
  };
  return api;
}
const base = (name: string) => name.split("/").pop()!;
export async function openDatabaseAsync(name: string) { return wrap(base(name)); }
export function openDatabaseSync(name: string) { return wrap(base(name)); }
export async function deleteDatabaseAsync() {}
export type SQLiteDatabase = any;
export default { openDatabaseAsync, openDatabaseSync, deleteDatabaseAsync };
