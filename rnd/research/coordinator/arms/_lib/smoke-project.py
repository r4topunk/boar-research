#!/usr/bin/env python3
"""smoke-project.py: mechanical verdict of an arm's smoke run (LOOP v2 D3/D4, S3 stop rules). stdlib only, 0 LLM calls, prints counts/numbers only.

  smoke-project.py <smoke.traces.jsonl|units.jsonl> <criterion.md> --n-full N [--marker code] [--run-type T --wall-cap-h H --parallelism P --token-budget B]
  smoke-project.py --check-block <criterion.md>        # rc 0 if the ## Precheck block is complete and filled, else rc 7 + one-line reason on stderr

Input kinds (auto): traces (one adapter trace per line: itemId, answer.text, route.reasonCodes, timing.totalMs/promptTokens, error)
or units (build/teacher runs: one line per unit with ok, empty, parsed, seconds [, promptTokens]).
The criterion's `## Precheck` block supplies run_type, wall_cap_h, parallelism, token_projection / token_budget (CLI flags only when the block is absent, e.g. Tags: blocker).
Writes <criterion dir>/smoke.verdict.json = {criterion_sha, verdict, reasons, projected_wall_h, wall_cap_h, empty_share, parse_share, s_per_unit,
mean_prompt_tokens, token_budget, computed_at, + run_type, n, n_full, marker}; prints the same JSON. rc: 0 PASS, 1 FAIL, 3 KILL, 2 usage/input error, 7 criterion/Precheck refused.
Rules: any empty/cut answer, rc != 0 (error / ok=false), identity of the option (marker) missing, mean prompt tokens > token_budget (exact, no tolerance: X2 incident),
projected wall (s/unit x n_full / parallelism) > 1.5 x wall_cap_h -> FAIL; build/teacher runs: empty share > 5 % or parse share < 90 % -> KILL (up to 5 % empty is tolerated there).
A verdict is bound to the sha256 of the criterion at verdict time: editing the criterion invalidates it (arm.sh crit_check)."""
import argparse, datetime, hashlib, json, os, re, sys
from fractions import Fraction

KEYS = ["token_projection", "token_budget", "disk_peak_gib", "off_baseline", "call_pattern", "lane", "opus_clause", "wall_cap_h", "parallelism", "run_type"]
NA_OK = {"token_projection", "token_budget", "disk_peak_gib", "off_baseline"}   # may be n/a (a build run has no prompt budget, a deep run no OFF patch baseline...)
LANES = {"mini-long", "mac-gen", "mac-cpu", "judge"}
RUN_TYPES = {"4b-patch", "deep", "build", "teacher", "pack-build", "latency", "judge"}
KILL_TYPES = {"build", "teacher"}
NOTOKEN_TYPES = {"build", "teacher", "pack-build", "judge"}
NUM = re.compile(r"^\s*([0-9][0-9,]*(?:\.[0-9]+)?)")
HEAD = ("criterion lacks the ## Precheck block (" + ", ".join(KEYS) + ") — see _lib/CRITERION-TEMPLATE.md")


def frozen_bytes(data):
    # boundary rule: through the line "<!-- END FROZEN -->" when the marker exists, else the whole file (same as sed '/^<!-- END FROZEN -->$/q')
    out = b""
    for ln in data.splitlines(True):
        if ln.rstrip(b"\n") == b"<!-- END FROZEN -->":
            return out + b"<!-- END FROZEN -->\n"
        out += ln
    return data
def sha_file(p):
    return hashlib.sha256(frozen_bytes(open(p, "rb").read())).hexdigest()


def block_of(path):
    """(found, {key: raw value}) for the ## Precheck section. token_projection / token_budget may share one line ('a / token_budget: b')."""
    sec, on, found = [], False, False
    for ln in open(path, encoding="utf-8"):
        if re.match(r"^## Precheck(\s|$)", ln):
            on, found = True, True
            continue
        if on and ln.startswith("## "):
            on = False
        if on:
            sec.append(ln.rstrip("\n"))
    text = re.sub(r"<!--.*?-->", "", "\n".join(sec), flags=re.S)   # comments in the template are not values
    vals = {}
    for k in KEYS:
        m = re.search(r"(?m)(?:^|[\s/])" + k + r":[ \t]*(.*)$", text)
        if m:
            v = m.group(1)
            if k == "token_projection":
                v = re.split(r"\s+/\s+token_budget:", v)[0]
            vals[k] = v.strip()
    return found, vals


def num(v):
    m = NUM.match(v or "")
    return float(m.group(1).replace(",", "")) if m else None


