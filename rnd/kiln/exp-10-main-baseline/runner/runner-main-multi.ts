/**
 * exp-10 O-main-2 COPY of runner-main.ts (the frozen one is untouched): several installed models, each loaded on
 * demand (main's 12 GB profile = the required Qwen2.5-1.5B + the 7B). Otherwise identical.
 * exp-10: BOAR's CURRENT main chat engine on the desktop (boar-app upstream 6b53ee83 = the restored pre-#18 engine).
 *
 * Mirrors ChatScreen.tsx's send path with adaptive routing on (the default, settings.getAdaptiveRoutingEnabled):
 *   runAdaptiveChat (src/services/adaptiveChat.ts, 60 lines of state wiring, MIRRORED here) ->
 *   classifyTask -> buildModelProfiles -> planRoute -> executeRoutingPlan (REAL app code), and ChatScreen's fallback
 *   (empty answer -> fixed-model path: classify -> retrieve -> generate, MIRRORED).
 * Real app code: classify.ts, profiles.ts, router.ts, executor.ts, rag/retrieve.ts + db.ts + embed.ts + packs.ts + pure.ts,
 *   seedCorpus.ts, settings.ts getters, personalities.ts, models/manifest.ts.
 * Replaced: llama.rn generation -> node-llama-cpp (the llamaEngine singleton's methods are patched); SQLite / file system /
 *   RAM readout -> the exp-06 Node shims; ModelManager.statusAll -> "present = the models passed with --installed".
 * Usage (tree root on the mini):
 *   tsx kiln/runner-main.ts --commit 6b53ee83 --model qwen2.5-1.5b-instruct-q4km --questions q.jsonl --out rows.jsonl
 *     [--installed id,id] [--ram-gb 4] [--platform ios] [--pack a.sqlite,b.sqlite] [--corpus essential|bundled]
 *     [--seed 42] [--temp 0] [--threads 4] [--label L] [--ids a,b]
 * --model qwen3-4b-instruct-2507-q4km is NOT in 6b53ee83's catalog: it is registered here as an extra catalog entry
 * (roles [], chat template) — a MODEL PROBE of the old engine, not a configuration a main user can install.
 */
