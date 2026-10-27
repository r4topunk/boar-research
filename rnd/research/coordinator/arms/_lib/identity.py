#!/usr/bin/env python3
"""identity.py: tree / patch / adapter identity of a run's traces (LOOP v2 D9/T5). stdlib only, 0 LLM calls, reads trace metadata only.

  identity.py --gen <traces.jsonl> [--replay <traces.jsonl>] [--patch-sha HEX] [--adapter STR] [--tree COMMIT-PREFIX] [--mode on|off]
              [--not-applied-re REGEX] [--ids FILE] [--write-verdict CRITERION.md]
Metadata read per trace: engine.commit, runtime.versions.adapter, runtime.versions['engine.patch.sha256'], route.reasonCodes (also engine.arm, config.settings, shown nowhere).
Checks: one commit / one patch / one adapter per file (mixed-tree, mixed-patch, mixed-adapter); replay file = generation file on all three (replay-tree, replay-patch, replay-adapter: the TK2 incident);
pinned values (--tree prefix, --patch-sha prefix either way, --adapter equal or contained) (pinned-mismatch); --mode on (default): any reason code matching --not-applied-re
(default ':(nosidecar|noopts|not-applied|notapplied)$') on any trace = option-not-applied (the X2b incident); --mode off ignores that rule.
A trace without the metadata is "unknown" and never fails a check; only contradictions and not-applied codes do.
Output: `identity: PASS n= tree= patch= adapter=` | `identity: FAIL <reason>[,<reason>] n= notapplied=k/n`. rc 0 PASS, 1 FAIL, 2 usage/unreadable.
--write-verdict C: on FAIL also write <C dir>/smoke.verdict.json {criterion_sha, verdict: FAIL, reasons: ["identity: ..."], computed_at} (same file arm.sh crit_check reads)."""
import argparse, datetime, hashlib, json, os, re, sys

DEFAULT_RE = r":(nosidecar|noopts|not-applied|notapplied)$"


def frozen_bytes(data):
    # boundary rule: through the line "<!-- END FROZEN -->" when the marker exists, else the whole file (same as sed '/^<!-- END FROZEN -->$/q')
    out = b""
    for ln in data.splitlines(True):
        if ln.rstrip(b"\n") == b"<!-- END FROZEN -->":
            return out + b"<!-- END FROZEN -->\n"
        out += ln
    return data

def load(path, want):
    out = []
    for i, ln in enumerate(open(path, encoding="utf-8"), 1):
        ln = ln.strip()
        if not ln:
            continue
        try:
            t = json.loads(ln)
        except ValueError:
            raise ValueError("%s line %d is not JSON" % (path, i))
        if not isinstance(t, dict):
            continue
        if want is not None and t.get("itemId") not in want:
            continue
        out.append(t)
    return out


def meta(t):
    eng = t.get("engine") if isinstance(t.get("engine"), dict) else {}
    rt = t.get("runtime") if isinstance(t.get("runtime"), dict) else {}
    ver = rt.get("versions") if isinstance(rt.get("versions"), dict) else None
    route = t.get("route") if isinstance(t.get("route"), dict) else {}
    return {"commit": eng.get("commit") or None,
            "adapter": (ver.get("adapter") or None) if ver is not None else None,
            "patch": ((ver.get("engine.patch.sha256") or "none") if ver is not None else None),
            "codes": [c for c in (route.get("reasonCodes") or []) if isinstance(c, str)]}


def summarize(traces):
    ms = [meta(t) for t in traces]
    return {k: sorted({m[k] for m in ms if m[k] is not None}) for k in ("commit", "patch", "adapter")}, ms


def main():
    ap = argparse.ArgumentParser(prog="identity.py")
    ap.add_argument("--gen"); ap.add_argument("--replay"); ap.add_argument("--patch-sha"); ap.add_argument("--adapter"); ap.add_argument("--tree")
    ap.add_argument("--mode", default="on", choices=["on", "off"]); ap.add_argument("--not-applied-re", default=DEFAULT_RE); ap.add_argument("--ids")
    ap.add_argument("--write-verdict")
    a = ap.parse_args()
    if not a.gen:
        print("usage: identity.py --gen <traces.jsonl> [--replay F] [--patch-sha HEX] [--adapter S] [--tree C] [--mode on|off] [--not-applied-re RE] [--ids F]", file=sys.stderr); return 2
    try:
        want = set(x.strip() for x in open(a.ids) if x.strip()) if a.ids else None
        gen = load(a.gen, want); rep = load(a.replay, want) if a.replay else None
        rx = re.compile(a.not_applied_re)
    except (OSError, ValueError, re.error) as e:
        print("identity: unreadable input: %s" % e, file=sys.stderr); return 2
    gs, gm = summarize(gen)
    reasons = []
    if len(gs["commit"]) > 1: reasons.append("mixed-tree")
    if len(gs["patch"]) > 1: reasons.append("mixed-patch")
    if len(gs["adapter"]) > 1: reasons.append("mixed-adapter")
    if rep is not None:
        rs, _ = summarize(rep)
        if len(rs["commit"]) > 1: reasons.append("mixed-tree")
        if len(rs["patch"]) > 1: reasons.append("mixed-patch")
        if len(rs["adapter"]) > 1: reasons.append("mixed-adapter")
        for k, name in (("commit", "replay-tree"), ("patch", "replay-patch"), ("adapter", "replay-adapter")):
            if gs[k] and rs[k] and gs[k] != rs[k]:
                reasons.append(name)
    tree = gs["commit"][0] if gs["commit"] else None
    patch = gs["patch"][0] if gs["patch"] else None
    adapter = gs["adapter"][0] if gs["adapter"] else None
    if a.tree and tree and not tree.startswith(a.tree) and not a.tree.startswith(tree): reasons.append("pinned-mismatch")
    if a.patch_sha and patch is not None and patch != "none" and not (patch.startswith(a.patch_sha) or a.patch_sha.startswith(patch)): reasons.append("pinned-mismatch")
    if a.patch_sha and patch == "none": reasons.append("pinned-mismatch")
    if a.adapter and adapter and not (adapter == a.adapter or a.adapter in adapter): reasons.append("pinned-mismatch")
    n = len(gen); na = 0
    if a.mode == "on":
        na = sum(any(rx.search(c) for c in m["codes"]) for m in gm)
        if na: reasons.append("option-not-applied")
    seen = []; [seen.append(r) for r in reasons if r not in seen]
    if seen:
        line = "identity: FAIL %s n=%d notapplied=%d/%d" % (",".join(seen), n, na, n)
        print(line)
        if a.write_verdict:
            c = a.write_verdict
            rec = {"criterion_sha": hashlib.sha256(frozen_bytes(open(c, "rb").read())).hexdigest(), "verdict": "FAIL", "reasons": [line],
                   "computed_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
            dest = os.path.join(os.path.dirname(os.path.abspath(c)), "smoke.verdict.json"); tmp = dest + ".tmp%d" % os.getpid()
            with open(tmp, "w") as f:
                json.dump(rec, f, indent=1); f.write("\n")
            os.replace(tmp, dest)
        return 1
    print("identity: PASS n=%d tree=%s patch=%s adapter=%s" % (n, tree[:8] if tree else "unknown", (patch[:8] if patch and patch != "none" else "none") if patch else "unknown", adapter or "unknown"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
