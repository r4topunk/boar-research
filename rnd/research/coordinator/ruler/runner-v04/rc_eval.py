#!/usr/bin/env python3
"""Drive the maintainer's native BOAR app (his release candidate) over adb, no taps: DEVICE-DAY-2026-10-22.
Python 3.8+ stdlib only. Nothing goes over the network; adb over USB only.

  python3 rc_eval.py check [--pkg P]                      # package, version, debuggable, airplane, RAM, battery, thermal, storage
  python3 rc_eval.py run <request-name> [--pkg P] [--timeout-min 30] [--tag T]   # requests/<name>.request.json -> results/<rid>[-<tag>]/
  python3 rc_eval.py run <request-name> --dry-run         # print the adb commands, touch nothing

How it reaches the app (read from upstream fullnative-dev 0be84acd, BenchActivity.kt:72-95, DeviceEvalRunner.kt):
  adb shell am start -n <pkg>/team.sopa.boar.bench.BenchActivity --es run eval --es request64 <base64 request> --ei waitmin 2
The app writes the request to files/eval/requests/pending.json, runs it on the legacy pipeline (its own questions), and,
because the request came in request64, copies files/eval/ to /sdcard/Android/data/<pkg>/files/eval-out/ when done.
UNKNOWN until tried: whether HIS release candidate keeps this hook (it was used for the 10-17 X6 run, "request64").
If `am start` reports an error (class does not exist), the hook is gone: use the manual fallback in DEVICE-DAY-2026-10-22.md.

While it runs, the host samples every 5 s: app PSS (dumpsys meminfo), MemAvailable, battery temp/level, thermal status,
and whether the app process is alive. At the end it saves logcat and counts low-memory kills of the package.
Output dir results/<rid>/: request.json, telemetry.csv, eval-out/ (rows .jsonl + status), rows.jsonl, logcat.txt,
lmk.txt, meminfo-end.txt, device.json, summary.json."""
import argparse, base64, json, re, statistics, subprocess, sys, threading, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKGS = ["team.sopa.aoair", "team.sopa.aoair.native", "team.sopa.aoair.devtest"]
ACT = "team.sopa.boar.bench.BenchActivity"
DRY = False


