#!/usr/bin/env node
// Forge copy of wt/plumb-bench-uiios/scripts/eval-iphone.mjs @ 00747371 + a --perf <json> option (sent as the request's "perf").
// Runs questions through BOAR's live answer pipeline on a USB-connected iPhone and pulls the rows back.
// Transport only: the evaluation runs inside the app (src/eval/answerEval.ts), triggered by a request file
// copied into the app container with devicectl (the iOS twin of scripts/eval-device.mjs). No UI automation,
// no WDA: the phone only has to stay unlocked with BOAR in the foreground.
// The build must answer requests: a development build, or one built with EXPO_PUBLIC_DEVICE_EVAL=1
// (src/eval/deviceEvalGate.ts); a shipped build ignores them.
//
//   node scripts/eval-iphone.mjs --questions eval/dataset/questions.v2.jsonl [options]
//
//   --questions <jsonl>     one {id, query, category?} per line (required)
//   --only <ids|categories> comma list, filters the questions
//   --limit <n>             first n questions (after --only)
//   --models <selectors>    comma list of installed model ids/fragments; default: the model the chat uses
//   --answer-anyway         re-ask a declined answer with "Answer anyway"
//   --dataset <name>        recorded on rows as dataset-<name> (default: from the file name, questions.<name>.jsonl)
//   --out <dir>             where to save the raw rows + report (default: eval-results/iphone/<date>)
//   --runs-file <path>      also write one row per question (the re-ask wins) in the eval/ judge format;
//                           with several --models, one file per model (<path minus .jsonl>__<model>.jsonl)
//   --bundle <id>           app bundle (default team.sopa.aoair)   --udid <id>   device (default: the only iPhone)
//   --install-places <a,b>  download these cities' places tiles before the run (world gazetteer names)
//   --install-places-from-questions   ...every city named by a question's grading.city (v2 food items)
//   --install-assets <ids>  download catalog packs first (e.g. boar-crypto,boar-wikivoyage-en)
//   --quick-first on|off    answer setting for this run only   --always-complete on|off   (device's restored after)
//   --no-launch             don't (re)launch the app; it must already be in the foreground
//   --timeout-min <n>       give up after n minutes (default 180)
//   --request-id <id>       reuse a request id: a run the OS killed resumes from its last answered question
//   --confirm-large-models  on a low-RAM phone, confirm the requested models (the app's "run it anyway") instead of failing
import { execFileSync, spawn } from "node:child_process";
import { mkdirSync, openSync, readFileSync, writeFileSync, existsSync, rmSync } from "node:fs";
import { basename, join } from "node:path";
import { tmpdir } from "node:os";

const POLL_MS = 10_000;
const PICKUP_TIMEOUT_MS = 5 * 60_000;
const DEVICECTL = ["xcrun", "devicectl"];

function parseArgs(argv) {
  const o = { launch: true, answerAnyway: false, bundle: "team.sopa.aoair", timeoutMin: 180 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => {
      if (i + 1 >= argv.length) throw new Error(`${a} needs a value`);
      return argv[++i];
    };
    if (a === "--questions") o.questions = next();
    else if (a === "--only") o.only = next().split(",").map((s) => s.trim()).filter(Boolean);
    else if (a === "--limit") o.limit = Number(next());
    else if (a === "--models") o.models = next().split(",").map((s) => s.trim()).filter(Boolean);
    else if (a === "--answer-anyway") o.answerAnyway = true;
    else if (a === "--dataset") o.dataset = next();
    else if (a === "--out") o.out = next();
    else if (a === "--runs-file") o.runsFile = next();
    else if (a === "--bundle") o.bundle = next();
    else if (a === "--udid") o.udid = next();
    else if (a === "--no-launch") o.launch = false;
    else if (a === "--install-places") o.installPlaces = next().split(",").map((x) => x.trim()).filter(Boolean);
    else if (a === "--install-places-from-questions") o.placesFromQuestions = true;
    else if (a === "--install-assets") o.installAssets = next().split(",").map((x) => x.trim()).filter(Boolean);
    else if (a === "--quick-first" || a === "--always-complete") {
      const v = next();
      if (v !== "on" && v !== "off") throw new Error(`${a} takes on|off`);
      (o.answerSettings ??= {})[a === "--quick-first" ? "quickFirst" : "alwaysComplete"] = v === "on";
    }
    else if (a === "--timeout-min") o.timeoutMin = Number(next());
    else if (a === "--request-id") o.requestId = next();
    else if (a === "--confirm-large-models") o.confirmLarge = true;
    // Forge: retrieval perf arms (src/rag/perfFlags.ts in the forge-arms build), e.g. --perf '{"sqlBatch":true}'
    else if (a === "--perf") o.perf = JSON.parse(next());
    else if (a === "--help" || a === "-h") o.help = true;
    else throw new Error(`unknown option ${a}`);
  }
  return o;
}

