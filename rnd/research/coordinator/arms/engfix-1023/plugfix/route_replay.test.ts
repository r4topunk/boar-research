// PLUGFIX route replay (0 LLM): runs the 110 PLUGBATCH rows through answer() on the current engfix tree with a fake model, the
// detector outcomes recorded in the arm-B traces, no retrieval. Copy to wt/engfix/src/routing/zzReplay.test.ts, run
// `REPLAY_OUT=/path/out.json npx vitest run src/routing/zzReplay.test.ts`, then `python3 -I route_replay_score.py out.json`.
import { it } from "vitest";
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { assemblePrompt, assembleChatMessages } from "../rag/pure";
import { createAnswerer, AnswerDeps, InstalledLlm } from "./answer";

const D = "<workspace>/rnd/research/coordinator/arms/plugbatch-self";
const GB = 1024 ** 3;
const q15: InstalledLlm = { id: "qwen1.5", label: "Qwen 1.5B", filename: "models/q15.gguf", sizeBytes: GB, roles: ["fast"], isDefault: true };

function load(dir: string, pat: RegExp) {
  return readdirSync(dir).filter((f) => pat.test(f)).sort().flatMap((f) => readFileSync(`${dir}/${f}`, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)));
}
it("replay", async () => {
  const reqs = load(`${D}/in`, /^pb-B-w\d\.requests\.jsonl$/);
  const det = new Map<string, { p: number; fire: boolean }>();
  for (const d of readdirSync(`${D}/gen`).filter((x) => /^pb-B-w\d-s42$/.test(x))) {
    for (const l of readFileSync(`${D}/gen/${d}/traces.jsonl`, "utf8").split("\n").filter(Boolean)) {
      const t = JSON.parse(l); const codes: string[] = t.route.reasonCodes;
      const pc = codes.find((c) => c.startsWith("detector:p="));
      det.set(t.itemId, { p: pc ? Number(pc.slice(11)) : 0, fire: codes.includes("detector:fire") });
    }
  }
  const out: Record<string, { codes: string[]; text: string }> = {};
  for (const r of reqs) {
    const it0 = r.item; const id = it0.id as string;
    let clock = 0;
    const d = det.get(id) ?? { p: 0, fire: false };
    const deps: AnswerDeps = {
      now: () => (clock += 5),
      engine: {
        async load(filename: string) { return { fit: null, warning: null }; },
        async generate(opts: any) { opts.onToken?.("MODEL "); opts.onTimings?.({ promptTokens: 10, promptMs: 1, predictedTokens: 1, predictedMs: 1 }); return "MODEL "; },
        async stop() {},
        getModelInfo: () => ({ filename: "models/q15.gguf" }),
        hasEmbeddedChatTemplate: () => true,
        async estimateFit() { return { verdict: "resident" } as any; },
      } as any,
      retrieve: async () => [],
      getSettings: async () => ({ quickFirst: true, alwaysComplete: false, deepModelId: undefined }) as any,
      listInstalledLlms: async () => [q15],
      getActiveModelId: async () => "qwen1.5",
      runMultipass: async () => ({ answer: "", subQuestions: [], citations: [] }) as any,
      assemblePrompt, assembleChatMessages,
      emergencyScore: async () => d,
      warn: true,
    } as any;
    const { answer } = createAnswerer(deps);
    const h = answer({ query: it0.question, tier: "auto" } as any, () => {}, { maxTokens: 64, history: it0.history } as any);
    const res = await h.done;
    out[id] = { codes: res.receipt.reasonCodes, text: res.text };
  }
  writeFileSync(process.env.REPLAY_OUT ?? "/tmp/replay.json", JSON.stringify(out));
}, 120000);