def adb(*args, check=False):
    if DRY:
        print("adb " + " ".join(args)); return ""
    try:
        p = subprocess.run(["adb", *args], capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit("x adb not found: fish_add_path ~/Library/Android/sdk/platform-tools")
    if check and p.returncode != 0:
        sys.exit(f"x adb {' '.join(args)[:100]} failed: {p.stderr[:300]}")
    return p.stdout


def find_pkg(want):
    if want:
        return want
    have = adb("shell", "pm", "list", "packages", "team.sopa.aoair")
    found = [p for p in PKGS if f"package:{p}\n" in have + "\n"]
    if len(found) != 1:
        sys.exit(f"x expected one of {PKGS} installed, found {found or 'none'}: pass --pkg")
    return found[0]


def state(pkg):
    g = lambda k: adb("shell", "settings", "get", "global", k).strip()
    pk = adb("shell", "dumpsys", "package", pkg)
    mem = adb("shell", "cat", "/proc/meminfo")
    bat = adb("shell", "dumpsys", "battery")
    th = adb("shell", "dumpsys", "thermalservice")
    num = lambda pat, s: (re.search(pat, s or "") or [None, None])[1]
    return {
        "pkg": pkg, "versionName": num(r"versionName=(\S+)", pk), "versionCode": num(r"versionCode=(\d+)", pk),
        "debuggable": bool(re.search(r"pkgFlags=\[[^\]]*DEBUGGABLE", pk or "")),
        "benchActivityListed": ACT in (pk or ""),  # activities without intent filters may not be listed: informative only
        "airplaneModeOn": g("airplane_mode_on") == "1", "wifiOn": g("wifi_on"), "bluetoothOn": g("bluetooth_on"),
        "memTotalKb": num(r"MemTotal:\s+(\d+)", mem), "memAvailableKb": num(r"MemAvailable:\s+(\d+)", mem),
        "batteryLevel": num(r"level: (\d+)", bat), "batteryDc": num(r"temperature: (\d+)", bat),
        "acPowered": "AC powered: true" in (bat or "") or "USB powered: true" in (bat or ""),
        "thermalStatus": num(r"Thermal Status: (\d+)", th),
        "dataFree": (adb("shell", "df", "-h", "/data").strip().splitlines() or [""])[-1:],
        "model": adb("shell", "getprop", "ro.product.model").strip(), "android": adb("shell", "getprop", "ro.build.version.release").strip(),
    }


def sampler(pkg, path, stop, every=5):
    with open(path, "w") as f:
        f.write("t_epoch_ms,app_pss_kb,mem_available_kb,battery_dC,battery_level,thermal_status,app_alive\n")
        while not stop.is_set():
            m = adb("shell", "dumpsys", "meminfo", pkg)
            pss = re.search(r"TOTAL PSS:\s+(\d+)|^\s*TOTAL\s+(\d+)", m or "", re.M)
            pss = (pss.group(1) or pss.group(2)) if pss else ""
            ma = re.search(r"MemAvailable:\s+(\d+)", adb("shell", "cat", "/proc/meminfo") or "")
            b = adb("shell", "dumpsys", "battery") or ""
            t = re.search(r"Thermal Status: (\d+)", adb("shell", "dumpsys", "thermalservice") or "")
            alive = "1" if adb("shell", "pidof", pkg).strip() else "0"
            f.write(",".join([str(int(time.time() * 1000)), pss, ma.group(1) if ma else "",
                              (re.search(r"temperature: (\d+)", b) or [None, ""])[1], (re.search(r"level: (\d+)", b) or [None, ""])[1],
                              t.group(1) if t else "", alive]) + "\n"); f.flush()
            stop.wait(every)


def pct(xs, q):
    xs = sorted(x for x in xs if x is not None)
    return round(xs[min(len(xs) - 1, max(0, int(round(q * (len(xs) - 1)))))], 1) if xs else None


def summarize(out, rows, tele):
    gen = [r for r in rows if (r.get("tokensGenerated") or 0) > 0]
    s = lambda k, R, d=1000: [r[k] / d for r in R if isinstance(r.get(k), (int, float))]
    pss = [int(x.split(",")[1]) for x in tele[1:] if x.split(",")[1].isdigit()]
    alive = [x.split(",")[6] for x in tele[1:] if x.count(",") == 6]
    return {
        "rows": len(rows), "outcomes": {o: sum(r.get("outcome") == o for r in rows) for o in {r.get("outcome") for r in rows}},
        "models": sorted({str(r.get("modelId")) for r in rows}), "personality": sorted({str(r.get("personalityId")) for r in rows}),
        "maxTokens": sorted({str(r.get("maxTokens")) for r in rows}), "appVersion": sorted({str(r.get("appVersion")) for r in rows}),
        "answer_s_p50": pct(s("totalLatencyMs", rows), .5), "answer_s_p90": pct(s("totalLatencyMs", rows), .9),
        "gen_rows": len(gen), "gen_answer_s_p50": pct(s("totalLatencyMs", gen), .5), "ttft_s_p50": pct(s("ttftMs", gen), .5),
        "decode_tok_s_p50": pct(s("tokPerSec", gen, 1), .5), "retrieval_s_p50": pct(s("retrievalMs", rows), .5),
        "peakRss_gb_max": round(max(s("peakRssBytes", rows, 1e9) or [0]), 2), "pss_peak_gb": round(max(pss or [0]) / 1048576, 2),
        "app_died_samples": alive.count("0") if "1" in alive else None,
        "lmk_lines": sum(1 for _ in open(out / "lmk.txt")) if (out / "lmk.txt").exists() else None,
    }


def cmd_check(a):
    print(json.dumps(state(find_pkg(a.pkg)), indent=1))


def cmd_run(a):
    rp = HERE / "requests" / f"{a.name}.request.json"
    if not rp.exists():
        sys.exit(f"x no such request {rp.name}; rc-* files: " + ", ".join(sorted(p.name[:-13] for p in (HERE / "requests").glob("rc-*.request.json"))))
    req = json.loads(rp.read_text()); rid = req["requestId"]
    pkg = find_pkg(a.pkg)
    st = state(pkg)
    if not DRY:
        if not st["airplaneModeOn"] and not a.allow_network:
            sys.exit("x airplane mode is OFF: turn it on (Wi-Fi and Bluetooth off), then rerun")
    out = HERE / "results" / (rid + (f"-{a.tag}" if a.tag else ""))
    if not DRY:
        out.mkdir(parents=True, exist_ok=True)
        (out / "request.json").write_text(json.dumps(req, indent=1)); (out / "device.json").write_text(json.dumps(st, indent=1))
    ext = f"/sdcard/Android/data/{pkg}/files/eval-out"
    b64 = base64.b64encode(json.dumps(req, separators=(",", ":"), ensure_ascii=False).encode()).decode()
    adb("shell", "am", "force-stop", pkg); adb("shell", "rm", "-rf", ext); adb("logcat", "-c")
    stop = threading.Event(); th = threading.Thread(target=sampler, args=(pkg, out / "telemetry.csv", stop), daemon=True)
    if not DRY:
        th.start()
    t0 = time.time()
    started = adb("shell", "am", "start", "-W", "-n", f"{pkg}/{ACT}", "--es", "run", "eval", "--es", "request64", b64, "--ei", "waitmin", "2")
    if not DRY and re.search(r"Error|does not exist|Permission Denial", started or ""):
        stop.set(); sys.exit(f"x the eval hook did not start ({started.strip()[:200]}): use the manual fallback (DEVICE-DAY-2026-10-22.md, section F)")
    print(f"ok {rid}: {len(req['questions'])} questions sent to {pkg} {st.get('versionName')}. Phone: screen on, app in front, nobody touches it.")
    if DRY:
        print(f"adb shell cat {ext}/requests/{rid}.status.json   # poll until state done/failed"); print(f"adb pull {ext} {out}/eval-out"); return
    status, died = {}, 0
    while time.time() - t0 < a.timeout_min * 60:
        time.sleep(10)
        raw = adb("shell", "cat", f"{ext}/requests/{rid}.status.json")
        if raw.strip().startswith("{"):
            status = json.loads(raw)
            if status.get("state") in ("done", "failed"):
                break
        if not adb("shell", "pidof", pkg).strip():
            died += 1
            if died >= 3:
                print("x the app process is gone (killed or crashed): pulling what exists"); break
        else:
            died = 0
        print(f"  {int(time.time() - t0)} s, waiting (results are copied out only at the end)", flush=True)
    stop.set(); th.join(timeout=15)
    adb("pull", ext, str(out / "eval-out"))
    log = adb("logcat", "-d"); (out / "logcat.txt").write_text(log)
    lmk = [l for l in log.splitlines() if re.search(r"lowmemorykiller|lmkd|Low on memory|kill.*" + re.escape(pkg), l, re.I) and pkg in l]
    (out / "lmk.txt").write_text("\n".join(lmk) + ("\n" if lmk else ""))
    (out / "meminfo-end.txt").write_text(adb("shell", "dumpsys", "meminfo", pkg))
    rows = []  # eval-out holds every earlier run of this app too: keep only this request's run
    runf = [out / "eval-out" / f"{status['runId']}.jsonl"] if status.get("runId") else sorted((out / "eval-out").glob("eval-*.jsonl"), key=lambda f: f.stat().st_mtime)[-1:]
    for f in runf:
        if f.exists():
            rows += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    (out / "rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    summ = {"requestId": rid, "status": status, "wall_s": round(time.time() - t0), **summarize(out, rows, (out / "telemetry.csv").read_text().splitlines())}
    (out / "summary.json").write_text(json.dumps(summ, indent=1)); print(json.dumps(summ, indent=1))
    if len(rows) < len(req["questions"]):
        print(f"WARNING: {len(rows)}/{len(req['questions'])} rows. Keep logcat.txt; see DEVICE-DAY §kill rules before rerunning.")


def main():
    global DRY
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("check"); c.add_argument("--pkg")
    r = sp.add_parser("run"); r.add_argument("name"); r.add_argument("--pkg"); r.add_argument("--timeout-min", type=int, default=30)
    r.add_argument("--tag", default=""); r.add_argument("--allow-network", action="store_true"); r.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    DRY = getattr(a, "dry_run", False)
    if DRY and not a.pkg:
        a.pkg = "team.sopa.aoair"
    {"check": cmd_check, "run": cmd_run}[a.cmd](a)


if __name__ == "__main__":
    main()
