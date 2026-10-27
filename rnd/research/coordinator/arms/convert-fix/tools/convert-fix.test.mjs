// usage: [LIB=<dir with wiki-pack-lib.mjs>] node --test convert-fix.test.mjs   (node:test; 0 LLM)
// 10 {{convert}} strings taken verbatim from simplewiki-20261001 (dump-count.json samples), run through cleanWikivoyage.
import test from "node:test";
import assert from "node:assert/strict";
const lib = process.env.LIB ?? new URL("./patched/scripts/lib", import.meta.url).pathname;
const { cleanWikivoyage } = await import(`${lib}/wiki-pack-lib.mjs`);
const cases = [
  ["The wall stretches {{convert|21196|km|mi}}.", "The wall stretches 21196 km."],
  ["It is {{convert|8848|m|abbr=off|disp=or}} high.", "It is 8848 m high."],
  ["It is {{convert|3|to|12|m}} long.", "It is 3 to 12 m long."],
  ["Size {{Convert|3|-|6|cm}}.", "Size 3 - 6 cm."],
  ["Area {{convert|abbr=off|251,826|mi2}}.", "Area 251,826 sq mi."],
  ["Area {{convert|2,220,930|km2|sqmi|abbr=on|sigfig=5}}.", "Area 2,220,930 km²."],
  ["Hot {{cvt|40.5|C|F}} today.", "Hot 40.5 °C today."],
  ["Cold {{cvt|-52.6|C|F}}.", "Cold -52.6 °C."],
  ["Speed {{convert|30|km/s|mi/s|abbr=on|lk=on}}.", "Speed 30 km/s."],
  ["Depth {{convert|\n6263|m|abbr=off|disp=or}}.", "Depth 6263 m."],
];
for (const [i, [src, want]] of cases.entries())
  test(`convert case ${i + 1}: ${src.slice(0, 40).replace(/\n/g, " ")}`, () => assert.equal(cleanWikivoyage(src).replace(/\s+/g, " ").trim(), want));
test("non-convert templates still dropped", () => assert.equal(cleanWikivoyage("A{{flag|X}} b."), "A b."));