def problems(found, vals):
    """List of one-line problems (empty = the block is complete and filled)."""
    if not found:
        return [HEAD]
    out = []
    for k in KEYS:
        v = vals.get(k)
        if v is None or v == "":
            out.append("Precheck block lacks key " + k); continue
        if v.startswith("<"):
            out.append("Precheck key " + k + " is unfilled (" + v[:40] + ")"); continue
        if k in NA_OK and v.lower().split()[0] in ("n/a", "na", "none"):
            continue
        if k in ("token_projection", "token_budget", "disk_peak_gib", "wall_cap_h", "parallelism"):
            n = num(v)
            if n is None or n <= 0:
                out.append("Precheck key " + k + " must start with a positive number" + (" or n/a" if k in NA_OK else "") + " (got '" + v[:30] + "')")
        elif k == "lane" and v.split()[0] not in LANES:
            out.append("Precheck key lane must be one of " + "|".join(sorted(LANES)) + " (got '" + v[:30] + "')")
        elif k == "run_type" and v.split()[0] not in RUN_TYPES:
            out.append("Precheck key run_type must be one of " + "|".join(sorted(RUN_TYPES)) + " (got '" + v[:30] + "')")
    return out


def load(path):
    rows = []
    for i, ln in enumerate(open(path, encoding="utf-8"), 1):
        ln = ln.strip()
        if ln:
            try:
                rows.append(json.loads(ln))
            except ValueError:
                sys.exit("smoke-project: %s line %d is not JSON" % (path, i))
    return rows


def norm_trace(t):
    ans = t.get("answer")
    txt = ans.get("text", "") if isinstance(ans, dict) else str(ans or "")
    ev = [e for e in (t.get("events") or []) if isinstance(e, dict) and e.get("kind") == "generation"]
    tm = t.get("timing") or {}
    pt = tm.get("promptTokens")
    if pt is None and ev:
        s = [e.get("promptTokens") for e in ev if isinstance(e.get("promptTokens"), (int, float))]
        pt = sum(s) if s else None
    route = t.get("route") or {}
    cut = any(e.get("timedOut") for e in ev) or route.get("outcome") in ("timeout", "error", "cut")
    ms = tm.get("totalMs")
    return {"id": t.get("itemId"), "ok": not t.get("error"), "empty": not txt.strip(), "cut": bool(cut), "parsed": None,
            "seconds": (ms / 1000.0) if isinstance(ms, (int, float)) else None, "tokens": pt, "codes": list(route.get("reasonCodes") or [])}


def norm_unit(u):
    s = u.get("seconds")
    pt = u.get("promptTokens", u.get("prompt_tokens"))
    return {"id": u.get("id") or u.get("unit"), "ok": bool(u.get("ok", True)), "empty": bool(u.get("empty", False)), "cut": bool(u.get("cut", False)),
            "parsed": (bool(u["parsed"]) if "parsed" in u else None), "seconds": float(s) if isinstance(s, (int, float)) else None,
            "tokens": pt if isinstance(pt, (int, float)) else None, "codes": []}


def verdict(units, kind, p, a):
    n = len(units); reasons = []; kill = fail = False
    rt = p["run_type"]
    ne = sum(u["empty"] for u in units); nc = sum(u["cut"] for u in units); nbad = sum(not u["ok"] for u in units)
    empty_share = ne / n if n else None
    pu = [u["parsed"] for u in units if u["parsed"] is not None]
    parse_share = (sum(pu) / len(pu)) if pu else None
    secs = [u["seconds"] for u in units if u["seconds"] is not None]
    s_per = (sum(secs) / len(secs)) if secs else None
    toks = [u["tokens"] for u in units if u["tokens"] is not None]
    mean_tok = (sum(Fraction(x) for x in toks) / len(toks)) if toks else None
    if n == 0:
        fail = True; reasons.append("FAIL: no units in the smoke input")
    if rt in KILL_TYPES:
        if empty_share is not None and empty_share > 0.05:
            kill = True; reasons.append("KILL: empty share %.3f > 0.05 (%d/%d units)" % (empty_share, ne, n))
        if parse_share is not None and parse_share < 0.90:
            kill = True; reasons.append("KILL: parse share %.3f < 0.90 (%d/%d units)" % (parse_share, sum(pu), len(pu)))
    elif ne:
        fail = True; reasons.append("FAIL: %d/%d empty answers (FAIL-INFRA)" % (ne, n))
    if nc:
        fail = True; reasons.append("FAIL: %d/%d cut/timed-out answers (FAIL-INFRA)" % (nc, n))
    if nbad:
        fail = True; reasons.append("FAIL: %d/%d units with an error or ok=false (rc != 0)" % (nbad, n))
    if a.marker:
        if kind != "traces":
            fail = True; reasons.append("FAIL: --marker %s cannot be verified on a units file (needs traces with route.reasonCodes)" % a.marker)
        else:
            miss = sum(not any(c == a.marker or c.startswith(a.marker) for c in u["codes"]) for u in units)
            if miss:
                fail = True; reasons.append("FAIL: option not applied: reason code '%s' missing on %d/%d traces" % (a.marker, miss, n))
    tb = p["token_budget"]
    if tb is not None:
        tp = p.get("token_projection")
        if tp is not None and Fraction(tp) > Fraction(tb):
            fail = True; reasons.append("FAIL: criterion token_projection %s > token_budget %s" % (tp, tb))
        if mean_tok is None:
            if kind == "traces" and rt not in NOTOKEN_TYPES:
                fail = True; reasons.append("FAIL: token_budget %s declared but no prompt token counts in the smoke traces" % tb)
        elif mean_tok > Fraction(tb):
            fail = True; reasons.append("FAIL: mean prompt tokens %s > token_budget %s (exact, no tolerance)" % (round(float(mean_tok), 3), tb))
    proj = None
    if s_per is None:
        fail = True; reasons.append("FAIL: no per-unit seconds in the smoke input: wall cannot be projected")
    else:
        proj = s_per * a.n_full / p["parallelism"] / 3600.0
        lim = 1.5 * p["wall_cap_h"]
        if proj > lim:
            fail = True; reasons.append("FAIL: projected_wall_h %.2f > 1.5 x wall_cap_h %s = %.2f (%.2f s/unit x %d / %s)" % (proj, p["wall_cap_h"], lim, s_per, a.n_full, p["parallelism"]))
    v = "KILL" if kill else ("FAIL" if fail else "PASS")
    r3 = lambda x: None if x is None else round(float(x), 3)
    return {"verdict": v, "reasons": reasons, "projected_wall_h": r3(proj), "wall_cap_h": p["wall_cap_h"], "empty_share": r3(empty_share),
            "parse_share": r3(parse_share), "s_per_unit": r3(s_per), "mean_prompt_tokens": r3(mean_tok), "token_budget": tb,
            "run_type": rt, "n": n, "n_full": a.n_full, "marker": a.marker or None}


