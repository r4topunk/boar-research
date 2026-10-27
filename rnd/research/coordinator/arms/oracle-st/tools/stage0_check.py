#!/usr/bin/env python3
"""ORACLE-ST stage 0 checks on 3 items: (a) OFF on the copy tree == S trace (answer text, kept list, raw list, reasonCodes, promptTokens, outputTokens);
(b) ADD prompt == OFF prompt + exactly one appended '\\n\\n[n] title\\nbody' block whose chunk text (body minus 'section: ') is byte-equal to the pack
chunk read from sqlite (zstd block, UTF-16 slice, trim; sha in oracle-facts.json). Usage: python3 -I stage0_check.py"""
import json, hashlib, sys, sqlite3
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/oracle-st/tools")
_src = open("<workspace>/rnd/research/coordinator/arms/oracle-st/tools/build_oracle.py").read().split("add, only, facts, missing")[0]
exec(_src)  # pub, article_text, js_slice, js_trim (the builder's own sqlite + zstd reader)
def chunk_text(f):
    db = sqlite3.connect(f"file:{pub(f['pack'])}?mode=ro", uri=True); cid = int(f["oracle_chunk"].rsplit(":", 1)[1])
    aid, s0, e0 = db.execute("SELECT article_id, start, end FROM chunks WHERE id=?", (cid,)).fetchone()
    return js_trim(js_slice(article_text(db, pub(f["pack"]), aid), s0, e0))
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/oracle-st"; SR = f"{ROOT}/rnd/research/coordinator/arms/packs/selftest-runs"
facts = json.load(open(f"{A}/tools/oracle-facts.json"))
sel = {"qa-bitcoin-se": "st-qa-bitcoin-se-001", "boar-simplewiki-en": "st-boar-simplewiki-en-002", "qa-travel-se": "st-qa-travel-se-003"}
L = lambda f: [json.loads(l) for l in open(f) if l.strip()]
offp = {r["query"]: r["prompt"] for r in L(f"{A}/runs/stage0/off.prompts.jsonl")}; addp = {r["query"]: r["prompt"] for r in L(f"{A}/runs/stage0/add.prompts.jsonl")}
def sysmsg(p): return p[0]["content"] if isinstance(p, list) else p
ok = True
for p, i in sel.items():
    s = next(t for t in L(f"{SR}/st-{p}-cut7-s42.traces.jsonl") if t["itemId"] == i)
    o = L(f"{A}/runs/stage0/off-{p}.traces.jsonl")[0]; a = L(f"{A}/runs/stage0/add-{p}.traces.jsonl")[0]
    eq = {k: f(s) == f(o) for k, f in {"answer.text": lambda t: t["answer"]["text"], "kept": lambda t: t["retrieval"]["kept"], "raw": lambda t: t["retrieval"]["raw"],
          "reasonCodes": lambda t: t["route"]["reasonCodes"], "promptTokens": lambda t: t["timing"]["promptTokens"], "outputTokens": lambda t: t["timing"]["outputTokens"]}.items()}
    q = s["question"]; po, pa = offp.get(q), addp.get(q)
    oc = [c for c in a["route"]["reasonCodes"] if c.startswith("oracle:")]
    line = f"{i}: OFF==S {eq} | oracle codes {oc} | promptTokens S/off/add {s['timing']['promptTokens']}/{o['timing']['promptTokens']}/{a['timing']['promptTokens']} | kept S/off/add {len(s['retrieval']['kept'])}/{len(o['retrieval']['kept'])}/{len(a['retrieval']['kept'])}"
    ok &= all(eq.values())
    so, sa = sysmsg(po), sysmsg(pa)
    if any(c.startswith("oracle:add:") for c in oc):
        n = len(o["retrieval"]["kept"]) + 1
        # OFF prompt's context block must be a prefix; the ADD prompt inserts one block after it
        ctx_end = so.index("\n\nQuestion:") if "\n\nQuestion:" in so else len(so)
        head, tail = so[:ctx_end], so[ctx_end:]
        if not o["retrieval"]["kept"]:  # no Context section in OFF: compare the source block only
            blk = sa[sa.index(f"[{n}] "):]
            blk = blk[:blk.index("\n\nQuestion:")] if "\n\nQuestion:" in blk else blk
            pre_ok = True
        else:
            pre_ok = sa.startswith(head) and sa.endswith(tail)
            blk = sa[len(head):len(sa) - len(tail)]
            assert blk.startswith(f"\n\n[{n}] "), blk[:40]; blk = blk[2:]
        title, body = blk.split("\n", 1)
        ctext = chunk_text(facts[i])
        # packHitToChunk: body = "<section>: <text>" (section = heading path at the chunk start) or just <text> for the lead
        bye = body.endswith(ctext) and (body == ctext or body[:-len(ctext)].endswith(": "))
        sha = hashlib.sha256(ctext.encode()).hexdigest()
        line += (f"\n   ADD: OFF prompt == ADD prompt minus one block: {pre_ok}; block '{title[:60]}' body {len(body)} chars; section prefix {body[:-len(ctext)]!r}; "
                 f"sqlite chunk text ({len(ctext)} chars, sha {sha[:16]} == builder sha {facts[i]['chunk_text_sha256'][:16]}: {sha == facts[i]['chunk_text_sha256']}) byte-equal to the body after the prefix: {bye}")
        bye = bye and sha == facts[i]["chunk_text_sha256"]
        ok &= pre_ok and bye
    else:
        line += f"\n   ADD: no append ({oc}); ADD prompt == OFF prompt: {so == sa}"
        ok &= so == sa and any(c.startswith("oracle:add-already-kept:") for c in oc)
    print(line)
print("STAGE0", "PASS" if ok else "FAIL")
