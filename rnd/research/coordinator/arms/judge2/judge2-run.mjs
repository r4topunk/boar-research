// JUDGE2 driver (Kiln): runs boar-eval/harness/judge.mjs on the MacBook with BOAR_EVAL_LIB = ./shim, against the mini's
// llama-server through an ssh port-forward (boar-eval is not on the mini). Enforces the frozen stop rules from the shim's
// calls.jsonl: JSON/schema failure rate > 10 % after >= 20 calls; median wall > 240 s over the first 10 calls.
// A judge.mjs verdict error (exit 4) is rerun (it resumes); a key that fails twice is excluded via --ids and logged.
// Usage: node judge2-run.mjs <leg> <traces.jsonl> <out.judgments.jsonl> <system>
import { execFileSync, spawn } from "node:child_process";
import { appendFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const HERE = dirname(fileURLToPath(import.meta.url));
const EVAL = "<workspace>/boar-eval";
const PORT = 18091, URL_ = `http://127.0.0.1:${PORT}`;
const [leg, traces, out, system] = process.argv.slice(2);
const logDir = join(dirname(out), leg); mkdirSync(logDir, { recursive: true });
const drvLog = join(logDir, "driver.log");
const say = (m) => { const l = `[${new Date().toISOString().slice(11, 19)}] ${m}`; console.log(l); appendFileSync(drvLog, l + "\n"); };
const rd = (p) => (existsSync(p) ? readFileSync(p, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l)) : []);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const median = (a) => { const s = [...a].sort((x, y) => x - y); return s.length ? s[Math.floor((s.length - 1) / 2)] : NaN; };

let tunnel = null;
async function healthy() { try { const r = await fetch(`${URL_}/health`, { signal: AbortSignal.timeout(5000) }); return r.ok; } catch { return false; } }
async function ensureTunnel() {
  if (await healthy()) return true;
  if (tunnel) { tunnel.kill(); tunnel = null; await sleep(1000); }
  say("starting ssh port-forward");
  tunnel = spawn("ssh", ["-N", "-o", "ServerAliveInterval=30", "-o", "ExitOnForwardFailure=yes", "-L", `${PORT}:127.0.0.1:${PORT}`, "MINI_HOST"], { stdio: "ignore" });
  for (let i = 0; i < 20; i++) { await sleep(1500); if (await healthy()) return true; }
  return false;
}
// Addendum 1: free disk + swap on the mini every 10 calls (disk.jsonl); free < 25 GiB -> stop.
let lastDiskCheck = -1, diskStop = null;
function diskCheck(n) {
  if (Math.floor(n / 10) === lastDiskCheck) return; lastDiskCheck = Math.floor(n / 10);
  try {
    const o = execFileSync("ssh", ["-n", "MINI_HOST", "bash -c 'df -k / | tail -1; sysctl -n vm.swapusage; ps -o rss= -p $(pgrep -x llama-server | head -1) 2>/dev/null; true'"], { encoding: "utf8", timeout: 60_000 }).trim().split("\n");
    const freeKiB = Number(o[0].trim().split(/\s+/)[3]), swapUsed = (o[1].match(/used = ([\d.,]+)M/) ?? [])[1];
    const rec = { calls: n, freeGiB: +(freeKiB / 1048576).toFixed(2), swapUsedMB: swapUsed ? Number(swapUsed.replace(",", ".")) : null, serverRssMB: Math.round(Number(o[2]) / 1024) };
    appendFileSync(join(logDir, "disk.jsonl"), JSON.stringify({ at: new Date().toISOString(), ...rec }) + "\n");
    if (rec.freeGiB < 25) diskStop = `mini free disk ${rec.freeGiB} GiB < 25 GiB at ${n} calls (swap ${rec.swapUsedMB} MB)`;
  } catch (e) { say(`disk check failed: ${e.message}`); }
}
function stopRule() {
  const c = rd(join(logDir, "calls.jsonl"));
  diskCheck(c.length); if (diskStop) return diskStop;
  const jf = c.filter((x) => x.kind === "json" || x.kind === "schema" || x.kind === "http").length;
  if (c.length >= 20 && jf / c.length > 0.10) return `JSON failures ${jf}/${c.length} > 10 % after >= 20 calls`;
  if (c.length >= 10) { const m = median(c.slice(0, 10).map((x) => x.wallMs)); if (m > 240_000) return `median ${m} ms > 240 s over first 10 calls`; }
  return null;
}
const qs = rd(join(EVAL, "bench/v0.1/questions.public.jsonl")).filter((q) => q.grading?.type !== "venue-list").map((q) => q.id);
const excluded = new Set(), failCount = {};
let reruns = 0;
while (true) {
  if (!(await ensureTunnel())) { say("STOP: llama-server not reachable through the tunnel"); process.exit(10); }
  const args = [join(EVAL, "harness/judge.mjs"), "--traces", traces, "--out", out, "--bench", join(EVAL, "bench/v0.1"),
    "--effort", "gemma4q2", "--gap-ms", "0", "--seed", "7", "--system", system];
  if (excluded.size) args.push("--ids", qs.filter((id) => !excluded.has(id)).join(","));
  say(`run judge.mjs (rerun ${reruns}, excluded ${[...excluded].join(",") || "none"})`);
  const child = spawn("node", args, { cwd: EVAL, env: { ...process.env, BOAR_EVAL_LIB: join(HERE, "shim"), JUDGE2_LOG_DIR: logDir, JUDGE2_URL: URL_ } });
  let text = "";
  const onData = (d) => { text += d; appendFileSync(join(logDir, "judge.log"), d); };
  child.stdout.on("data", onData); child.stderr.on("data", onData);
  let stopped = null;
  const poll = setInterval(() => { const s = stopRule(); if (s && !stopped) { stopped = s; child.kill("SIGTERM"); } }, 20_000);
  const code = await new Promise((r) => child.on("close", r));
  clearInterval(poll);
  stopped ??= stopRule();
  if (stopped) { say(`STOP RULE: ${stopped}`); process.exit(5); }
  if (code === 0) { say("judge.mjs done"); break; }
  const m = text.match(/ERROR at ([^/\s]+)\/(boar[AB])/g);
  if (code === 4 && m) {
    const key = m.at(-1).replace("ERROR at ", ""); const last = rd(join(logDir, "calls.jsonl")).at(-1);
    if (last?.kind !== "transport") failCount[key] = (failCount[key] ?? 0) + 1;
    say(`exit 4 at ${key} (kind ${last?.kind}, failure #${failCount[key] ?? 0})`);
    if (failCount[key] >= 2) { excluded.add(key.split("/")[0]); say(`excluded ${key.split("/")[0]} after 2 failures`); }
    reruns++; if (reruns > 30) { say("STOP: > 30 reruns"); process.exit(6); }
    continue;
  }
  say(`STOP: judge.mjs exit ${code}`); process.exit(7);
}
if (tunnel) tunnel.kill();
