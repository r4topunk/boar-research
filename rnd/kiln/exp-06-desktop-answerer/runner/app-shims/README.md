# App shims for the desktop runner

TL;DR: lets `eval/runner/desktop.ts --retrieval app` import the source tree's own retrieval code (`src/rag/retrieve.ts`,
`seedCorpus.ts`, `packs.ts`, `db.ts`, `embed.ts`) in Node instead of mirroring it. Only native modules are replaced:

| Module | Shim |
|---|---|
| `expo-sqlite` | `node:sqlite` (one file per database under `${BOAR_APP_DIR}/SQLite/`) |
| `expo-file-system`, `expo-file-system/legacy` | the real file system under `${BOAR_APP_DIR}` (= `documentDirectory`) |
| `llama.rn` | node-llama-cpp embedding context (the app's `EmbeddingEngine` runs unchanged on top) |
| `react-native` | `Platform.OS = "node"` |

Installed packs are what the app would see: files under `${BOAR_APP_DIR}/corpus/` named as in the catalog.
Loaded with `node --import ./eval/runner/app-shims/register.mjs` (tsx forwards it).