import { createHash } from "node:crypto";
import { appendFileSync, createReadStream, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import os from "node:os";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const SHARED_MODELS = process.env.BOAR_SHARED_MODELS ?? join(os.homedir(), "boar/shared-models");
const argv = process.argv.slice(2);
const get = (k: string, d?: string) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
const opt = {
  commit: get("--commit") ?? "UNKNOWN",
  model: get("--model", "qwen2.5-1.5b-instruct-q4km")!,
  installed: (get("--installed") ?? "").split(",").filter(Boolean),
  questions: get("--questions")!,
  out: get("--out")!,
  ids: get("--ids")?.split(","),
  ramGb: Number(get("--ram-gb", "4")),
  platform: get("--platform", "ios")!,
  corpus: get("--corpus", "essential") as "bundled" | "essential",
  pack: get("--pack")?.split(",").filter(Boolean) ?? [],
  threads: Number(get("--threads", "4")),
  seed: Number(get("--seed", "42")),
  temp: get("--temp") === undefined ? undefined : Number(get("--temp")),
  timeoutMs: Number(get("--timeout-ms", "120000")),
  label: get("--label", ""),
};
if (!opt.installed.length) opt.installed = [opt.model];
process.env.KILN_RAM_BYTES = String(Math.round(opt.ramGb * 1024 ** 3));
process.env.KILN_PLATFORM = opt.platform;
process.env.BOAR_APP_GPU = process.env.BOAR_APP_GPU ?? "1";

const MODELS: Record<string, { file: string; sha256: string; label: string }> = {
  "qwen2.5-1.5b-instruct-q4km": { file: "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf", sha256: "1adf0b11065d8ad2e8123ea110d1ec956dab4ab038eab665614adba04b6c3370", label: "Qwen2.5 1.5B" },
  "qwen2.5-7b-instruct-q4km": { file: "Qwen2.5-7B-Instruct-Q4_K_M.gguf", sha256: "65b8fcd92af6b4fefa935c625d1ac27ea29dcb6ee14589c55a8f115ceaaa1423", label: "Qwen2.5 7B" },
  "qwen3-4b-instruct-2507-q4km": { file: "Qwen3-4B-Instruct-2507-Q4_K_M.gguf", sha256: "3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597", label: "Qwen3 4B 2507 (probe)" },
};
const EMBED_FILE = "bge-small-en-v1.5-q8_0.gguf";
async function sha256File(path: string) {
  const h = createHash("sha256");
  for await (const c of createReadStream(path)) h.update(c as Buffer);
  return h.digest("hex");
}

async function setup() {
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
      try { return next(spec, ctx); } catch (e) { if (/^[./]/.test(spec)) throw e; return next(spec, { ...ctx, parentURL: import.meta.url }); }
    },
  });
  const { symlinkSync, rmSync } = await import("node:fs");
  const code = ["src/rag/seedCorpus.ts", "src/rag/db.ts", "src/rag/retrieve.ts", "src/rag/packs.ts", "src/models/manifest.ts"]
    .map((f) => (existsSync(join(ROOT, f)) ? readFileSync(join(ROOT, f), "utf8") : "")).join("\n");
  const key = createHash("sha256").update(code).update(opt.corpus).update(opt.pack.join(",")).update(opt.model).digest("hex").slice(0, 16);
  const appDir = join(HERE, ".cache", "appdir", key);
  process.env.BOAR_APP_DIR = appDir;
  mkdirSync(join(appDir, "corpus"), { recursive: true });
  const manifest: any = await import(join(ROOT, "src/models/manifest.ts"));
  const link = (src: string, rel: string) => {
    const dst = join(appDir, rel);
    mkdirSync(dirname(dst), { recursive: true });
    rmSync(dst, { force: true });
    symlinkSync(src, dst);
  };
  // The 4B probe: an extra catalog entry (not in 6b53ee83's catalog).
  for (const id of opt.installed) {
    if (!manifest.MODEL_CATALOG.some((m: any) => m.id === id)) {
      const s = MODELS[id];
      manifest.MODEL_CATALOG.push({ id, kind: "llm", label: s.label, filename: `models/${id}.gguf`, sizeBytes: 0, sha256: s.sha256,
        sourceUrl: "", license: "", description: "exp-10 probe", required: false, capabilities: { roles: [], usesChatTemplate: true } });
    }
  }
  const catalog: any[] = [...manifest.MODEL_CATALOG, ...(manifest.CORPUS_CATALOG ?? [])];
  const emb = catalog.find((m) => m.kind === "embedding" && m.required);
  link(join(SHARED_MODELS, EMBED_FILE), emb.filename);
  for (const id of opt.installed) link(join(SHARED_MODELS, MODELS[id].file), catalog.find((m) => m.id === id).filename);
  if (opt.corpus === "essential") for (const id of ["corpus-standard", "corpus-full"]) {
    const entry = catalog.find((m) => m.id === id);
    if (!entry) throw new Error(`catalog has no ${id}`);
    link(join(ROOT, "assets/corpus", `${id}.json`), entry.filename);
  }
  const packs: { id: string; sha256: string; inCatalog: boolean }[] = [];
  for (const p of opt.pack) {
    const id = p.split("/").pop()!.replace(/\.sqlite$/, "");
    const entry = catalog.find((m) => m.id === id);
    link(p, entry?.filename ?? `corpus/${id}.sqlite`);
    packs.push({ id, sha256: await sha256File(p), inCatalog: !!entry });
  }
  const S: any = await import(join(ROOT, "src/models/settings.ts"));
  await S.setActiveModelId("llm", opt.model);
  const { embeddingEngine } = await import(join(ROOT, "src/rag/embed.ts"));
  await embeddingEngine.load(emb.filename);
  const { seedKnowledgeBaseIfEmpty } = await import(join(ROOT, "src/rag/seedCorpus.ts"));
  await seedKnowledgeBaseIfEmpty();
  return { packs, catalog, S };
}

