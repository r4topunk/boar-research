#!/bin/bash
# Tree content hash: sha256 of the sorted per-file sha256 list (node_modules, be/.cache, .DS_Store excluded). Usage: treehash.sh <tree dir> -> 16-hex hash + file count
cd "$1" && find . -type f -not -path "*/node_modules/*" -not -path "./be/.cache/*" -not -name ".DS_Store" | LC_ALL=C sort | xargs shasum -a 256 > /tmp/treehash.list && shasum -a 256 /tmp/treehash.list | cut -c1-16 && wc -l < /tmp/treehash.list
