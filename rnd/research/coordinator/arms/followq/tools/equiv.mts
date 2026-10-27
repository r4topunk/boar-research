// equiv.mts <engine-tree>: the TS rule (followUpQuery.ts) vs the FOLLOWQ python rule (variants.json): follow-up flag and Q1 string on the 192 dev chat messages.
import { readFileSync } from "node:fs";
const T = process.argv[2];
const { isFollowUp, followUpQuery } = await import(`${T}/src/routing/followUpQuery.ts`);
const V = JSON.parse(readFileSync("<workspace>/rnd/research/coordinator/arms/followq/variants.json", "utf8"));
let bad = 0, fl = 0;
for (const v of V) {
  const f = isFollowUp(v.q.Q0, v.history), q = followUpQuery(v.q.Q0, v.history);
  if (f) fl++;
  if (f !== v.follow || q !== (v.follow ? v.q.Q1 : v.q.Q0)) { bad++; console.log("DIFF", v.id, f, v.follow, JSON.stringify(q)); }
}
console.log(`192 messages, flagged ${fl}, mismatches ${bad}`);
