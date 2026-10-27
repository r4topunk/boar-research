// llama.rn stub: the embedding context returns the query vector the Node recorder got from bge-small (native work on the
// phone, excluded from the JS stage table).
import { timed } from "./clock";
declare const globalThis: any;
export async function initLlama() {
  return {
    embedding: async (text: string) => timed("embedReplay", () => {
      const v = globalThis.__REPLAY.embeds[text];
      if (!v) throw new Error(`no recorded embedding for: ${text}`);
      return { embedding: v };
    }),
    release: async () => {},
  };
}
export function getBackendDevicesInfo() { return []; }
export async function loadLlamaModelInfo() { return {}; }
export class LlamaContext {}
export default { initLlama, getBackendDevicesInfo, LlamaContext, loadLlamaModelInfo };
