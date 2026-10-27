#!/usr/bin/env python3
"""PACK-VISA aliases: redirect titles (from the enwiki-20261001 index grep) -> their target, via enwiki-20261001-redirect.sql.gz.
usage: aliases.py <index-titles.txt> <redirect.sql.gz> <out aliases.json>   (out: {target title: [redirect titles]})"""
import gzip, json, re, sys
idx, red, out = sys.argv[1:4]
ids = {}
for l in open(idx):
    off, pid, title = l.rstrip("\n").split(":", 2); ids[int(pid)] = title
tup = re.compile(r"\((\d+),(-?\d+),'((?:[^'\\]|\\.)*)'")
res = {}
with gzip.open(red, "rt", encoding="utf-8", errors="replace") as f:
    for line in f:
        for m in tup.finditer(line):
            pid = int(m.group(1))
            if pid in ids and m.group(2) == "0":
                tgt = m.group(3).replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\").replace("_", " ")
                res.setdefault(tgt, []).append(ids[pid])
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
print(len(res), sum(map(len, res.values())))
