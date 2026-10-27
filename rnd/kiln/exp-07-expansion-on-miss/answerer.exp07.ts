#!/usr/bin/env -S npx tsx
/**
 * exp-06: BOAR's REAL answer engine (src/routing/answer.ts createAnswerer) on a desktop, for eval.
 *
 * - The app's src/ comes from a checkout of boar-app AT A COMMIT (setup-tree.sh: `git archive <sha>`), never copied into
 *   this harness. This file is placed at <tree>/kiln/answerer.ts; ROOT = <tree>. The commit is written on every row.
 * - Deps are wired as the app wires them (src/routing/answerService.ts:75 at 14de107): the app's retrieve, ptLexicon
 *   englishNames, assemblePrompt/assembleChatMessages, answerPromptPrefix, defaultContextSize, geo, depth… Only the
 *   native parts are replaced:
 *     llama.rn generation -> node-llama-cpp (this file's NodeEngine; GGUF chat template, app sampling defaults)
 *     embeddings (llama.rn) / expo-sqlite / expo-file-system -> Node shims (kiln/app-shims, from eval/runner 0a024db)
 *     ram-monitor -> SIMULATED device RAM (--ram-gb), react-native Platform -> --platform
 * - Packs are the real files, linked (not copied) into a per-config app documentDirectory (setupAppRetrieval, from
 *   eval/runner/desktop.ts 0a024db).
 * One JSONL row per question: question, route/reason codes, tier, model, sources (title, section), cited sources,
 * final text, flags (weak_sources, declined), receipt (TTFT, tok/s, prefill, retrieval), commit.
 *
 *   KILN_RAM_BYTES / KILN_PLATFORM are set from the flags before any app module loads.
 *   npx tsx kiln/answerer.ts --commit 14de107 --model qwen2.5-1.5b-instruct-q4km --questions q.jsonl --out rows.jsonl \
 *     [--ram-gb 4] [--platform ios] [--settings '{"quickFirst":true,"alwaysComplete":false}'] [--corpus essential]
 *     [--pack a.sqlite,b.sqlite] [--places world-places.sqlite,berlin.sqlite] [--ids a,b] [--limit N] [--threads 4]
 *     [--seed 42] [--gpu] [--timeout-ms 120000] [--expansion]   (--expansion: exp-07 branch flag, read by the tree)
 */
