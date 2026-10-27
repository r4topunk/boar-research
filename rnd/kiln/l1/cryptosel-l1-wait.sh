#!/usr/bin/env bash
# Wait for the mini's heavy lock holders (CVO) to finish, so its detector shutdown cannot hit this run, then generate.
while echo 'pgrep -f "boar/bin/run-heavy" >/dev/null && echo busy || echo free' | <on the mini> bash -s | grep -q busy; do sleep 60; done
sleep 30
exec <workspace>/rnd/kiln/l1/cryptosel-l1.sh
