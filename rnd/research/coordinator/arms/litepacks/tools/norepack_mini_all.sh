#!/bin/bash
# runs the four mini arms sequentially (stage on the mini: <runner>/kiln/nr/{mini_gen.sh,norepack_mini.sh,req.jsonl})
cd <runner>/kiln/nr
bash norepack_mini.sh mini-def1 ""; bash norepack_mini.sh mini-def2 ""; bash norepack_mini.sh mini-nr "--no-repack"; bash norepack_mini.sh mini-nr2 "--no-repack"
