// expo-sqlite on node:sqlite (from boar-eval desktop-node app-shims) + a recorder: while globalThis.__REC.on, every
// call's (db, method, sql, params) and result are logged, so the Hermes replay can return the same rows without SQLite.
import { DatabaseSync } from "node:sqlite";
import { mkdirSync, rmSync } from "node:fs";
import { dirname, isAbsolute, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = process.env.BOAR_APP_DIR;
const REC = (globalThis.__REC ??= { on: false, calls: [], sqlMs: 0 });
function log(key, method, sql, params, result) {
  if (REC.on) REC.calls.push({ db: key, m: method, sql, p: params, r: result });
  return result;
}
function pathFor(name, directory) {
  const n = name.startsWith("file://") ? fileURLToPath(name) : name;
  if (isAbsolute(n)) return n;
  const dir = directory ? (directory.startsWith("file://") ? fileURLToPath(directory) : directory) : join(ROOT, "SQLite");
  return join(dir, n);
}
function wrap(db, key = "?") {
  const params = (p) => (p === undefined ? [] : Array.isArray(p) ? p : [p]);
  const timed = (f) => { const t = performance.now(); try { return f(); } finally { REC.sqlMs += performance.now() - t; } };
  const api = {
    raw: db,
    async execAsync(sql) { timed(() => db.exec(sql)); log(key, "exec", sql, [], null); },
    async getAllAsync(sql, ...p) { const a = params(p.length > 1 ? p : p[0]); return log(key, "all", sql, a, timed(() => db.prepare(sql).all(...a))); },
    async getFirstAsync(sql, ...p) { const a = params(p.length > 1 ? p : p[0]); return log(key, "first", sql, a, timed(() => db.prepare(sql).get(...a) ?? null)); },
    async runAsync(sql, ...p) { const a = params(p.length > 1 ? p : p[0]); const r = timed(() => db.prepare(sql).run(...a)); return log(key, "run", sql, a, { changes: Number(r.changes), lastInsertRowId: Number(r.lastInsertRowid) }); },
    async withTransactionAsync(work) {
      db.exec("BEGIN");
      try { await work(); db.exec("COMMIT"); } catch (e) { db.exec("ROLLBACK"); throw e; }
    },
    async withExclusiveTransactionAsync(work) {
      db.exec("BEGIN EXCLUSIVE");
      try { await work(api); db.exec("COMMIT"); } catch (e) { db.exec("ROLLBACK"); throw e; }
    },
    async prepareAsync(sql) {
      const st = db.prepare(sql);
      return {
        async executeAsync(...p) { const r = st.run(...params(p.length > 1 ? p : p[0])); return { changes: Number(r.changes), lastInsertRowId: Number(r.lastInsertRowid), async getAllAsync() { return []; } }; },
        async finalizeAsync() {},
      };
    },
    async closeAsync() { try { db.close(); } catch {} },
    closeSync() { try { db.close(); } catch {} },
  };
  return api;
}
export async function openDatabaseAsync(name, options, directory) {
  const path = pathFor(name, directory);
  mkdirSync(dirname(path), { recursive: true });
  return wrap(new DatabaseSync(path, options?.readOnly ? { readOnly: true } : {}), path.split("/").pop());
}
export function openDatabaseSync(name, options, directory) {
  const path = pathFor(name, directory);
  mkdirSync(dirname(path), { recursive: true });
  return wrap(new DatabaseSync(path), path.split("/").pop());
}
export async function deleteDatabaseAsync(name, directory) {
  const path = pathFor(name, directory);
  for (const f of [path, path + "-wal", path + "-shm", path + "-journal"]) rmSync(f, { force: true });
}
export default { openDatabaseAsync, openDatabaseSync, deleteDatabaseAsync };
