/** QWRITE step 0 copy of h8st/tools/replay-h8.ts (changes marked "QW"): --qmap <json {id: query}>; mode "qw" replaces the query of the
 * FIRST retrieve() call and of the --pool extra retrieve with the item's rewritten query; everything else keeps the engine's own query. */
/** H8-ST step 0 copy of arms/packs/tk2-replay/tools/replay-tk2.ts (changes marked "H8"): BOAR root 6 levels up;
 * --modes off,lead,off : "lead" sets process.env.BOAR_H8_INDEX = "lead" for the item (the tree's wikiPack.ts then matches
 * against the copy's fts_h8 = same index + the article's first sentence); any other mode deletes it (setting absent). */
/** TK2-REPLAY copy of arms/groundst/tools/replay-gs.ts (changes marked "TK2"): BOAR root 7 levels up; the first
 * engine.generate() call's prompt (opts.prompt, else JSON of opts.messages) is recorded as `prompt` + `promptSha`. */
/**
 * GROUND-ST step 0 copy of arms/densechunk-st/tools/replay-st.ts (changes marked "GST"):
 *   --modes off,ground,top1,off : "ground" = getSettings adds {packGround: true}, "top1" = {packGround: "top1"},
 *                          "perpack" = {packGround: "perpack"} (addendum 1, X3), "off" =
 *                          setting absent (packDense2 / packRoute never set). Each line adds `keepCodes` (the engine's
 *                          packground:* reasonCodes) and, on "off"-mode lines, `diag` = a replay-side reconstruction of the
 *                          OFF keep stages with the tree's context.ts functions: sub (isSubstantive), comp (compressContext
 *                          at the engine's fast-tier budget: max(256, min(quickBudget(task).contextTokens, ctx - 512 - 512 -
 *                          FAST_THINKING_BUDGET)), pinned identifiers), ground (onTopic(matchQuery) on comp; matchQuery =
 *                          the search query without the " what to do" suffix when the engine rewrote the question, else the
 *                          question); chunkIds only (no text). `diag.agree` = ground ids == the engine's kept ids (non-health);
 *                          `diag.health` = grounding:health-strict in the codes (the health filter replaces grounding).
 *   `keepMs` (addendum 1): engine wall time from the first retrieve() return to the sources event (or the stubbed generate
 *                          call / the answer settling when no sources are emitted) = the keep step (substantive filter,
 *                          compressContext, packGround re-compression, grounding, health filter) measured in the engine.
 */
/**
 * DENSECHUNK-ST step 0 copy of arms/packs/tools/replay-crowd.ts (changes marked "DCST"):
 *   --modes off,on[,off] : passes over all items in one process; "on" = getSettings adds {packDense2: true}, "extra" =
 *                          {packDense2: "extra"} (DENSECHUNK-ST2) (the
 *                          wt/packs packDense2 setting), "off" = setting absent. Each output line carries `mode`.
 *   refs add `chunkId` (pack:<id>:<chunk id>) and `sim`; `dense` = the WikiPack.denseScans entries of the item's
 *                          retrieve (lead scan ms, chunk scan ms, candidates, kept, first-load ms).
 *   --gold none skips gold. Blind-safe stderr: errors print the item id only.
 */
/**
 * T-K4a (arms/packs) copy of arms/packcond/tools/replay-pg.ts; only change: refOf adds `pack` = the pack id in the
 * chunkId ("pack:<id>:...") or "seed" (essential/bundled corpus), so kept/raw slots are attributed to their pack.
 */
/**
 * PACKCOND P4 copy of arms/deepcovfb/tools/replay-deep.ts (changes marked "PACKCOND"):
 *   --pack-ground : getSettings adds {packGround: true} (the wt/packcond lever; absent = setting undefined).
 *   --diag        : per item, a replay-side reconstruction of the grounding stages from the first retrieve call's
 *                   chunks with the tree's own context.ts functions: sub (isSubstantive), comp (compressContext,
 *                   budget --budget, default 400 = DEEP_CONTEXT_TOKENS, pinned identifiers), ground (onTopic(query)
 *                   on comp); `diag.agree` = ground titles+sections == the engine's sources event. Valid for English
 *                   non-health, non-history questions (matchQuery = the question); others are flagged.
 */
