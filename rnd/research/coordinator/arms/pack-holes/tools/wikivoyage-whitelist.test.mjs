// usage: node wikivoyage-whitelist.test.mjs <path/to/patched/wiki-pack-lib.mjs>   (exit 1 on any failure)
import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
const { cleanWikivoyage } = await import(pathToFileURL(process.argv[2]).href);
const cases = [
  ["Schiphol Airport ({{IATA|AMS}}) is big.", "Schiphol Airport (AMS) is big."],
  ["It occupies an area of {{km2|77}}.", "It occupies an area of 77 km²."],
  ["about {{convert|500|m|ft}} high", "about 500 m high"],
  ["between {{convert|40|to|50|F|C}} in winter", "between 40 to 50 °F in winter"],
  ["{{convert|202|km|0|abbr=on}} away", "202 km away"],
  ["temperatures between {{C|16-17}} and {{c|37}}", "temperatures between 16-17 °C and 37 °C"],
  ["Mains from {{EUR|17.80}}, taxi {{USD|5}}, bus {{PHP|50-200}}.", "Mains from €17.80, taxi $5, bus ₱50-200."],
  ["fare is {{currency|ZAR|500}}", "fare is R500"],
  ["Call {{phone|+31 412 484 41}}.", "Call +31 412 484 41."],
  ["Abashiri ({{lang|ja|網走}}) is a city", "Abashiri (網走) is a city"],
  ["The belfry is a {{UNESCO}}.", "The belfry is a UNESCO World Heritage Site."],
  ["Take {{European road|UK|A|1094}} and {{European road|UK|M|4}}", "Take A1094 and M4"],
  ["Trams {{rint|amsterdam|5}} and {{rint|bus}}", "Trams 5 and"],
  ["by Laura Pedersen ({{ISBN|978-1605206219}})", "by Laura Pedersen (ISBN 978-1605206219)"],
  ["leaves at {{time|8:30AM|5PM}}", "leaves at 8:30AM–5PM"],
  ["pronounced {{IPA|tʃ}}", "pronounced /tʃ/"],
  ["Link ([https://example.org/x ])", "Link"],
  ["* {{see|name=Belfry|alt=|address=Grote Markt|directions=|hours=|price={{EUR|5}}|content=A {{UNESCO}}.}}", "- Belfry: Grote Markt. €5. A UNESCO World Heritage Site."],
  ["a {{dead link|date=May 2025}} stays dropped {{flag|Austria}}.", "a stays dropped ."],
  ["Mongolian ({{unknowntpl|x}}) text", "Mongolian text"],
];
let bad = 0;
for (const [i, o] of cases) {
  const got = cleanWikivoyage(i);
  if (got !== o) { bad++; console.error(`FAIL\n  in : ${i}\n  exp: ${o}\n  got: ${got}`); }
}
console.log(`${cases.length - bad}/${cases.length} ok`);
process.exit(bad ? 1 : 0);
