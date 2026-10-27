// The app's fzstd, timed ("zstd").
import { decompress as fz } from "../app/node_modules/fzstd/esm/index.mjs";
import { timed } from "./clock";
export function decompress(d: Uint8Array, out?: Uint8Array) { return timed("zstd", () => fz(d, out)); }