/**
 * DEEPCOV-FB copy of boar-eval/adapters/desktop-node/tools/replay-retrieval.ts (unchanged except where marked "DEEPCOVFB"):
 *   --deep      : engine configured as the deep tier of the adapter's --deep-model runs (same as arms/deeprerank/tools/
 *                 rerank-replay.ts: fast 4B roles ["fast"] + deep model roles ["reasoning"], settings {quickFirst: true,
 *                 alwaysComplete: true, deepModelId}); planAnswer's deep branch -> k = DEEP_RETRIEVE_K 6, ctx 400.
 *   --pool N    : an extra Rt.retrieve(query, N) per retrieving item, recorded as `pool` (not returned to the engine).
 *   output adds `codes` (receipt reasonCodes from the done event) and `kept` [{title, section, source}] of the sources event.
 */
/**
 * replay-retrieval: BOAR's real retrieval, no LLM, no judge, on the MacBook in seconds.
 *
 * USAGE (from anywhere; the .sh wrapper picks tsx and the node-llama-cpp install):
 *   boar-eval/adapters/desktop-node/tools/replay-retrieval.sh \
 *     --questions boar-eval/bench/v0.1/questions.public.jsonl \
 *     [--tree wt/detmax] [--ids a,b] [--topk N] [--out f.jsonl] [--compress] \
 *     [--tasks-from <ref traces.jsonl>] [--gate search|rules] [--gold bench/v0.1/gold/sources.json] [--k 5] \
 *     [--packs a.sqlite,b.sqlite] [--corpus essential|bundled] [--cpu-embed] [--verify-sha]
 *
 * WHAT IT RUNS: the engine's own `createAnswerer(...).answer()` (src/routing/answer.ts) with the same shims as the
 * desktop-node adapter (runner/app-shims: expo-sqlite -> node:sqlite, expo-file-system -> fs, llama.rn embeddings ->
 * node-llama-cpp bge-small), so the search query (answer.ts `searchQuery`: PT->EN terms, canonical health terms,
 * "what to do" suffix), k (planAnswer's retrieveK per task: lookup 3, others 4, deep 6) and the skip rules
 * (instant/places/calculator/small talk never retrieve) are the engine's, not a re-implementation. The LLM is a stub:
 * `generate` throws right after retrieval, so nothing is generated. `retrieve()` (src/rag/retrieve.ts) is the
 * engine's single retrieve dependency, wrapped exactly as runner/adapter.ts wraps it (Rt.retrieve(q, k), no opts).
 *
 * WHAT NEEDS A MODEL, AND HOW IT IS REPLACED:
 *   - Route gate (4B next-token SEARCH/ANS; only when the rules do not skip it). Default `--gate search`: the gate says
 *     SEARCH every time it is asked (what the 4B said on all 24 gated v0.1 items of ctl-v01-s44). `--gate rules`: no gate
 *     (rule task type only: a rule type that skips retrieval, e.g. conversation/greeting, is not turned into "chat";
 *     identical to `search` on v0.1). `--tasks-from`: per item, the
 *     decision and score in the reference trace's reasonCodes (route-gate:search|answer|unavailable, score-x).
 *   - Learned emergency detector (mmBERT on a llama-server; changes `health`, hence the search query and the k
 *     floor). Default: absent -> the engine's lexical predicate. `--tasks-from`: the trace's `detector:p=x` (+
 *     `detector:fire`) is returned as the detector's score for that item; items without one get no detector.
 *
 * OUTPUT: one JSON line per item (stdout, or --out):
 *   {id, task, tier, query, k, raw: [{title, section, source, similarity, via}], sources: [titles of the engine's
 *    pre-answer `sources` event (after compressContext + grounding)], pre?: [compressForAnswer kept titles],
 *    ms (retrieve() wall time), ref?: {task, query, k, raw: [titles], same}}
 * then a summary on stderr: n, retrieved items, recall@k vs gold (scorers/retrieval.py rule), identical-raw count vs
 * --tasks-from, total seconds.
 *
 * CACHE: the app dir (knowledge-base SQLite with the bundled + essential seed corpus embedded, symlinked packs and
 * embedding model) lives in boar-eval/runs/replay-cache/appdir/<key>; key = sha of the tree's seed/db/retrieve/packs/
 * manifest code + corpus mode + pack paths. First run per key indexes the seed corpus (timed, printed).
 *
 * Writes nothing outside --out and the cache dir. No network.
 *
 * VALIDATION (2026-10-06, MacBook M1 Ultra, wt/detmax 5e5567ca = 0cfd4a77 + detmax patch 824e0b35): all 60 v0.1 items vs
 * runs/kiln/cryptotruth/ctl-v01-s44.traces.jsonl: identical ordered raw titles 60/60 (also 60/60 without --tasks-from),
 * same query/k/task 60/60, recall@5 0.3333 over 39 gold items (= scorers/retrieval.py on the reference). The engine's
 * `sources` list matches 57/60; the 3 others are food-* places answers (POI packs are not wired: getGeoProviders null;
 * retrieve() is never called on that path). Full run: ~7 s warm; first run per cache key +61 s to index the seed corpus.
 * Limits: title match uses toLowerCase (python casefold differs only on rare Unicode); only the first retrieve call
 * per item is reported (answer.ts makes one); multi-turn `history` is passed as the adapter does.
 */
