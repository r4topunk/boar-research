/**
 * CHATFAIL S1 context builder (0 LLM calls). For every turn of CHAT-FU-v1 it records, per ROUTING (base | patched):
 *   class (classifyTask | classifyTaskInContext), the follow-up plan, the engine's retrieval on the planner's search text
 *   (searchWithFollowUp wrapped around the engine's own retrieve dependency, so k, compressContext and the relevance floor are the
 *   engine's: answer.ts runs with a stubbed generate and the sources it hands to assembleChatMessages are captured), and the style
 *   string the engine composes (ctx.styleReminder is a sentinel, replaced per arm later). Retrieval-irrelevant classes get no context.
 *   tools/contexts.sh --tree scratch/s1-c0 --routing base --out tools/out/ctx-base.jsonl     (C0, A1 share it)
 *   tools/contexts.sh --tree scratch/s1-a2 --routing patched --out tools/out/ctx-patched.jsonl (A2, A3 share it)
 * Setup (app dir, shims, embedding model, claim kit crypto + wikivoyage-en) is replay-retrieval.ts's, copied.
 */
import { createHash } from "node:crypto";
import { createReadStream, existsSync, mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync, appendFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";


const HERE = dirname(fileURLToPath(import.meta.url));
const ADAPTER = "<workspace>/boar-eval/adapters/desktop-node";
const BOAR = "<workspace>";
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
  tree: abs(get("--tree")!),
  routing: get("--routing", "base") as "base" | "patched",
  chats: get("--chats", join(BOAR, "boar-eval/bench/slices/chat-fu-v1/chats.jsonl"))!,
  out: get("--out")!,
  limit: Number(get("--limit", "0")),
  packs: [join(BOAR, "shared-data/crypto/boar-crypto.sqlite"), join(BOAR, "shared-data/packs/boar-wikivoyage-en.sqlite")],
  corpus: "essential" as "essential" | "bundled",
  cpuEmbed: argv.includes("--cpu-embed"),
  verifySha: true,
  modelId: "qwen3-4b-instruct-2507-q4km",
  ramGb: 12,
  platform: "android",
};
const fail = (m: string): never => { console.error(`[ctx] FATAL: ${m}`); process.exit(1); };
const log = (m: string) => console.error(`[ctx] ${m}`);
if (!cli.out) fail("--out required");
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
const SENT = "@@STYLE@@";
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
  const CLS: any = await import(join(T, "src/routing/classify.ts"));
  const FU: any = await import(join(T, "src/routing/followUp.ts"));
  const entry = catalog.find((m: any) => m.id === cli.modelId);
  if (!entry) fail(`model ${cli.modelId} not in the tree's catalog`);
  const llm = { id: entry.id, label: entry.label, filename: entry.filename, sizeBytes: entry.sizeBytes ?? 0,
                roles: entry.capabilities?.roles ?? ["fast"], isDefault: true, answerTier: entry.answerTier };
  const p = PERS.getPersonality("succinct");
  const patchedRouting = cli.routing === "patched";
  if (patchedRouting && typeof CLS.classifyTaskInContext !== "function") fail("patched routing needs classifyTaskInContext in the tree");
  const classify = (q: string, prior: string[]) => (patchedRouting ? CLS.classifyTaskInContext(q, prior) : CLS.classifyTask(q));

  let curHist: any = { turns: [] };
  let calls: { q: string; k: number; planKind: string; searchedFor: string; nChunks: number }[] = [];
  let captured: any = null;
  const NO_GEN = "ctx: generation stubbed out";
  let loaded: string | null = null;
  const engine: any = {
    async load(filename: string) { loaded = filename; return { fit: null, warning: null }; },
    async stop() {}, getModelInfo: () => (loaded ? { filename: loaded } : null), hasEmbeddedChatTemplate: () => true,
    async estimateFit() { return null; }, setAnswerPrefix() {}, async generate() { throw new Error(NO_GEN); },
    nextTokenProbs: async () => [{ token: "SEARCH", prob: 1 }, { token: "ANS", prob: 0 }], // the gate says SEARCH, as replay-retrieval's default
  };
  const deps: any = {
    engine,
    retrieve: async (q: string, k: number) => {
      const plan = FU.followUpSearch(q, curHist);
      const r = await FU.searchWithFollowUp(q, curHist, (text: string) => Rt.retrieve(text, k), (c: any) => `${c.title} ${c.body}`);
      calls.push({ q, k, planKind: plan.direct ? "direct" : plan.fallback ? "fallback" : "none", searchedFor: r.searchedFor, nChunks: r.chunks.length });
      return r.chunks;
    },
    knowledgeReady: async () => {},
    englishNames: (q: string) => PL.englishNamesIn(q, PLA.ptLexicon()),
    getSettings: async () => ({ quickFirst: false, alwaysComplete: false, largeModelConfirmedIds: [], loadCrashedIds: [] }),
    listInstalledLlms: async () => [llm], getActiveModelId: async () => llm.id,
    runMultipass: async () => { throw new Error(NO_GEN); },
    assemblePrompt: pure.assemblePrompt,
    assembleChatMessages: (q: string, chunks: any[], system: any, history: any, style: any) => { captured = { q, chunks, style }; return pure.assembleChatMessages(q, chunks, system, history, style); },
    answerPrefix: pure.answerPromptPrefix, now: () => performance.now(), contextSize: LE.defaultContextSize,
    deviceRamBytes: () => Number(process.env.BOAR_EVAL_RAM_BYTES), getGeoProviders: () => null, getModelSpeeds: async () => new Map(),
    recordExecution: async () => {}, memoryBytes: () => process.memoryUsage().rss,
  };
  const answerer = A.createAnswerer(deps);

  let chats = readFileSync(cli.chats, "utf8").trim().split("\n").map((l) => JSON.parse(l));
  if (cli.limit) chats = chats.slice(0, cli.limit);
  mkdirSync(dirname(abs(cli.out)), { recursive: true }); writeFileSync(abs(cli.out), "");
  const warn0 = console.warn, log0 = console.log;
  let nCap = 0, nEng = 0, nSkip = 0, nNo = 0;
  for (const ch of chats) {
    const hist: any[] = [], users: string[] = [];
    for (const t of ch.turns) {
      curHist = { turns: hist.map((x) => ({ ...x })) };
      const cls = classify(t.text, users.slice());
      const irrelevant = A && CLS.isRetrievalIrrelevant(cls);
      const rec: any = { chat: ch.chat, turn: t.turn, text: t.text, routing: cli.routing, class: cls, captured: false, reason: null, planned: null, plan_kind: null, searched_for: null, k: null, style: SENT, sources: [] };
      const pl = FU.followUpSearch(t.text, curHist);
      rec.plan_kind = pl.direct ? "direct" : pl.fallback ? "fallback" : "none"; rec.planned = pl.direct ?? pl.fallback ?? null;
      if (irrelevant) { rec.captured = true; rec.reason = "retrieval-irrelevant-class"; nSkip++; }
      else {
        calls = []; captured = null;
        console.warn = () => {}; console.log = () => {};
        let res: any = null;
        try { res = await answerer.answer({ query: t.text }, () => {}, { systemPrompt: p.systemPrompt, styleReminder: SENT, maxTokens: 512, history: { summary: null, turns: curHist.turns } }).done; }
        catch { /* stubbed generation */ } finally { console.warn = warn0; console.log = log0; }
        const codes: string[] = res?.receipt?.reasonCodes ?? [];
        rec.reason_codes = codes;
        if (calls[0]) { rec.k = calls[0].k; rec.searched_for = calls[0].searchedFor; rec.engine_query = calls[0].q; rec.plan_kind = calls[0].planKind; }
        if (captured) {
          rec.captured = true; rec.style = captured.style ?? SENT; nEng++;
          rec.sources = captured.chunks.map((c: any) => ({ title: c.title, section: c.section ?? null, source: c.source ?? null, similarity: c.similarity ?? null, body: c.body }));
          rec.reason = "engine";
        } else { rec.reason = "no-generation-reached"; nNo++; rec.result_tier = res?.tier ?? null; rec.result_text = res?.text ?? ""; }
      }
      if (t.capability_request) nCap++;
      appendFileSync(abs(cli.out), JSON.stringify(rec) + "\n");
      users.push(t.text); hist.push({ role: "user", text: t.text }, { role: "assistant", text: "…" });
    }
    log(`${ch.chat} done`);
  }
  console.error(JSON.stringify({ routing: cli.routing, tree: cli.tree, chats: chats.length, engine_captured: nEng, irrelevant_class: nSkip, no_generation_reached: nNo, seconds: +((performance.now() - t0) / 1000).toFixed(1) }));
  process.exit(0);
}
main().catch((e) => fail(String(e?.stack ?? e)));
