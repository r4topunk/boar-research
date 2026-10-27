#!/usr/bin/env python3
"""replylang keep/kill read-out from Kiln's runs (no judge): lang_match + routing parity on chat-slice v0 for 4B and
1.5B (arm vs main), every changed answer printed for a hand read, safety v0.8.1 on both sides, and L1
outofkit-quality identity (arm vs main, expected byte-identical: 0 prompt changes on v0.1)."""
import importlib.util, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CS = HERE.parent
RUNS = Path("<workspace>/boar-eval/runs/kiln")
sys.path.insert(0, str(CS))
from score_l0 import lang_of, searched_from_trace, REPLY_LANG  # noqa: E402

spec = importlib.util.spec_from_file_location("s8", CS.parent / "exp/safety-v08/safety_check.v0.8.py")
sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
S = sc.load(rules_path=CS.parent / "exp/safety-v081/rules.v0.8.1.json", overlay_path=CS.parent / "exp/safety-v081/overlay.v0.4.json")
ITEMS = {json.loads(l)["id"]: json.loads(l) for l in open(CS / "slice.v0.jsonl")}


def tr(p):
    return {t["itemId"]: t for t in map(json.loads, open(p))} if Path(p).exists() else None


def unsafe(it, t):
    r = sc.rules_for_v08(it, S)
    return [h["rule"] for h in sc.check(t["answer"]["text"], r, S) if h.get("status", "unsafe") == "unsafe"] if r else []


def compare(name, main_p, arm_p, verbose=True):
    a, b = tr(main_p), tr(arm_p)
    if a is None or b is None:
        print(f"## {name}: missing ({'main' if a is None else 'arm'})"); return
    want = {i: it.get("reply_lang") or REPLY_LANG.get(i) or it["lang"] for i, it in ITEMS.items()}
    lm = lambda T: sum(lang_of(T[i]["answer"]["text"]) == want[i] for i in ITEMS if i in T)
    route = sum(searched_from_trace(a[i]) == searched_from_trace(b[i]) for i in ITEMS if i in a and i in b)
    fixed = [i for i in ITEMS if lang_of(a[i]["answer"]["text"]) != want[i] and lang_of(b[i]["answer"]["text"]) == want[i]]
    broke = [i for i in ITEMS if lang_of(a[i]["answer"]["text"]) == want[i] and lang_of(b[i]["answer"]["text"]) != want[i]]
    changed = [i for i in ITEMS if a[i]["answer"]["text"] != b[i]["answer"]["text"]]
    ua = {i: unsafe(ITEMS[i], a[i]) for i in ITEMS}; ub = {i: unsafe(ITEMS[i], b[i]) for i in ITEMS}
    cit = lambda T, ids: sum("[" in T[i]["answer"]["text"] for i in ids)
    print(f"## {name}\nlang_match main {lm(a)}/64 → arm {lm(b)}/64; fixed {len(fixed)} {fixed}; broke {len(broke)} {broke}")
    print(f"routing identical {route}/64; answers changed {len(changed)}/64; with [n] among changed: main {cit(a, changed)} → arm {cit(b, changed)}")
    print(f"unsafe (v0.8.1): main {sum(map(bool, ua.values()))} {[(i, v) for i, v in ua.items() if v]} → arm {sum(map(bool, ub.values()))} {[(i, v) for i, v in ub.items() if v]}")
    print(f"declined main {sum(a[i]['answer']['declined'] for i in ITEMS)} → arm {sum(b[i]['answer']['declined'] for i in ITEMS)}")
    if verbose:
        for i in changed:
            print(f"--- {i} ({ITEMS[i]['lang']},{ITEMS[i]['kind']}) want {want[i]}: {lang_of(a[i]['answer']['text'])}→{lang_of(b[i]['answer']['text'])} | expected: {ITEMS[i]['expected']}")
            print("  MAIN:", a[i]["answer"]["text"].replace("\n", " / ")[:300])
            print("  ARM :", b[i]["answer"]["text"].replace("\n", " / ")[:300])
    print()


compare("4B chat-slice v0", RUNS / "chat-slice-base-s42/traces.jsonl", RUNS / "replylang/chat-v0-4b-replylang/traces.jsonl")
compare("1.5B chat-slice v0", RUNS / "replylang/chat-v0-15b-main/traces.jsonl", RUNS / "replylang/chat-v0-15b-replylang/traces.jsonl")
a, b = tr(RUNS / "l1/main-node-outofkit-quality-s42/traces.jsonl"), tr(RUNS / "l1/replylang-outofkit-quality-s42/traces.jsonl")
if a and b:
    ids = [i for i in a if i in b]
    same = [i for i in ids if a[i]["answer"]["text"] == b[i]["answer"]["text"]]
    print(f"## L1 outofkit-quality 4B: identical answers {len(same)}/{len(ids)}; differ: {[i for i in ids if i not in same]}")
else:
    print("## L1 outofkit-quality: missing")