import { createHash } from "node:crypto";
import { createReadStream, existsSync, mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync, appendFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const BOAR = resolve(HERE, "../../../../../.."); // H8
const ADAPTER = join(BOAR, "boar-eval/adapters/desktop-node"); // DEEPCOVFB
const SHARED_MODELS = process.env.BOAR_SHARED_MODELS ?? join(BOAR, "shared-models");
const LLAMA_NODE_MODULES = process.env.BOAR_REPLAY_NODE_MODULES ?? join(BOAR, "wt/eval/eval/node_modules");
const CACHE = process.env.BOAR_REPLAY_CACHE ?? join(BOAR, "boar-eval/runs/replay-cache");
const EMBED_FILE = "bge-small-en-v1.5-q8_0.gguf";
const EMBED_SHA256 = "ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514";

// ---------------------------------------------------------------- args
const argv = process.argv.slice(2);
const get = (k: string, d?: string) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
const abs = (p: string) => resolve(process.cwd(), p);
const cli = {
  tree: abs(get("--tree", join(BOAR, "wt/detmax"))!),
  questions: get("--questions"),
  ids: get("--ids")?.split(",").filter(Boolean),
  topk: get("--topk") ? Number(get("--topk")) : null,
  out: get("--out"),
  compress: argv.includes("--compress"),
  tasksFrom: get("--tasks-from"),
  gate: get("--gate", "search") as "search" | "rules",
  gold: get("--gold", join(BOAR, "boar-eval/bench/v0.1/gold/sources.json"))!,
  k: Number(get("--k", "5")),
  packs: (get("--packs") ?? [join(BOAR, "shared-data/crypto/boar-crypto.sqlite"), join(BOAR, "shared-data/packs/boar-wikivoyage-en.sqlite")].join(","))
    .split(",").filter(Boolean).map(abs),
  corpus: get("--corpus", "essential") as "essential" | "bundled",
  cpuEmbed: argv.includes("--cpu-embed"),
  verifySha: argv.includes("--verify-sha"),
  modelId: get("--model", "qwen3-4b-instruct-2507-q4km")!,
  ramGb: Number(get("--ram-gb", "12")),
  platform: get("--platform", "android")!,
  deep: argv.includes("--deep"), // DEEPCOVFB
  pool: get("--pool") ? Number(get("--pool")) : 0, // DEEPCOVFB
  packGround: argv.includes("--pack-ground"), // PACKCOND
  diag: argv.includes("--diag"), // PACKCOND
  budget: Number(get("--budget", "400")), // PACKCOND
  modes: get("--modes", "off")!.split(","), // DCST
  qvec: argv.includes("--qvec"), // DCST: engine query vector (float32 base64) on the first pass
  qmap: get("--qmap") ? JSON.parse(readFileSync(get("--qmap")!, "utf8")) : null, // QW
};
const fail = (m: string): never => { console.error(`[replay] FATAL: ${m}`); process.exit(1); };
if (!cli.questions) fail("--questions <jsonl> is required");
if (cli.gate !== "search" && cli.gate !== "rules") fail("--gate must be search or rules");
const log = (m: string) => console.error(`[replay] ${m}`);

// ---------------------------------------------------------------- items + reference
type Item = { id: string; question: string; history?: { turns: { role: string; text: string }[] } };
let items: Item[] = readFileSync(abs(cli.questions!), "utf8").split("\n").filter((l) => l.trim()).map((l) => {
  const r = JSON.parse(l);
  const it = r.item ?? r; // EvalRequest lines or plain question lines
  return { id: it.id, question: it.question, ...(it.history ? { history: it.history } : {}) };
});
if (cli.ids) {
  const missing = cli.ids.filter((id) => !items.some((x) => x.id === id));
  if (missing.length) fail(`--ids not in questions: ${missing.join(",")}`);
  items = items.filter((x) => cli.ids!.includes(x.id));
}

type Ref = { task: string | null; codes: string[]; raw: string[]; query: string | null; k: number | null; kit: string[] };
const refs = new Map<string, Ref>();
if (cli.tasksFrom) {
  for (const l of readFileSync(abs(cli.tasksFrom), "utf8").split("\n")) {
    if (!l.trim()) continue;
    const t = JSON.parse(l);
    const ev = (t.events ?? []).filter((e: any) => e.type === "retrieve");
    refs.set(t.itemId, {
      task: t.route?.task ?? null, codes: t.route?.reasonCodes ?? [], raw: (t.retrieval?.raw ?? []).map((r: any) => r.title),
      query: ev[0]?.query ?? null, k: ev[0]?.k ?? null, kit: (t.config?.kit ?? []).map((p: any) => p.id),
    });
  }
  const kits = new Set([...refs.values()].map((r) => r.kit.slice().sort().join(",")));
  const ours = cli.packs.map((p) => p.split("/").pop()!.replace(/\.sqlite$/, "")).sort().join(",");
  if (kits.size === 1 && !kits.has(ours)) log(`WARNING: reference kit ${[...kits][0]} != --packs ${ours}`);
}
/** Gate verdict for an item from its reference reasonCodes: probabilities that give the same decision and score. */
function refGateProbs(r: Ref | undefined): { token: string; prob: number }[] | null {
  if (!r) return null;
  const d = r.codes.find((c) => c === "route-gate:search" || c === "route-gate:answer");
  if (!d) return null; // unavailable / never asked -> null -> the rules
  const s = Number(r.codes.find((c) => c.startsWith("route-gate:score-"))?.slice("route-gate:score-".length));
  const score = Number.isFinite(s) ? s : d.endsWith("search") ? 1 : 0;
  return [{ token: "SEARCH", prob: score }, { token: "ANS", prob: 1 - score }];
}
function refDetector(r: Ref | undefined): { p: number; fire: boolean } | null {
  const c = r?.codes.find((x) => x.startsWith("detector:p="));
  return c ? { p: Number(c.slice("detector:p=".length)), fire: r!.codes.includes("detector:fire") } : null;
}

// ---------------------------------------------------------------- gold (scorers/retrieval.py rule)
const norm = (s: unknown) => String(s ?? "").split(/\s+/).filter(Boolean).join(" ").toLowerCase();
const LIB = /^[^:]{2,40}:\s+/;
const bare = (t: string) => String(t ?? "").replace(LIB, "");
function goldMatch(gold: string, ref: { title: string; section?: string | null }) {
  const i = gold.indexOf("#");
  const title = i < 0 ? gold : gold.slice(0, i), section = i < 0 ? "" : gold.slice(i + 1);
  if (norm(title) !== norm(ref.title) && (LIB.test(title) || norm(title) !== norm(bare(ref.title)))) return false;
  return !section || norm(section) === norm(ref.section);
}
const gold: Record<string, string[]> = existsSync(cli.gold) ? JSON.parse(readFileSync(cli.gold, "utf8")) : {};

// ---------------------------------------------------------------- shims (runner/adapter.ts setupAppRetrieval, same files)
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
  if (cli.verifySha) {
    const got = await sha256File(embPath);
    if (got !== EMBED_SHA256) fail(`embedding sha256 ${got}`);
    for (const p of cli.packs) log(`pack ${p.split("/").pop()} sha256 ${(await sha256File(p)).slice(0, 12)}`);
  }
  process.env.BOAR_EVAL_RAM_BYTES = String(Math.round(cli.ramGb * 1024 ** 3));
  process.env.BOAR_EVAL_PLATFORM = cli.platform;
  process.env.BOAR_APP_GPU = cli.cpuEmbed ? "0" : process.env.BOAR_APP_GPU ?? "1";

  const { registerHooks } = await import("node:module");
  const shim = (f: string) => pathToFileURL(join(ADAPTER, "runner/app-shims", f)).href;
  const SHIMS: Record<string, string> = {
    "expo-sqlite": shim("expo-sqlite.mjs"), "expo-file-system": shim("expo-file-system.mjs"),
    "expo-file-system/legacy": shim("expo-file-system.mjs"), "llama.rn": shim("llama-rn.mjs"),
    "react-native": shim("react-native.mjs"), "ram-monitor": shim("ram-monitor.mjs"),
  };
  // Bare specifiers the shims need (node-llama-cpp) resolve from the eval install (same 3.21.1 as the mini runner).
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
  const tl = performance.now();
  await embeddingEngine.load(emb.filename);
  const loadMs = performance.now() - tl;
  const ts = performance.now();
  const { seedKnowledgeBaseIfEmpty } = await import(join(T, "src/rag/seedCorpus.ts"));
  await seedKnowledgeBaseIfEmpty();
  const seedMs = performance.now() - ts;
  log(`app dir ${appDir} (${fresh ? "NEW: seed corpus indexed" : "cached"}) embed load ${Math.round(loadMs)} ms, seed ${(seedMs / 1000).toFixed(1)} s`);
  const lex: any = await import(join(T, "src/rag/ptLexiconAsset.ts"));
  if (!Object.keys(lex.ptLexicon() ?? {}).length) fail("LEXICON-NOT-LOADED");
  return { catalog };
}

