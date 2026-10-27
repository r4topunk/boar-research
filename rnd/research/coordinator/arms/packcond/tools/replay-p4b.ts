/**
 * PACKCOND P4b (PACKDENSE D0) copy of replay-pg.ts (changes marked "P4B"). Same engine run (OFF baseline: run it
 * WITHOUT --pack-ground), plus, per retrieving item, a dense-router diagnostic computed with the tree's own functions
 * on the engine's search query (c0.query) and the engine's embedding of it (embeddingEngine.embed(c0.query)):
 *   --p4b             : enable the diagnostic (output field `p4b`, ids/titles/sections/numbers only).
 *   --f0 <json>       : aggregates/p4-diag.json (H.items[].f0_articles / f0_packs = targets of the in-pack items).
 *   --gold <json>     : gold titles are targets too ("Wikivoyage: X" -> wikivoyage pack; plain -> crypto pack enwiki).
 *   --top N           : top-N lead-cosine articles kept per pack per item (default 10; passages read for them).
 * Per pack: stems, titlesInQuestion (named), engine named/step chunk ids (searchWikiPacks, same options as
 * retrieveOne), a full lead_vecs scan (scan_ms = SQL read + cosine; cos_ms = cosine only over cached vectors).
 * Per target: resolved id (resolveTitle, fuzzy false), named/share, bm25 article rank at pool 80/400/2000
 * (perArticle 1) and in_pool80 (perArticle 2), cov_best over all its chunks, lead_cos, lead_rank, passages.
 * Blind-safe stderr: a raw-list DIFF prints only the item id (no query or titles).
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
const BOAR = resolve(HERE, "../../../../../.."); // DEEPCOVFB
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
  p4b: argv.includes("--p4b"), // P4B
  f0: get("--f0", join(BOAR, "rnd/research/coordinator/arms/packcond/aggregates/p4-diag.json"))!, // P4B
  top: Number(get("--top", "10")), // P4B
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
type Ref1 = { title: string; section: string | null; source: string | null; similarity: number | null; via: string | null };
const refOf = (c: any): Ref1 => ({
  title: String(c.title ?? ""), section: typeof c.section === "string" ? c.section : null, source: typeof c.source === "string" ? c.source : null,
  similarity: typeof c.similarity === "number" && Number.isFinite(c.similarity) ? +c.similarity.toFixed(4) : null, via: c.matchType ?? null,
});

// ---------------------------------------------------------------- P4B dense-router diagnostic
const CRYPTO_LABELS = ["Ethereum EIPs/ERCs: ", "ethereum.org: ", "Bitcoin BIPs: ", "Ethereum specs: "];
const CRYPTO_SOURCES = ["enwiki", "eips", "ethspecs", "ethereumorg", "bips"];
const vecCache = new Map<string, { ids: Int32Array; vecs: Uint8Array[] }>();
const titleCache = new Map<string, Map<number, string>>();
async function titleOf(pk: string, wp: any, id: number) {
  let m = titleCache.get(pk); if (!m) titleCache.set(pk, (m = new Map()));
  if (!m.has(id)) m.set(id, (await wp.db.getFirstAsync("SELECT title FROM articles WHERE id = ?", [id]))?.title ?? null);
  return m.get(id)!;
}
async function p4bDiag(id: string, c0: any, PK: any, WP: any, EX: any, EMB: any, pure: any, f0: any, goldTitles: string[] | undefined) {
  // Targets: F0 articles (pack known) + gold titles.
  const targets: { kind: string; title: string; pack: string; sources: string[] }[] = [];
  for (const t of f0?.titles ?? []) for (const p of f0.packs) targets.push({ kind: "f0", title: t, pack: p, sources: p === "wikivoyage" ? ["enwikivoyage"] : CRYPTO_SOURCES });
  for (const g0 of goldTitles ?? []) {
    const g = g0.split("#")[0];
    if (g.startsWith("Wikivoyage: ")) targets.push({ kind: "gold", title: g.slice(12), pack: "wikivoyage", sources: ["enwikivoyage"] });
    else {
      const lab = CRYPTO_LABELS.find((l) => g.startsWith(l));
      targets.push({ kind: "gold", title: lab ? g.slice(lab.length) : g, pack: "crypto", sources: lab ? CRYPTO_SOURCES.slice(1) : ["enwiki"] });
    }
  }
  if (!c0) return { no_retrieve: true, targets: targets.map((t) => ({ kind: t.kind, title: t.title, pack: t.pack })) };
  const query: string = c0.query;
  const queryVec: Float32Array = await EMB.embeddingEngine.embed(query);
  const action = WP.ACTION_INTENT.test(query), explain = !action && EX.EXPLAIN_INTENT.test(query);
  // Same call as retrieveOne's (English path: no titles/action/explain options).
  const W: any[] = await PK.searchWikiPacks(query, { k: c0.k, queryVec });
  const rawIds: string[] = c0.chunks.map((c: any) => String(c.chunkId));
  const packs: Record<string, any> = {};
  const firstIds = new Set<string>();
  const byPack: Record<string, { wp: any; stems: any[]; packId: string }> = {};
  for (const w of W) {
    const pk = /wikivoyage/.test(w.packId) ? "wikivoyage" : "crypto";
    const wp = w.pack, stems = w.stems;
    byPack[pk] = { wp, stems, packId: w.packId };
    const named = await wp.titlesInQuestion(query, stems);
    const namedHits = w.hits.filter((h: any) => h.via === "title");
    const stepHits = action ? w.hits.filter((h: any) => h.via !== "title" && h.action) : [];
    for (const h of [...namedHits, ...stepHits]) firstIds.add(`pack:${w.packId}:${h.chunkId}`);
    // Full lead scan.
    const t0 = performance.now();
    const rows: any[] = await wp.db.getAllAsync("SELECT article_id, vec FROM lead_vecs", []);
    const cos = new Float64Array(rows.length), ids = new Int32Array(rows.length);
    for (let i = 0; i < rows.length; i++) { ids[i] = rows[i].article_id; cos[i] = pure.cosineSimilarityInt8(queryVec, new Uint8Array(rows[i].vec)); }
    const scanMs = performance.now() - t0;
    if (!vecCache.has(pk)) vecCache.set(pk, { ids, vecs: rows.map((r) => new Uint8Array(r.vec)) });
    const vc = vecCache.get(pk)!;
    const t1 = performance.now();
    const cos2 = new Float64Array(vc.vecs.length);
    for (let i = 0; i < vc.vecs.length; i++) cos2[i] = pure.cosineSimilarityInt8(queryVec, vc.vecs[i]);
    const cosMs = performance.now() - t1;
    const order = Array.from(ids.keys()).sort((a, b) => cos[b] - cos[a] || ids[a] - ids[b]);
    const rank = new Map<number, number>(); order.forEach((ix, r) => rank.set(ids[ix], r + 1));
    const cosOf = new Map<number, number>(); for (let i = 0; i < ids.length; i++) cosOf.set(ids[i], cos[i]);
    const top = [];
    for (const ix of order.slice(0, cli.top)) {
      const aid = ids[ix];
      const ps = await wp.articlePassages(aid, stems, 2, action, explain);
      top.push({ id: aid, title: await titleOf(pk, wp, aid), cos: +cos[ix].toFixed(4),
        passages: ps.map((h: any) => ({ cid: `pack:${w.packId}:${h.chunkId}`, title: PK.packHitToChunk(w.packId, h).title, section: h.section, lead: h.lead,
          cov: +WP.coverage(`${h.title} ${h.text}`, stems).toFixed(3) })) });
    }
    packs[pk] = { n_articles: rows.length, scan_ms: +scanMs.toFixed(1), cos_ms: +cosMs.toFixed(1), n_stems: stems.length,
      named: await Promise.all(named.map(async (n: any) => ({ id: n.id, title: await titleOf(pk, wp, n.id), share: +n.share.toFixed(3) }))),
      engine_named_ids: [...new Set(namedHits.map((h: any) => h.articleId))], n_named_hits: namedHits.length, n_step_hits: stepHits.length,
      n_hits: w.hits.length, top, _rank: rank, _cos: cosOf };
  }
  let prefix = 0; while (prefix < rawIds.length && firstIds.has(rawIds[prefix])) prefix++;
  const tout = [];
  for (const t of targets) {
    const P = byPack[t.pack];
    const rec: any = { kind: t.kind, title: t.title, pack: t.pack, id: null };
    if (!P) { rec.pack_missing = true; tout.push(rec); continue; }
    const { wp, stems, packId } = P;
    let aid: number | null = null, src: string | null = null;
    for (const s of t.sources) { aid = await wp.resolveTitle(t.title, { fuzzy: false, source: s }); if (aid !== null) { src = s; break; } }
    rec.id = aid; rec.source = src;
    if (aid === null) { tout.push(rec); continue; }
    rec.resolved_title = await titleOf(t.pack, wp, aid);
    const named = (await wp.titlesInQuestion(query, stems)).find((n: any) => n.id === aid);
    rec.named = !!named; rec.share = named ? +named.share.toFixed(3) : null;
    rec.engine_named = packs[t.pack].engine_named_ids.includes(aid);
    const prior = wp.tuning.prior;
    for (const pool of [80, 400, 2000]) {
      const cs = await wp.bm25Candidates(stems, pool, prior, 1);
      const r = cs.findIndex((c: any) => c.articleId === aid);
      rec[`bm25_${pool}`] = r < 0 ? null : r + 1;
    }
    rec.bm25_rank = rec.bm25_2000;
    rec.in_pool80 = (await wp.bm25Candidates(stems, 80, prior, 2)).some((c: any) => c.articleId === aid);
    const a = await wp.article(aid);
    const ch: any[] = await wp.db.getAllAsync("SELECT id, start, end FROM chunks WHERE article_id = ? ORDER BY id", [aid]);
    rec.n_chunks = ch.length;
    rec.cov_best = ch.length ? +Math.max(...ch.map((c) => WP.coverage(`${a.title} ${a.text.slice(c.start, c.end).trim()}`, stems))).toFixed(3) : null;
    rec.lead_cos = packs[t.pack]._cos.has(aid) ? +packs[t.pack]._cos.get(aid).toFixed(4) : null;
    rec.lead_rank = packs[t.pack]._rank.get(aid) ?? null;
    const ps = await wp.articlePassages(aid, stems, 2, action, explain);
    rec.passages = ps.map((h: any) => ({ cid: `pack:${packId}:${h.chunkId}`, title: PK.packHitToChunk(packId, h).title, section: h.section, lead: h.lead,
      cov: +WP.coverage(`${h.title} ${h.text}`, stems).toFixed(3) }));
    tout.push(rec);
  }
  for (const p of Object.values(packs)) { delete p._rank; delete p._cos; }
  return { action, explain, raw_ids: rawIds, prefix_n: prefix, packs, targets: tout };
}

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
  const PK: any = await import(join(T, "src/rag/packs.ts")); // P4B
  const WP: any = await import(join(T, "src/rag/wikiPack.ts")); // P4B
  const EX: any = await import(join(T, "src/rag/explain.ts")); // P4B
  const EMB: any = await import(join(T, "src/rag/embed.ts")); // P4B
  const f0: Map<string, { titles: string[]; packs: string[] }> = new Map(); // P4B
  if (cli.p4b && existsSync(cli.f0)) for (const x of JSON.parse(readFileSync(cli.f0, "utf8")).H.items) f0.set(x.id, { titles: x.f0_articles, packs: x.f0_packs });
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
    async generate() { throw new Error(NO_GEN); },
  };
  if (cli.tasksFrom || cli.gate === "search")
    engine.nextTokenProbs = async () =>
      cli.tasksFrom ? refGateProbs(refs.get(cur!.id)) : [{ token: "SEARCH", prob: 1 }, { token: "ANS", prob: 0 }];
  const deps: any = {
    engine,
    retrieve: async (q: string, k: number) => {
      const t = performance.now();
      const chunks = await Rt.retrieve(q, cli.topk ?? k);
      calls.push({ query: q, k: cli.topk ?? k, chunks, ms: performance.now() - t });
      if (cli.pool && calls.length === 1) poolCh = await Rt.retrieve(q, cli.pool); // DEEPCOVFB
      return chunks;
    },
    knowledgeReady: async () => {},
    englishNames: (q: string) => PL.englishNamesIn(q, PLA.ptLexicon()),
    getSettings: async () => ({ ...(cli.deep ? { quickFirst: true, alwaysComplete: true, deepModelId: DEEP_ID, largeModelConfirmedIds: [], loadCrashedIds: [] }
      : { quickFirst: true, alwaysComplete: false, largeModelConfirmedIds: [], loadCrashedIds: [] }), ...(cli.packGround ? { packGround: true } : {}) }), // DEEPCOVFB + PACKCOND
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
  for (const it of items) {
    cur = it; calls = []; sourcesEv = null; loaded = null; keptEv = null; doneCodes = null; poolCh = null; // DEEPCOVFB
    let res: any = null;
    console.warn = () => {}; console.log = () => {};
    try {
      const ctx = it.history ? { ...ctx0, history: { summary: null, turns: it.history.turns } } : ctx0;
      res = await answerer.answer({ query: it.question }, (e: any) => {
        if (e.type === "sources" && Array.isArray(e.sources)) { sourcesEv = e.sources.map((s: any) => String(s.title ?? "")); keptEv = e.sources.map(refOf); }
        if (e.type === "done" && e.receipt?.reasonCodes) doneCodes = e.receipt.reasonCodes; // DEEPCOVFB
      }, ctx).done;
    } catch { /* stubbed generation */ } finally { console.warn = warn0; console.log = log0; }
    const codes: string[] = res?.receipt?.reasonCodes ?? doneCodes ?? []; // DEEPCOVFB
    const task = codes.find((c) => c.startsWith("task:"))?.slice(5) ?? null;
    const c0 = calls[0];
    if (calls.length > 1) log(`${it.id}: ${calls.length} retrieve calls (only the first is reported)`);
    const raw = (c0?.chunks ?? []).map(refOf);
    if (c0) retrieved++;
    const line: any = { id: it.id, task, tier: res?.tier ?? null, query: c0?.query ?? null, k: c0?.k ?? null, raw,
                        sources: sourcesEv ?? [], ms: c0 ? +c0.ms.toFixed(1) : null,
                        kept: keptEv ?? [], codes, ...(poolCh ? { pool: poolCh.map(refOf) } : {}) }; // DEEPCOVFB
    if (cli.diag && c0) { // PACKCOND
      const q = it.question;
      const sub = c0.chunks.filter(CTX.isSubstantive);
      const ids = CTX.identifiersIn(q);
      const pinned = new Set(ids.length ? sub.filter((c: any) => CTX.titleHasIdentifier(c.title, ids)).map((c: any) => c.chunkId) : []);
      const comp = CTX.compressContext(q, sub, { tokenBudget: cli.budget, pinned });
      const ground = comp.chunks.filter((c: any) => CTX.onTopic(q, c));
      const key = (x: any) => `${x.title}#${x.section ?? ""}`;
      const health = codes.includes("grounding:health-strict");
      const special = health || codes.some((c) => c.startsWith("retrieve:pt-en-terms") || c.startsWith("match:pt-en-names") || c === "grounding:today-in-history");
      // per substantive chunk: onTopic on the full passage, on its compressed cut, kept by compression, relative relevance
      const cutOf = (c: any) => comp.chunks.find((x: any) => x.chunkId === c.chunkId);
      const feats = sub.map((c: any) => ({ pack: String(c.chunkId).startsWith("pack:"), sim: c.similarity ?? null, inComp: !!cutOf(c),
        topicFull: CTX.onTopic(q, c), topicCut: cutOf(c) ? CTX.onTopic(q, cutOf(c)) : null, cov: +CTX.termCoverage(q, `${c.title} ${c.body}`).toFixed(3) }));
      // PACKCOND lever screen (replay-side, step 0 only): alternative kept lists
      const full = (c: any) => sub.find((x: any) => x.chunkId === c.chunkId) ?? c;
      const variants: Record<string, any[]> = {};
      for (const N of [1, 2, 3]) {
        const top = new Set(sub.slice(0, N).map((c: any) => c.chunkId));
        const cp = CTX.compressContext(q, sub, { tokenBudget: cli.budget, pinned: new Set([...pinned, ...top]) });
        variants[`pin${N}`] = cp.chunks.filter((c: any) => top.has(c.chunkId) || CTX.onTopic(q, c)).map(refOf);
        // pin only when grounding would otherwise drop it AND its full passage is on topic
        variants[`pinTopic${N}`] = cp.chunks.filter((c: any) => CTX.onTopic(q, c) || (top.has(c.chunkId) && CTX.onTopic(q, full(c)))).map(refOf);
      }
      { // full-passage topic + restore the best compress-dropped on-topic (full) chunk
        const g = comp.chunks.filter((c: any) => CTX.onTopic(q, c) || CTX.onTopic(q, full(c)));
        const lost = sub.filter((c: any) => !comp.chunks.some((x: any) => x.chunkId === c.chunkId) && CTX.onTopic(q, c));
        variants.fullTopic = g.map(refOf);
        variants.fullTopicRestore = [...g, ...lost.slice(0, 1)].map(refOf);
      }
      { // no-good-source fallback: when grounding empties, keep compression's top 2
        variants.fallback2 = (ground.length ? ground : comp.chunks.slice(0, 2)).map(refOf);
      }
      line.diag = { sub: sub.map(refOf), comp: comp.chunks.map(refOf), ground: ground.map(refOf), special, feats, variants,
                    agree: JSON.stringify(ground.map(refOf).map(key)) === JSON.stringify((keptEv ?? []).map(key)) };
    }
    if (cli.p4b) { // P4B
      try { line.p4b = await p4bDiag(it.id, c0, PK, WP, EX, EMB, pure, f0.get(it.id), gold[it.id]); }
      catch { line.p4b = { error: true }; log(`${it.id}: p4b error`); }
    }
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
      else diffs.push(`${it.id}: task ${r.task}->${task} k ${r.k}->${c0?.k ?? null} query-same ${r.query === (c0?.query ?? null)} n ${r.raw.length}->${titles.length}`); // P4B: no text
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
  for (const d of diffs) log(`DIFF ${d}`);
  console.error(JSON.stringify(summary));
  process.exit(0); // node-llama-cpp keeps handles open
}

main().catch((e) => fail(String(e?.stack ?? e)));
