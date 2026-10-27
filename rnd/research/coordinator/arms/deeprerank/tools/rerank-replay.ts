/**
 * rerank-replay: what a cross-encoder rerank over the engine's top-N retrieval candidates would change, with no LLM
 * generation and no judge (DEEPRERANK step 0, HANDOFF-2026-10-11 §4 step 4).
 *
 * USAGE (from anywhere; the .sh wrapper picks boar-eval's tsx):
 *   rnd/research/coordinator/arms/deeprerank/tools/rerank-replay.sh \
 *     [--questions boar-eval/bench/v0.1/questions.public.jsonl] [--gold boar-eval/bench/v0.1/gold/sources.json] \
 *     [--tree wt/cut7] [--ids a,b] [--k 6,4] [--topk 20] [--out f.jsonl] [--agg f.json] [--tau 0.05] \
 *     [--server-url http://127.0.0.1:8097 | --port 8097] [--server-bin <llama-server>] [--reranker <gguf>] \
 *     [--doc-chars 2000] [--threads 4] [--packs a.sqlite,b.sqlite] [--corpus essential|bundled] [--gate rules|search]
 *
 * WHAT IT RUNS
 *   - The engine's own createAnswerer(...).answer() configured as the DEEP tier of the desktop-node adapter's
 *     `--deep-model` runs (runner/adapter.ts l.655-662 + 740-745): two installed LLMs (the 4B active, a deep model with
 *     roles ["reasoning"]), settings {quickFirst: true, alwaysComplete: true, deepModelId} -> planAnswer's deep branch
 *     (retrieveK = DEEP_RETRIEVE_K = 6). Generation is stubbed (throws right after retrieval). Default gate "rules"
 *     (no nextTokenProbs) = the deep runs' server backend, which is gate-less. Detector: the engine's lexical predicate
 *     (no learned detector), as replay-retrieval.ts's default.
 *   - At the engine's retrieve(q, k) call: Rt.retrieve(q, topk) = the candidate pool (text = chunk.body, which the
 *     engine's RetrievedChunk carries: no SQLite lookup needed), plus Rt.retrieve(q, k) for every --k (the engine's
 *     real top-k = baseline). Only the first retrieve call per item is used.
 *   - The pool is scored against the engine's search query by bge-reranker-v2-m3 through llama-server --rerank
 *     (POST /rerank, {query, documents}); document = title + "\n" + body, cut to --doc-chars. Reranked top-k = the k
 *     highest-scoring candidates of the pool (ties -> original rank). Scores: raw logit and sigmoid.
 *
 * SETUP: setup() is copied from boar-eval/adapters/desktop-node/tools/replay-retrieval.ts l.148-230 (that file runs
 * main() on import and exports nothing), with the cache dir defaulting to this arm's cache/ (BOAR_REPLAY_CACHE) so
 * nothing under boar-eval/ is written.
 *
 * OUTPUT: --out JSONL, one line per item: {id, task, tier, query, engineK, pool: [{rank, title, section, via, sim,
 * score, p}], base: {k: titles}, poolHead: {k: titles}, rr: {k: titles}, added/removed per k, gold?, recall per k,
 * rrMs, retrieveMs}; no passage text. stderr: summary table; --agg: aggregate JSON.
 */
