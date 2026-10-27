/**
 * G5 cold load (reconstruction of the r6 measurement, whose script was not saved): one fresh process per run.
 * json parse = readFileSync + JSON.parse of src/rag/facts.v1.json (separate, informative); module load = dynamic import of
 * src/rag/facts.ts (includes its own JSON import); cold first call = first factsAnswer() (builds the alias index).
 * Bar (CUT7 criterion G5): module load + first call <= 250 ms. Usage: tsx g5_cold.mts <tree>   (run 5x)
 */
import { readFileSync } from "node:fs";
import { performance } from "node:perf_hooks";
const tree = process.argv[2];
const a = performance.now(); JSON.parse(readFileSync(`${tree}/src/rag/facts.v1.json`, "utf8")); const jp = performance.now() - a;
const b = performance.now(); const { factsAnswer } = await import(`${tree}/src/rag/facts.ts`); const ml = performance.now() - b;
const c = performance.now(); factsAnswer("How big is Iceland in square kilometres?"); const fc = performance.now() - c;
console.log(`json parse ${jp.toFixed(1)} ms; facts.ts module load ${ml.toFixed(1)} ms; cold first call (index build) ${fc.toFixed(1)} ms; load+first call ${(ml + fc).toFixed(1)} ms`);
