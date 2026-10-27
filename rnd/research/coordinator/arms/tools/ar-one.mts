const { arithmeticAnswer } = await import(process.argv[2] + "/src/routing/arithmetic.ts");
for (const q of process.argv.slice(3)) console.log(JSON.stringify(arithmeticAnswer(q)));
