#!/usr/bin/env python3
"""Ruler v0.4 runner kit for the maintainer's native APK on the Pixel (RULER-SPEC-v1 r3 §0, §4). Python 3.8+ stdlib; adb over USB only.

  python3 -I ruler_v04.py gate                                   # 0 adb: are spec, refs (both families) and errata frozen?
  python3 -I ruler_v04.py state --arm AU [--packs a,b] [--photo f.png ...] [--refusal-file f] [--warning-file f]   # adb: RC state -> state/<arm>.json
  python3 -I ruler_v04.py build --arm AU --gen 1 [--family travel]   # 0 adb: requests/rv04-<arm>[-<family>]-g<gen>.request.json + ui-queue
  python3 -I rc_eval.py run rv04-AU-g1                            # adb: the run itself (pinned copy of the device-day driver)
  python3 -I ruler_v04.py convert --arm AU --gen 1 [--ui ui-rows.jsonl]   # 0 adb: results -> traces/<arm>-g<gen>.traces.jsonl (judge.mjs input)
  python3 -I ruler_v04.py selftest                               # 0 adb: convert on an existing RC1 rows file with fake items

Never prints item text. Arms in arms.json. Phone use only after r4to answers "pixel livre?" (kit README)."""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOAR = Path("<workspace>")
ITEMS = BOAR / "boar-eval/bench/v0.4/items.jsonl"
ITEMS_SHA = "f9ad2f2f0fc367811ea03690bc9b05e52d85b1ee5fb662600efa818587d33594"
REFS_MAN = BOAR / "boar-eval/bench/v0.4/refs/v2/MANIFEST.json"
SPEC_SHA = HERE.parent / "RULER-SPEC-v1-r4.sha256"          # written when the spec is frozen (r4 supersedes r3)
ERRATA_SHA = BOAR / "boar-eval/bench/v0.4/refs/v2/errata.sha256"  # written after the contested-point pass
ARMS = json.loads((HERE / "arms.json").read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()


def items():
    b = ITEMS.read_bytes()
    if sha(b) != ITEMS_SHA:
        sys.exit("x items sha mismatch")
    return [json.loads(l) for l in b.decode().splitlines() if l.strip()]


def gate(verbose=True):
    miss = []
    if not SPEC_SHA.exists(): miss.append("spec r4 not frozen (RULER-SPEC-v1-r4.sha256 missing)")
    man = json.loads(REFS_MAN.read_text()) if REFS_MAN.exists() else {"families": {}}
    for f in ("claude", "codex"):
        if f not in man["families"]: miss.append(f"references v2 {f} not frozen in MANIFEST.json")
    if not ERRATA_SHA.exists(): miss.append("errata (contested points) not frozen")
    if not (HERE.parent / "factavail/out/factavail-items.sha256").exists(): miss.append("FACT-AVAIL labels not frozen (spec r4 §2.4)")
    if verbose:
        print("GATE OK: app arms may answer v0.4" if not miss else "GATE CLOSED:\n  " + "\n  ".join(miss))
    return not miss


def adb(*a):
    p = subprocess.run(["adb", *a], capture_output=True, text=True)
    return p.stdout


def cmd_state(a):
    if a.arm not in ARMS: sys.exit(f"x unknown arm {a.arm}")
    out = subprocess.run([sys.executable, "-I", str(HERE / "rc_eval.py"), "check"] + (["--pkg", a.pkg] if a.pkg else []), capture_output=True, text=True)
    if out.returncode: sys.exit(out.stdout + out.stderr)
    st = json.loads(out.stdout); pkg = st["pkg"]
    apk_paths = [l.split(":", 1)[1].strip() for l in adb("shell", "pm", "path", pkg).splitlines() if l.startswith("package:")]
    shas = {}
    for p in apk_paths:
        local = HERE / "state" / f"{pkg}-{Path(p).name}"; local.parent.mkdir(exist_ok=True)
        adb("pull", p, str(local)); shas[Path(p).name] = sha(local.read_bytes()) if local.exists() else None
    files = adb("shell", "run-as", pkg, "ls", "-l", "files", "files/models", "files/packs", "files/knowledge") if st.get("debuggable") else ""
    rec = {"arm": a.arm, "armSpec": ARMS[a.arm], "device": st, "apkSha256": shas, "debuggableListing": files or None,
           "installedPacksDeclared": [x for x in (a.packs or "").split(",") if x],
           "photos": {Path(p).name: sha(Path(p).read_bytes()) for p in (a.photo or [])},
           "refusalStringSha256": sha(Path(a.refusal_file).read_bytes()) if a.refusal_file else None,
           "warningLineSha256": sha(Path(a.warning_file).read_bytes()) if a.warning_file else None,
           "refusalFile": a.refusal_file, "warningFile": a.warning_file,
           "hookCapabilities": ARMS["_hook_capabilities_default"], "note": "edit hookCapabilities only from a probe or a code reading of THIS RC, and say which"}
    (HERE / "state").mkdir(exist_ok=True)
    p = HERE / "state" / f"{a.arm}.json"; p.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"state -> {p} (apk {list(shas.values())[:1]}, version {st.get('versionName')}, airplane {st.get('airplaneModeOn')})")


