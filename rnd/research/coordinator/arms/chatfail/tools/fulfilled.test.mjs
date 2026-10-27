// 12 hand-made unit answers (6 fulfilled, 6 not) for tools/fulfilled.mjs, plus refusal checks. Run: node tools/fulfilled.test.mjs
import assert from "node:assert/strict";
import { fulfilled, refusal } from "./fulfilled.mjs";
const T = [
  // ---- fulfilled (6)
  [true, { expected_intent: "code", turnText: "can you write it?", answer: "Sure:\n```solidity\ncontract Counter {\n  uint public n;\n  function inc() public { n += 1; }\n}\n```\nIt counts calls." }],
  [true, { expected_intent: "code", turnText: "write it in Python", answer: "def orbit(r, t):\n    x = r * cos(t)\n    y = r * sin(t)\n    return x, y\nThat gives one point." }],
  [true, { expected_intent: "format", turnText: "put that in a table", answer: "| Feature | Wallet A | Wallet B |\n|---|---|---|\n| Security | High | Low |" }],
  [true, { expected_intent: "format", turnText: "can you put the steps in a numbered list?", answer: "1. Rinse the burn with cool water.\n2. Cover it loosely.\n3. Do not pop blisters." }],
  [true, { expected_intent: "translate", turnText: "em português", answer: "Os contratos inteligentes são programas que são executados em uma blockchain e que fazem o que foi escrito para eles." }],
  [true, { expected_intent: "format", turnText: "shorter", prevAnswer: "Vaccines train the immune system by showing it a harmless piece of a germ so that it can build memory cells and antibodies, which then respond faster if the real germ ever appears later.", answer: "They teach your body to recognise a germ safely." }],
  // ---- not fulfilled (6)
  [false, { expected_intent: "code", turnText: "can you write it?", answer: "Sorry, but I can't write the code here. A smart contract is a program on a blockchain that runs automatically." }],
  [false, { expected_intent: "code", turnText: "what does it look like?", answer: "A smart contract looks like a digital program that lives on the blockchain and runs when conditions are met." }],
  [false, { expected_intent: "format", turnText: "put that in a table", answer: "Hardware wallets are more secure than paper wallets because they keep the keys offline, but paper wallets are cheaper." }],
  [false, { expected_intent: "format", turnText: "shorter", prevAnswer: "Short earlier answer here.", answer: "Here is a much longer rewrite that, despite being asked to shorten, repeats everything and adds more detail on top of the previous reply." }],
  [false, { expected_intent: "translate", turnText: "translate that to Portuguese", answer: "I can't translate that, but the answer is that vaccines train the immune system and that it then remembers the germ." }],
  [false, { expected_intent: "translate", turnText: "say it in German", answer: "Vaccines show the body a harmless piece of the germ, so that it can learn to fight it and remember it for the future." }],
];
let n = 0;
for (const [want, c] of T) { const r = fulfilled(c); assert.equal(r.ok, want, `case ${n}: ${JSON.stringify(r)}`); n++; }
for (const [t, want] of [["I'm sorry, but I can't help with that.", true], ["Sure. I can't run it, but here is the code: x = 1", true], ["Here is the function you asked for.", false],
  ["Unfortunately the library has nothing on this.", true], ["You can't deploy it without gas.", false], ["Não posso fazer isso.", true]]) assert.equal(refusal(t), want, t);
console.log(`fulfilled.test: ${n} cases + 6 refusal checks passed`);