def main():
    ap = argparse.ArgumentParser(prog="smoke-project.py", add_help=True)
    ap.add_argument("input", nargs="?"); ap.add_argument("criterion", nargs="?")
    ap.add_argument("--check-block", metavar="CRITERION"); ap.add_argument("--n-full", type=int); ap.add_argument("--marker")
    ap.add_argument("--run-type"); ap.add_argument("--wall-cap-h", type=float); ap.add_argument("--parallelism", type=float); ap.add_argument("--token-budget", type=float)
    a = ap.parse_args()
    if a.check_block:
        found, vals = block_of(a.check_block); pr = problems(found, vals)
        if pr:
            print("launch refused: " + pr[0], file=sys.stderr); return 7
        return 0
    if not a.input or not a.criterion or a.n_full is None or a.n_full <= 0:
        print("usage: smoke-project.py <traces|units.jsonl> <criterion.md> --n-full N [--marker code]", file=sys.stderr); return 2
    for f in (a.input, a.criterion):
        if not os.path.isfile(f):
            print("smoke-project: file not found: " + f, file=sys.stderr); return 2
    found, vals = block_of(a.criterion)
    if found:
        pr = problems(True, vals)
        if pr:
            print("smoke refused: " + "; ".join(pr), file=sys.stderr); return 7
        tb, tp = num(vals["token_budget"]) if vals["token_budget"].lower() not in ("n/a", "na", "none") else None, None
        if vals["token_projection"].lower().split()[0] not in ("n/a", "na", "none"):
            tp = num(vals["token_projection"])
        p = {"run_type": vals["run_type"].split()[0], "wall_cap_h": num(vals["wall_cap_h"]), "parallelism": num(vals["parallelism"]), "token_budget": tb, "token_projection": tp}
    elif a.run_type and a.wall_cap_h and a.parallelism:
        p = {"run_type": a.run_type, "wall_cap_h": a.wall_cap_h, "parallelism": a.parallelism, "token_budget": a.token_budget, "token_projection": None}
    else:
        print("smoke refused: " + HEAD + " (or pass --run-type --wall-cap-h --parallelism for a Tags: blocker criterion)", file=sys.stderr); return 7
    if p["run_type"] not in RUN_TYPES:
        print("smoke refused: unknown run_type " + p["run_type"], file=sys.stderr); return 7
    rows = load(a.input)
    kind = "traces" if rows and "itemId" in rows[0] else "units"
    units = [norm_trace(r) if kind == "traces" else norm_unit(r) for r in rows]
    out = verdict(units, kind, p, a)
    rec = {"criterion_sha": sha_file(a.criterion)}; rec.update(out)
    rec["computed_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dest = os.path.join(os.path.dirname(os.path.abspath(a.criterion)), "smoke.verdict.json")
    tmp = dest + ".tmp%d" % os.getpid()
    with open(tmp, "w") as f:
        json.dump(rec, f, indent=1); f.write("\n")
    os.replace(tmp, dest)
    print(json.dumps(rec))
    return {"PASS": 0, "FAIL": 1, "KILL": 3}[out["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
