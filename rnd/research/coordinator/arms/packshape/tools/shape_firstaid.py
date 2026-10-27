#!/usr/bin/env python3
"""PACKSHAPE-FIRSTAID shaper (0 LLM; criterion ../FIRSTAID-criterion.md). Structure only: no word of the source is changed,
reordered or removed. Reads the v3proto boar-firstaid-en pack read-only and writes builder input <out>/firstaid.jsonl,
<out>/manifest.json, <out>/stats.json (--control writes the unshaped text).
Rules:
  F1 topic = the article title's last '/' segment (e.g. "Chest & Abdominal Injuries" for "First Aid/Chest & Abdominal Injuries").
  F2 prose paragraphs are split into sentences (after [a-z0-9)%] or two capitals + .!?); each list item ('- ', '* ', 'N. ', 'N) ')
     is one unit; a unit that does not contain the topic (case-insensitive) gets "<topic>: " in front (after the list marker).
     Headings, 'Key facts:' lines, table lines (' · ' or '|') and the title line are left exactly as they are.
  F3 inside each heading section, units are packed in order into blocks of <= 120 words and <= 950 chars; a new block of the
     same section repeats the section's heading line verbatim (so chunks never exceed the cap and keep the same section path).
     Paragraph/list boundaries inside a block are kept ('\\n\\n' between paragraphs, '\\n' between list items).
  F4 a single unit over the cap stays whole (never cut: no medical sentence is split).
Usage: python3 -I shape_firstaid.py <outdir> [--control]"""
import json, re, sys, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import fbread
F = "<workspace>/shared-data/packs/v3proto/boar-firstaid-en.sqlite"
MAXW, MAXC = 120, 950
LIST = re.compile(r"^(\s*(?:[-*]|\d+[.)])\s+)(.*)$")
SPLIT = re.compile(r"(?:(?<=[a-z0-9\)%][.!?])|(?<=[A-Z]{2}[.!?]))\s+(?=[A-Z\"'(])")
nw = lambda s: len(s.split())
def topic_of(title): return title.split("/")[-1].strip()
def tag(topic, s):
    return s if topic.lower() in s.lower() else f"{topic}: {s}"
def paragraph_units(topic, par):
    """-> list of (unit text, joiner) where joiner is the separator to the previous unit inside the same paragraph."""
    lines = par.split("\n")
    if lines[0].startswith(("Key facts:", "#")) or any(" · " in l or l.lstrip().startswith("|") for l in lines):
        return [("\n".join(lines), None)]  # left as is
    out = []
    if all(LIST.match(l) or not l.strip() for l in lines if l.strip()) and any(LIST.match(l) for l in lines):
        for l in lines:
            m = LIST.match(l)
            out.append((m.group(1) + tag(topic, m.group(2)) if m else l, "\n"))
        return out
    if len(lines) > 1:  # mixed lines (e.g. a lead line then list items): each line is a unit
        for l in lines:
            m = LIST.match(l)
            out.append((m.group(1) + tag(topic, m.group(2)) if m else (tag(topic, l) if l.strip() else l), "\n"))
        return out
    return [(tag(topic, s), " ") for s in SPLIT.split(par.strip()) if s.strip()]
def shape(a):
    topic = topic_of(a["title"]); text = a["text"]
    m = re.match(r"^# [^\n]*\n+", text); head = m.group(0) if m else ""; body = text[len(head):]
    # sections: split before heading lines
    secs = re.split(r"\n\n(?=#{1,6} )", body)
    out_secs = []
    for sec in secs:
        hm = re.match(r"^(#{1,6} [^\n]*)(?:\n+|$)", sec); hline = hm.group(1) if hm else None; rest = sec[hm.end():] if hm else sec
        blocks, cur, cw, cc = [], [], 0, 0
        for pi, par in enumerate([p for p in rest.split("\n\n") if p.strip()]):
            for ui, (u, j) in enumerate(paragraph_units(topic, par)):
                sep = "\n\n" if ui == 0 else (j or "\n")
                if cur and (cw + nw(u) > MAXW or cc + len(u) + len(sep) > MAXC):
                    blocks.append("".join(cur)); cur, cw, cc = [], 0, 0; sep = ""
                if not cur: sep = ""
                cur.append(sep + u); cw += nw(u); cc += len(u) + len(sep)
        if cur: blocks.append("".join(cur))
        if not blocks: out_secs.append(hline or ""); continue
        for bi, b in enumerate(blocks):
            out_secs.append((hline + "\n\n" + b) if hline else (b if bi == 0 else b))  # unheaded lead: blocks split by paragraph only
    return head + "\n\n".join(s for s in out_secs if s), topic
def main():
    out = sys.argv[1]; control = "--control" in sys.argv; os.makedirs(out, exist_ok=True)
    import sqlite3
    SRCN = {0: "enwiki", 1: "enwikivoyage", 2: "enwikibooks", 3: "appropedia", 4: "usgov"}
    sid = dict(sqlite3.connect(f"file:{F}?mode=ro", uri=True).execute("select id, source from articles").fetchall())
    A = fbread.articles(F)
    for a in A: a["src_name"] = SRCN[sid[a["id"]]]
    st = dict(articles=0, chars=0); docs, man, topics = [], [], {}
    for a in A:
        text, topic = (a["text"], topic_of(a["title"])) if control else shape(a); topics[a["title"]] = topic
        st["articles"] += 1; st["chars"] += len(text)
        d = dict(page_id=a["page_id"], title=a["title"], text=text, source=a["src_name"], url=a["url"], license=a["license"], views=a["views"], infoboxes=None)
        if a["attribution"]: d["attribution"] = a["attribution"]
        if a["aliases"]: d["aliases"] = a["aliases"]
        docs.append(d); man.append(dict(page_id=a["page_id"], title=a["title"], source=a["src_name"], url=a["url"], license=a["license"]))
    with open(f"{out}/firstaid.jsonl", "w") as f:
        for d in docs: f.write(json.dumps(d, ensure_ascii=False) + "\n")
    json.dump(man, open(f"{out}/manifest.json", "w"), ensure_ascii=False); json.dump(topics, open(f"{out}/topics.json", "w"), ensure_ascii=False)
    st["jsonl_sha256"] = hashlib.sha256(open(f"{out}/firstaid.jsonl", "rb").read()).hexdigest(); json.dump(st, open(f"{out}/stats.json", "w"), indent=1); print(json.dumps(st))
if __name__ == "__main__": main()
