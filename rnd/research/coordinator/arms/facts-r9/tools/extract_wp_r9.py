#!/usr/bin/env python3
"""Extract the two Wikipedia articles used for adjudication from the local enwiki top-100k pack (CC BY-SA; kept out of git).
Usage: python3 -I extract_wp_r9.py <boar-wiki-en-top100k.sqlite> <out_dir>"""
import sqlite3, subprocess, sys
db = sqlite3.connect(sys.argv[1])
for t in ["Mains electricity by country", "Left- and right-hand traffic"]:
    b, o, n = db.execute("select block_id,off,len from articles where title = ? collate nocase", (t,)).fetchone()
    z = db.execute("select zdata from blocks where id=?", (b,)).fetchone()[0]
    s = subprocess.run(["zstd", "-dc"], input=z, capture_output=True, check=True).stdout[o:o + n].decode("utf8", "replace")
    open(f"{sys.argv[2]}/wp-{t.replace(' ', '_')}.txt", "w").write(s)