import { createHash } from "node:crypto";
import { spawn, type ChildProcess } from "node:child_process";
import { createReadStream, existsSync, mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync, appendFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const ARM = resolve(HERE, "..");
const BOAR = resolve(HERE, "../../../../../..");
const ADAPTER = join(BOAR, "boar-eval/adapters/desktop-node");
const SHARED_MODELS = process.env.BOAR_SHARED_MODELS ?? join(BOAR, "shared-models");
const LLAMA_NODE_MODULES = process.env.BOAR_REPLAY_NODE_MODULES ?? join(BOAR, "wt/eval/eval/node_modules");
const CACHE = process.env.BOAR_REPLAY_CACHE ?? join(ARM, "cache");
const EMBED_FILE = "bge-small-en-v1.5-q8_0.gguf";
const EMBED_SHA256 = "ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514";
const RERANKER_SHA256 = "e186a244ed455b4ab66ec64339ce7427a6ae13f5c0b5e544de96e50f0f8b3673";
const DEFAULT_SERVER_BIN =
  "<scratch>";
const DEEP_ID = "qwen3.6-35b-a3b-ud-q2kxl"; // the deep runs' --deep-model id (DT512/DEEPVPARA criteria)

// ---------------------------------------------------------------- args
const argv = process.argv.slice(2);
const get = (k: string, d?: string) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
const abs = (p: string) => resolve(process.cwd(), p);
const cli = {
  tree: abs(get("--tree", join(BOAR, "wt/cut7"))!),
  questions: abs(get("--questions", join(BOAR, "boar-eval/bench/v0.1/questions.public.jsonl"))!),
  gold: abs(get("--gold", join(BOAR, "boar-eval/bench/v0.1/gold/sources.json"))!),
  ids: get("--ids")?.split(",").filter(Boolean),
  ks: get("--k", "6,4")!.split(",").map(Number),
  topk: Number(get("--topk", "20")),
  out: get("--out"),
  agg: get("--agg"),
  tau: get("--tau") ? Number(get("--tau")) : null,
  serverUrl: get("--server-url"),
  port: Number(get("--port", "8097")),
  serverBin: get("--server-bin", process.env.BOAR_RERANK_SERVER_BIN ?? DEFAULT_SERVER_BIN)!,
  reranker: abs(get("--reranker", join(SHARED_MODELS, "bge-reranker-v2-m3-q4km.gguf"))!),
  docChars: Number(get("--doc-chars", "2000")),
  threads: Number(get("--threads", "4")),
  packs: (get("--packs") ?? [join(BOAR, "shared-data/crypto/boar-crypto.sqlite"), join(BOAR, "shared-data/packs/boar-wikivoyage-en.sqlite")].join(","))
    .split(",").filter(Boolean).map(abs),
  corpus: get("--corpus", "essential") as "essential" | "bundled",
  gate: get("--gate", "rules") as "search" | "rules",
  modelId: get("--model", "qwen3-4b-instruct-2507-q4km")!,
  ramGb: Number(get("--ram-gb", "12")),
  platform: get("--platform", "android")!,
};
const log = (m: string) => console.error(`[rerank-replay] ${m}`);
const fail = (m: string): never => { log(`FATAL: ${m}`); process.exit(1); };
if (!cli.ks.length || cli.ks.some((k) => !(k > 0))) fail("--k must be a comma list of positive ints");
if (cli.ks.some((k) => k > cli.topk)) fail("--k larger than --topk");
const K0 = cli.ks[0];

// ---------------------------------------------------------------- items + gold (replay-retrieval.ts l.93-104, 136-146)
type Item = { id: string; question: string; history?: { turns: { role: string; text: string }[] } };
let items: Item[] = readFileSync(cli.questions, "utf8").split("\n").filter((l) => l.trim()).map((l) => {
  const r = JSON.parse(l);
  const it = r.item ?? r;
  return { id: it.id, question: it.question, ...(it.history ? { history: it.history } : {}) };
});
if (cli.ids) {
  const missing = cli.ids.filter((id) => !items.some((x) => x.id === id));
  if (missing.length) fail(`--ids not in questions: ${missing.join(",")}`);
  items = items.filter((x) => cli.ids!.includes(x.id));
}
const norm = (s: unknown) => String(s ?? "").split(/\s+/).filter(Boolean).join(" ").toLowerCase();
const LIB = /^[^:]{2,40}:\s+/;
const bare = (t: string) => String(t ?? "").replace(LIB, "");
function goldMatch(gold: string, ref: { title: string; section?: string | null }) {
  const i = gold.indexOf("#");
  const title = i < 0 ? gold : gold.slice(0, i), section = i < 0 ? "" : gold.slice(i + 1);
  if (norm(title) !== norm(ref.title) && (LIB.test(title) || norm(title) !== norm(bare(ref.title)))) return false;
  return !section || norm(section) === norm(ref.section);
}
const goldAll: Record<string, unknown> = existsSync(cli.gold) ? JSON.parse(readFileSync(cli.gold, "utf8")) : {};
if (!existsSync(cli.gold)) log(`no gold file ${cli.gold}: recall not computed`);

// ---------------------------------------------------------------- setup (copied from replay-retrieval.ts l.148-230)
async function sha256File(path: string) {
  const h = createHash("sha256");
  for await (const c of createReadStream(path)) h.update(c as Buffer);
  return h.digest("hex");
}

async function setup() {
  const T = cli.tree;
  if (!existsSync(join(T, "src/rag/retrieve.ts"))) fail(`--tree ${T}: no src/rag/retrieve.ts`);
  if (!existsSync(join(LLAMA_NODE_MODULES, "node-llama-cpp"))) fail(`no node-llama-cpp in ${LLAMA_NODE_MODULES} (set BOAR_REPLAY_NODE_MODULES)`);
  for (const p of cli.packs) if (!existsSync(p)) fail(`pack ${p} missing`);
  const embPath = join(SHARED_MODELS, EMBED_FILE);
  process.env.BOAR_EVAL_RAM_BYTES = String(Math.round(cli.ramGb * 1024 ** 3));
  process.env.BOAR_EVAL_PLATFORM = cli.platform;
  process.env.BOAR_APP_GPU = process.env.BOAR_APP_GPU ?? "1";

  const { registerHooks } = await import("node:module");
  const shim = (f: string) => pathToFileURL(join(ADAPTER, "runner/app-shims", f)).href;
  const SHIMS: Record<string, string> = {
    "expo-sqlite": shim("expo-sqlite.mjs"), "expo-file-system": shim("expo-file-system.mjs"),
    "expo-file-system/legacy": shim("expo-file-system.mjs"), "llama.rn": shim("llama-rn.mjs"),
    "react-native": shim("react-native.mjs"), "ram-monitor": shim("ram-monitor.mjs"),
  };
  const fallbackParent = pathToFileURL(join(LLAMA_NODE_MODULES, "_replay_.js")).href;
  (registerHooks as any)({
    resolve: (spec: string, ctx: any, next: any) => {
      if (SHIMS[spec]) return { url: SHIMS[spec], shortCircuit: true };
      try {
        return next(spec, ctx);
      } catch (e) {
        if (/^[./]/.test(spec) || spec.startsWith("node:")) throw e;
        return next(spec, { ...ctx, parentURL: fallbackParent });
      }
    },
  });

  const code = ["src/rag/seedCorpus.ts", "src/rag/db.ts", "src/rag/retrieve.ts", "src/rag/packs.ts", "src/models/manifest.ts"]
    .map((f) => (existsSync(join(T, f)) ? readFileSync(join(T, f), "utf8") : "")).join("\n");
  const key = createHash("sha256").update(code).update(cli.corpus).update(cli.packs.join(",")).digest("hex").slice(0, 16);
  const appDir = join(CACHE, "appdir", key);
  const fresh = !existsSync(join(appDir, "SQLite"));
  process.env.BOAR_APP_DIR = appDir;
  mkdirSync(join(appDir, "corpus"), { recursive: true });
  const manifest: any = await import(join(T, "src/models/manifest.ts"));
  const catalog: any[] = [...(manifest.MODEL_CATALOG ?? []), ...(manifest.CORPUS_CATALOG ?? [])];
  const link = (src: string, rel: string) => {
    const dst = join(appDir, rel);
    mkdirSync(dirname(dst), { recursive: true });
    rmSync(dst, { force: true });
    symlinkSync(src, dst);
  };
  const emb = catalog.find((m) => m.kind === "embedding" && m.required);
  link(embPath, emb.filename);
  if (cli.corpus === "essential") for (const id of ["corpus-standard", "corpus-full"]) {
    const entry = catalog.find((m) => m.id === id);
    if (!entry) fail(`catalog has no ${id}`);
    link(join(T, "assets/corpus", `${id}.json`), entry.filename);
  }
  for (const m of ["src/rag/cryptoPack.ts", "src/rag/preparedness.ts"]) if (existsSync(join(T, m))) await import(join(T, m));
  for (const p of cli.packs) {
    const id = p.split("/").pop()!.replace(/\.sqlite$/, "");
    link(p, catalog.find((m) => m.id === id)?.filename ?? `corpus/${id}.sqlite`);
  }
  const { embeddingEngine } = await import(join(T, "src/rag/embed.ts"));
  await embeddingEngine.load(emb.filename);
  const ts = performance.now();
  const { seedKnowledgeBaseIfEmpty } = await import(join(T, "src/rag/seedCorpus.ts"));
  await seedKnowledgeBaseIfEmpty();
  log(`app dir ${appDir} (${fresh ? "NEW: seed corpus indexed" : "cached"}) seed ${((performance.now() - ts) / 1000).toFixed(1)} s`);
  const lex: any = await import(join(T, "src/rag/ptLexiconAsset.ts"));
  if (!Object.keys(lex.ptLexicon() ?? {}).length) fail("LEXICON-NOT-LOADED");
  return { catalog };
}

// ---------------------------------------------------------------- reranker server
let child: ChildProcess | null = null;
let serverCmd = "";
async function startServer(): Promise<string> {
  if (cli.serverUrl) return cli.serverUrl.replace(/\/$/, "");
  if (!existsSync(cli.serverBin)) fail(`llama-server not found: ${cli.serverBin} (pass --server-bin or --server-url)`);
  const args = ["-m", cli.reranker, "--rerank", "--host", "127.0.0.1", "--port", String(cli.port), "-c", "8192", "-b", "8192",
                "-ub", "8192", "--parallel", "1", "-t", String(cli.threads), "--no-webui"];
  serverCmd = [cli.serverBin, ...args].join(" ");
  const url = `http://127.0.0.1:${cli.port}`;
  try { await fetch(`${url}/health`); fail(`port ${cli.port} already in use (pass --server-url to reuse it or --port)`); } catch { /* free */ }
  child = spawn(cli.serverBin, args, { stdio: ["ignore", "ignore", "ignore"] });
  process.on("exit", () => child?.kill("SIGTERM"));
  for (let i = 0; i < 120; i++) {
    await new Promise((r) => setTimeout(r, 500));
    try { if ((await fetch(`${url}/health`)).ok) return url; } catch { /* starting */ }
  }
  return fail("reranker server did not become healthy in 60 s");
}
async function rerank(url: string, query: string, docs: string[]): Promise<{ scores: number[]; ms: number; tokens: number }> {
  const t = performance.now();
  const r = await fetch(`${url}/rerank`, { method: "POST", headers: { "content-type": "application/json" },
                                          body: JSON.stringify({ query, documents: docs }) });
  if (!r.ok) fail(`/rerank HTTP ${r.status}: ${(await r.text()).slice(0, 200)}`);
  const j: any = await r.json();
  const ms = performance.now() - t;
  const scores = new Array(docs.length).fill(NaN);
  for (const x of j.results ?? []) scores[x.index] = x.relevance_score;
  if (scores.some((s) => !Number.isFinite(s))) fail("/rerank returned no score for some document");
  return { scores, ms, tokens: j.usage?.prompt_tokens ?? 0 };
}

// ---------------------------------------------------------------- main
type Ref1 = { title: string; section: string | null; via: string | null; sim: number | null };
const refOf = (c: any): Ref1 => ({
  title: String(c.title ?? ""), section: typeof c.section === "string" ? c.section : null, via: c.matchType ?? null,
  sim: typeof c.similarity === "number" && Number.isFinite(c.similarity) ? +c.similarity.toFixed(4) : null,
});
const sig = (x: number) => 1 / (1 + Math.exp(-x));
const q = (a: number[], p: number) => {
  if (!a.length) return null;
  const s = [...a].sort((x, y) => x - y), i = (s.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i);
  return +(s[lo] + (s[hi] - s[lo]) * (i - lo)).toFixed(4);
};
const mean = (a: number[]) => (a.length ? +(a.reduce((s, x) => s + x, 0) / a.length).toFixed(4) : null);

async function main() {
  const t0 = performance.now();
  const rrSha = await sha256File(cli.reranker);
  if (rrSha !== RERANKER_SHA256) log(`WARNING: reranker sha256 ${rrSha} != ${RERANKER_SHA256}`);
  const url = await startServer();
  const { catalog } = await setup();
  const T = cli.tree;
  const A: any = await import(join(T, "src/routing/answer.ts"));
  const pure: any = await import(join(T, "src/rag/pure.ts"));
  const Rt: any = await import(join(T, "src/rag/retrieve.ts"));
  const PL: any = await import(join(T, "src/rag/ptLexicon.ts"));
  const PLA: any = await import(join(T, "src/rag/ptLexiconAsset.ts"));
  const LE: any = await import(join(T, "src/inference/LlamaEngine.ts"));
  const PERS: any = await import(join(T, "src/constants/personalities.ts"));
  const entry = catalog.find((m) => m.id === cli.modelId) ?? fail(`model ${cli.modelId} not in the tree's catalog`);
  // runner/adapter.ts l.655-662: fast model active with roles ["fast"], deep model roles ["reasoning"].
  const llm = { id: entry.id, label: entry.label, filename: entry.filename, sizeBytes: entry.sizeBytes ?? 0,
                roles: ["fast"], isDefault: true, answerTier: entry.answerTier };
  const deepLlm = { id: DEEP_ID, label: "Qwen3.6 35B-A3B", filename: "Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf", sizeBytes: 0,
                    roles: ["reasoning"], isDefault: false, answerTier: undefined };
  const p = PERS.getPersonality(PERS.DEFAULT_PERSONALITY_ID ?? "succinct");
  const ctx0 = { systemPrompt: p.systemPrompt, styleReminder: p.styleReminder, maxTokens: 512 };

  let calls: { query: string; k: number; pool: any[]; base: Record<number, any[]>; ms: number }[] = [];
  const NO_GEN = "rerank-replay: generation stubbed out";
  let loaded: string | null = null;
  const engine: any = {
    async load(filename: string) { loaded = filename; return { fit: null, warning: null }; },
    async stop() {},
    getModelInfo: () => (loaded ? { filename: loaded } : null),
    hasEmbeddedChatTemplate: () => true,
    async estimateFit() { return null; },
    setAnswerPrefix() {},
    async generate() { throw new Error(NO_GEN); },
  };
  if (cli.gate === "search") engine.nextTokenProbs = async () => [{ token: "SEARCH", prob: 1 }, { token: "ANS", prob: 0 }];
  const answerer = A.createAnswerer({
    engine,
    retrieve: async (qq: string, k: number) => {
      const t = performance.now();
      const pool = await Rt.retrieve(qq, cli.topk);
      const ms = performance.now() - t;
      const base: Record<number, any[]> = {};
      for (const kk of cli.ks) base[kk] = await Rt.retrieve(qq, kk);
      calls.push({ query: qq, k, pool, base, ms });
      return pool;
    },
    knowledgeReady: async () => {},
    englishNames: (s: string) => PL.englishNamesIn(s, PLA.ptLexicon()),
    getSettings: async () => ({ quickFirst: true, alwaysComplete: true, deepModelId: DEEP_ID, largeModelConfirmedIds: [], loadCrashedIds: [] }),
    listInstalledLlms: async () => [llm, deepLlm],
    getActiveModelId: async () => llm.id,
    runMultipass: async () => { throw new Error(NO_GEN); },
    assemblePrompt: pure.assemblePrompt,
    assembleChatMessages: pure.assembleChatMessages,
    answerPrefix: pure.answerPromptPrefix,
    now: () => performance.now(),
    contextSize: LE.defaultContextSize,
    deviceRamBytes: () => Number(process.env.BOAR_EVAL_RAM_BYTES),
    getGeoProviders: () => null,
    getModelSpeeds: async () => new Map(),
    recordExecution: async () => {},
    memoryBytes: () => process.memoryUsage().rss,
  });

  if (cli.out) { mkdirSync(dirname(abs(cli.out)), { recursive: true }); writeFileSync(abs(cli.out), ""); }
  const emit = (o: unknown) => (cli.out ? appendFileSync(abs(cli.out), JSON.stringify(o) + "\n") : process.stdout.write(JSON.stringify(o) + "\n"));

  type Acc = { recBase: number[]; recRr: number[]; recHead: number[]; changed: string[]; enter: string[]; leave: string[];
               recUp: string[]; recDown: string[]; belowTau: string[]; minTopP: number[]; headDiffers: string[] };
  const acc: Record<number, Acc> = {};
  for (const k of cli.ks) acc[k] = { recBase: [], recRr: [], recHead: [], changed: [], enter: [], leave: [], recUp: [], recDown: [], belowTau: [], minTopP: [], headDiffers: [] };
  const rrMs: number[] = [], allP: number[] = [], topP: number[] = [], docChars: number[] = [];
  let retrieved = 0, goldItems = 0, emptyPool = 0, maxTok = 0;
  const engineKs = new Map<string, number>();
  const warn0 = console.warn, log0 = console.log;
  for (const it of items) {
    calls = []; loaded = null;
    let res: any = null;
    console.warn = () => {}; console.log = () => {};
    try {
      const ctx = it.history ? { ...ctx0, history: { summary: null, turns: it.history.turns } } : ctx0;
      res = await answerer.answer({ query: it.question }, () => {}, ctx).done;
    } catch { /* stubbed generation */ } finally { console.warn = warn0; console.log = log0; }
    const codes: string[] = res?.receipt?.reasonCodes ?? [];
    const task = codes.find((c) => c.startsWith("task:"))?.slice(5) ?? null;
    const c0 = calls[0];
    if (calls.length > 1) log(`${it.id}: ${calls.length} retrieve calls (only the first is used)`);
    const g = goldAll[it.id];
    const gold = Array.isArray(g) && g.length ? (g as string[]) : null;
    const line: any = { id: it.id, task, tier: res?.tier ?? null, query: c0?.query ?? null, engineK: c0?.k ?? null };
    if (!c0) { line.retrieved = false; emit(line); continue; }
    retrieved++;
    engineKs.set(String(c0.k), (engineKs.get(String(c0.k)) ?? 0) + 1);
    const pool = c0.pool.map(refOf);
    let scores: number[] = [], ms = 0;
    if (pool.length) {
      const docs = c0.pool.map((c: any) => `${c.title ?? ""}\n${String(c.body ?? "")}`.slice(0, cli.docChars));
      docs.forEach((d: string, i: number) => docChars.push(Math.min(String(c0.pool[i].body ?? "").length + String(c0.pool[i].title ?? "").length + 1, 1e9)));
      const r = await rerank(url, c0.query, docs);
      scores = r.scores; ms = r.ms; maxTok = Math.max(maxTok, r.tokens);
      rrMs.push(ms);
    } else emptyPool++;
    const order = pool.map((_: Ref1, i: number) => i).sort((a: number, b: number) => scores[b] - scores[a] || a - b);
    const probs = scores.map(sig);
    allP.push(...probs);
    if (probs.length) topP.push(Math.max(...probs));
    line.pool = pool.map((r: Ref1, i: number) => ({ rank: i + 1, ...r, score: +scores[i]?.toFixed(3), p: +probs[i]?.toFixed(4),
                                                   rrRank: order.indexOf(i) + 1 }));
    line.rrMs = +ms.toFixed(1); line.retrieveMs = +c0.ms.toFixed(1);
    line.base = {}; line.poolHead = {}; line.rr = {}; line.added = {}; line.removed = {};
    if (gold) { line.gold = gold; line.recall = {}; goldItems++; }
    for (const k of cli.ks) {
      const a = acc[k];
      const base = c0.base[k].map(refOf);
      const head = pool.slice(0, k);
      const rr = order.slice(0, k).map((i: number) => pool[i]);
      const key = (x: Ref1) => `${x.title}#${x.section ?? ""}`;
      const bset = new Set(base.map(key)), rset = new Set(rr.map(key));
      line.base[k] = base.map((x: Ref1) => x.title);
      line.poolHead[k] = head.map((x: Ref1) => x.title);
      line.rr[k] = rr.map((x: Ref1) => x.title);
      line.added[k] = rr.filter((x: Ref1) => !bset.has(key(x))).map((x: Ref1) => x.title);
      line.removed[k] = base.filter((x: Ref1) => !rset.has(key(x))).map((x: Ref1) => x.title);
      if (line.added[k].length || line.removed[k].length) a.changed.push(it.id);
      if (JSON.stringify(line.base[k]) !== JSON.stringify(line.poolHead[k])) a.headDiffers.push(it.id);
      const pk = order.slice(0, k).map((i: number) => probs[i]);
      if (pk.length) a.minTopP.push(Math.min(...pk));
      if (cli.tau !== null && !pk.some((x: number) => x >= cli.tau!)) a.belowTau.push(it.id);
      if (gold) {
        const fb = gold.filter((x) => base.some((r: Ref1) => goldMatch(x, r)));
        const fr = gold.filter((x) => rr.some((r: Ref1) => goldMatch(x, r)));
        const fh = gold.filter((x) => head.some((r: Ref1) => goldMatch(x, r)));
        const rb = fb.length / gold.length, rrr = fr.length / gold.length;
        a.recBase.push(rb); a.recRr.push(rrr); a.recHead.push(fh.length / gold.length);
        line.recall[k] = { base: +rb.toFixed(4), rr: +rrr.toFixed(4), poolHead: +(fh.length / gold.length).toFixed(4) };
        if (fr.some((x) => !fb.includes(x))) a.enter.push(it.id);
        if (fb.some((x) => !fr.includes(x))) a.leave.push(it.id);
        if (rrr > rb) a.recUp.push(it.id); else if (rrr < rb) a.recDown.push(it.id);
      }
    }
    if (gold) line.goldInPool = gold.filter((x) => pool.some((r: Ref1) => goldMatch(x, r))).length;
    emit(line);
  }

  const perK: any = {};
  for (const k of cli.ks) {
    const a = acc[k];
    perK[k] = {
      recallBase: mean(a.recBase), recallRerank: mean(a.recRr), recallPoolHead: mean(a.recHead),
      itemsChanged: a.changed.length, goldEnter: a.enter, goldLeave: a.leave, recallUp: a.recUp, recallDown: a.recDown,
      itemsEmptied: 0, // rerank re-orders a non-empty pool: top-k is empty only if the pool is (counted in emptyPool)
      baseNePoolHead: a.headDiffers.length,
      minTopkP: { p10: q(a.minTopP, 0.1), p50: q(a.minTopP, 0.5), p90: q(a.minTopP, 0.9) },
      ...(cli.tau !== null ? { allBelowTau: a.belowTau } : {}),
    };
  }
  const summary = {
    n: items.length, retrieved, goldItems, emptyPool, engineK: Object.fromEntries(engineKs), topk: cli.topk, ks: cli.ks, tau: cli.tau,
    perK,
    scoreP: { all: { p10: q(allP, 0.1), p50: q(allP, 0.5), p90: q(allP, 0.9) }, top1: { p10: q(topP, 0.1), p50: q(topP, 0.5), p90: q(topP, 0.9) } },
    rerankMs: { p50: q(rrMs, 0.5), p90: q(rrMs, 0.9), max: rrMs.length ? +Math.max(...rrMs).toFixed(1) : null },
    maxPromptTokensPerCall: maxTok, docCharsP90: q(docChars, 0.9), docCharsMax: docChars.length ? Math.max(...docChars) : null, docCharsCut: cli.docChars,
    reranker: { file: cli.reranker, sha256: rrSha, server: cli.serverUrl ?? serverCmd },
    tree: cli.tree, questions: cli.questions, gold: cli.gold, gate: cli.gate, detector: "lexical", tier: "deep (alwaysComplete + deepModelId)",
    totalSeconds: +((performance.now() - t0) / 1000).toFixed(1),
  };
  if (cli.agg) { mkdirSync(dirname(abs(cli.agg)), { recursive: true }); writeFileSync(abs(cli.agg), JSON.stringify(summary, null, 1) + "\n"); }
  console.error(JSON.stringify(summary, null, 1));
  child?.kill("SIGTERM");
  process.exit(0);
}

main().catch((e) => fail(String(e?.stack ?? e)));