import { createHash } from "node:crypto";
import { appendFileSync, createReadStream, existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import os from "node:os";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const SHARED_MODELS = process.env.BOAR_SHARED_MODELS ?? join(os.homedir(), "boar/shared-models");

// ---------------------------------------------------------------- args (before any app import: shims read env)
const argv = process.argv.slice(2);
const get = (k: string, d?: string) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
const opt = {
  commit: get("--commit") ?? "UNKNOWN",
  model: get("--model", "qwen2.5-1.5b-instruct-q4km")!,
  questions: get("--questions")!,
  out: get("--out")!,
  ids: get("--ids")?.split(","),
  limit: Number(get("--limit", "0")),
  ramGb: Number(get("--ram-gb", "4")),
  platform: get("--platform", "ios")!,
  settings: JSON.parse(get("--settings", '{"quickFirst":true,"alwaysComplete":false}')!),
  corpus: get("--corpus", "essential") as "bundled" | "essential",
  pack: get("--pack")?.split(",").filter(Boolean) ?? [],
  places: get("--places")?.split(",").filter(Boolean) ?? [],
  threads: Number(get("--threads", "4")),
  seed: Number(get("--seed", "42")),
  gpu: argv.includes("--gpu"),
  timeoutMs: Number(get("--timeout-ms", "120000")),
  label: get("--label", ""),
};
if (!opt.questions || !opt.out) throw new Error("--questions and --out are required");
process.env.KILN_RAM_BYTES = String(Math.round(opt.ramGb * 1024 ** 3));
process.env.KILN_PLATFORM = opt.platform;
process.env.BOAR_APP_GPU = opt.gpu ? "1" : process.env.BOAR_APP_GPU ?? "1"; // embeddings: Metal is fine (not timed)

// ---------------------------------------------------------------- models (sha256 = HF LFS oid, as eval/runner/desktop.ts)
const MODELS: Record<string, { file: string; sha256: string }> = {
  "qwen2.5-1.5b-instruct-q4km": { file: "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf", sha256: "1adf0b11065d8ad2e8123ea110d1ec956dab4ab038eab665614adba04b6c3370" },
  "qwen3-4b-instruct-2507-q4km": { file: "Qwen3-4B-Instruct-2507-Q4_K_M.gguf", sha256: "3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597" },
};
const EMBED_FILE = "bge-small-en-v1.5-q8_0.gguf";
const EMBED_SHA256 = "ec38e8da142596baa913124ae50550de284b6916bf59577ef2f0cb9660c2f514";

async function sha256File(path: string) {
  const h = createHash("sha256");
  for await (const c of createReadStream(path)) h.update(c as Buffer);
  return h.digest("hex");
}

// ---------------------------------------------------------------- shims + app retrieval (from eval/runner/desktop.ts 0a024db)
async function setupAppRetrieval() {
  const { registerHooks } = await import("node:module");
  const shim = (f: string) => new URL(`./app-shims/${f}`, import.meta.url).href;
  const SHIMS: Record<string, string> = {
    "expo-sqlite": shim("expo-sqlite.mjs"), "expo-file-system": shim("expo-file-system.mjs"),
    "expo-file-system/legacy": shim("expo-file-system.mjs"), "llama.rn": shim("llama-rn.mjs"),
    "react-native": shim("react-native.mjs"), "ram-monitor": shim("ram-monitor.mjs"),
  };
  (registerHooks as any)({
    resolve: (spec: string, ctx: any, next: any) => {
      if (SHIMS[spec]) return { url: SHIMS[spec], shortCircuit: true };
      try {
        return next(spec, ctx);
      } catch (e) {
        if (/^[./]/.test(spec)) throw e;
        return next(spec, { ...ctx, parentURL: import.meta.url });
      }
    },
  });
  const { symlinkSync, rmSync } = await import("node:fs");
  const code = ["src/rag/seedCorpus.ts", "src/rag/db.ts", "src/rag/retrieve.ts", "src/rag/packs.ts", "src/models/manifest.ts"]
    .map((f) => (existsSync(join(ROOT, f)) ? readFileSync(join(ROOT, f), "utf8") : "")).join("\n");
  const key = createHash("sha256").update(code).update(opt.corpus).update(opt.pack.join(",")).update(opt.places.join(",")).digest("hex").slice(0, 16);
  const appDir = join(HERE, ".cache", "appdir", key);
  process.env.BOAR_APP_DIR = appDir;
  mkdirSync(join(appDir, "corpus"), { recursive: true });
  const manifest: any = await import(join(ROOT, "src/models/manifest.ts"));
  const catalog: any[] = [...(manifest.MODEL_CATALOG ?? []), ...(manifest.CORPUS_CATALOG ?? [])];
  const link = (src: string, rel: string) => {
    const dst = join(appDir, rel);
    mkdirSync(dirname(dst), { recursive: true });
    rmSync(dst, { force: true });
    symlinkSync(src, dst);
  };
  const emb = catalog.find((m) => m.kind === "embedding" && m.required);
  link(join(SHARED_MODELS, EMBED_FILE), emb.filename);
  if (opt.corpus === "essential") for (const id of ["corpus-standard", "corpus-full"]) {
    const entry = catalog.find((m) => m.id === id);
    if (!entry) throw new Error(`catalog has no ${id}`);
    link(join(ROOT, "assets/corpus", `${id}.json`), entry.filename);
  }
  for (const m of ["src/rag/cryptoPack.ts", "src/rag/preparedness.ts"]) if (existsSync(join(ROOT, m))) await import(join(ROOT, m));
  const packs: { id: string; sha256: string }[] = [];
  for (const p of opt.pack) {
    const id = p.split("/").pop()!.replace(/\.sqlite$/, "");
    const filename = catalog.find((m) => m.id === id)?.filename ?? `corpus/${id}.sqlite`;
    link(p, filename);
    packs.push({ id, sha256: await sha256File(p) });
  }
  for (const p of opt.places) link(p, join("poi", p.split("/").pop()!));
  const { embeddingEngine } = await import(join(ROOT, "src/rag/embed.ts"));
  await embeddingEngine.load(emb.filename);
  const { seedKnowledgeBaseIfEmpty } = await import(join(ROOT, "src/rag/seedCorpus.ts"));
  await seedKnowledgeBaseIfEmpty();
  const lex: any = await import(join(ROOT, "src/rag/ptLexiconAsset.ts"));
  if (!Object.keys(lex.ptLexicon() ?? {}).length) throw new Error("LEXICON-NOT-LOADED: the app's PT lexicon did not load");
  let geo: any = null;
  const point: { current: { lat: number; lon: number; accuracyM: number } | null } = { current: null };
  if (existsSync(join(ROOT, "src/routing/geoWiring.ts")) && existsSync(join(ROOT, "src/rag/pois.ts"))) {
    const { geoProvidersFrom } = await import(join(ROOT, "src/routing/geoWiring.ts"));
    const pois = await import(join(ROOT, "src/rag/pois.ts"));
    const regions = existsSync(join(ROOT, "src/rag/poiRegions.ts")) ? await import(join(ROOT, "src/rag/poiRegions.ts")) : { POI_REGIONS: [] };
    const fix = async () => point.current ?? { error: "unavailable" as const };
    geo = geoProvidersFrom({
      installedPoiPacks: pois.installedPoiPacks, getCurrentPoint: fix, getLocationFix: fix,
      resolvePlace: pois.resolvePlace, searchPois: pois.searchPois,
      cities: () => (regions.POI_REGIONS ?? []).flatMap((r: any) => r.cities ?? []),
    });
  }
  return { packs, geo, point, catalog };
}

// ---------------------------------------------------------------- AnswerEngine on node-llama-cpp
async function makeEngine(modelPath: string, fileName: string) {
  const { getLlama, LlamaChatSession, LlamaCompletion, resolveChatWrapper } = await import("node-llama-cpp");
  const llama = await getLlama({ gpu: opt.gpu ? "auto" : false });
  const t0 = performance.now();
  const model = await llama.loadModel({ modelPath, gpuLayers: opt.gpu ? "auto" : 0, useMlock: false });
  const loadMs = performance.now() - t0;
  const hasTemplate = model.fileInfo.metadata?.tokenizer?.chat_template != null;
  let abort: AbortController | null = null;
  let last: any = null;
  const engine = {
    loadMs,
    last: () => last,
    resetLast: () => { last = null; },
    async load() { return { fit: null, warning: null } as any; },
    async stop() { abort?.abort(); },
    getModelInfo: () => ({ filename: fileName }),
    hasEmbeddedChatTemplate: () => hasTemplate,
    async estimateFit() { return null; },
    setAnswerPrefix() { /* the app prefills its fixed prefix in llama.rn's KV; not emulated (fresh context per answer) */ },
    async generate(o: any): Promise<string> {
      const ctx = await model.createContext({ contextSize: Math.max(2048, o.nCtx ?? 4096), threads: opt.threads, seed: opt.seed });
      const seq = ctx.getSequence();
      abort = new AbortController();
      const timer = setTimeout(() => abort?.abort(), o.timeoutMs ?? opt.timeoutMs);
      const start = performance.now();
      let first: number | null = null, firstText: number | null = null, tokens = 0, promptTokens = 0;
      const sampling = { temperature: o.temperature ?? 0.7, topK: 40, topP: 0.95, minP: 0.05, seed: opt.seed,
                         maxTokens: (o.nPredict ?? 512) + (o.enableThinking === false ? 0 : o.thinkingBudget ?? 0),
                         signal: abort.signal, stopOnAbortSignal: true,
                         onToken: (t: readonly unknown[]) => {
                           if (first === null) { first = performance.now(); promptTokens = Math.max(0, seq.contextTokens.length - t.length); }
                           tokens += t.length;
                         } };
      let text = "";
      try {
        if (hasTemplate && o.messages) {
          const msgs = o.messages as { role: string; content: string }[];
          const system = msgs.find((m) => m.role === "system")?.content ?? "";
          const user = [...msgs].reverse().find((m) => m.role === "user")!.content;
          const history = msgs.filter((m) => m.role !== "system").slice(0, -1).map((m) =>
            m.role === "user" ? { type: "user" as const, text: m.content } : { type: "model" as const, response: [m.content] });
          // enableThinking:false -> "discourage" only for a template that has a thinking switch: on Qwen3-4B-Instruct-2507 (no
          // enable_thinking in its template) the discourage wrapper made every 48-token call return "" (exp-07 debug).
          const thinkingTemplate = /enable_thinking/.test(String((model as any).fileInfo?.metadata?.tokenizer?.chat_template ?? ""));
          const wrapper = resolveChatWrapper(model, o.enableThinking === false && thinkingTemplate
            ? { customWrapperSettings: { qwen: { thoughts: "discourage" }, jinjaTemplate: { additionalRenderParameters: { enable_thinking: false } } } } as any : {});
          const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: system, ...(wrapper ? { chatWrapper: wrapper } : {}) });
          if (history.length) session.setChatHistory([{ type: "system", text: system }, ...history] as any);
          text = await session.prompt(user, { ...sampling, onTextChunk: (c: string) => { if (firstText === null && c.trim()) firstText = performance.now(); o.onToken?.(c); } } as any);
        } else {
          const completion = new LlamaCompletion({ contextSequence: seq });
          text = await completion.generateCompletion(o.prompt ?? "", { ...sampling, customStopTriggers: o.stop ?? ["\nUser:", "\nQuestion:"],
            onTextChunk: (c: string) => { if (firstText === null && c.trim()) firstText = performance.now(); o.onToken?.(c); } } as any);
        }
      } catch (e) {
        if (!abort.signal.aborted) throw e;
      } finally {
        clearTimeout(timer);
        await ctx.dispose();
      }
      const end = performance.now();
      const promptMs = (first ?? end) - start;
      last = { promptTokens, promptMs, predictedTokens: tokens, predictedMs: end - (first ?? end), firstTextMs: (firstText ?? end) - start,
               timedOut: abort.signal.aborted };
      o.onTimings?.({ promptTokens, promptMs, predictedTokens: tokens, predictedMs: end - (first ?? end), cachedTokens: 0 });
      if (process.env.KILN_DEBUG_GEN) console.error("[kiln-gen]", JSON.stringify({ nPredict: o.nPredict, hasTemplate, messages: !!o.messages, prompt: o.prompt ? o.prompt.slice(0, 80) : null, temp: o.temperature, think: o.enableThinking, text: text.slice(0, 200) }));
      return text;
    },
  };
  return engine;
}

