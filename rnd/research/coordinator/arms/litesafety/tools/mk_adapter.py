"""LITESAFETY side adapter: <tree>/be/adapter-litesafety.ts = <tree>/be/adapter.ts (55adc5ff...) + NUMGUARD eval switch (numguard-r3-adapter.patch)
+ the lite5 hunks (qwen3-1.7b-q4km entries, BOAR_SERVER_EXTRA_ARGS, versions server.extra_args). Also writes be/replay-stub-litesafety.ts
(= healthgap/tools/mk_replay_stub.py applied to the side adapter). be/adapter.ts is not modified. Usage: python3 -I mk_adapter.py <tree>"""
import sys, hashlib
t = sys.argv[1]; src = open(f"{t}/be/adapter.ts").read()
assert hashlib.sha256(src.encode()).hexdigest().startswith("55adc5ff83d37d20"), "adapter.ts sha"
def rep(s, old, new):
    assert s.count(old) == 1, old[:60]; return s.replace(old, new)
s = src
g = '  "gemma-4-26b-a4b-ud-q2kxl": { file: "gemma-4-26B-A4B-it-UD-Q2_K_XL.gguf", sha256: "2a1d26dfe6ea00a467940a5728316af6edb366bbdba950d65b85d232392fb658" },\n'
s = rep(s, g, g + '  // LITE2/LITE5 (2026-10-15): unsloth/Qwen3-1.7B-GGUF @ d7f544ee (Apache-2.0; Q4_K_M); stock llama.cpp b11010; thinking OFF (BOAR_SERVER_EXTRA_ARGS="--reasoning off" + enable_thinking:false).\n'
          '  "qwen3-1.7b-q4km": { file: "lite/Qwen3-1.7B-Q4_K_M.gguf", sha256: "b139949c5bd74937ad8ed8c8cf3d9ffb1e99c866c823204dc42c0d91fa181897" },\n')
c = "const ADAPTER_CATALOG: Record<string, Record<string, unknown>> = {\n"
s = rep(s, c, c + '  // LITE2/LITE5: same shape as the BONSAI2 entries (roles general + fast, answerTier default), so the fast tier picks it.\n'
          '  "qwen3-1.7b-q4km": {\n    id: "qwen3-1.7b-q4km", kind: "llm", label: "Qwen3-1.7B (Q4_K_M)",\n'
          '    filename: "models/qwen3-1.7b-q4km.gguf", sizeBytes: 1107409472, answerTier: "default",\n'
          '    capabilities: { roles: ["general", "fast"], usesChatTemplate: true },\n  },\n')
k = '...(process.env.BOAR_KV_TYPE ? ["--cache-type-k", process.env.BOAR_KV_TYPE, "--cache-type-v", process.env.BOAR_KV_TYPE] : [])]; // KVQ8 arm: KV cache type (unset = llama-server default f16)'
s = rep(s, k, '...(process.env.BOAR_KV_TYPE ? ["--cache-type-k", process.env.BOAR_KV_TYPE, "--cache-type-v", process.env.BOAR_KV_TYPE] : []), // KVQ8 arm: KV cache type (unset = llama-server default f16)\n'
          '                // BONSAI2: extra llama-server args, whitespace-split, appended last (unset = byte-identical args); recorded in versions["server.extra_args"].\n'
          '                ...(process.env.BOAR_SERVER_EXTRA_ARGS ? process.env.BOAR_SERVER_EXTRA_ARGS.trim().split(/\\s+/) : [])];')
v = '    ...(process.env.BOAR_SAMPLER_JSON ? { "sampler.override": process.env.BOAR_SAMPLER_JSON } : {}),\n'
s = rep(s, v, v + '    ...(server && process.env.BOAR_SERVER_EXTRA_ARGS ? { "server.extra_args": process.env.BOAR_SERVER_EXTRA_ARGS.trim() } : {}),\n')
e = '    ...(emergencyScore ? { emergencyScore } : {}),\n'
s = rep(s, e, e + '    // NUMGUARD (engine deps.numguard, src/routing/numguard.ts): the eval-side switch; the engine reads deps only.\n'
          '    ...(process.env.NUMGUARD === "1" ? { numguard: true } : {}),\n')
open(f"{t}/be/adapter-litesafety.ts", "w").write(s)
old = "    : await (server ? makeServerEngine : makeEngine)(genPath, (deepEntry ?? entry).filename, R0.seed, R0.temperature, onGeneration);"
st = rep(s, old, "    : stubEngine((deepEntry ?? entry).filename, onGeneration) as any;")
M = "// HEALTHGAP replay stub (tools/mk_replay_stub.py)"; st += "\n" + M + open(f"{t}/be/replay-stub.ts").read().split(M)[1]  # the stubEngine function, verbatim
open(f"{t}/be/replay-stub-litesafety.ts", "w").write(st)
for f in ("adapter-litesafety.ts", "replay-stub-litesafety.ts"): print(f, hashlib.sha256(open(f"{t}/be/{f}", "rb").read()).hexdigest()[:16])
