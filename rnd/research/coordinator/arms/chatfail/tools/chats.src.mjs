// Source of boar-eval/bench/slices/chat-fu-v1/chats.jsonl (agent-written dev data; run: node tools/chats.src.mjs <out.jsonl>).
// Turn = [text, expected_intent, expected_anchor (1-based turn whose subject applies), capability_request (0|1)].
// expected_intent: lookup | chat | code | format | translate | compare.  capability_request = the user asks the assistant to PRODUCE or
// TRANSFORM something (code, example program, table, shorter, translation) rather than to look something up.
import fs from "node:fs";
const L = "lookup", C = "code", F = "format", T = "translate", K = "compare", H = "chat";
const chats = [
  // ---- intent-change chats (24) ----
  ["c01", "crypto", "change", [ // r4to's live chat, boar-ios 2026-10-18
    ["What can a smart contract do?", L, 1, 0], ["what it look like?", C, 1, 1], ["but how it look like? the program", C, 1, 1],
    ["i want to see the code", C, 1, 1], ["can you write it?", C, 1, 1], ["not even an example?", C, 1, 1]]],
  ["c02", "crypto", "change", [
    ["How does Ethereum staking work?", L, 1, 0], ["what is the minimum to stake?", L, 1, 0], ["and what happens if the validator goes offline?", L, 1, 0],
    ["show me what the deposit call looks like in code", C, 1, 1], ["can you write it in Solidity?", C, 1, 1], ["just the function, no explanation", C, 1, 1]]],
  ["c03", "crypto", "change", [
    ["Why are Ethereum gas fees so high sometimes?", L, 1, 0], ["who decides how much I pay?", L, 1, 0], ["What is EIP-1559?", L, 3, 0],
    ["how does it change the fee?", L, 3, 0], ["can you show the fee formula in code?", C, 3, 1], ["write it in Python", C, 3, 1]]],
  ["c04", "crypto", "change", [
    ["What is an ERC-20 token?", L, 1, 0], ["how is it different from Ether itself?", L, 1, 0], ["who can create one?", L, 1, 0],
    ["what does the contract for it look like?", C, 1, 1], ["can you write one for me?", C, 1, 1], ["how do I deploy it?", L, 1, 0]]],
  ["c05", "crypto", "change", [
    ["What is a hardware wallet?", L, 1, 0], ["is it safer than a phone app?", L, 1, 0], ["compare it with a paper wallet", K, 1, 0],
    ["put that in a table", F, 1, 1], ["shorter", F, 1, 1], ["em português", T, 1, 1]]],
  ["c06", "crypto", "change", [
    ["What is a Merkle tree?", L, 1, 0], ["why does Bitcoin use it?", L, 1, 0], ["what does one look like?", C, 1, 1],
    ["can you show me an example in JavaScript?", C, 1, 1], ["just the hash part, five lines max", C, 1, 1]]],
  ["c07", "travel", "change", [
    ["What are the best neighborhoods to stay in Lisbon?", L, 1, 0], ["is it safe at night?", L, 1, 0], ["and getting around?", L, 1, 0],
    ["can you put that in a table?", F, 1, 1], ["shorter please", F, 1, 1], ["em português", T, 1, 1]]],
  ["c08", "travel", "change", [
    ["What is the best time of year to visit Kyoto?", L, 1, 0], ["what about the food there?", L, 1, 0], ["and the temples?", L, 1, 0],
    ["compare it with Osaka", K, 1, 0], ["in bullet points", F, 1, 1], ["say that in Spanish", T, 1, 1]]],
  ["c09", "travel", "change", [
    ["Is Bali worth visiting in the rainy season?", L, 1, 0], ["how bad is the rain really?", L, 1, 0], ["What is Nyepi?", L, 3, 0],
    ["can I visit during it?", L, 3, 0], ["give me that as a short checklist", F, 3, 1]]],
  ["c10", "travel", "change", [
    ["How many days do I need for the Ring Road in Iceland?", L, 1, 0], ["can I do it in winter?", L, 1, 0], ["what does the road look like in January?", L, 1, 0],
    ["compare it with the Golden Circle", K, 1, 0], ["translate that to Portuguese", T, 1, 1], ["and in a table?", F, 1, 1]]],
  ["c11", "travel", "change", [
    ["Do I need a permit for Machu Picchu?", L, 1, 0], ["how far in advance should I book?", L, 1, 0], ["What is the Inca Trail like?", L, 3, 0],
    ["is it hard for beginners?", L, 3, 0], ["summarize it in two lines", F, 3, 1]]],
  ["c12", "travel", "change", [
    ["What should I know before taking the U-Bahn in Berlin?", L, 1, 0], ["do I need to validate the ticket?", L, 1, 0], ["how much is a day pass?", L, 1, 0],
    ["what about the airport train?", L, 1, 0], ["say it in German", T, 1, 1]]],
  ["c13", "first aid", "change", [
    ["What should I do for a minor burn?", L, 1, 0], ["how long should I cool it?", L, 1, 0], ["what about blisters?", L, 1, 0],
    ["can you put the steps in a numbered list?", F, 1, 1], ["shorter", F, 1, 1], ["em português", T, 1, 1]]],
  ["c14", "first aid", "change", [
    ["How do I do CPR on an adult?", L, 1, 0], ["how fast should the compressions be?", L, 1, 0], ["what about a child?", L, 1, 0],
    ["give me the steps as a checklist", F, 1, 1], ["translate it to Spanish", T, 1, 1]]],
  ["c15", "first aid", "change", [
    ["What do I do if someone has a nosebleed?", L, 1, 0], ["should I tilt their head back?", L, 1, 0], ["when should I call an ambulance?", L, 1, 0],
    ["explain it like I'm five", F, 1, 1], ["can you make that shorter?", F, 1, 1]]],
  ["c16", "first aid", "change", [
    ["How do I help a choking adult?", L, 1, 0], ["what about a baby?", L, 1, 0], ["how is it different?", L, 1, 0],
    ["compare the two in a table", K, 1, 0], ["shorter", F, 1, 1]]],
  ["c17", "first aid", "change", [
    ["How do I treat a sprained ankle at home?", L, 1, 0], ["how long until I can walk on it?", L, 1, 0], ["when should I see a doctor?", L, 1, 0],
    ["can you put that in a table?", F, 1, 1], ["em português", T, 1, 1]]],
  ["c18", "science", "change", [
    ["How does photosynthesis work?", L, 1, 0], ["where does it happen?", L, 1, 0], ["What is ATP?", L, 3, 0],
    ["how does it connect to the light reactions?", L, 3, 0], ["can you give me an example from everyday life?", H, 3, 0]]],
  ["c19", "science", "change", [
    ["What happens when something falls into a black hole?", L, 1, 0], ["can light escape?", L, 1, 0], ["What is Hawking radiation?", L, 3, 0],
    ["why does it matter?", L, 3, 0], ["compare it with a neutron star", K, 3, 0], ["in a table", F, 3, 1]]],
  ["c20", "science", "change", [
    ["How do vaccines train the immune system?", L, 1, 0], ["what are the side effects?", L, 1, 0], ["are they safe for kids?", L, 1, 0],
    ["translate that to Portuguese", T, 1, 1], ["shorter", F, 1, 1]]],
  ["c21", "science", "change", [
    ["Why do planets orbit the sun instead of falling into it?", L, 1, 0], ["what keeps them going?", L, 1, 0], ["can you show me a simulation of that in code?", C, 1, 1],
    ["write it in Python", C, 1, 1], ["how would I plot the orbit?", C, 1, 1]]],
  ["c22", "science", "change", [
    ["What does DNA actually do?", L, 1, 0], ["how long is it?", L, 1, 0], ["how is it copied?", L, 1, 0],
    ["what does a sequence look like?", L, 1, 0], ["compare DNA and RNA", K, 5, 0]]],
  ["c23", "science", "change", [
    ["What is the greenhouse effect?", L, 1, 0], ["is it the same as global warming?", L, 1, 0], ["what causes it?", L, 1, 0],
    ["give me that in bullet points", F, 1, 1], ["translate it to Portuguese", T, 1, 1]]],
  ["c24", "science", "change", [
    ["How does a neural network learn?", L, 1, 0], ["How does backpropagation adjust the weights of a network?", L, 2, 0], ["what does that look like in code?", C, 2, 1],
    ["write it using only numpy", C, 2, 1], ["not a library, from scratch?", C, 2, 1]]],
  // ---- control chats (6): follow-ups stay lookup; includes non-technical "look like" / "example of" asks that L2 must not turn into code ----
  ["c25", "crypto", "control", [
    ["What is the Bitcoin halving?", L, 1, 0], ["how often does it happen?", L, 1, 0], ["when is the next one?", L, 1, 0],
    ["does it affect the price?", L, 1, 0], ["Who invented Bitcoin?", L, 5, 0]]],
  ["c26", "travel", "control", [
    ["What is the cheapest way to get from Narita airport to central Tokyo?", L, 1, 0], ["how long does it take?", L, 1, 0], ["what does Shinjuku Station look like at rush hour?", L, 3, 0],
    ["is it easy to get lost there?", L, 3, 0], ["What about Osaka?", L, 5, 0]]],
  ["c27", "first aid", "control", [
    ["What should I do about a bee sting?", L, 1, 0], ["how do I remove the stinger?", L, 1, 0], ["when is it an emergency?", L, 1, 0],
    ["What are the signs of a severe allergic reaction to a sting?", L, 4, 0]]],
  ["c28", "science", "control", [
    ["How does a volcano erupt?", L, 1, 0], ["what is lava made of?", L, 1, 0], ["can you give me an example of a supervolcano?", L, 1, 0],
    ["which one was the biggest?", L, 3, 0], ["what's an example of an igneous rock?", L, 5, 0]]],
  ["c29", "science", "control", [
    ["Why does the moon have phases?", L, 1, 0], ["does the far side always stay dark?", L, 1, 0], ["what does the surface look like up close?", L, 1, 0],
    ["who walked on it first?", L, 1, 0], ["list the phases in order", L, 1, 0]]],
  ["c30", "travel", "control", [
    ["What is there to see in Rome in two days?", L, 1, 0], ["do I need tickets for the Colosseum?", L, 2, 0], ["what does the Forum look like today?", L, 3, 0],
    ["is it worth it?", L, 3, 0], ["how do I get there from Termini?", L, 3, 0]]],
];
const out = process.argv[2];
const rows = chats.map(([id, topic, kind, turns]) => {
  if (turns.length < 4 || turns.length > 6) throw new Error(id + " turns " + turns.length);
  turns.forEach(([, , a], i) => { if (a < 1 || a > i + 1) throw new Error(id + " anchor " + i); });
  return { chat: id, topic, kind, turns: turns.map(([text, expected_intent, expected_anchor, cap], i) => ({ turn: i + 1, text, expected_intent, expected_anchor, capability_request: !!cap })) };
});
if (out) fs.writeFileSync(out, rows.map((r) => JSON.stringify(r)).join("\n") + "\n");
const n = rows.reduce((s, r) => s + r.turns.length, 0), cap = rows.flatMap((r) => r.turns).filter((t) => t.capability_request).length;
console.error(`chats ${rows.length} turns ${n} capability ${cap} change ${rows.filter(r=>r.kind==="change").length} control ${rows.filter(r=>r.kind==="control").length}`);