def cmd_build(a):
    if not gate(verbose=False) and not a.allow_closed_gate: gate(); sys.exit("x build refused: the gate is closed (spec r3 §3.2: references before any app answer)")
    arm = ARMS.get(a.arm) or sys.exit(f"x unknown arm {a.arm}")
    if arm["where"] != "phone": sys.exit(f"x arm {a.arm} does not run on the phone ({arm['where']})")
    sp = HERE / "state" / f"{a.arm}.json"
    if not sp.exists() and not a.allow_closed_gate: sys.exit(f"x no state/{a.arm}.json: run `state --arm {a.arm}` after installing the arm's packs")
    st = json.loads(sp.read_text()) if sp.exists() else {"hookCapabilities": ARMS["_hook_capabilities_default"]}
    caps = st["hookCapabilities"]
    its = items()
    if a.family: its = [i for i in its if i["family"] == a.family]
    single = [i for i in its if len(i["turns"]) == 1]; multi = [i for i in its if len(i["turns"]) > 1]
    loc = [i["id"] for i in single if i.get("context")]
    q = []
    for i in single:
        e = {"id": i["id"], "category": i["type"], "query": i["turns"][0]}
        if i.get("context") and caps.get("location"): e["location"] = i["context"]
        q.append(e)
    rid = f"rv04-{a.arm}" + (f"-{a.family}" if a.family else "") + f"-g{a.gen}"
    req = {"requestId": rid, "pipeline": caps.get("pipeline", "legacy"), "evalSetVersion": "v0.4-ruler", "questions": q}
    if a.model: req["models"] = [a.model]
    rd = HERE / ("requests" if gate(verbose=False) else "requests-dry")  # rc_eval.py only reads requests/: a closed-gate build cannot be run
    rd.mkdir(exist_ok=True)
    (rd / f"{rid}.request.json").write_text(json.dumps(req, indent=1, ensure_ascii=False) + "\n")
    uq = [{"id": i["id"], "turns": i["turns"], "context": i.get("context"), "via": "multi-turn"} for i in (multi if not caps.get("multiTurn") else [])]
    (HERE / "ui-queue").mkdir(exist_ok=True)
    (HERE / "ui-queue" / f"{rid}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in uq))
    print(f"{rd.name}/{rid}: hook {len(q)} single-turn ({len(loc)} with location: {'sent' if caps.get('location') else 'NOT sent, scored as given'}); "
          f"ui-queue {len(uq)} multi-turn; show-anyway {'hook' if caps.get('showAnyway') else 'ui-queue after the run (refused ids)'}")


def strip_warning(text, warn):
    return (text[len(warn):].lstrip(), True) if warn and text.startswith(warn) else (text, False)


def convert_rows(rows, arm, gen, st, item_ids, ui_rows=()):
    ref = Path(st["refusalFile"]).read_text().strip() if st.get("refusalFile") else None
    warn = Path(st["warningFile"]).read_text().strip() if st.get("warningFile") else None
    apk = next(iter((st.get("apkSha256") or {}).values()), None)
    out, seen = [], set()
    for r in list(rows) + list(ui_rows):
        qid = r.get("queryId") or r.get("id")
        if qid not in item_ids: continue
        text = r.get("answer") or ""
        text, warned = strip_warning(text, warn)
        refused = bool(r.get("notFound")) if "notFound" in r and st.get("hookCapabilities", {}).get("declinedField") == "notFound" else False
        refused = refused or (ref is not None and text.strip() == ref)
        err = None if r.get("outcome", "success") == "success" and text.strip() else f"outcome {r.get('outcome')}: {r.get('errorMessage')}"
        out.append({"itemId": qid, "runId": r.get("runId"), "answer": {"text": text}, "error": err,
                    "engine": {"arm": f"rv04-{arm}-g{gen}", "commit": (apk or "unknown")[:12], "apkSha256": apk, "appVersion": r.get("appVersion"), "engine": r.get("engine")},
                    "ruler": {"kept": bool(r.get("retrievalUsed")) or bool(r.get("retrievedTitles")), "retrievedTitles": r.get("retrievedTitles"),
                              "refusedZ": refused, "warningLine": warned, "via": r.get("via", "hook"), "modelId": r.get("modelId"),
                              "personalityId": r.get("personalityId"), "maxTokens": r.get("maxTokens"), "ttftMs": r.get("ttftMs"),
                              "totalLatencyMs": r.get("totalLatencyMs"), "tokPerSec": r.get("tokPerSec"), "tokensGenerated": r.get("tokensGenerated"),
                              "peakRssBytes": r.get("peakRssBytes"), "turns": r.get("turns")}})
        seen.add(qid)
    return out, sorted(set(item_ids) - seen)


def cmd_convert(a):
    st = json.loads((HERE / "state" / f"{a.arm}.json").read_text())
    rid = f"rv04-{a.arm}" + (f"-{a.family}" if a.family else "") + f"-g{a.gen}"
    rows = [json.loads(l) for l in (HERE / "results" / rid / "rows.jsonl").read_text().splitlines() if l.strip()]
    ui = [json.loads(l) for l in Path(a.ui).read_text().splitlines() if l.strip()] if a.ui else []
    its = items(); ids = [i["id"] for i in its if not a.family or i["family"] == a.family]
    tr, missing = convert_rows(rows, a.arm, a.gen, st, ids, ui)
    (HERE / "traces").mkdir(exist_ok=True)
    p = HERE / "traces" / f"{rid}.traces.jsonl"; p.write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in tr))
    print(json.dumps({"traces": str(p), "sha256": sha(p.read_bytes()), "rows": len(tr), "missing": missing, "kept": sum(t["ruler"]["kept"] for t in tr),
                      "refusedZ": sum(t["ruler"]["refusedZ"] for t in tr), "warned": sum(t["ruler"]["warningLine"] for t in tr),
                      "errors": sum(bool(t["error"]) for t in tr)}, indent=1))


