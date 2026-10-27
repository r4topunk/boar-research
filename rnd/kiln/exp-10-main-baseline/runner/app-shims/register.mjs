// Points native app modules at Node shims (see README.md). registerHooks (sync) covers require() and import, so it
// works for trees compiled as CommonJS by tsx too.
import { registerHooks } from "node:module";
const SHIMS = {
  "expo-sqlite": "./expo-sqlite.mjs",
  "expo-file-system": "./expo-file-system.mjs",
  "expo-file-system/legacy": "./expo-file-system.mjs",
  "llama.rn": "./llama-rn.mjs",
  "react-native": "./react-native.mjs",
};
registerHooks({
  resolve(specifier, context, next) {
    if (SHIMS[specifier]) return { url: new URL(SHIMS[specifier], import.meta.url).href, shortCircuit: true };
    return next(specifier, context);
  },
});
