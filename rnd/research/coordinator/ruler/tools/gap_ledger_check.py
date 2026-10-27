#!/usr/bin/env python3
"""C1-GAP-LEDGER check (0 LLM, 0 judge, 0 phone). python3 -I gap_ledger_check.py <ledger.json> [out.json]
Each ledger row: a page sentence + snapshot checks (read with 'git show/grep' at the frozen commit, never the working tree) + device-evidence
checks (file sha256 prefix, then one fact). Check kinds:
  snapshot: line (expected substring within cited line +-3), absent (case-insensitive fixed-string git grep count 0 under a path),
            count (exact occurrences in a file), sha (blob sha256 prefix)
  device:   sha (file sha256 prefix), line (substring at the cited line +-3), json_eq / json_contains (value at a key path),
            rows_count (jsonl rows minus warmup, optionally restricted to ids: count with field op value == expect, and n rows == of)
Sentence rules: established rows that cite the snapshot must carry the ledger label; every sentence passes the a2_state_check.py
'ships/default near 1.7B/Succinct/packs' regex (bad_verb, read from that file's source).
Verdict per row: verified | FAILED | not established (status 'not established' stays so whatever its evidence says).
Negative controls must FAIL. Exit 0 iff apk precondition holds, every established row verifies and every control fails."""
import json, sys, re, hashlib, subprocess
B = "<workspace>/"
L = json.load(open(sys.argv[1])); out_f = sys.argv[2] if len(sys.argv) > 2 else None
REPO, COMMIT = L["snapshot"]["repo"], L["snapshot"]["commit"]; LABEL = L["label"]
src = open(B + L["verb_check_source"]).read()
bad_line = next(l for l in src.splitlines() if l.startswith("bad_verb = re.compile("))
ns = {"re": re}; exec(bad_line, ns); BAD = ns["bad_verb"]
head = subprocess.run(["git", "-C", REPO, "rev-parse", COMMIT], capture_output=True, text=True).stdout.strip()
def blob(path): return subprocess.run(["git", "-C", REPO, "show", f"{COMMIT}:{path}"], capture_output=True, check=True).stdout
def sha_ok(data, pref): return hashlib.sha256(data).hexdigest().startswith(pref)
def near(lines, n, exp):
    hit = [i + 1 for i in range(max(0, n - 4), min(len(lines), n + 3)) if exp in lines[i]]
    return (bool(hit), f"found at {hit}" if hit else f"not within {n}+-3")
def jpath(d, p):
    for k in p: d = d[k]
    return d
OPS = {"eq": lambda a, b: a == b, "truthy": lambda a, b: bool(a), "gt": lambda a, b: (a or 0) > b,
       "icontains": lambda a, b: b.lower() in (a or "").lower()}
def snap(c):
    try:
        if c["kind"] == "sha": return sha_ok(blob(c["path"]), c["expect_prefix"]), hashlib.sha256(blob(c["path"])).hexdigest()[:8]
        if c["kind"] == "line": return near(blob(c["path"]).decode().splitlines(), c["line"], c["expect"])
        if c["kind"] == "count":
            n = blob(c["path"]).decode().count(c["pattern"]); return n == c["expect"], f"count {n}"
        if c["kind"] == "absent":
            hits = {}
            for p in c["patterns"]:
                r = subprocess.run(["git", "-C", REPO, "grep", "-i", "-F", "-c", "-e", p, COMMIT, "--", c["path"]], capture_output=True, text=True)
                n = sum(int(l.rsplit(":", 1)[1]) for l in r.stdout.splitlines() if l.strip())
                if n: hits[p] = n
            return not hits, f"hits {hits}" if hits else "0 hits"
    except Exception as e: return False, f"error {e!r}"[:200]
    return False, "unknown kind"
def dev(c):
    try:
        data = open(B + c["file"], "rb").read()
        if not sha_ok(data, c["sha256"]): return False, f"sha {hashlib.sha256(data).hexdigest()[:8]} != {c['sha256']}"
        if c["kind"] == "sha": return True, "sha ok"
        if c["kind"] == "line": return near(data.decode().splitlines(), c["line"], c["expect"])
        if c["kind"] in ("json_eq", "json_contains"):
            v = jpath(json.loads(data), c["path"])
            ok = v == c["expect"] if c["kind"] == "json_eq" else c["expect"] in v
            return ok, f"value {json.dumps(v)[:80]}"
        if c["kind"] == "rows_count":
            rows = [json.loads(l) for l in data.decode().splitlines() if l.strip()]
            rows = [r for r in rows if not str(r.get("queryId", "")).startswith("warmup")]
            if c.get("ids"): rows = [r for r in rows if r.get("queryId") in c["ids"]]
            n = sum(1 for r in rows if OPS[c["op"]](r.get(c["field"]), c.get("value")))
            return n == c["expect"] and len(rows) == c["of"], f"{n}/{len(rows)}"
    except Exception as e: return False, f"error {e!r}"[:200]
    return False, "unknown kind"
def check(row):
    res = {"row": row["row"], "cause": row["cause"], "checks": []}
    for c in row["snapshot"]:
        ok, why = snap(c); res["checks"].append({"side": "snapshot", "kind": c["kind"], "where": f"{c['path']}" + (f":{c['line']}" if "line" in c else ""), "ok": ok, "why": why})
    for c in row["device"]:
        ok, why = dev(c); res["checks"].append({"side": "device", "kind": c["kind"], "where": c["file"] + (f":{c['line']}" if "line" in c else ""), "ok": ok, "why": why})
    verb = BAD.findall(row["sentence"]); res["verb_hits"] = len(verb)
    res["label_ok"] = (LABEL in row["sentence"]) or not row["snapshot"] or row["status"] != "established"
    allok = all(c["ok"] for c in res["checks"]) and not verb and res["label_ok"]
    res["evidence_ok"] = allok
    res["verdict"] = "not established" if row["status"] != "established" else ("verified" if allok else "FAILED")
    return res
apk = L["apk"]; apk_data = open(B + apk["file"], "rb").read()
apk_ok = sha_ok(apk_data, apk["sha256"]) and json.loads(apk_data)[apk["field"]].startswith(apk["expect_prefix"])
R = [check(r) for r in L["rows"]]; N = [check(r) for r in L["negative_controls"]]
summary = {"snapshot_commit_resolves": head == COMMIT, "apk_precondition": apk_ok,
           "verified": [r["row"] for r in R if r["verdict"] == "verified"], "failed": [r["row"] for r in R if r["verdict"] == "FAILED"],
           "not_established": [r["row"] for r in R if r["verdict"] == "not established"],
           "negative_controls_failed_as_required": all(r["verdict"] == "FAILED" for r in N),
           "ledger_sha256": hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest()}
summary["pass"] = bool(summary["snapshot_commit_resolves"] and apk_ok and not summary["failed"] and summary["negative_controls_failed_as_required"])
out = {"summary": summary, "rows": R, "negative_controls": N}
js = json.dumps(out, indent=1)
if out_f: open(out_f, "w").write(js + "\n")
for r in R + N:
    print(f"row {r['row']:>3} {r['cause'][:44]:44} {r['verdict']:16} " + "; ".join(f"{c['side'][0]}:{'ok' if c['ok'] else 'FAIL'}({c['why'][:40]})" for c in r["checks"])
          + (f" verb_hits {r['verb_hits']}" if r["verb_hits"] else "") + ("" if r["label_ok"] else " NO-LABEL"))
print(json.dumps(summary)); sys.exit(0 if summary["pass"] else 1)
