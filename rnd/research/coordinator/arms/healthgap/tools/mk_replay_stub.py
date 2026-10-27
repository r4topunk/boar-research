"""HEALTHGAP 0-LLM route replay: writes <tree>/be/replay-stub.ts = <tree>/be/adapter.ts with the generation engine replaced by
a stub that never loads a model (records each generation request as a zero-token generation and returns "[STUB-MODEL]").
Everything else is the adapter's: real retrieval over the kit, the live detector (:8094), the tree's answer.ts, the trace.
Usage: python3 -I mk_replay_stub.py <tree>"""
import sys
t = sys.argv[1]; s = open(f"{t}/be/adapter.ts").read()
old = "    : await (server ? makeServerEngine : makeEngine)(genPath, (deepEntry ?? entry).filename, R0.seed, R0.temperature, onGeneration);"
assert s.count(old) == 1
s = s.replace(old, "    : stubEngine((deepEntry ?? entry).filename, onGeneration) as any;")
s += '''
// HEALTHGAP replay stub (tools/mk_replay_stub.py): no model; a generation request is recorded (0 tokens) and answered "[STUB-MODEL]".
function stubEngine(fileName: string, onGeneration: (g: Generation) => void) {
  return {
    loadMs: 0,
    async load() { return { fit: null, warning: null } as any; },
    async stop() {},
    getModelInfo: () => ({ filename: fileName }),
    hasEmbeddedChatTemplate: () => true,
    async estimateFit() { return null; },
    setAnswerPrefix() {},
    async generate(o: any): Promise<string> {
      onGeneration({ promptTokens: 0, promptMs: 0, predictedTokens: 0, predictedMs: 0, firstTextMs: 0, timedOut: false, temperature: 0 });
      o.onToken?.("[STUB-MODEL]");
      return "[STUB-MODEL]";
    },
  };
}
'''
open(f"{t}/be/replay-stub.ts", "w").write(s); print(f"{t}/be/replay-stub.ts")