// ---------------------------------------------------------------- main
type Ref1 = { chunkId?: string; title: string; section: string | null; source: string | null; similarity: number | null; via: string | null; pack: string };
const refOf = (c: any): Ref1 => ({
  chunkId: String(c.chunkId ?? ""), // DCST
  pack: /^pack:([^:]+):/.exec(String(c.chunkId ?? ""))?.[1] ?? "seed", // T-K4a: originating pack id (chunkId prefix)
  title: String(c.title ?? ""), section: typeof c.section === "string" ? c.section : null, source: typeof c.source === "string" ? c.source : null,
  similarity: typeof c.similarity === "number" && Number.isFinite(c.similarity) ? +c.similarity.toFixed(4) : null, via: c.matchType ?? null,
});

async function main() {
  const t0 = performance.now();
  const { catalog } = await setup();
  const T = cli.tree;
  const A: any = await import(join(T, "src/routing/answer.ts"));
  const pure: any = await import(join(T, "src/rag/pure.ts"));
  const Rt: any = await import(join(T, "src/rag/retrieve.ts"));
  const PL: any = await import(join(T, "src/rag/ptLexicon.ts"));
  const PLA: any = await import(join(T, "src/rag/ptLexiconAsset.ts"));
  const LE: any = await import(join(T, "src/inference/LlamaEngine.ts"));
  const PERS: any = await import(join(T, "src/constants/personalities.ts"));
  const CMP: any = cli.compress ? await import(join(T, "src/rag/compress.ts")) : null;
  const CTX: any = await import(join(T, "src/routing/context.ts")); // PACKCOND
  const DEP: any = await import(join(T, "src/routing/depth.ts")); // GST
  const WP: any = await import(join(T, "src/rag/wikiPack.ts")); // DCST: same module instance as retrieve.ts's
  let mode = "off"; // DCST
  let tRet: number | null = null, tEnd: number | null = null; // GST: keep step = first retrieve return -> sources event / generate / settle
  let keptTok = 0; // GST
  let genPrompt: string | null = null; // TK2: approxTokens of the sources event (title + body), as compressContext counts
  const EMB: any = await import(join(T, "src/rag/embed.ts")); // DCST
  const entry = catalog.find((m) => m.id === cli.modelId);
  if (!entry) fail(`model ${cli.modelId} not in the tree's catalog`);
  const llm = { id: entry.id, label: entry.label, filename: entry.filename, sizeBytes: entry.sizeBytes ?? 0,
                roles: entry.capabilities?.roles ?? ["fast"], isDefault: true, answerTier: entry.answerTier };
  const DEEP_ID = "qwen3.6-35b-a3b-ud-q2kxl"; // DEEPCOVFB: deeprerank's DEEP_ID
  if (cli.deep) llm.roles = ["fast"];
  const deepLlm = { id: DEEP_ID, label: "Qwen3.6 35B-A3B", filename: "Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf", sizeBytes: 0,
                    roles: ["reasoning"], isDefault: false, answerTier: undefined };
  const p = PERS.getPersonality(PERS.DEFAULT_PERSONALITY_ID ?? "succinct");
  const ctx0 = { systemPrompt: p.systemPrompt, styleReminder: p.styleReminder, maxTokens: 512 };

  // Per-item recorders.
  let cur: Item | null = null;
  let curMode = "off"; let engineQ: string | null = null; // QW
  let calls: { query: string; k: number; chunks: any[]; ms: number }[] = [];
  let sourcesEv: string[] | null = null;
  let keptEv: any[] | null = null, doneCodes: string[] | null = null, poolCh: any[] | null = null; // DEEPCOVFB
  const NO_GEN = "replay: generation stubbed out";
  let loaded: string | null = null;
  const engine: any = {
    async load(filename: string) { loaded = filename; return { fit: null, warning: null }; },
    async stop() {},
    getModelInfo: () => (loaded ? { filename: loaded } : null),
    hasEmbeddedChatTemplate: () => true,
    async estimateFit() { return null; },
    setAnswerPrefix() {},
    async generate(o: any) { if (tEnd === null) tEnd = performance.now(); if (genPrompt === null) genPrompt = typeof o?.prompt === "string" ? o.prompt : JSON.stringify(o?.messages ?? null); throw new Error(NO_GEN); }, // GST + TK2
  };
  if (cli.tasksFrom || cli.gate === "search")
    engine.nextTokenProbs = async () =>
      cli.tasksFrom ? refGateProbs(refs.get(cur!.id)) : [{ token: "SEARCH", prob: 1 }, { token: "ANS", prob: 0 }];
  const deps: any = {
    engine,
    retrieve: async (q: string, k: number, o?: any) => {
      const t = performance.now();
      if (curMode === "qw" && calls.length === 0 && cli.qmap?.[cur!.id]) { engineQ = q; q = cli.qmap[cur!.id]; } // QW
      const chunks = o ? await Rt.retrieve(q, cli.topk ?? k, o) : await Rt.retrieve(q, cli.topk ?? k); // DCST
      calls.push({ query: q, k: cli.topk ?? k, chunks, ms: performance.now() - t });
      if (calls.length === 1) tRet = performance.now(); // GST: keep-step clock starts when the first retrieve returns
      if (cli.pool && calls.length === 1) poolCh = await Rt.retrieve(q, cli.pool); // DEEPCOVFB
      return chunks;
    },
    knowledgeReady: async () => {},
    englishNames: (q: string) => PL.englishNamesIn(q, PLA.ptLexicon()),
    getSettings: async () => ({ ...(cli.deep ? { quickFirst: true, alwaysComplete: true, deepModelId: DEEP_ID, largeModelConfirmedIds: [], loadCrashedIds: [] }
      : { quickFirst: true, alwaysComplete: false, largeModelConfirmedIds: [], loadCrashedIds: [] }), ...(mode === "ground" ? { packGround: true } : mode === "top1" ? { packGround: "top1" } : mode === "perpack" ? { packGround: "perpack" } : {}) }), // DEEPCOVFB + GST
    listInstalledLlms: async () => (cli.deep ? [llm, deepLlm] : [llm]), // DEEPCOVFB
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
  };
  if (cli.tasksFrom) deps.emergencyScore = async () => refDetector(refs.get(cur!.id));
  const answerer = A.createAnswerer(deps);

  if (cli.out) { mkdirSync(dirname(abs(cli.out)), { recursive: true }); writeFileSync(abs(cli.out), ""); }
  const emit = (o: unknown) => (cli.out ? appendFileSync(abs(cli.out), JSON.stringify(o) + "\n") : process.stdout.write(JSON.stringify(o) + "\n"));
  const tRun = performance.now();
  const recalls: number[] = [];
  let same = 0, compared = 0, retrieved = 0;
  const diffs: string[] = [];
  // The engine logs "[answer] ..." warnings for the stubbed generation; keep stderr readable.
  const warn0 = console.warn, log0 = console.log;
  for (const m of cli.modes) for (const it of items) { // DCST: one pass per mode
    mode = m;
    if (m === "lead") process.env.BOAR_H8_INDEX = "lead"; else delete process.env.BOAR_H8_INDEX; // H8
    curMode = m; engineQ = null; // QW
    if (WP.denseScans) WP.denseScans.length = 0;
    keptTok = 0; tRet = null; tEnd = null; genPrompt = null; // GST + TK2
    cur = it; calls = []; sourcesEv = null; loaded = null; keptEv = null; doneCodes = null; poolCh = null; // DEEPCOVFB
    let res: any = null;
    console.warn = () => {}; console.log = () => {};
    try {
      const ctx = it.history ? { ...ctx0, history: { summary: null, turns: it.history.turns } } : ctx0;
      res = await answerer.answer({ query: it.question }, (e: any) => {
        if (e.type === "sources" && tEnd === null) tEnd = performance.now(); // GST
        if (e.type === "sources" && Array.isArray(e.sources)) { sourcesEv = e.sources.map((s: any) => String(s.title ?? "")); keptEv = e.sources.map(refOf);
          keptTok = e.sources.reduce((a: number, s: any) => a + CTX.approxTokens(`${s.title}\n${s.body}`), 0); } // GST
        if (e.type === "done" && e.receipt?.reasonCodes) doneCodes = e.receipt.reasonCodes; // DEEPCOVFB
      }, ctx).done;
    } catch (e: any) { if (!String(e?.message ?? e).includes(NO_GEN)) console.error(`[replay] ${it.id}: error in answer()`); } finally { console.warn = warn0; console.log = log0; }
    if (tEnd === null) tEnd = performance.now(); // GST
    const codes: string[] = res?.receipt?.reasonCodes ?? doneCodes ?? []; // DEEPCOVFB
    const task = codes.find((c) => c.startsWith("task:"))?.slice(5) ?? null;
    const c0 = calls[0];
    if (calls.length > 1) log(`${it.id}: ${calls.length} retrieve calls (only the first is reported)`);
    const raw = (c0?.chunks ?? []).map(refOf);
    if (c0) retrieved++;
    const line: any = { engineQuery: engineQ, mode, dense: WP.denseScans ? WP.denseScans.map((x: any) => ({ ...x })) : [], id: it.id, task, tier: res?.tier ?? null, query: c0?.query ?? null, k: c0?.k ?? null, raw,
                        sources: sourcesEv ?? [], ms: c0 ? +c0.ms.toFixed(1) : null,
                        kept: keptEv ?? [], codes, keepCodes: codes.filter((c) => c.startsWith("packground:")), keptTokens: keptTok, keepMs: tRet !== null && tEnd !== null ? +(tEnd - tRet).toFixed(3) : null, // GST
                        budget: c0 ? Math.max(256, Math.min(DEP.quickBudget(task ?? "lookup").contextTokens, LE.defaultContextSize() - 512 - 512 - A.FAST_THINKING_BUDGET)) : null, // GST
                         ...(poolCh ? { pool: poolCh.map(refOf) } : {}), // DEEPCOVFB
                        prompt: genPrompt, promptSha: genPrompt === null ? null : createHash("sha256").update(genPrompt).digest("hex") }; // TK2
    if (mode === "off" && c0) { // GST: OFF keep-stage reconstruction (chunkIds only)
      const rewrote = c0.query !== it.question;
      const q = rewrote ? String(c0.query).replace(/ what to do$/, "") : it.question;
      const sub = c0.chunks.filter(CTX.isSubstantive);
      const ids = CTX.identifiersIn(it.question);
      const pinned = new Set(ids.length ? sub.filter((c: any) => CTX.titleHasIdentifier(c.title, ids)).map((c: any) => c.chunkId) : []);
      const ct = DEP.quickBudget(task ?? "lookup").contextTokens;
      const budget = Math.max(256, Math.min(ct, LE.defaultContextSize() - 512 - 512 - A.FAST_THINKING_BUDGET));
      const comp = CTX.compressContext(q, sub, { tokenBudget: budget, pinned });
      const ground = comp.chunks.filter((c: any) => CTX.onTopic(q, c));
      const health = codes.includes("grounding:health-strict");
      const special = health || rewrote || codes.some((c) => c.startsWith("match:pt-en-names") || c === "grounding:today-in-history");
      const idl = (xs: any[]) => xs.map((c: any) => String(c.chunkId));
      line.diag = { budget, rewrote, health, special, sub: idl(sub), comp: idl(comp.chunks), ground: idl(ground),
                    agree: JSON.stringify(idl(ground)) === JSON.stringify((keptEv ?? []).map((x: any) => x.chunkId)) };
    }
    if (cli.qvec && c0 && mode === cli.modes[0]) line.qvec = Buffer.from((await EMB.embeddingEngine.embed(c0.query)).buffer).toString("base64"); // DCST
    if (cli.compress && c0) line.pre = CMP.compressForAnswer(c0.query, c0.chunks, task ?? "lookup").chunks.map((c: any) => c.title);
    const g = gold[it.id];
    if (Array.isArray(g) && g.length) {
      const top = raw.slice(0, cli.k);
      const found = g.filter((x) => top.some((r: Ref1) => goldMatch(x, r)));
      line.recall = found.length / g.length;
      recalls.push(line.recall);
    }
    const r = refs.get(it.id);
    if (r) {
      compared++;
      const titles = raw.map((x: Ref1) => x.title);
      const ok = JSON.stringify(titles) === JSON.stringify(r.raw);
      if (ok) same++;
      else diffs.push(`${it.id}: task ${r.task}->${task} k ${r.k}->${c0?.k ?? null} query ${r.query === (c0?.query ?? null) ? "same" : `"${r.query}" -> "${c0?.query}"`}\n    ref    ${JSON.stringify(r.raw)}\n    replay ${JSON.stringify(titles)}`);
      line.ref = { task: r.task, query: r.query, k: r.k, raw: r.raw, same: ok };
    }
    emit(line);
  }
  const runS = (performance.now() - tRun) / 1000, totalS = (performance.now() - t0) / 1000;
  const mean = (a: number[]) => (a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN);
  const summary = {
    n: items.length, retrieved, [`recall@${cli.k}`]: recalls.length ? +mean(recalls).toFixed(4) : null, goldItems: recalls.length,
    ...(cli.tasksFrom ? { identicalRaw: `${same}/${compared}` } : {}),
    gate: cli.tasksFrom ? "trace" : cli.gate, detector: cli.tasksFrom ? "trace" : "lexical",
    runSeconds: +runS.toFixed(2), totalSeconds: +totalS.toFixed(2), tree: cli.tree,
  };
  for (const d of diffs) log(`DIFF ${d.split(":")[0]}`); // DCST: ids only (blind-safe)
  console.error(JSON.stringify(summary));
  process.exit(0); // node-llama-cpp keeps handles open
}

main().catch((e) => fail(String(e?.stack ?? e)));