const fail = (msg) => {
  console.error(`\n✗ ${msg}`);
  process.exit(1);
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const devicectl = (args, { allowFail = false } = {}) => {
  try {
    return execFileSync(DEVICECTL[0], [...DEVICECTL.slice(1), ...args], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
  } catch (e) {
    if (allowFail) return null;
    throw new Error(`devicectl ${args.slice(0, 3).join(" ")} failed: ${(e.stderr || e.message || "").toString().trim().slice(0, 400)}`);
  }
};

function findIphone() {
  const tmp = join(tmpdir(), `devicectl-${process.pid}.json`);
  devicectl(["list", "devices", "--json-output", tmp]);
  const devices = JSON.parse(readFileSync(tmp, "utf8")).result?.devices ?? [];
  rmSync(tmp, { force: true });
  // A paired phone whose tunnel is idle (screen off) shows as "available (paired)"; devicectl reconnects on demand.
  const phones = devices.filter(
    (d) =>
      d.hardwareProperties?.platform === "iOS" &&
      d.hardwareProperties?.reality === "physical" &&
      (d.connectionProperties?.tunnelState === "connected" || (d.connectionProperties?.pairingState === "paired" && d.connectionProperties?.transportType))
  );
  if (phones.length !== 1) throw new Error(`expected exactly one connected physical iPhone, found ${phones.length} (pass --udid)`);
  return phones[0].hardwareProperties.udid;
}

const copyTo = (o, src, dst) =>
  devicectl(["device", "copy", "to", "--device", o.udid, "--domain-type", "appDataContainer", "--domain-identifier", o.bundle, "--source", src, "--destination", dst]);
const copyFrom = (o, src, dst) =>
  devicectl(
    ["device", "copy", "from", "--device", o.udid, "--domain-type", "appDataContainer", "--domain-identifier", o.bundle, "--source", src, "--destination", dst],
    { allowFail: true }
  ) !== null && existsSync(dst);

const median = (xs) => {
  const v = xs.filter((x) => typeof x === "number").sort((a, b) => a - b);
  return v.length ? v[Math.floor((v.length - 1) / 2)] : null;
};
const s1 = (ms) => (ms == null ? "-" : (ms / 1000).toFixed(1));

/** One final row per (config, question): the "Answer anyway" re-ask replaces its declined first try. */
function finalRows(rows) {
  const final = new Map();
  for (const r of rows) {
    const k = `${r.configId}|${r.queryId}`;
    if (!final.has(k) || r.answeredAnyway) final.set(k, r);
  }
  return [...final.values()];
}

function report(rows) {
  const final = finalRows(rows);
  const lines = [
    "| config | category | n | ok | declined | ttft p50 s | first source p50 s | total p50 s | tok/s p50 | tiers |",
    "|---|---|---|---|---|---|---|---|---|---|",
  ];
  const groups = new Map();
  for (const r of final) {
    const k = `${r.configId}|${r.category}`;
    groups.set(k, [...(groups.get(k) ?? []), r]);
  }
  for (const [k, v] of [...groups.entries()].sort()) {
    const [config, cat] = k.split("|");
    const tiers = {};
    for (const r of v) tiers[r.tier] = (tiers[r.tier] ?? 0) + 1;
    const declined = rows.filter((r) => r.configId === config && r.category === cat && r.declined && !r.answeredAnyway).length;
    lines.push(
      `| ${config} | ${cat} | ${v.length} | ${v.filter((r) => r.outcome === "success" && r.answer).length} | ${declined} | ${s1(median(v.map((r) => r.ttftMs)))} | ${s1(
        median(v.map((r) => r.firstSourcesMs))
      )} | ${s1(median(v.map((r) => r.totalLatencyMs)))} | ${median(v.map((r) => r.tokPerSec))?.toFixed(1) ?? "-"} | ${Object.entries(tiers)
        .map(([t, n]) => `${t} ${n}`)
        .join(", ")} |`
    );
  }
  return { lines, final };
}

async function main() {
  let o;
  try {
    o = parseArgs(process.argv.slice(2));
  } catch (e) {
    fail(e.message);
  }
  if (o.help || !o.questions) {
    console.log(readFileSync(new URL(import.meta.url), "utf8").split("\n").slice(1).filter((l, i, a) => a.slice(0, i + 1).every((x) => x.startsWith("//"))).map((l) => l.replace(/^\/\/ ?/, "")).join("\n"));
    process.exit(o.help ? 0 : 1);
  }
  const rawQuestions = readFileSync(o.questions, "utf8")
    .split("\n")
    .filter((l) => l.trim())
    .map((l) => JSON.parse(l));
  let questions = rawQuestions.map((q) => ({ id: q.id, query: q.query, category: q.category }));
  if (o.only) questions = questions.filter((q) => o.only.includes(q.id) || o.only.includes(q.category));
  if (o.limit) questions = questions.slice(0, o.limit);
  if (!questions.length) fail("no questions left after --only/--limit");
  const dataset = o.dataset ?? (basename(o.questions).match(/^questions\.(.+)\.jsonl$/)?.[1] ?? "custom");

  o.udid ??= findIphone();
  console.log(`✓ iPhone ${o.udid}, app ${o.bundle}, ${questions.length} questions (dataset ${dataset})`);

  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  // A fixed id resumes: the app skips the questions its result file for that id already answers.
  const requestId = o.requestId ?? `req-${stamp.toLowerCase().replace(/[^a-z0-9-]/g, "")}`.slice(0, 64);
  if (o.requestId && !/^[a-z0-9][a-z0-9-]{0,63}$/.test(o.requestId)) fail("--request-id: 1-64 lowercase letters, digits or dashes");
  const out = o.out ?? join("eval-results", "iphone", stamp.slice(0, 10), requestId);
  mkdirSync(out, { recursive: true });
  const places = [...new Set([...(o.installPlaces ?? []), ...(o.placesFromQuestions ? rawQuestions.map((q) => q.grading?.city).filter(Boolean) : [])])];
  const install = places.length || o.installAssets?.length ? { ...(places.length ? { places } : {}), ...(o.installAssets ? { assets: o.installAssets } : {}) } : null;
  const request = {
    requestId,
    pipeline: "answer",
    questions,
    evalSetVersion: `dataset-${dataset}`,
    ...(o.models ? { models: o.models } : {}),
    ...(o.answerAnyway ? { answerAnyway: true } : {}),
    ...(install ? { install } : {}),
    ...(o.answerSettings ? { answerSettings: o.answerSettings } : {}),
    ...(o.confirmLarge ? { confirmLargeModels: true } : {}),
    ...(o.perf ? { perf: o.perf } : {}),
  };
  if (install) console.log(`  install first: ${JSON.stringify(install)}`);
  const reqFile = join(out, "request.json");
  writeFileSync(reqFile, JSON.stringify(request));

  if (o.launch) {
    // Fresh process in the foreground; the console (llama.cpp + [javascript] logs) goes to console.log.
    const log = join(out, "console.log");
    // The console goes straight to a file descriptor (no pipe through this process), so unref() lets the CLI exit.
    const fd = openSync(log, "a");
    const child = spawn(
      DEVICECTL[0],
      [...DEVICECTL.slice(1), "device", "process", "launch", "--device", o.udid, "--terminate-existing", "--console", "-e", '{"GGML_METAL_DEVICES":"0","OS_ACTIVITY_DT_MODE":"YES"}', o.bundle],
      { stdio: ["ignore", fd, fd], detached: true }
    );
    child.unref();
    console.log(`✓ launched ${o.bundle} (console → ${log})`);
    await sleep(8000);
  }
  // A reused request id has an old status file on the device: ignore any status written before this request.
  const sentAt = Date.now();
  copyTo(o, reqFile, "Documents/eval/requests/pending.json");
  console.log(`✓ request ${requestId} copied; waiting for the app to pick it up (BOAR must stay in the foreground, phone unlocked)`);

  const statusLocal = join(out, "status.json");
  const t0 = Date.now();
  let last = "";
  let status = null;
  let warned = false;
  while (Date.now() - t0 < o.timeoutMin * 60_000) {
    await sleep(POLL_MS);
    if (!copyFrom(o, `Documents/eval/requests/${requestId}.status.json`, statusLocal)) {
      if (Date.now() - t0 > PICKUP_TIMEOUT_MS) fail("the app never picked the request up: is BOAR in the foreground, and was it built with EXPO_PUBLIC_DEVICE_EVAL=1 (or a development build)?");
      continue;
    }
    status = JSON.parse(readFileSync(statusLocal, "utf8"));
    if ((status.updatedAt ?? 0) < sentAt - 5000) {
      status = null;
      continue;
    }
    if (!warned && status.state !== "failed") {
      warned = true;
      // A build older than these flags ignores the fields it doesn't know: say so instead of running something else.
      const missing = Object.keys(request).filter((k) => !(status.understood ?? ["requestId", "models", "adaptive", "queries", "pipeline", "questions", "answerAnyway", "evalSetVersion"]).includes(k));
      if (missing.length) console.warn(`  ⚠ this build ignores: ${missing.join(", ")} (older than the CLI); results run WITHOUT them`);
    }
    const line = `${status.state} ${status.completed ?? 0}/${status.total ?? "?"} ${status.current ?? ""}`;
    if (line !== last) console.log(`  [${Math.round((Date.now() - t0) / 1000)}s] ${line}`);
    last = line;
    if (status.state === "done" || status.state === "failed") break;
  }
  if (!status || status.state !== "done") fail(`run did not finish: ${status ? `${status.state} ${status.error ?? ""}` : "no status"}`);

  const rowsLocal = join(out, "rows.jsonl");
  const src = status.resultPath.replace(/^files\//, "Documents/");
  if (!copyFrom(o, src, rowsLocal)) fail(`could not copy ${src}`);
  const rows = readFileSync(rowsLocal, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const { lines, final } = report(rows);
  // A generated answer from another model than its config (the app replaced it: low RAM, a crashed load) would be
  // scored as the requested one: say so loudly.
  const mismatched = final.filter((r) => r.configId?.startsWith("answer:") && r.configId !== "answer:current" && (r.tokensGenerated ?? 0) > 0 && r.modelId && r.modelId !== r.configId.slice("answer:".length));
  if (mismatched.length) {
    const msg = `⚠ ${mismatched.length} answer(s) came from another model than requested (e.g. ${mismatched[0].queryId}: ${mismatched[0].modelId} for ${mismatched[0].configId}); their scores are not that model's`;
    console.warn(`  ${msg}`);
    lines.unshift(msg, "");
  }
  const installLine = status.install
    ? `Install: ${status.install.installed.length} new, ${status.install.already.length} already there, failed: ${status.install.failed.map((f) => `${f.id} (${f.error})`).join("; ") || "none"}.`
    : "";
  const settingsLine = rows[0]?.answerSettings ? `Answer settings: ${JSON.stringify(rows[0].answerSettings)}.` : "";
  const md = [`# iPhone answer-pipeline eval ${requestId}`, "", `${rows.length} rows, ${final.length} answers, dataset ${dataset}${status.stopped ? " (STOPPED)" : ""}.`, installLine, settingsLine, "", ...lines, ""].join("\n");
  writeFileSync(join(out, "report.md"), md);
  if (o.runsFile) {
    // One judge file per config: <runs-file> for a single config, <name>__<model>.jsonl for several.
    const configs = [...new Set(final.map((r) => r.configId))];
    for (const c of configs) {
      const file = configs.length === 1 ? o.runsFile : o.runsFile.replace(/(\.jsonl)?$/, `__${c.replace(/^answer:/, "").replace(/[^\w.-]/g, "_")}.jsonl`);
      writeFileSync(file, final.filter((r) => r.configId === c).map((r) => JSON.stringify(r)).join("\n") + "\n");
      console.log(`✓ judge rows (${c}) → ${file}`);
    }
  }
  console.log(`\n${md}\nRaw rows: ${rowsLocal}`);
}

main()
  .then(() => process.exit(0))
  .catch((e) => fail(e.message));
