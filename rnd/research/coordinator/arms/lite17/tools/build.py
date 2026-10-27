#!/usr/bin/env python3
"""LITE17 build (criterion 453826c0, 0 LLM). Input = CHAINWHEN OFF prompts (arms/chainwhen/data/prompts.jsonl, arm OFF): the 150 RELGATE contexts
with prompt D4 exactly as PACKREAD (CHAINWHEN build.py asserts the context is byte-identical to the cut7+X2b engine prompt). Writes ../data/:
  prompts.jsonl  rows {id, pack, arm, messages}: B (= OFF verbatim), T (= B messages; thinking handled in gen.py), Q1 (pass-1 quote prompt), S (only where S != B)
  s-drops.json   per-item S drops (rule below), counts per pack, 2 examples
  ids-150.ids, ids-S.ids
S rule (deterministic, text only; the chunk = "[n] <title>\\n<body>" of the X2b context):
  a source is an SE post when its pack is qa-*-se, its title has no source label (Wikivoyage: / ethereum.org: / Ethereum EIPs/ERCs: / Wikipedia:)
  and its body does not start with a wiki section path ("A > B: ...", at least one " > "; a bare "Edit: ..." is a question edit, not a section);
  an SE post chunk is ANSWER text iff its body starts with "Answers > Answer" (the pack chunker prefixes every answer chunk so);
  every other SE post chunk (head chunk "Tags: ..." or an unprefixed continuation of the question body) is QUESTION-ONLY and is dropped.
  The kept sources are renumbered 1..k in their original order. If every source would be dropped, nothing is dropped (S = B; counted).
Q pass 1: system = B system (D4 + context, unchanged); user = question + "\\n\\n" + QUOTE (criterion text verbatim); thinking off; max 200 tokens.
Usage: python3 -I build.py"""
import json, os, re, hashlib, collections
ROOT = "<workspace>"; ARMS = f"{ROOT}/rnd/research/coordinator/arms"; H = f"{ARMS}/lite17"
CTX = "\n\nContext:\n"
QUOTE = "Quote the sentence(s) from the sources that answer the question, with their source number, or write NONE."
LABELS = ("Wikivoyage:", "ethereum.org:", "Ethereum EIPs/ERCs:", "Wikipedia:")
SECTION = re.compile(r"^[A-Z][^\n:.?!]{0,80}(?: > [^\n:]{1,80})+: ")
STYLE = "\n\n(Response style:"

def split_ctx(sysm):  # = chainwhen/tools/build.py split_ctx (= relgate build_sets split_context)
    i = sysm.find(CTX); ctx = sysm[i + len(CTX):]
    parts = re.split(r"(?:^|\n\n)\[(\d+)\] ", ctx)
    assert parts[0] == "", parts[0][:80]
    ch = [(int(parts[k]), parts[k + 1]) for k in range(1, len(parts), 2)]
    assert [n for n, _ in ch] == list(range(1, len(ch) + 1))
    assert sysm[:i] + CTX + "\n\n".join(f"[{n}] {b}" for n, b in ch) == sysm, "roundtrip"
    return sysm[:i], ch

def classify(pack, chunk):
    if not (pack.startswith("qa-") and pack.endswith("-se")): return "non-se-pack"
    title, _, body = chunk.partition("\n")
    if title.startswith(LABELS): return "doc"
    if body.startswith("Answers > Answer"): return "se-answer"
    if body.startswith("Tags:"): return "se-question"
    if SECTION.match(body): return "doc"
    return "se-question"

def main():
    src = f"{ARMS}/chainwhen/data/prompts.jsonl"
    rows = [json.loads(l) for l in open(src)]; B = sorted((r for r in rows if r["arm"] == "OFF"), key=lambda r: r["id"])
    assert len(B) == 150 and len({r["id"] for r in B}) == 150
    out, drops, ex = [], {}, []
    cnt = collections.Counter(); kinds = collections.Counter(); allq = []
    for r in B:
        iid, pack, msgs = r["id"], r["pack"], r["messages"]
        sysm, user = msgs[0]["content"], msgs[1]["content"]
        q = user[:user.rindex(STYLE)]
        base = dict(id=iid, pack=pack)
        out.append(dict(base, arm="B", messages=msgs))
        out.append(dict(base, arm="T", messages=msgs))
        out.append(dict(base, arm="Q1", messages=[{"role": "system", "content": sysm}, {"role": "user", "content": q + "\n\n" + QUOTE}]))
        head, ch = split_ctx(sysm)
        cls = [classify(pack, b) for _, b in ch]
        for c in cls: kinds[(pack, c)] += 1
        keep = [b for (n, b), c in zip(ch, cls) if c != "se-question"]
        dropped = [n for (n, b), c in zip(ch, cls) if c == "se-question"]
        if dropped and not keep:
            allq.append(iid); dropped = []; keep = [b for _, b in ch]
        if dropped:
            new_sys = head + CTX + "\n\n".join(f"[{k + 1}] {b}" for k, b in enumerate(keep))
            out.append(dict(base, arm="S", messages=[{"role": "system", "content": new_sys}, msgs[1]]))
            drops[iid] = dict(pack=pack, n_src=len(ch), dropped=dropped, kept_old_nums=[n for (n, b), c in zip(ch, cls) if c != "se-question"])
            cnt[pack] += len(dropped)
            if len(ex) < 2 and any(ch[d - 1][1].split("\n", 1)[1].startswith("Tags:") for d in dropped) == (len(ex) == 0):
                ex.append(dict(id=iid, dropped={d: ch[d - 1][1][:400] for d in dropped}))
    os.makedirs(f"{H}/data", exist_ok=True)
    open(f"{H}/data/prompts.jsonl", "w").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out))
    open(f"{H}/data/ids-150.ids", "w").write("".join(r["id"] + "\n" for r in B))
    open(f"{H}/data/ids-S.ids", "w").write("".join(i + "\n" for i in drops))
    per_pack_items = collections.Counter(d["pack"] for d in drops.values())
    json.dump(dict(source=src, source_sha256=hashlib.sha256(open(src, "rb").read()).hexdigest(),
                   items_changed=len(drops), chunks_dropped=sum(cnt.values()), dropped_chunks_per_pack=dict(cnt),
                   items_changed_per_pack=dict(per_pack_items), all_question_only_items_kept_as_B=allq,
                   chunk_classes={f"{p}|{c}": v for (p, c), v in sorted(kinds.items())}, examples=ex, items=drops),
              open(f"{H}/data/s-drops.json", "w"), indent=1, ensure_ascii=False)
    print("rows", collections.Counter(x["arm"] for x in out), "S items", len(drops), "chunks dropped", dict(cnt), "all-question kept", allq)

if __name__ == "__main__":
    main()
