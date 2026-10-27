#!/usr/bin/env python3
"""NOTES35 replay hit-rate: share of items whose engine-kept `sources` and whose `raw` retrieval contain >= 1 note.

usage: python3 -I hitrate.py <replay.jsonl> <notes.jsonl> [--ids FILE] [--gate 0.15]

replay.jsonl: replay-retrieval.sh output ({id, raw: [{title, section, source, ...}], sources: [titles], ...}).
A raw chunk is a note when its `source` carries the pack's tag (notes35.boar.invalid) -- exact, immune to a curated
pack article with the same title (e.g. the crypto pack's enwiki "Sahara"); only if the replay rows have no `source`
key at all does it fall back to the title.
`sources` holds titles only (the engine's pre-answer sources event), so it is matched by note title (casefold);
items where that title also appears in raw from a non-note source are counted separately (title collisions).
Prints counts only (no titles, no text). Gate: sources hit-rate >= --gate (default 0.15) -> PASS.
"""
import json
import sys

TAG = "notes35.boar.invalid"


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    replay_path, notes_path = argv[0], argv[1]
    gate = float(argv[argv.index("--gate") + 1]) if "--gate" in argv else 0.15
    ids = None
    if "--ids" in argv:
        raw_ids = open(argv[argv.index("--ids") + 1]).read().replace(",", "\n").split()
        ids = set(x.strip() for x in raw_ids if x.strip())
    titles = set()
    for line in open(notes_path):
        if line.strip():
            titles.add(json.loads(line)["title"].casefold())
    items = [json.loads(l) for l in open(replay_path) if l.strip()]
    if ids is not None:
        items = [it for it in items if it["id"] in ids]
    n = len(items)
    retrieved = raw_hit = src_hit = src_hit_collide = 0
    note_chunks = raw_chunks = 0
    for it in items:
        raw = it.get("raw") or []
        if raw:
            retrieved += 1
        is_note = []
        for c in raw:
            if "source" in c:  # format-2 pack chunks always carry a source; None = seed corpus / format-1 chunk
                is_note.append(TAG in (c.get("source") or ""))
            else:  # replay output without source strings: title match (may count same-titled curated articles)
                is_note.append((c.get("title") or "").casefold() in titles)
        raw_chunks += len(raw)
        note_chunks += sum(is_note)
        if any(is_note):
            raw_hit += 1
        kept = [(s or "").casefold() for s in (it.get("sources") or [])]
        hit = [s for s in kept if s in titles]
        if hit:
            note_titles_in_raw = {(c.get("title") or "").casefold() for c, f in zip(raw, is_note) if f}
            if any(h in note_titles_in_raw for h in hit):
                src_hit += 1
            else:
                src_hit_collide += 1  # kept title equals a note title but no note chunk was retrieved for it
    rate = lambda k: (k / n) if n else 0.0
    print(json.dumps({
        "items": n, "retrievedItems": retrieved, "noteTitles": len(titles),
        "rawHitItems": raw_hit, "rawHitRate": round(rate(raw_hit), 4),
        "sourcesHitItems": src_hit, "sourcesHitRate": round(rate(src_hit), 4),
        "sourcesTitleCollisionsOnly": src_hit_collide,
        "noteChunksInRaw": note_chunks, "rawChunks": raw_chunks,
        "gate": gate, "verdict": "PASS" if rate(src_hit) >= gate else "FAIL",
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
