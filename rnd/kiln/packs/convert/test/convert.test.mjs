// Unit tests: 3 synthetic sample docs per format + the shared helpers. Run: node --test test/
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { decodeEntities, htmlToText, seLicenseByDate, xmlAttrs } from "../lib/common.mjs";
import { questionDoc, siteHostOf, tagsOf } from "../formats/stackexchange.mjs";
import { topicDoc } from "../formats/medlineplus.mjs";
import { manualDocs, tocSections } from "../formats/pdf.mjs";
import { countryDoc } from "../formats/factbook.mjs";

const here = fileURLToPath(new URL("..", import.meta.url));

test("htmlToText keeps lists, code and paragraphs, never emits headings or table rows", () => {
  const t = htmlToText("<p>Intro &amp; more</p><ol><li>one</li><li>two<ul><li>sub</li></ul></li></ol><pre><code>x = 1\n# not a heading\n| a |</code></pre><h2>Head</h2><p>use <code>ls</code> <a href='u'>link</a><img src='i.png'></p>");
  assert.match(t, /^Intro & more\n\n1\. one\n2\. two\n  - sub/);
  assert.match(t, /x = 1\n​# not a heading\n¦ a \|/);
  assert.match(t, /\n\nHead\n\nuse `ls` link$/);
  assert.doesNotMatch(t, /^#+\s/m);
  assert.doesNotMatch(t, /^\|/m);
});

test("entities and attributes", () => {
  assert.equal(decodeEntities("Bras&iacute;lia &#xA;&#233; &bogus;"), "Brasília \né &bogus;");
  assert.deepEqual(xmlAttrs('<row Id="5" Body="&lt;p&gt;a&lt;/p&gt;" />'), { Id: "5", Body: "<p>a</p>" });
});

test("Stack Exchange licence by date", () => {
  assert.equal(seLicenseByDate("2010-12-01T00:00:00"), "CC BY-SA 2.5");
  assert.equal(seLicenseByDate("2011-04-08T00:00:00"), "CC BY-SA 3.0");
  assert.equal(seLicenseByDate("2018-05-01T23:59:59"), "CC BY-SA 3.0");
  assert.equal(seLicenseByDate("2018-05-02T00:00:00"), "CC BY-SA 4.0");
});

// ---- Stack Exchange: 3 questions ----
const users = new Map([["8", "Jez"], ["26", "Ann"]]);
const host = siteHostOf("/x/health.stackexchange.com.7z");
const long = "<p>" + "Words about blisters and care. ".repeat(10) + "</p>";
const q1 = { Id: "2", Title: "Pop a blister?", Body: long, Tags: "|first-aid|skin|", OwnerUserId: "8", AcceptedAnswerId: "11", CreationDate: "2015-03-31T19:00:01", ViewCount: "540", ContentLicense: "CC BY-SA 3.0" };
const ans = [
  { Id: "10", ParentId: "2", Score: "9", Body: "<p>High score</p>", OwnerUserId: "26", CreationDate: "2019-01-01", ContentLicense: "CC BY-SA 4.0" },
  { Id: "11", ParentId: "2", Score: "0", Body: "<p>Accepted</p>", OwnerUserId: "99", CreationDate: "2015-04-01", ContentLicense: "CC BY-SA 3.0" },
  { Id: "12", ParentId: "2", Score: "0", Body: "<p>Dropped</p>", OwnerDisplayName: "anon", CreationDate: "2015-04-01" },
];

test("SE doc 1: accepted first, score order, low-score dropped, attribution and licences", () => {
  const d = questionDoc(q1, ans, users, host);
  assert.equal(host, "medicalsciences.stackexchange.com");
  assert.equal(d.url, "https://medicalsciences.stackexchange.com/questions/2");
  assert.equal(d.source, "stackexchange");
  assert.equal(d.license, "CC BY-SA 3.0");
  assert.equal(d.views, 540);
  assert.ok(d.text.startsWith("Tags: first-aid, skin\n\n"));
  assert.ok(d.text.indexOf("### Answer (score 0, accepted)\n\nAccepted") < d.text.indexOf("### Answer (score 9)\n\nHigh score"));
  assert.ok(!d.text.includes("Dropped"));
  assert.equal(
    d.attribution,
    "Q by Jez (https://medicalsciences.stackexchange.com/users/8); A by user99 (https://medicalsciences.stackexchange.com/users/99); A by Ann (https://medicalsciences.stackexchange.com/users/26); https://medicalsciences.stackexchange.com/questions/2; answers also under CC BY-SA 4.0"
  );
});

test("SE doc 2: unanswered question skipped unless --keep-unanswered", () => {
  const q = { ...q1, Id: "3", AcceptedAnswerId: undefined };
  assert.equal(questionDoc(q, [], users, host), null);
  const d = questionDoc(q, [], users, host, { keepUnanswered: true });
  assert.ok(!d.text.includes("## Answers"));
});

test("SE doc 3: old-style tags, no ContentLicense → date rule, answer cap", () => {
  assert.deepEqual(tagsOf("<a><b-c>"), ["a", "b-c"]);
  const q = { ...q1, Id: "4", Tags: "<a><b>", ContentLicense: undefined, CreationDate: "2010-01-01", AcceptedAnswerId: undefined };
  const many = Array.from({ length: 8 }, (_, i) => ({ Id: String(100 + i), Score: String(i + 1), Body: `<p>a${i}</p>`, OwnerUserId: "26", CreationDate: "2010-02-01" }));
  const d = questionDoc(q, many, users, host, { maxAnswers: 5 });
  assert.equal(d.license, "CC BY-SA 2.5");
  assert.equal((d.text.match(/### Answer/g) ?? []).length, 5);
  assert.ok(d.text.includes("### Answer (score 8)"));
});

// ---- MedlinePlus: 3 topics ----
const topic = (attrs, body) => `<health-topic ${attrs}>${body}</health-topic>`;
const summary = "&lt;p&gt;" + "A1C is a blood test for &lt;a href=&quot;https://medlineplus.gov/x.html&quot;&gt;diabetes&lt;/a&gt;. ".repeat(4) + "&lt;/p&gt;&lt;ul&gt;&lt;li&gt;below 5.7%&lt;/li&gt;&lt;/ul&gt;";
const t1 = topic('title="A1C" url="https://medlineplus.gov/a1c.html" id="6308" language="English"', `<also-called>HbA1C</also-called><also-called>a1c</also-called><full-summary>${summary}</full-summary><related-topic url="u" id="1">Diabetes</related-topic><group url="g" id="2">Diagnostic Tests</group><see-reference>Hemoglobin A1c</see-reference><site title="A1C test" url="https://medlineplus.gov/ency/article/003640.htm"><organization>Medical Encyclopedia</organization></site><site title="Metformin" url="https://medlineplus.gov/druginfo/meds/a696005.html"></site>`);

test("MedlinePlus doc 1: summary, also-called, see also, aliases; ency/druginfo links dropped", () => {
  const d = topicDoc(t1, { lang: "English" });
  assert.equal(d.page_id, 11e9 + 6308);
  assert.equal(d.source, "medlineplus");
  assert.match(d.text, /A1C is a blood test for diabetes\./);
  assert.match(d.text, /- below 5\.7%/);
  assert.match(d.text, /Also called: HbA1C, a1c/);
  assert.match(d.text, /See also: Diabetes/);
  assert.deepEqual(d.aliases, ["HbA1C", "Hemoglobin A1c"]);
  assert.doesNotMatch(d.text, /ency\/|druginfo|Encyclopedia|Metformin/);
  assert.match(d.attribution, /^Courtesy of MedlinePlus from the National Library of Medicine; https:\/\/medlineplus\.gov\/a1c\.html$/);
});

test("MedlinePlus doc 2: Spanish topic skipped", () => {
  assert.equal(topicDoc(t1.replace('language="English"', 'language="Spanish"'), { lang: "English" }), null);
});

test("MedlinePlus doc 3: topic without full-summary skipped", () => {
  assert.equal(topicDoc(topic('title="X" url="u" id="1" language="English"', "<also-called>Y</also-called>"), { lang: "English" }), null);
});

// ---- PDF: a synthetic layout text with 3 sections ----
const pad = (s) => `                              ${s}`;
const footer = "23 March 2026                    ATP 9-99                    #";
const para = (n) => `${n}. ${`Apply firm pressure to wound ${n} and keep the casualty warm. `.repeat(4)}`;
const layout = [
  [pad("ATP 9-99"), "Distribution Restriction: Approved for public release.", "Contents", "      Overview of Bleeding ........................ 1", "      Tier 1 Skills for Bleeding", "      Control ......................... 2", "      Overview of Burns ........................ 3", footer.replace("#", "i")].join("\n"),
  [pad("Chapter 1"), pad("Bleeding Control"), "", "OVERVIEW OF BLEEDING", "195B", "", para("1-1"), "", footer.replace("#", "1")].join("\n"),
  ["Chapter 1", "", "TIER 1 SKILLS FOR BLEEDING CONTROL", "", para("1-2"), "APPLICATION OF TOURNIQUETS", "", para("1-3"), "   • Place the tourniquet high and tight.", "   • Tighten until bleeding stops.", footer.replace("#", "2")].join("\n"),
  [pad("Chapter 2"), pad("Burns"), "", "OVERVIEW OF BURNS", "", para("2-1"), footer.replace("#", "3")].join("\n"),
  ["Chapter 2", "", para("2-2"), footer.replace("#", "4")].join("\n"),
  [pad("References"), "FM 1 something", footer.replace("#", "5")].join("\n"),
].join("\f");

test("PDF: TOC sections, chapters, subsections, steps kept, boilerplate and footers dropped", () => {
  assert.ok(tocSections(layout.split("\n")).has("TIER 1 SKILLS FOR BLEEDING CONTROL"));
  const docs = manualDocs(layout, { manual: "ATP 9-99", url: "https://example.org/atp", date: "2026-03-23", idBase: 1 });
  assert.deepEqual(docs.map((d) => d.title), [
    "ATP 9-99 — Chapter 1 Bleeding Control: Overview Of Bleeding",
    "ATP 9-99 — Chapter 1 Bleeding Control: Tier 1 Skills For Bleeding Control",
    "ATP 9-99 — Chapter 2 Burns: Overview Of Burns",
  ]);
  const [a, b, c] = docs;
  assert.doesNotMatch(a.text, /195B|23 March|Distribution/);
  assert.match(b.text, /\n\n## Application Of Tourniquets\n\n1-3\./);
  assert.match(b.text, /\n- Place the tourniquet high and tight\.\n- Tighten until bleeding stops\./);
  assert.match(c.text, /^2-1\.[\s\S]*\n\n2-2\./);
  assert.equal(c.source, "usgov");
  assert.equal(c.page_id, 3);
  assert.match(c.attribution, /ATP 9-99, 2026-03-23; https:\/\/example\.org\/atp/);
});

// ---- Factbook: 3 countries ----
const country = (short, extra = {}) => ({
  Introduction: { Background: { text: "<p>" + `${short} has a long history. `.repeat(12) + "</p>" } },
  Government: { "Country name": { "conventional short form": { text: short }, "conventional long form": { text: `Republic of ${short}` }, "local short form": { text: "none" }, former: { text: "Old Name / Older" } }, Capital: { name: { text: "Bras&iacute;lia" } } },
  "People and Society": { Population: { total: { text: "1,000 (2025 est.)" } } },
  Economy: { "Real GDP per capita": { "Real GDP per capita 2024": { text: "$19,600 (2024 est.)" }, "Real GDP per capita 2023": { text: "$19,100" }, note: "<b>note:</b> 2021 dollars" } },
  ...extra,
});

test("Factbook doc 1: Key facts first, background section, aliases", () => {
  const d = countryDoc(country("Brazil"), "br", { snapshot: "2026-09-11" });
  assert.equal(d.title, "Brazil");
  assert.ok(d.text.startsWith("Key facts:\nOfficial name: Republic of Brazil\nCapital: Brasília\nPopulation: 1,000 (2025 est.)\nReal GDP per capita: $19,600 (2024 est.)\n\n## Background\n\n"));
  assert.deepEqual(d.aliases, ["Republic of Brazil", "Old Name", "Older"]);
  assert.equal(d.license, "CC0 (CIA World Factbook archive, data as of 2026-09-11)");
  assert.equal(d.page_id, 12e9 + parseInt("br", 36));
});

test("Factbook doc 2: every field flattened into its category section, notes kept", () => {
  const d = countryDoc(country("Kenya"), "ke");
  assert.match(d.text, /## Economy\n\nReal GDP per capita \(Real GDP per capita 2024\): \$19,600[\s\S]*Real GDP per capita \(note\): note: 2021 dollars/);
});

test("Factbook doc 3: Key facts stay under one chunk even with long fields", () => {
  const big = country("Japan", { Geography: { Location: { text: "x ".repeat(400) }, Climate: { text: "y ".repeat(400) } } });
  const d = countryDoc(big, "ja");
  const kf = d.text.split("\n\n")[0];
  assert.ok(kf.startsWith("Key facts:") && kf.length <= 1400);
});

test("CLI + validate on a tiny Factbook dir", () => {
  const dir = mkdtempSync(join(tmpdir(), "conv-"));
  writeFileSync(join(dir, "br.json"), JSON.stringify(country("Brazil")));
  execFileSync("node", [join(here, "convert.mjs"), "factbook", dir, "--out", join(dir, "out"), "--source", "usgov"]);
  const out = JSON.parse(execFileSync("node", [join(here, "validate.mjs"), join(dir, "out")]).toString());
  assert.equal(out.files[0].rows, 1);
  assert.deepEqual(out.errors, {});
});

test("validate flags a medlineplus row with encyclopedia text and an SE row without attribution", () => {
  const dir = mkdtempSync(join(tmpdir(), "val-"));
  const text = "x ".repeat(150);
  const rows = [
    { page_id: 1, title: "A", text: `${text} see https://medlineplus.gov/ency/article/1.htm`, source: "usgov", source_family: "medlineplus", url: "u", license: "Public domain (NLM); courtesy of MedlinePlus from the National Library of Medicine" },
    { page_id: 2, title: "B", text, source: "stackexchange", url: "https://s/questions/2", license: "CC BY-SA 4.0" },
  ];
  writeFileSync(join(dir, "a.jsonl"), rows.map((r) => JSON.stringify(r)).join("\n"));
  let out;
  try {
    execFileSync("node", [join(here, "validate.mjs"), dir]);
  } catch (e) {
    out = JSON.parse(e.stdout.toString());
  }
  assert.equal(out.errors["medlineplus row with encyclopedia/drug text"], 1);
  assert.equal(out.errors["stackexchange row without attribution"], 1);
});