async function patchEngine(LE: any, files: Map<string, string>) {
  // filename (catalog) -> GGUF path; each model is loaded once, on first use.
  const { getLlama, LlamaChatSession, LlamaCompletion } = await import("node-llama-cpp");
  const llama = await getLlama({ gpu: false });
  const models = new Map<string, any>();
  const eng = LE.llamaEngine;
  let loaded: string | null = null;
  let abort: AbortController | null = null;
  const modelFor = async (f: string) => {
    if (!models.has(f)) models.set(f, await llama.loadModel({ modelPath: files.get(f)!, gpuLayers: 0, useMlock: false }));
    return models.get(f);
  };
  eng.getModelInfo = () => (loaded ? { filename: loaded } : null);
  eng.load = async (f: string) => {
    if (!files.has(f)) throw new Error(`exp-10: ${f} is not installed`);
    await modelFor(f);
    loaded = f;
  };
  eng.hasEmbeddedChatTemplate = () => !!loaded && models.get(loaded)?.fileInfo.metadata?.tokenizer?.chat_template != null;
  eng.stop = async () => abort?.abort();
  eng.generate = async (o: any): Promise<string> => {
    const model = await modelFor(loaded!);
    const ctx = await model.createContext({ contextSize: 4096, threads: opt.threads, seed: opt.seed });
    const seq = ctx.getSequence();
    abort = new AbortController();
    const timer = setTimeout(() => { abort?.abort(); o.onTimeout?.(); }, o.timeoutMs ?? opt.timeoutMs);
    const sampling = { temperature: opt.temp ?? o.temperature ?? 0.7, topK: 40, topP: 0.95, minP: 0.05, seed: opt.seed,
      maxTokens: o.nPredict ?? 512, signal: abort.signal, stopOnAbortSignal: true };
    let text = "";
    try {
      if (o.messages) {
        const msgs = o.messages as { role: string; content: string }[];
        const system = msgs.find((m) => m.role === "system")?.content ?? "";
        const user = [...msgs].reverse().find((m) => m.role === "user")!.content;
        const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: system });
        text = await session.prompt(user, { ...sampling, onTextChunk: (c: string) => o.onToken?.(c) } as any);
      } else {
        const completion = new LlamaCompletion({ contextSequence: seq });
        text = await completion.generateCompletion(o.prompt ?? "", { ...sampling,
          customStopTriggers: o.stop ?? ["\nUser:", "\n\nUser:", "\nQuestion:", "\n\nQuestion:"], onTextChunk: (c: string) => o.onToken?.(c) } as any);
      }
    } catch (e) {
      if (!abort.signal.aborted) throw e;
    } finally {
      clearTimeout(timer);
      await ctx.dispose();
    }
    return text;
  };
}

