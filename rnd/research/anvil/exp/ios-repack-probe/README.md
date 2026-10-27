# iPhone 13 repack probe: result (Anvil, 2026-10-03 10:58–10:59 -03)

**TL;DR: Q1 = NO. llama.rn on iOS does not repack the Qwen2.5-1.5B Q4_K_M on the iPhone 13 (A15).** The weights stay file-backed (`CPU_Mapped`), and there is no `CPU_REPACK` buffer. The jetsam footprint after load is 346–377 MB, well below the 0.9 GiB a repack copy would add. Per the frozen reading in `../../specs/probe-ios-repack-iphone13.md`: **Fix 1 must set `repack: false` on iOS**, and Kiln's `fit-repack.patch` stays scoped to Android, as the coordinator already did. Q2 (should the iPhone 13 default to no-repack?) is not applicable: there is nothing to turn off.

## What ran
- Device: iPhone 13 (iPhone14,5), UDID <DEVICE_UDID>.
- Installed build: `builds/ios/device/evalbench-0074737` (main 0cfd4a77 + PR #62 + iPhone bench; llama.rn 0.13.0-rc.4; EXPO_PUBLIC_DEVICE_EVAL=1; JS bundle embedded, no Metro).
- Command: `wt/plumb-bench-uiios`, `node scripts/bench-iphone.mjs --only base --reps 2 --pp 512 --tg 64 --cool-max-s 120`.
- Logs: console captured over devicectl.
- Device time: about 1 minute.
- The app was not reinstalled or deleted, no settings were changed, and the tree was not modified (`git status` clean).

## Result

| | Value |
|---|---|
| 1.5B load buffers (3 loads: the chat model at launch, then 2 bench contexts) | `CPU_Mapped model buffer size = 934.69 MiB` ×3; **`CPU_REPACK` lines: 0**; KV 56 MiB; compute 302.75 MiB |
| `[BOAR mem]` footprint | 47 MB before load → 346–348 MB with the chat model → peak **377 MB** during the bench |
| rss_mb | up to 1049 (counts the mapped file pages; jetsam doesn't count them) |
| bench base, median of 2 | pp512 **165.8 tok/s**, tg64 **18.3 tok/s** |
| thermal / power | nominal before and after both reps; battery 70%, **charging** |

- **Same evidence in older builds:** every earlier iPhone 13 console log in `builds/ios/device/{1b447b7,f7e8eb2,d88f85b-probe}` and `device-console-90b87dd.log` shows the same `CPU_Mapped 934.69 MiB` and no `CPU_REPACK` buffer. The footprint after load there is 337–342 MB.
- **On Android (g75, Probe A on the mini), repack was the root cause:** a Q4_K anon copy of about 2.3 GiB on the 4B.

## Deviations from the frozen spec (logged)
1. **Scope cut by the coordinator (r4to needed the phone back):**
   - Part 1 only;
   - 2 reps instead of 3;
   - Part 2 (answers) only if Q1 = repack active, which it isn't, so it was skipped.
2. **No `norepack` config.** The installed build's bench parser (`src/bench/modelBench.pure.ts` `parseConfig`) keeps only whitelisted keys and drops `no_extra_bufts`. That config would have needed a rebuild, which was not possible in the device window.
   - Q1 was therefore answered by mechanism, not by the frozen base-vs-norepack footprint difference. The evidence is the load-time buffer log plus a footprint below the weights' size.
   - The frozen rule's intent still holds: the "< 0.2 GiB difference" case covers this. The repack-attributable footprint is 0, because a copy that doesn't exist can't be removed. It would only be different if llama.rn hid a repack inside `CPU_Mapped`; it doesn't, since `CPU_REPACK` is a separate buffer type in llama.cpp.
3. **USB-plugged and charging** (driven over the cable, per r4to). Thermal and battery are logged per rep above. The tok/s figures are reported, not gated.

## Consequence
- `memoryFit` repack term: Android only. iOS = `repack: false`, measured on A15 + llama.rn rc.4.
- Re-check if llama.rn is bumped. Upstream could enable ARM repack in the iOS framework build. Signal: a `CPU_REPACK` line in the iOS load log.
