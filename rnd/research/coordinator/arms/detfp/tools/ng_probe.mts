// DETFP: the PR tree's own numericGuard / numguardHealthLexicon / healthGap classify on the 7 detector FPs (booleans only, no text).
import { readFileSync } from "node:fs";
const T = "<workspace>/kiln-local/be-cut7-warn/src/routing";
const NG: any = await import(`${T}/numguard.ts`); const HG: any = await import(`${T}/healthGap.ts`);
const IDS = "v02-reasoning-A02 v02-reasoning-A03 v02-reasoning-A06 v02-reasoning-A07 v02-reasoning-B01 v02-reasoning-B09 v02-crypto-B03".split(" ");
const Q = new Map(readFileSync("<private held-out dir>", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)).map((q: any) => [q.id, q]));
for (const id of IDS) { const q: any = Q.get(id); console.log(JSON.stringify({ id, numericGuard: NG.numericGuard(q.question, false, [q.question]), healthLexicon: NG.numguardHealthLexicon(q.question), healthGap: HG.classify(q.question, [q.question])?.kind ?? HG.classify(q.question, [q.question]) ?? null })); }
