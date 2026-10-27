// VEXACT-ACCEPT runner hook, loaded into the adapter process with NODE_OPTIONS="--import file://<this>" (no change to the engine tree).
// 1) VXA_PROMPT_JSON=<d4.json>: rewrites every answer request the engine sends to llama-server (POST /v1/chat/completions whose system
//    message contains " You are BOAR, an offline AI research app") exactly as PACKREAD's build.py did with the dumped engine prompts:
//    system = arm.sys + (arm.ci if the system message carries "\n\nContext:") + system[from " You are BOAR..."], the user's trailing
//    "(Response style: ...)" -> arm.rem, max_tokens -> arm.max_tokens. Context block, identity text and question stay byte-identical.
//    Unset = the engine's own prompt (Succinct persona), nothing rewritten.
// 2) VXA_FACTS_JSON=<facts.json>: the engine's `import table from "./facts.v1.json"` (src/rag/facts.ts) resolves to this file instead.
// 3) VXA_REWRITE_LOG=<jsonl>: one row per rewritten request {n, rewritten, hadContext, sys, user, max_tokens} (audit trail).
import { registerHooks } from "node:module";
import { appendFileSync, readFileSync, existsSync } from "node:fs";
import { pathToFileURL } from "node:url";

const CUT = " You are BOAR, an offline AI research app";
const LOG = process.env.VXA_REWRITE_LOG;
const log = (o) => { if (LOG) appendFileSync(LOG, JSON.stringify(o) + "\n"); };

if (process.env.VXA_PROMPT_JSON) {
  const arm = JSON.parse(readFileSync(process.env.VXA_PROMPT_JSON, "utf8"));
  for (const k of ["sys", "ci", "rem", "max_tokens"]) if (arm[k] === undefined) throw new Error(`vxa-hook: ${k} missing in ${process.env.VXA_PROMPT_JSON}`);
  const f0 = globalThis.fetch;
  let n = 0;
  globalThis.fetch = async (input, init) => {
    const url = typeof input === "string" ? input : input?.url ?? String(input);
    if (init?.method === "POST" && /\/v1\/chat\/completions$/.test(url) && typeof init.body === "string") {
      const b = JSON.parse(init.body);
      const m = b.messages;
      const sys = Array.isArray(m) && m[0]?.role === "system" ? m[0].content : null;
      if (typeof sys === "string" && sys.includes(CUT)) {
        const last = m[m.length - 1];
        if (last?.role !== "user" || typeof last.content !== "string") throw new Error("vxa-hook: answer request without a final user message");
        const i = sys.indexOf(CUT);
        const hadContext = sys.slice(i).includes("\n\nContext:");
        m[0] = { ...m[0], content: arm.sys + (hadContext ? arm.ci : "") + sys.slice(i) };
        const j = last.content.lastIndexOf("\n\n(Response style:");
        m[m.length - 1] = { ...last, content: (j >= 0 ? last.content.slice(0, j) : last.content) + "\n\n(Response style: " + arm.rem + ")" };
        b.max_tokens = arm.max_tokens;
        n += 1;
        log({ n, rewritten: true, hadContext, hadStyle: j >= 0, max_tokens: b.max_tokens, sys: m[0].content, user: m[m.length - 1].content });
        init = { ...init, body: JSON.stringify(b) };
      } else {
        log({ rewritten: false, reason: "no answer-prompt marker", sysHead: typeof sys === "string" ? sys.slice(0, 120) : null });
      }
    }
    return f0(input, init);
  };
}

if (process.env.VXA_FACTS_JSON) {
  // module.registerHooks (sync, in-thread) covers both require() and import: tsx may compile the tree's .ts to CJS, where async ESM hooks never fire.
  const target = process.env.VXA_FACTS_JSON;
  if (!existsSync(target)) throw new Error(`vxa-hook: VXA_FACTS_JSON ${target} does not exist`);
  JSON.parse(readFileSync(target, "utf8")); // must be valid JSON
  const href = pathToFileURL(target).href;
  let hits = 0;
  registerHooks({
    resolve(specifier, context, next) {
      const spec = specifier.split("?")[0];
      const parent = (context.parentURL ?? "").split("?")[0];
      if (/(^|\/)facts\.v1\.json$/.test(spec) && /\/src\/rag\/facts\.ts$/.test(parent)) {
        hits += 1; log({ factsOverride: target, specifier, hits });
        const r = next(specifier, context);
        return { ...r, url: href, shortCircuit: true };
      }
      return next(specifier, context);
    },
  });
}
