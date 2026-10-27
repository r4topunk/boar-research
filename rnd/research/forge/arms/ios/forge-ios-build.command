#!/bin/bash
# Forge iOS JS-arms build, run ON THE MAC MINI from its GUI session (codesign needs the login keychain).
# Needs r4to's OK (shared machine). Prepared by Forge 2026-10-03; NOT run yet.
#   MacBook:  git -C <workspace>/wt/forge-ios archive -o /tmp/forge-ios.tar HEAD      # cc3ca10f
#             scp /tmp/forge-ios.tar forge-ios-build.command MINI_HOST:boar/forge/
#             (team id: the TeamIdentifier of builds/ios/device/evalbench-0074737/std/BOAR.app's profile → <runner>/forge/ios-team.txt on the mini; never committed)
#   mini:     open -a Terminal <runner>/forge/forge-ios-build.command        (log: <runner>/forge/ios-build.log)
# What it does: APFS-clones <runner>-ios-build (00747371's prebuild + node_modules, untouched) into <runner>/forge/ios-build,
# syncs the forge tree over it WITHOUT modules/boar-zstd (native zstd skipped today → JS keeps fzstd), reuses the prebuild
# (IOS_SKIP_DEPS=1: the native side is byte-identical to 00747371), builds a signed Release .app with
# EXPO_PUBLIC_DEVICE_EVAL=1, the same entitlement strip as evalbench-0074737, and info logs.
set -uo pipefail
LOG=<runner>/forge/ios-build.log; exec > "$LOG" 2>&1
echo "[forge] start $(date +%T) free=$(df -g ~ | tail -1 | awk '{print $4}')G"
set -e
rm -rf <runner>/forge/ios-build <runner>/forge/ios-src                  # Forge's own dirs only
cp -cR <runner>-ios-build <runner>/forge/ios-build                      # clone: ~0 extra disk
mkdir -p <runner>/forge/ios-src && tar -xf <runner>/forge/forge-ios.tar -C <runner>/forge/ios-src
rm -rf <runner>/forge/ios-src/modules/boar-zstd
rsync -a --delete --exclude node_modules --exclude /ios --exclude .expo --exclude .env --exclude build.log --exclude .boar-ref \
  <runner>/forge/ios-src/ <runner>/forge/ios-build/
echo forge-ios-cc3ca10f > <runner>/forge/ios-build/.boar-ref
cd <runner>/forge/ios-build
export IOS_SKIP_DEPS=1 IOS_TEAM="$(cat <runner>/forge/ios-team.txt)" IOS_RN_LOG_INFO=1 EXPO_PUBLIC_DEVICE_EVAL=1 IOS_OUT_DIR=<runner>/forge/ios-out
export IOS_STRIP_ENTITLEMENTS=com.apple.developer.kernel.extended-virtual-addressing,com.apple.developer.kernel.increased-memory-limit,com.apple.developer.devicecheck.appattest-environment
scripts/ios-build-on-host.sh device
echo "[forge] done $(date +%T)"
