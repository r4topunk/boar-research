// exp-08: O2 test-set gates A1-A3 (exp-03 spec §5.1) on Lantern's 32 fixture cases, per variant (v1 / a / c).
// Run from the patched 611a4b92 tree: tsx kiln/testset_gates.mts
import { readFileSync } from "node:fs";
import { o2Decide } from "../src/routing/o2WeakSupport.ts";
const cases = readFileSync(new URL("../src/routing/testing/fixtures/o2-testset.jsonl", import.meta.url), "utf8").trim().split("\n").map((l) => JSON.parse(l));
const out: any = {};
for (const v of ["", "a", "c"]) {
  process.env.EXPO_PUBLIC_O2_V2 = v;
  const dec = cases.map((c: any) => ({ id: c.case_id, bucket: c.bucket, ref: c.reference, ...o2Decide(c.question, c.passages) }));
  const b = (k: string) => dec.filter((d) => d.bucket === k);
  out[v || "v1"] = {
    A1_must_refuse_refused: `${b("must_refuse").filter((d) => d.action === "refuse").length}/${b("must_refuse").length}`,
    A2_must_keep_kept: `${b("must_keep").filter((d) => d.action === "keep").length}/${b("must_keep").length}`,
    A3_gate_kept: `${b("gate_must_not_worsen").filter((d) => d.action === "keep").length}/${b("gate_must_not_worsen").length}`,
    changed_vs_reference: dec.filter((d) => d.action !== d.ref).map((d) => `${d.id} ${d.ref}->${d.action} (${d.reason})`),
  };
}
console.log(JSON.stringify(out, null, 1));
