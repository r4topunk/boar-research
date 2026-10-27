// microbench: healthTopicFallback cost per call (switch off vs 1), on 2 queries (jellyfish card, no card)
(async () => {
const fb: any = await import("<workspace>/kiln-local/rs-H2/src/routing/healthTopicFallback.ts");
const ctx: any = await import("<workspace>/kiln-local/rs-H2/src/routing/context.ts");
const qs = ["My friend just got stung by a jellyfish while swimming in Thailand. Should I pour vinegar or fresh water on it?", "How do I treat a burn on my arm with boiling water?", "What are the symptoms of dehydration in a toddler?"];
for (const mode of ["", "1"]) {
  if (mode) process.env.RS_HEALTH_TOPIC_FB = mode; else delete process.env.RS_HEALTH_TOPIC_FB;
  for (let w = 0; w < 200; w++) for (const q of qs) fb.healthTopicFallback(q, null, []);
  const t0 = process.hrtime.bigint(); const N = 2000;
  for (let i = 0; i < N; i++) for (const q of qs) fb.healthTopicFallback(q, null, []);
  console.log(`switch=${mode || "off"}: ${(Number(process.hrtime.bigint() - t0) / 1e6 / (N * qs.length)).toFixed(4)} ms per call`);
}
const t0 = process.hrtime.bigint(); for (let i = 0; i < 6000; i++) ctx.healthTopicTerms(qs[i % 3], null);
console.log(`healthTopicTerms alone: ${(Number(process.hrtime.bigint() - t0) / 1e6 / 6000).toFixed(4)} ms per call`);
})();
