import fs from "fs";
const m = await import("../health-embed/context.upstream.ts");
const S = JSON.parse(fs.readFileSync("sample400.json", "utf8"));
fs.writeFileSync("rx.json", JSON.stringify(S.map((q) => m.isHealthQuestion(q)))); console.log("ok");