async function main() {
  const spec = MODELS[opt.model];
  if (!spec) throw new Error(`unknown model ${opt.model}`);
  for (const id of opt.installed) {
    const p = join(SHARED_MODELS, MODELS[id].file);
    if ((await sha256File(p)) !== MODELS[id].sha256) throw new Error(`sha256 mismatch ${p}`);
  }
  const t0 = performance.now();
  const env = await setup();
  const setupMs = performance.now() - t0;
  const LE: any = await import(join(ROOT, "src/inference/LlamaEngine.ts"));
  await patchEngine(LE, new Map(opt.installed.map((id) => [env.catalog.find((m: any) => m.id === id).filename, join(SHARED_MODELS, MODELS[id].file)])));
  const C: any = await import(join(ROOT, "src/routing/classify.ts"));
  const P: any = await import(join(ROOT, "src/routing/profiles.ts"));
  const RT: any = await import(join(ROOT, "src/routing/router.ts"));
  const EX: any = await import(join(ROOT, "src/routing/executor.ts"));
  const R: any = await import(join(ROOT, "src/rag/retrieve.ts"));
  const pure: any = await import(join(ROOT, "src/rag/pure.ts"));
  const PERS: any = await import(join(ROOT, "src/constants/personalities.ts"));
  const S = env.S;
  let qs = readFileSync(opt.questions, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  if (opt.ids) qs = qs.filter((q: any) => opt.ids!.includes(q.id));
  mkdirSync(dirname(opt.out), { recursive: true });
  writeFileSync(opt.out, "");
  const runStart = performance.now();
  for (const q of qs) {
    const query: string = q.query ?? q.question;
    const started = performance.now();
    // ChatScreen.tsx: maxTokens, personality, fresh history (no earlier turns).
    const [maxTokens, personalityId, customPrompt] = await Promise.all([S.getMaxTokens(), S.getPersonalityId(), S.getCustomSystemPrompt?.() ?? ""]);
    const pers = PERS.getPersonality(personalityId);
    const systemPrompt = personalityId === "custom" ? customPrompt : pers.systemPrompt;
    const styleReminder = personalityId === "custom" ? undefined : pers.styleReminder;
    const input = { query, systemPrompt, styleReminder, history: { summary: null, turns: [] } };
    let answer = "", route = "adaptive", result: any = null, err: any = null, tokens = 0;
    const onToken = () => { tokens++; };
    try {
      // MIRROR of runAdaptiveChat (adaptiveChat.ts @6b53ee83).
      const [preset, overrides, fallbackId] = await Promise.all([S.getRoutingPreset(), S.getModelRoleAssignments(), S.getActiveModelId("llm")]);
      const available = env.catalog.filter((m: any) => m.kind === "llm").map((m: any) => ({ model: m, present: opt.installed.includes(m.id) }));
      const deviceRamBytes = Number(process.env.KILN_RAM_BYTES);
      const taskType = C.classifyTask(query);
      const profiles = P.buildModelProfiles(preset, available, overrides, deviceRamBytes, fallbackId ?? undefined);
      const plan = RT.planRoute({ taskType, query, hasLocalKnowledgeBase: true, retrievalAvailable: true, availableModels: profiles, preset,
        budget: { maxTokens, allowVerification: true, allowRetrieval: true } });
      const modelById = new Map(available.filter((a: any) => a.present).map((a: any) => [a.model.id,
        { id: a.model.id, filename: a.model.filename, usesChatTemplate: a.model.capabilities?.usesChatTemplate }]));
      result = await EX.executeRoutingPlan(plan, input, (id: string) => modelById.get(id), { onToken });
      result.taskType = taskType;
      answer = result.answer;
      // ChatScreen fallback: an empty answer -> the fixed-model path (classify -> retrieve -> generate).
      if (!answer.trim()) {
        route = "fixed-fallback";
        const c = C.isRetrievalIrrelevant(taskType) ? [] : await R.retrieve(query, pure.ANSWER_CONTEXT_CHUNKS);
        answer = await LE.llamaEngine.generate(LE.llamaEngine.hasEmbeddedChatTemplate()
          ? { messages: pure.assembleChatMessages(query, c, systemPrompt, input.history, styleReminder), nPredict: maxTokens, onToken }
          : { prompt: pure.assemblePrompt(query, c, systemPrompt, input.history, styleReminder), nPredict: maxTokens, onToken });
        result.citations = c;
      }
    } catch (e: any) {
      err = String(e?.message ?? e);
    }
    const row = {
      id: q.id, question: query, set: q.set ?? q.category ?? null, commit: opt.commit, model: opt.model, installed: opt.installed,
      label: opt.label, device: { ramGb: opt.ramGb, platform: opt.platform }, route, taskType: result?.taskType ?? null,
      planReasonCodes: result?.plan?.reasonCodes ?? [], planSteps: (result?.plan?.steps ?? []).map((s: any) => `${s.type}:${s.modelId ?? ""}`),
      sources: (result?.citations ?? []).map((c: any) => ({ title: c.title, similarity: c.similarity ?? null, matchType: c.matchType ?? null })),
      answer, verification: result?.verification ?? null, warnings: result?.warnings ?? [], error: err,
      receipt: { ttftMs: result?.ttftMs ?? null, generationLatencyMs: result?.generationLatencyMs ?? null, modelLoadMs: result?.modelLoadMs ?? null,
        totalMs: performance.now() - started, tokens, timedOut: !!result?.timedOut },
      temp: opt.temp ?? null, seed: opt.seed, packs: env.packs, createdAt: new Date().toISOString(),
    };
    appendFileSync(opt.out, JSON.stringify(row) + "\n");
    console.log(`${q.id} ${route} ${row.taskType} steps=${row.planSteps.join(",")} src=${row.sources.length} ${err ? "ERR " + err : ""}`);
  }
  console.log(JSON.stringify({ done: qs.length, setupMs: Math.round(setupMs), runMs: Math.round(performance.now() - runStart), out: opt.out }));
  process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(1); });
