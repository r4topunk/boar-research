#!/usr/bin/env python3
"""DEEPBO2 selector driver (criterion DEEPBO2-criterion.md sha256 c7e2232f...).

The selector prompt is FROZEN here (build_messages); build.py imports it to write prompts.jsonl.
Usage: select.py <S1|S2> <server-url> [--prompts P] [--replies-dir D] [--agg-dir D] [--limit N]
Posts each prompt (one at a time) to <server-url>/v1/chat/completions: temperature 0, max_tokens 8,
chat_template_kwargs.enable_thinking=false, seed 7, stream false. Appends <S>.replies.jsonl
(id, order, reply, ms, promptTokens) and writes <S>.picks.json. Resumable (skips (id, order) already replied).
Pick rule: first standalone A or B letter in the reply; a pick counts only if both orders map to the same seed,
otherwise "fallback" (scored as s42). Prints numbers only.
"""
import os, sys
# This file is named select.py and would shadow the stdlib `select` module (socket/urllib import it): drop our own dir.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:] = [p for p in sys.path if os.path.abspath(p or ".") != _HERE]
import json, re, time, statistics, urllib.request

SYSTEM = ("You compare two answers to the same question and reply with exactly one letter: A or B, "
          "the more accurate, complete and well-sourced answer.")
TAIL = "Which is better? Reply A or B."
LETTER = re.compile(r"\b([AB])\b")


def build_messages(question, answer_a, answer_b):
    user = f"{question}\n\nAnswer A:\n{answer_a}\n\nAnswer B:\n{answer_b}\n\n{TAIL}"
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def parse_letter(reply):
    m = LETTER.search(reply or "")
    return m.group(1) if m else None


def seed_of(order, letter):
    if letter is None:
        return None
    if order == "AB":
        return "s42" if letter == "A" else "s43"
    return "s43" if letter == "A" else "s42"


def rd(p):
    if not os.path.exists(p):
        return []
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    a = sys.argv[1:]
    if len(a) < 2 or a[0] not in ("S1", "S2"):
        sys.exit("usage: select.py <S1|S2> <server-url> [--prompts P] [--replies-dir D] [--agg-dir D] [--limit N]")
    sel, url = a[0], a[1].rstrip("/")
    opt = {a[i]: a[i + 1] for i in range(2, len(a) - 1, 2)}
    root = os.path.abspath(os.path.join(_HERE, "../../../../../.."))  # workspace root when run in place
    prompts_p = opt.get("--prompts", os.path.join(root, "blind/V-para/runs-deepbo2/prompts.jsonl"))
    rep_dir = opt.get("--replies-dir", os.path.join(root, "blind/V-para/runs-deepbo2"))
    agg_dir = opt.get("--agg-dir", os.path.join(_HERE, "../aggregates"))
    limit = int(opt["--limit"]) if "--limit" in opt else None
    os.makedirs(rep_dir, exist_ok=True); os.makedirs(agg_dir, exist_ok=True)
    rep_p = os.path.join(rep_dir, f"{sel}.replies.jsonl")
    prompts = rd(prompts_p)
    done = {(r["id"], r["order"]) for r in rd(rep_p)}
    todo = [p for p in prompts if (p["id"], p["order"]) not in done]
    if limit is not None:
        todo = todo[:limit]
    t0 = time.time()
    with open(rep_p, "a") as out:
        for p in todo:
            body = {"messages": p["messages"], "temperature": 0, "max_tokens": 8, "seed": 7, "stream": False,
                    "chat_template_kwargs": {"enable_thinking": False}}
            req = urllib.request.Request(url + "/v1/chat/completions", data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            s = time.time()
            with urllib.request.urlopen(req, timeout=900) as r:
                j = json.loads(r.read())
            ms = round((time.time() - s) * 1000, 1)
            reply = (j.get("choices") or [{}])[0].get("message", {}).get("content") or ""
            pt = (j.get("usage") or {}).get("prompt_tokens")
            out.write(json.dumps({"id": p["id"], "order": p["order"], "reply": reply, "ms": ms, "promptTokens": pt}) + "\n")
            out.flush()
            print(json.dumps({"n": len(done) + todo.index(p) + 1, "ms": ms, "promptTokens": pt}), flush=True)
    wall = time.time() - t0
    rows = rd(rep_p)
    by = {}
    for r in rows:
        by.setdefault(r["id"], {})[r["order"]] = seed_of(r["order"], parse_letter(r["reply"]))
    ids = sorted({p["id"] for p in prompts})
    picks, agree, both = {}, 0, 0
    for i in ids:
        o = by.get(i, {})
        if "AB" in o and "BA" in o:
            both += 1
            if o["AB"] is not None and o["AB"] == o["BA"]:
                picks[i] = o["AB"]; agree += 1
            else:
                picks[i] = "fallback"
    fails = sum(1 for r in rows if parse_letter(r["reply"]) is None)
    msl = [r["ms"] for r in rows]
    pp = os.path.join(agg_dir, f"{sel}.picks.json")  # keep cumulative wall across resumes
    prev_wall = json.load(open(pp)).get("wallS", 0) if (done and os.path.exists(pp)) else 0
    agg = {"selector": sel, "picks": picks, "nIds": len(ids), "nIdsComplete": both,
           "agreeRate": agree / both if both else None, "parseFailRate": fails / len(rows) if rows else None,
           "nCalls": len(rows), "wallS": round(prev_wall + wall, 1), "msMedian": statistics.median(msl) if msl else None,
           "nPick": {k: sum(1 for v in picks.values() if v == k) for k in ("s42", "s43", "fallback")},
           "promptsSha256": __import__("hashlib").sha256(open(prompts_p, "rb").read()).hexdigest()}
    with open(os.path.join(agg_dir, f"{sel}.picks.json"), "w") as f:
        json.dump(agg, f, indent=1)
    print(json.dumps({k: agg[k] for k in ("nIds", "nIdsComplete", "agreeRate", "parseFailRate", "nCalls", "wallS", "msMedian", "nPick")}))


if __name__ == "__main__":
    main()
