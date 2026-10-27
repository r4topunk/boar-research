#!/usr/bin/env python3
"""HUMANSFT download (criterion 83d4e9d0...): fetch the train files of CLAPnq, HAGRID and Dolly from the HF Hub public
resolve URLs (no login, no token, generic User-Agent) into <raw_root>/<dataset>/, record sha256 + row counts.
Refuses to write into a non-empty dataset dir. Hard cap 60 MB total. Up to 2 attempts per file.
Usage: python3 -I download.py <raw_root> <manifest.json>"""
import hashlib, json, sys, time, urllib.request
from pathlib import Path

UA = "Mozilla/5.0"
CAP = 60 * 1024 * 1024
FILES = [  # (dataset dir, repo, path in repo)
    ("clapnq", "PrimeQA/clapnq", "clapnq_train_answerable.jsonl"),
    ("clapnq", "PrimeQA/clapnq", "clapnq_train_unanswerable.jsonl"),
    ("hagrid", "miracl/hagrid", "hagrid-v1.0-en/train.jsonl"),
    ("dolly", "databricks/databricks-dolly-15k", "databricks-dolly-15k.jsonl"),
]


def main():
    root, manifest = Path(sys.argv[1]), Path(sys.argv[2])
    total, rows = 0, []
    for d in {f[0] for f in FILES}:
        p = root / d
        if p.exists() and any(p.iterdir()):
            sys.exit(f"refusing: {p} not empty")
        p.mkdir(parents=True, exist_ok=True)
    for d, repo, path in FILES:
        url = f"https://huggingface.co/datasets/{repo}/resolve/main/{path}"
        out = root / d / Path(path).name
        data, err = None, None
        for attempt in range(2):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read(CAP - total + 1)
                break
            except Exception as e:  # noqa: BLE001
                err = repr(e); time.sleep(3)
        if data is None:
            rows.append({"dataset": d, "file": out.name, "url": url, "error": err}); continue
        total += len(data)
        if total > CAP:
            sys.exit("60 MB cap exceeded")
        out.write_bytes(data)
        n = sum(1 for l in data.decode("utf-8").splitlines() if l.strip())
        rows.append({"dataset": d, "file": out.name, "url": url, "bytes": len(data),
                     "sha256": hashlib.sha256(data).hexdigest(), "rows": n})
    manifest.write_text(json.dumps({"total_bytes": total, "files": rows}, indent=1) + "\n")
    print(json.dumps(rows, indent=1), total)


if __name__ == "__main__":
    main()
