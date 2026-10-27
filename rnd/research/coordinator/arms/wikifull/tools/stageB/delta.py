#!/usr/bin/env python3
"""WIKIFULL stage B delta: enwiki 20261001 multistream index pages (ns0, not a redirect per redirect.sql) whose
page_id AND title are both absent from FineWiki enwiki Aug-2025. Writes delta.tsv (offset, length, page_id, title)
and prints counts + exact stream bytes. usage: delta.py INDEX.bz2 REDIRECT.sql.gz FINEWIKI_IDS.tsv OUTDIR DUMP_BYTES [PAGE_PROPS.sql.gz]
Disambiguation pages (page_props) are dropped up front (no facts; not article content)."""
import bz2, gzip, re, sys, json, random, collections
idx, red, fw, od = sys.argv[1:5]
NS = ["Talk", "User", "User talk", "Wikipedia", "Wikipedia talk", "File", "File talk", "MediaWiki", "MediaWiki talk",
      "Template", "Template talk", "Help", "Help talk", "Category", "Category talk", "Portal", "Portal talk", "Draft",
      "Draft talk", "TimedText", "TimedText talk", "Module", "Module talk", "Book", "Book talk", "Education Program",
      "Education Program talk", "Gadget", "Gadget talk", "Gadget definition", "Gadget definition talk", "Topic",
      "MOS", "MOS talk", "Event", "Event talk", "Special", "Media"]
NSP = tuple(n + ":" for n in NS)
fw_ids, fw_titles = set(), set()
for line in open(fw, encoding="utf-8"):
    p, _, t = line.rstrip("\n").partition("\t")
    if p.isdigit(): fw_ids.add(int(p))
    fw_titles.add(t)
print("finewiki rows", len(fw_ids), "titles", len(fw_titles), flush=True)
rd = set(); rx = re.compile(rb"\((\d+),(-?\d+),'")
with gzip.open(red, "rb") as f:
    for line in f:
        if line.startswith((b"INSERT INTO", b"(")):
            rd.update(int(m.group(1)) for m in rx.finditer(line))
print("redirect rows", len(rd), flush=True)
PP = sys.argv[6] if len(sys.argv) > 6 else None; dis = set()
if PP:
    rx2 = re.compile(rb"\((\d+),'disambiguation'")
    with gzip.open(PP, "rb") as f:
        for line in f:
            if b"disambiguation" in line: dis.update(int(m.group(1)) for m in rx2.finditer(line))
    print("disambiguation pages", len(dis), flush=True)
fwmax = max(fw_ids)
offs = set(); c = collections.Counter(); delta = []
with bz2.open(idx, "rt", encoding="utf-8") as f:
    for line in f:
        a = line.index(":"); b = line.index(":", a + 1)
        off, pid, t = int(line[:a]), int(line[a+1:b]), line[b+1:].rstrip("\n")
        offs.add(off); c["index"] += 1
        if t.startswith(NSP): continue
        c["ns0"] += 1
        if pid in rd: continue
        c["ns0_nonredirect"] += 1
        inid, intt = pid in fw_ids, t in fw_titles
        if inid and intt: c["in_fw_same"] += 1
        elif inid: c["in_fw_renamed"] += 1
        elif intt: c["new_id_same_title"] += 1
        elif pid in dis: c["delta_disambiguation_dropped"] += 1
        else:
            delta.append((off, pid, t)); c["delta_id_above_fw_max"] += pid > fwmax
c["delta"] = len(delta)
so = sorted(offs); nxt = {so[i]: so[i+1] for i in range(len(so) - 1)}
END = int(sys.argv[5]) if len(sys.argv) > 5 else None
streams = sorted({d[0] for d in delta})
ln = {o: (nxt.get(o) or END) - o for o in streams}
c["streams_needed"] = len(streams); c["streams_total"] = len(so)
c["bytes_needed"] = sum(ln.values())
with open(f"{od}/delta.tsv", "w", encoding="utf-8") as o:
    for off, pid, t in delta: o.write(f"{off}\t{ln[off]}\t{pid}\t{t}\n")
json.dump(dict(c), open(f"{od}/delta-counts.json", "w"), indent=1)
print(json.dumps(dict(c)))