def cmd_selftest(a):
    src = BOAR / "handoff/pixel8-2026-10-20/bench/results/rc-cv5-51-15b/rows.jsonl"
    rows = [json.loads(l) for l in src.read_text().splitlines() if l.strip()]
    ids = [r["queryId"] for r in rows if r.get("category") != "warmup"]
    st = {"apkSha256": {"base.apk": "2ef43258" + "0" * 56}, "hookCapabilities": ARMS["_hook_capabilities_default"]}
    tr, missing = convert_rows(rows, "SELFTEST", 1, st, ids)
    assert len(tr) == len(ids) and not missing, (len(tr), len(ids), missing)
    assert all(set(t) == {"itemId", "runId", "answer", "error", "engine", "ruler"} for t in tr)
    assert sum(t["ruler"]["kept"] for t in tr) == 1, "RC1 used retrieval on 1/51 (GAP row 6)"
    print(f"selftest ok: {len(tr)} traces, kept {sum(t['ruler']['kept'] for t in tr)}, refusedZ {sum(t['ruler']['refusedZ'] for t in tr)}")


def main():
    ap = argparse.ArgumentParser(); s = ap.add_subparsers(dest="cmd", required=True)
    s.add_parser("gate"); s.add_parser("selftest")
    p = s.add_parser("state"); p.add_argument("--arm", required=True); p.add_argument("--pkg"); p.add_argument("--packs")
    p.add_argument("--photo", nargs="*"); p.add_argument("--refusal-file"); p.add_argument("--warning-file")
    p = s.add_parser("build"); p.add_argument("--arm", required=True); p.add_argument("--gen", type=int, default=1); p.add_argument("--family")
    p.add_argument("--model"); p.add_argument("--allow-closed-gate", action="store_true", help="dry build for testing; never run its output")
    p = s.add_parser("convert"); p.add_argument("--arm", required=True); p.add_argument("--gen", type=int, default=1); p.add_argument("--family"); p.add_argument("--ui")
    a = ap.parse_args()
    {"gate": lambda a: sys.exit(0 if gate() else 1), "state": cmd_state, "build": cmd_build, "convert": cmd_convert, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    main()