// ---------------------------------------------------------------- main
async function main() {
  const spec = MODELS[opt.model];
  if (!spec) throw new Error(`unknown model ${opt.model}`);
  const modelPath = join(SHARED_MODELS, spec.file);
  for (const [p, h] of [[modelPath, spec.sha256], [join(SHARED_MODELS, EMBED_FILE), EMBED_SHA256]] as const) {
    const got = await sha256File(p);
    if (got !== h) throw new Error(`sha256 mismatch ${p}: ${got}`);
  }
  const t0 = performance.now();
  const env = await setupAppRetrieval();
  const setupMs = performance.now() - t0;
  const A: any = await import(join(ROOT, "src/routing/answer.ts"));
  const pure: any = await import(join(ROOT, "src/rag/pure.ts"));
  const R: any = await import(join(ROOT, "src/rag/retrieve.ts"));
  const PL: any = await import(join(ROOT, "src/rag/ptLexicon.ts"));
  const PLA: any = await import(join(ROOT, "src/rag/ptLexiconAsset.ts"));
  const LE: any = await import(join(ROOT, "src/inference/LlamaEngine.ts"));
  const PERS: any = await import(join(ROOT, "src/constants/personalities.ts"));
  const entry = env.catalog.find((m: any) => m.id === opt.model);
  if (!entry) throw new Error(`model ${opt.model} not in this tree's catalog`);
  const engine = await makeEngine(modelPath, entry.filename);
  const llm = { id: entry.id, label: entry.label, filename: entry.filename, sizeBytes: entry.sizeBytes ?? 0,
                roles: entry.capabilities?.roles ?? ["fast"], isDefault: true, answerTier: entry.answerTier };
  const records: any[] = [];
  const answerer = A.createAnswerer({
    engine,
    retrieve: (q: string, k: number) => R.retrieve(q, k),
    knowledgeReady: async () => {},
    englishNames: (q: string) => PL.englishNamesIn(q, PLA.ptLexicon()),
    getSettings: async () => ({ quickFirst: true, alwaysComplete: false, largeModelConfirmedIds: [], loadCrashedIds: [], ...opt.settings }),
    listInstalledLlms: async () => [llm],
    getActiveModelId: async () => llm.id,
    runMultipass: async () => { throw new Error("multipass is not wired in exp-06 (alwaysComplete=false)"); },
    assemblePrompt: pure.assemblePrompt,
    assembleChatMessages: pure.assembleChatMessages,
    answerPrefix: pure.answerPromptPrefix,
    now: () => performance.now(),
    contextSize: LE.defaultContextSize,
    deviceRamBytes: () => Number(process.env.KILN_RAM_BYTES),
    getGeoProviders: () => env.geo,
    getModelSpeeds: async () => new Map(),
    recordExecution: async (r: any) => { records.push(r); },
    memoryBytes: () => process.memoryUsage().rss,
  });
  const pers = PERS.getPersonality(PERS.DEFAULT_PERSONALITY_ID ?? "succinct");
  const ctx = { systemPrompt: pers.systemPrompt, styleReminder: pers.styleReminder, maxTokens: 512 };
  let qs = readFileSync(opt.questions, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)).filter((q: any) => !q.duplicate_of);
  if (opt.ids) qs = qs.filter((q: any) => opt.ids!.includes(q.id));
  if (opt.limit) qs = qs.slice(0, opt.limit);
  mkdirSync(dirname(opt.out), { recursive: true });
  const runStart = performance.now();
  for (const q of qs) {
    const query = q.query ?? q.question;
    env.point.current = q.context?.lat ? { lat: q.context.lat, lon: q.context.lon, accuracyM: 20 } : null;
    const warnings: any[] = [];
    let cited: number[] | undefined, err: any;
    let shown: any[] = [];
    const started = performance.now();
    records.length = 0;
    let res: any;
    try {
      res = await answerer.answer({ query }, (e: any) => {
        if (e.type === "warning") warnings.push({ code: e.code, declined: !!e.declined, message: e.message });
        if (e.type === "sources" && Array.isArray(e.sources)) shown = e.sources; // what the chat showed (kept on a decline)
        if (e.type === "done") { if (Array.isArray(e.cited)) cited = e.cited; if (e.error) err = e.error; }
      }, ctx).done;
    } catch (e: any) {
      err = { code: "exception", message: String(e?.message ?? e) };
    }
    const total = performance.now() - started;
    const gen = engine.last();
    const sources = (res?.sources ?? []).map((c: any) => ({ title: c.title, section: c.section ?? null, source: c.source ?? null, similarity: c.similarity ?? null }));
    const row = {
      id: q.id, question: query, category: q.category, commit: opt.commit, model: opt.model, label: opt.label,
      device: { ramGb: opt.ramGb, platform: opt.platform }, settings: opt.settings,
      tier: res?.tier, outcome: res?.outcome, reasonCodes: res?.receipt?.reasonCodes ?? [],
      route: (res?.receipt?.reasonCodes ?? []).filter((c: string) => /^(task:|route:|instant:|places:|grounding:|generate:|calc|emergency|health)/.test(c)),
      sources, shownSources: shown.map((c: any) => ({ title: c.title, section: c.section ?? null })), citedIdx: cited ?? null, citedTitles: (cited ?? []).map((i) => res?.sources?.[i - 1]?.title).filter(Boolean),
      answer: res?.text ?? "", modelCalled: !!gen && gen.predictedTokens > 0,
      flags: { weak_sources: warnings.some((w) => w.code === "weak_sources"), declined: warnings.some((w) => w.declined), warnings },
      error: err ?? null,
      receipt: { ttftMs: res?.receipt?.ttftMs ?? null, totalMs: Math.round(total), retrievalMs: res?.receipt?.retrievalMs ?? null,
                 prefillMs: gen ? Math.round(gen.promptMs) : null, promptTokens: gen?.promptTokens ?? null,
                 tokens: gen?.predictedTokens ?? 0, tokPerSec: gen && gen.predictedMs > 0 ? +((gen.predictedTokens - 1) / (gen.predictedMs / 1000)).toFixed(2) : null,
                 timedOut: gen?.timedOut ?? false },
      host: { cpu: `${os.cpus()[0]?.model} cpu x${opt.threads}`, loadAvg1m: +os.loadavg()[0].toFixed(2) },
      packs: env.packs, createdAt: new Date().toISOString(),
    };
    appendFileSync(opt.out, JSON.stringify(row) + "\n");
    engine.resetLast();
    console.log(`${q.id} ${row.tier} ${row.outcome} ttft=${row.receipt.ttftMs ?? "-"} tok/s=${row.receipt.tokPerSec ?? "-"} src=${sources.length} ${row.flags.declined ? "DECLINED" : ""}`);
  }
  console.log(JSON.stringify({ done: qs.length, setupMs: Math.round(setupMs), modelLoadMs: Math.round(engine.loadMs), runMs: Math.round(performance.now() - runStart), out: opt.out }));
}

main().catch((e) => { console.error(e); process.exit(1); });
