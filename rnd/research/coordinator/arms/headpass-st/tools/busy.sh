#!/bin/bash
# rc 0 (busy) if a llama-server other than the :8094 emergency detector, or an adapter.ts job, is running; prints what. rc 1 = free.
b=1
for p in $(pgrep -x llama-server); do c=$(ps -o command= -p $p); case "$c" in *emergency-detector*) ;; *) echo "busy llama-server pid $p: ${c:0:160}"; b=0;; esac; done
for p in $(pgrep -f "be/adapter[.]ts"); do echo "busy adapter pid $p"; b=0; done
exit $b
