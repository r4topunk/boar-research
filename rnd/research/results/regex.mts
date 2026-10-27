import fs from "fs";
const rows = JSON.parse(fs.readFileSync("emb.json", "utf8"));
const out: Record<string, boolean[]> = {};
for (const v of ["upstream", "iosmain"]) { const m = await import(`${process.argv[2]}/context.${v}.ts`); out[v] = rows.map((r: any) => m.isHealthQuestion(r.q)); }
fs.writeFileSync("regex.json", JSON.stringify(out)); console.log("ok");
