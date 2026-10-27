#!/usr/bin/env python3
"""preflight.py: pre-call guards of `shard_judge.sh --preflight` (LOOP v2 D5/T5). stdlib only, 0 LLM calls, prints counts/ids/hashes only.

  preflight.py check  --traces T --out O --ids FILE --model haiku|opus [--set S] [--sets-tsv F] [--criterion C] [--control J] [--control-required]
                      [--declared N] [--allow-splice] [--probe-ids K]
  preflight.py verify --file J --ids a,b,c            # live-probe file has an ok row in both orders for every id
Checks in order: provenance, control rows, calls (cap, declared), opus-on-dev. Every refusal: `PREFLIGHT REFUSED <code>: <detail>` on stderr, rc 8, nothing written.
`check` success prints `PREFLIGHT OK set= status= model= ids= planned_calls= spent= cap= control=` (the shell appends ` probe=<k ids>` after the live probe). rc 2 = usage."""
import argparse, fnmatch, hashlib, importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def refuse(code, detail):
    print("PREFLIGHT REFUSED %s: %s" % (code, detail), file=sys.stderr)
    sys.exit(8)


def rows_of(path):
    out = []
    if not os.path.isfile(path):
        return out
    for ln in open(path, encoding="utf-8", errors="replace"):
        ln = ln.strip()
        if ln:
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if isinstance(r, dict):
                out.append(r)
    return out


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_ids(p):
    return [x.strip() for x in open(p, encoding="utf-8") if x.strip()]


def ok_both(rows):
    """set of ids with an ok row in both orders"""
    have = {}
    for r in rows:
        if r.get("ok") and r.get("queryId") is not None:
            have.setdefault(r["queryId"], set()).add(r.get("order"))
    return {i for i, o in have.items() if {"boarA", "boarB"} <= o}


def real_calls(rows):
    return [r for r in rows if r.get("ok") and not r.get("floorScored")]


def model_of_row(r):
    s = (str(r.get("requestedModel") or "") + " " + str(r.get("judgeModel") or "")).lower()
    return "opus" if "opus" in s else ("haiku" if "haiku" in s else None)


def set_status(tsv, name):
    exact, globs = {}, []
    if os.path.isfile(tsv):
        for ln in open(tsv, encoding="utf-8"):
            if not ln.strip() or ln.startswith("#"):
                continue
            f = ln.rstrip("\n").split("\t")
            if len(f) >= 2:
                (globs.append((f[0], f[1])) if f[0].endswith("*") else exact.__setitem__(f[0], f[1]))
    if name in exact:
        return exact[name]
    for g, st in globs:
        if fnmatch.fnmatch(name, g):
            return st
    return "dev"   # fail closed: unknown set = dev


def calls_cap(criterion, model):
    """(cap, error). cap parsed from `calls_cap: Haiku A / Opus B` in the ## Budget block."""
    sec, on = [], False
    for ln in open(criterion, encoding="utf-8"):
        if re.match(r"^## Budget(\s|$)", ln):
            on = True
            continue
        if on and ln.startswith("## "):
            break
        if on:
            sec.append(ln)
    text = re.sub(r"<!--.*?-->", "", "".join(sec), flags=re.S)
    m = re.search(r"(?mi)calls_cap:[ \t]*(.*)$", text)
    if not m:
        return None, "calls_cap unfilled (no calls_cap line in the ## Budget block of %s)" % os.path.basename(criterion)
    v = m.group(1).strip()
    mm = re.search(r"(?i)\b" + model + r"\b[^0-9A-Za-z]*([0-9][0-9,]*)", v)
    if v.startswith("<") or not mm:
        return None, "calls_cap unfilled ('%s'; need '%s <number>')" % (v[:40], model.capitalize())
    return int(mm.group(1).replace(",", "")), None


def opus_clause(criterion):
    if not criterion or not os.path.isfile(criterion):
        return None
    spec = importlib.util.spec_from_file_location("smoke_project", os.path.join(HERE, "smoke-project.py"))
    sp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sp)
    found, vals = sp.block_of(criterion)
    v = (vals.get("opus_clause") or "").strip() if found else ""
    if not v or v.startswith("<") or v.lower().split()[0].strip(".;,") in ("none", "n/a", "na"):
        return None
    return v


