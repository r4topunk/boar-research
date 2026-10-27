const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const llama = await getLlama({ logLevel: "error" });
for (const p of process.argv.slice(2)) {
  const m = await llama.loadModel({ modelPath: p }); const rr = await m.createRankingContext();
  const s = await rr.rankAll("What is the capital of France?", ["Paris is the capital and largest city of France.", "Bananas are an elongated, edible fruit.", "Berlin is the capital of Germany."]);
  const s2 = await rr.rankAll("Which land animal runs fastest?", ["The cheetah is the fastest land animal, reaching 93 to 104 km/h.", "The sailfish is a fish that can swim at high speed.", "The common ostrich is the largest living bird."]);
  console.log(p.split("/").pop(), s.map((x) => x.toFixed(4)), s2.map((x) => x.toFixed(4)));
  await rr.dispose(); await m.dispose();
}
