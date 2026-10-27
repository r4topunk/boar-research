#!/usr/bin/env python3
"""exp-04: Jev (typesafe-ai/jev via Vercel AI Gateway) as a classifier of BOAR eval answers. DESKTOP EVAL ONLY.

State per batch = keyed object of items (never positional indexes): items.<key> = {question, reference, rubric, answer,
retrieved_titles}. Per item, 2 questions: a 4-way `choice` label and a `boolean` unsafe_advice. 20 items per request
(40 questions, under the ~60 where the gateway starts 503-ing). Disk cache keyed by sha256 of the request body
(Jev is deterministic, so a cached answer is the answer). Backoff 1-8 s on 5xx, 5 retries. Spend tracked per response
(providerMetadata.gateway.marketCost) and HARD-STOPPED at --budget-usd cumulative.

Usage: python3 jev_judge.py --prompts prompts/v1.json --rows rows.jsonl --out preds/v1-<set>.jsonl [--no-cache]
Key: $VERCEL_AI_GATEWAY (never logged).
"""
import argparse, hashlib, json, os, sys, time, urllib.error, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--prompts", required=True)
ap.add_argument("--rows", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--batch", type=int, default=20)
ap.add_argument("--no-cache", action="store_true", help="bypass the cache (determinism check); still writes a separate cache entry")
ap.add_argument("--budget-usd", type=float, default=0.90)
ap.add_argument("--spend-file", default="spend.jsonl")
a = ap.parse_args()

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
P = json.load(open(a.prompts))
prompt_sha = hashlib.sha256(open(a.prompts, "rb").read()).hexdigest()
rows = [json.loads(l) for l in open(a.rows) if l.strip()]


def spent():
    p = os.path.join(HERE, a.spend_file)
    return sum(json.loads(l)["usd"] for l in open(p)) if os.path.exists(p) else 0.0


def call(body):
    raw = json.dumps(body, sort_keys=True, ensure_ascii=False).encode()
    h = hashlib.sha256(raw).hexdigest()
    path = os.path.join(CACHE, h + (".nocache-" + str(int(time.time() * 1000)) if a.no_cache else "") + ".json")
    hit = os.path.join(CACHE, h + ".json")
    if not a.no_cache and os.path.exists(hit):
        return json.load(open(hit)), 0.0, 0.0, True
    if spent() >= a.budget_usd:
        sys.exit(f"BUDGET STOP: cumulative spend {spent():.4f} USD >= {a.budget_usd}")
    req = urllib.request.Request("https://ai-gateway.vercel.sh/v1/evaluate", data=raw,
                                 headers={"authorization": f"Bearer {os.environ['VERCEL_AI_GATEWAY']}", "content-type": "application/json"})
    for attempt in range(6):
        t0 = time.perf_counter()
        try:
            r = json.load(urllib.request.urlopen(req, timeout=60))
            dt = time.perf_counter() - t0
            usd = float(((r.get("providerMetadata") or {}).get("gateway") or {}).get("marketCost") or 0)
            json.dump(r, open(path, "w"))
            with open(os.path.join(HERE, a.spend_file), "a") as f:
                f.write(json.dumps({"t": time.time(), "usd": usd, "secs": round(dt, 3), "inTok": (r.get("usage") or {}).get("inputTokens"), "body": h}) + "\n")
            return r, usd, dt, False
        except urllib.error.HTTPError as e:
            if e.code >= 500 and attempt < 5:
                time.sleep(min(8, 2 ** attempt))
                continue
            sys.exit(f"HTTP {e.code}: {e.read()[:300]!r}")


def item_state(r):
    return {"question": r["query"], "reference": r["reference"], "rubric": r.get("rubric") or "",
            "answer": r["answer"] if r["answer"].strip() else "(empty: the app showed no answer text)",
            "retrieved_titles": r.get("titles") or []}


out = []
for i in range(0, len(rows), a.batch):
    chunk = rows[i:i + a.batch]
    keys = [f"k{j:02d}" for j in range(len(chunk))]
    state = {"items": {k: item_state(r) for k, r in zip(keys, chunk)}}
    qs = {}
    for k in keys:
        qs[f"{k}_label"] = {"type": "choice", "instructions": P["label"]["instructions"].replace("{item}", f"items.{k}"),
                            "criteria": P["label"]["criteria"]}
        qs[f"{k}_unsafe"] = {"type": "boolean", "instructions": P["unsafe"]["instructions"].replace("{item}", f"items.{k}"),
                             **({"criteria": P["unsafe"]["criteria"]} if P["unsafe"].get("criteria") else {})}
    body = {"model": "typesafe-ai/jev", "state": state, "questions": qs}
    r, usd, dt, cached = call(body)
    A = r["answers"]
    for k, row in zip(keys, chunk):
        lab, un = A[f"{k}_label"], A[f"{k}_unsafe"]
        out.append({"src": row["src"], "model": row["model"], "queryId": row["queryId"], "hand": row["hand4"],
                    "jev": lab["choice"], "probs": lab.get("probabilities"), "confidence": lab.get("confidence"),
                    "unsafe_p": un.get("probability"), "batch_secs": round(dt, 3), "batch_usd": usd, "cached": cached,
                    "batch_n": len(chunk), "prompt_sha": prompt_sha})
    print(f"batch {i // a.batch + 1}: {len(chunk)} items, {'cache' if cached else f'{dt:.2f}s ${usd:.6f}'}; cumulative ${spent():.5f}", flush=True)

with open(a.out, "w") as f:
    for o in out:
        f.write(json.dumps(o) + "\n")
print(f"wrote {a.out} ({len(out)} rows), prompts sha256 {prompt_sha[:16]}…, cumulative spend ${spent():.5f}")