def cmd_check(a):
    for f in (a.traces, a.ids):
        if not os.path.isfile(f):
            print("preflight: file not found: " + f, file=sys.stderr); return 2
    ids = read_ids(a.ids); n = len(ids)
    model = a.model
    if model not in ("haiku", "opus"):
        print("preflight: model must be haiku|opus", file=sys.stderr); return 2
    rqm = "opus" if model == "opus" else "claude-haiku-5-5"
    shards = os.path.splitext(a.out)[0] + ".shards"
    prior = rows_of(a.out)
    if os.path.isdir(shards):
        for fn in sorted(os.listdir(shards)):
            if fn.startswith("shard-") and fn.endswith(".jsonl"):
                prior += rows_of(os.path.join(shards, fn))
    # (a) provenance of rows that a resume would reuse
    tsha = sha_file(a.traces)
    okr = [r for r in prior if r.get("ok")]
    if okr:
        jm = sorted({str(r.get("judgeModel")) for r in okr if not r.get("floorScored")})
        if len(jm) > 1:
            refuse("provenance", "%d judge models in the existing rows of %s: %s" % (len(jm), os.path.basename(a.out), ",".join(jm)))
        rq = sorted({str(r["requestedModel"]) for r in okr if r.get("requestedModel") is not None})
        lg = sorted({str(r.get("judgeModel")) for r in okr if not r.get("floorScored") and r.get("requestedModel") is None and r.get("tracesSha256") is not None and rqm not in str(r.get("judgeModel"))})
        if any(x != rqm for x in rq) or lg:
            refuse("provenance", "existing rows were judged by %s, this request is %s" % (",".join(rq + lg), rqm))
        ts = sorted({r["tracesSha256"] for r in okr if r.get("tracesSha256") is not None})
        bad = [x for x in ts if x != tsha]
        if bad and not a.allow_splice:
            refuse("provenance", "existing rows carry tracesSha256 %s != traces %s (ALLOW_SPLICE=1 declares a splice)" % (",".join(x[:12] for x in bad), tsha[:12]))
    # (b) control rows present for every id
    control = "n/a"
    if a.control or a.control_required:
        if not a.control:
            refuse("control_missing", "no control judgments file given (PREFLIGHT_CONTROL_REQUIRED=1)")
        have = ok_both(rows_of(a.control))
        miss = [i for i in ids if i not in have]
        if miss:
            refuse("control_missing", "%d of %d ids (%s%s) have no ok row in both orders in %s" % (len(miss), n, ",".join(miss[:10]), ",..." if len(miss) > 10 else "", os.path.basename(a.control)))
        control = "ok"
    # (c) calls declared
    done = ok_both(prior)
    planned = 2 * len([i for i in ids if i not in done])
    spent_rows = real_calls(rows_of(a.out) if os.path.isfile(a.out) else prior)
    spent = len(spent_rows)
    ledger = os.path.join(os.path.dirname(os.path.abspath(a.out)), ".calls.ledger")
    if os.path.isfile(ledger):
        for ln in open(ledger, encoding="utf-8"):
            p = ln.strip()
            if not p or p.startswith("#"):
                continue
            if not os.path.isabs(p):
                p = os.path.join(os.path.dirname(ledger), p)
            if os.path.abspath(p) == os.path.abspath(a.out):
                continue
            spent += len([r for r in real_calls(rows_of(p)) if model_of_row(r) in (None, model)])
    cap = None
    if a.criterion:
        if not os.path.isfile(a.criterion):
            refuse("calls_cap", "criterion file not found: " + a.criterion)
        cap, err = calls_cap(a.criterion, model)
        if err:
            refuse("calls_cap", err)
        if planned + spent > cap:
            refuse("calls_cap", "planned %d + spent %d > cap %d (%s)" % (planned, spent, cap, model))
    if a.declared is not None and planned != a.declared:
        refuse("calls_declared", "planned %d != declared %d" % (planned, a.declared))
    # (d) Opus on a dev set needs a pre-L1 clause
    status = set_status(a.sets_tsv, a.set)
    if model == "opus" and status != "held-out" and status != "clean":
        if opus_clause(a.criterion) is None:
            refuse("opus_on_dev", "set %s is dev and the criterion declares no pre-L1 clause (opus_clause: none)" % a.set)
    print("PREFLIGHT OK set=%s status=%s model=%s ids=%d planned_calls=%d spent=%d cap=%s control=%s" % (a.set, status, model, n, planned, spent, "none" if cap is None else cap, control))
    return 0


def cmd_verify(a):
    want = [x for x in a.ids.split(",") if x]
    have = ok_both(rows_of(a.file))
    miss = [i for i in want if i not in have]
    if miss:
        refuse("probe_failed", "%s has no ok row in both orders for %s" % (os.path.basename(a.file), ",".join(miss)))
    return 0


def main():
    ap = argparse.ArgumentParser(prog="preflight.py")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check")
    c.add_argument("--traces"); c.add_argument("--out"); c.add_argument("--ids"); c.add_argument("--model", default="haiku")
    c.add_argument("--set", default="unknown"); c.add_argument("--sets-tsv", default=os.path.join(HERE, "sets.tsv"))
    c.add_argument("--criterion"); c.add_argument("--control"); c.add_argument("--control-required", action="store_true")
    c.add_argument("--declared", type=int); c.add_argument("--allow-splice", action="store_true")
    v = sub.add_parser("verify"); v.add_argument("--file"); v.add_argument("--ids")
    a = ap.parse_args()
    if a.cmd == "check" and a.traces and a.out and a.ids:
        return cmd_check(a)
    if a.cmd == "verify" and a.file and a.ids:
        return cmd_verify(a)
    ap.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
