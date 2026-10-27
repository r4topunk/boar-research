import { readFileSync } from "node:fs";
const [mod, ...files] = process.argv.slice(2);
const NG: any = await import(mod);
const CX: any = await import("<workspace>/kiln-local/be-0cfd4a77-cut7-numguard/src/routing/context.ts");
for (const f of files) { const [name,path]=f.split("="); const ids:string[]=[]; let n=0;
  for (const q of readFileSync(path,"utf8").split("\n").filter(Boolean).map((l)=>JSON.parse(l))) { n++; if (NG.numericGuard(q.question, CX.isPortugueseQuestion(q.question))) ids.push(q.id); }
  console.log(`${name}: n=${n} guard=${ids.length} [${ids.join(" ")}]`); }
