import { describe, it, expect } from "vitest";
import * as pureA from "../rag/pure";
import * as pureB from "../../../dt512-base/src/rag/pure";
import { createAnswerer as cA } from "./answer";
import { createAnswerer as cB } from "../../../dt512-base/src/routing/answer";

const ch = (id: string, title: string, body: string) => ({ chunkId: id, docId: id, title, body, score: 1, source: "wikipedia", matchType: "hybrid" }) as any;
const CAN = ch("c1", "Canberra", "Canberra is the capital city of Australia. The site of Canberra was selected in 1908 as a compromise between Sydney and Melbourne. The city was designed after an international design contest.");
const OFF = ch("x1", "Mold", "A mold is one of the structures that certain fungi can form. Mold growth needs moisture and warmth in most homes.");
const SNAKE = ch("s1", "Snakebite", "Snakebite first aid: keep the person still and calm, remove rings and tight items, keep the bitten limb at heart level, and get to a hospital quickly.");
const GB = 1024 ** 3;
const fast = { id: "fast4b", label: "F", filename: "models/fast.gguf", sizeBytes: 2.5 * GB, roles: ["general", "fast"], isDefault: true };
const deep = { id: "deep35", label: "D", filename: "models/deep.gguf", sizeBytes: 12 * GB, roles: ["reasoning"] };

async function go(create: any, pure: any, sc: any, settings: any) {
  const log: any[] = [];
  let clock = 0; let loaded: string | null = sc.resident ? deep.filename : null;
  const deps: any = {
    now: () => (clock += 5),
    today: () => new Date("2026-10-11T12:00:00Z"),
    engine: {
      async load(f: string) { log.push(["load", f]); loaded = f; return { fit: null, warning: null }; },
      async generate(o: any) { log.push(["gen", JSON.parse(JSON.stringify(o)), typeof o.onToken]); o.onToken?.("Answer [1]."); o.onTimings?.({ promptTokens: 100, promptMs: 10, predictedTokens: 3, predictedMs: 5 }); return "Answer [1]."; },
      async stop() {},
      getModelInfo: () => (loaded ? { filename: loaded } : null),
      hasEmbeddedChatTemplate: () => true,
      async estimateFit() { return null; },
    },
    retrieve: async (q: string, k: number) => { log.push(["ret", q, k]); return sc.chunks; },
    getSettings: async () => ({ quickFirst: true, alwaysComplete: sc.complete, deepModelId: deep.id, ...settings }),
    listInstalledLlms: async () => [fast, deep],
    getActiveModelId: async () => fast.id,
    runMultipass: async () => { throw new Error("no multipass"); },
    assemblePrompt: pure.assemblePrompt, assembleChatMessages: pure.assembleChatMessages,
  };
  const events: any[] = [];
  const result = await create(deps).answer({ query: sc.q }, (e: any) => events.push(e), { systemPrompt: "You are Boar. Answer succinctly.", styleReminder: "Be brief.", maxTokens: 512 }).done;
  return JSON.stringify({ events, log, result }).replace(/ans-[a-z0-9]+-[a-z0-9]+/g, "ANS");
}

const scenarios: Record<string, any> = {
  deepCold: { q: "Why was Canberra chosen as the capital of Australia?", chunks: [CAN, OFF], complete: true },
  deepResident: { q: "Why was Canberra chosen as the capital of Australia?", chunks: [CAN, OFF], complete: true, resident: true },
  deepNoOnTopic: { q: "Why was Canberra chosen as the capital of Australia?", chunks: [OFF], complete: true },
  deepPT: { q: "Por que Canberra foi escolhida como capital da Austrália?", chunks: [CAN], complete: true },
  deepHealth: { q: "How do I treat a snake bite?", chunks: [SNAKE], complete: true },
  fast: { q: "Why was Canberra chosen as the capital of Australia?", chunks: [CAN, OFF], complete: false },
};

describe("DIFF dt512 vs deepcover", () => {
  for (const [name, sc] of Object.entries(scenarios)) {
    it(name, async () => {
      const b = await go(cB, pureB, sc, {});
      const b2 = await go(cB, pureB, sc, {});
      if (b !== b2) { let i = 0; while (b[i] === b2[i]) i++; console.log("SELFDIFF", name, i, b.slice(Math.max(0, i - 80), i + 60), "|||", b2.slice(Math.max(0, i - 80), i + 60)); }
      const offU = await go(cA, pureA, sc, {});
      const offF = await go(cA, pureA, sc, { deepCover: false });
      const on = await go(cA, pureA, sc, { deepCover: true });
      console.log("DIFF", name, "off-undef identical:", offU === b, "off-false identical(ex setting):", offF === b, "on differs:", on !== b, b.length);
      expect(offU).toBe(b);
    });
  }
});
