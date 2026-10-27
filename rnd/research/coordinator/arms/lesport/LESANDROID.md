# LESANDROID: Android arm64 build of the LES fork (llama.cpp-omni) for an 8 GB phone. Verdict: **BUILD-OK** (no blocker for an 8 GB run; storage 21.3 GiB because the CPU path needs the full GGUF; phone speed unmeasured)

Runner: coordinator subagent, 2026-10-19 18:4x–19:0x, Mac mini (M4). 0 judge/LLM/API calls, nothing pushed or sent, nothing committed. Original fork tree `<runner>/spikes/llama-omni/src` not modified (clone used). Disk stayed at ≥ 35 GiB free (work dir 1.3 GiB).

## What was built
| item | value |
|---|---|
| source | `git clone <runner>/spikes/llama-omni/src` → `<runner>/spikes/llama-omni-android/src`, HEAD `0b74404c9b3dfe2c6b11aebe0dd58fc23f133ee2` (= S0/S1/L1/THINK revision) + 2 patches below |
| toolchain | NDK 27.1.12297006, CMake 4.4.3 + Ninja, host macOS arm64 |
| target | arm64-v8a, `android-28`, `-march=armv8.2-a+dotprod+fp16` (Snapdragon 870 = Cortex-A77/A55: dotprod + fp16 yes, i8mm/SVE no), CPU backend only, static libs, OpenMP off (ggml thread pool) |
| binaries | `llama-cli` (chat path, wires `--reasoning-budget`), `llama-completion` (raw prompt, used for the desktop-identity item). **No `llama-server` exists in this fork** (tools/server builds only the omni/voxcpm2 servers; the plain server is gone, `llama-cli` links `server-context`). `llama-bench` builds but has no `--moe-experts` flag, so on the 35B it would load all experts and OOM an 8 GB phone: left out of `out/` |
| linkage | PIE, `/system/bin/linker64`, NEEDED only `libc.so libm.so libdl.so` (Bionic system libs; libc++ static). Stripped with `llvm-strip` |
| Vulkan | not attempted (the LES slot runtime requires host-addressable slot tensors, `llama-moe-slot.cpp:681-686`; a Vulkan device buffer would fail that check, so it is not "trivial") |

### Outputs on the mini: `<runner>/spikes/llama-omni-android/out/`
| file | bytes | sha256 |
|---|---|---|
| `llama-cli` | 8,280,920 | `c7dd47e3396c012b8fbfe6d933b1bd370ee6fc36ce41efc326c9161b6da57e76` |
| `llama-completion` | 6,486,680 | `f225ed6b3ad9877a0c0661a364f422234b9b4952a46f10cc76b66a60add4a49a` |
| `lesandroid-run.sh` (phone driver; copy in `tools/`) | 4,607 | `388e224ed795431f0c9099d01f3ed39f921840b81916dc72817c835abcd57f6c` |
| `prompt-00-lan-exp-001.rendered.txt` (S0/S1 item 00) | 2,875 | `d8b3126fc2384e2382596511ad9cb6b87d222004dcfc36675c600cf3727238cf` |
| `patches-android.diff` | 1,732 | `61c8c5fa8f909196e82d7a87c6df67c44f6bd7e9872cea07d9f05225a6f05509` |
| `experts.sha256` (40 layer .bin hashes, for the handoff) | 3,200 | — |
| `SHA256SUMS` | 431 | — |

Copies of the diff, the hash lists, configure.log and the desktop recheck log are in `raw/android/`.

### Exact commands
```bash
export PATH=/opt/homebrew/bin:$PATH
NDK=~/Library/Android/sdk/ndk/27.1.12297006
cd <runner>/spikes/llama-omni-android
cmake -S src -B build-android -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake \
  -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-28 -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS="-march=armv8.2-a+dotprod+fp16" -DCMAKE_CXX_FLAGS="-march=armv8.2-a+dotprod+fp16" \
  -DGGML_OPENMP=OFF -DGGML_LLAMAFILE=OFF -DBUILD_SHARED_LIBS=OFF -DLLAMA_CURL=OFF -DLLAMA_OPENSSL=OFF \
  -DGGML_NATIVE=OFF -DGGML_METAL=OFF -DLLAMA_BUILD_TESTS=OFF
cmake --build build-android --config Release -j 6 --target llama-cli llama-completion
T=$NDK/toolchains/llvm/prebuilt/darwin-x86_64/bin
for b in llama-cli llama-completion; do $T/llvm-strip -o out/$b build-android/bin/$b; done
```
Build wall ≈ 45 s compile + link after configure (1.6 s).

### Patches (2, 8 lines, `patches-android.diff`)
1. `src/llama-moe-slot.cpp` (2 sites, ~l.1351 and ~l.1375): `F_NOCACHE` is an Apple-only `fcntl`; wrapped in `#ifdef F_NOCACHE`. Effect on Android: the optional env knob `LLAMA_MOE_F_NOCACHE` becomes a no-op. Default mode (unset) never calls it, so the measured desktop path is unchanged.
2. `tools/omni/omni-impl.h` (l.161): `#define g_logger_state omni_g_logger_state` before the extern. A static link pulls both `tools/omni/vision.cpp:33` and `tools/mtmd/clip.cpp:29`, which define different structs under the same global name (`ld.lld: duplicate symbol`). macOS used shared libs, which hid the clash. Symbol rename only; omni code is not on the text path.

## Desktop re-check (same source revision, mini CPU build sha `29cbcbc2…` = L1's binary)
- 10 tokens, temp 0, `LLAMA_MOE_LOOKAHEAD_PREFETCH=1`, `--moe-experts experts --moe-slot-bank 1280 --no-mmap -t 4 -c 4096`, item 00: rc 0, text prefix = S0/S1 ("Singapore is an island city-state located at the"), prefill 615 tok 34.1 tok/s, decode 14.3 tok/s (9 tokens), max RSS 3.02 GB, peak footprint 2.99 GB. Log: `raw/android/recheck-desk-00.err`.
- The phone driver (`lesandroid-run.sh desk`), pointed at the desktop build, reproduced S1 warm/prefetch-on item 00 **byte-identical** (64 tokens, 15.9 tok/s). On the phone, the same item gives an identity check against S1. Kernel paths differ (M4 i8mm vs SD870 dotprod), so a late divergence there would be numeric, not LES.
- The runbook's `llama-cli` commands (no-think and thinking with a budget) were smoke-run on the desktop build: both rc 0, thinking closed by the budget message, RSS 2.87 GB, 15.6–16.3 tok/s. The three no-think questions ran 9–10 s each on the M4.

## Blocker analysis (code read at 0b74404c)
| S0/S1/FLASH blocker | finding (file:line) | blocks the 8 GB phone? |
|---|---|---|
| **alloc-only buffer is Metal-only** | `make_alloc_only_buft` looks up the proc address `ggml_backend_dev_buffer_type_alloc_only` (`src/llama-model.cpp:918-934`); only `ggml-metal.cpp:902,923` exports it, and it is only queried for the `devices` (GPU) list (`llama-model.cpp:1296-1303`), never for the CPU device. So on CPU `create_tensor_own_alloc` falls back to the normal `create_tensor` (`:1719-1721`), and `create_expert_tensor_from_manifest` throws for a stripped GGUF (`:1743-1748`). | **No.** It only rules out `stripped.gguf`. The full GGUF + `--no-mmap` path is the same code on Android as on the M4 CPU build. |
| **`--no-mmap` on a 12 GB GGUF: does RSS stay ~3 GiB?** | Yes, by construction. `qwen35moe.cpp:120-170` (`create_routed_tensor`) calls `llama_model_loader::virtualize_expert_tensor` (`src/llama-model-loader.cpp:1321-1366`), which shrinks each expert tensor from 256 experts to `n_slots` (`ne[2] = n_slots`, l.1345-1346) and **erases it from `weights_map`** (l.1361), so `load_all_data` never reads the 9.8 GiB of experts from the GGUF. Only the ~1.64 GiB of non-expert weights are read into anonymous memory, plus the 1.20 GiB slot bank and small KV/compute buffers. Desktop: RSS 2.75–3.02 GiB. Why mmap fails: with mmap, default-buft tensors are wrapped in the read-only file mapping (comment `llama-model.cpp:909-915`), so the slot tensors get no writable host buffer, and `llama-moe-slot.cpp:681-686` throws "not CPU-addressable". | **No.** ~3 GiB RSS fits an 8 GB phone (MemAvailable is typically 3.5–4.5 GiB with apps closed). The margin is thin: fallback `--moe-slot-bank 640` (-0.6 GiB). |
| **slot bank cap 1.20 GiB** | `llama-model.cpp:1236-1244`: bank ≤ 32 × 40 MoE layers = 1280 slots × 0.961 MiB. | **No.** It caps speed (cache hit rate), not feasibility. On 8 GB the cap is roughly the right size anyway. |
| repack trap (new check) | On CPU, ggml's extra "repack" buffer could claim expert tensors, and raw `preadv` into a repacked layout would corrupt silently. Expert types here are IQ2_XS ×78, IQ3_XXS ×38, IQ4_XS ×4 (manifest). `ggml-cpu/repack.cpp:4573-4700` only repacks Q4_0/Q4_K/Q2_K(AVX512/RVV)/Q5_K/Q6_K/IQ4_NL/MXFP4/Q8_0, and KleidiAI is off. | No (would matter for a Q4_0/Q4_K expert GGUF). |
| Linux I/O APIs | `preadv` is in Bionic since API 24; off_t is 64-bit on arm64; only `F_NOCACHE` was Apple-only (patched). | No. |
| `--fit` auto-adjust | It projects 4468 MiB of host memory (desktop log). On a phone with low free RAM it could change unset params. | No. The runbook passes `-fit off`. |

### New observations from the recheck log (n = 1 prompt; descriptive)
- **Prefill streams almost every expert:** the 615-token prompt read 14.2 GiB from the experts files (ubatch 512 → ~205 unique experts per layer). On UFS 3.1 (~1.5–2 GB/s) that is ≈ 7–10 s of I/O per such prompt, before compute. Prefill, not decode, may dominate time to first token on the phone (M4: 18 s at 34 tok/s; a phone CPU is probably 2–4× slower → estimate 40–70 s for a 615-token RAG prompt).
- **Lookahead prefetch gives hits in decode:** from decode token 2 on, 57–136 of 320 expert reads per token hit (pfhit), so reads drop from 314 MiB to 180–260 MiB per token. LESPORT-FLASH's "0 hits" was measured with prefetch off. With prefetch on, the flash bound is ~20–40 % looser than FLASH's table (estimate; 10 tokens only).

### Smallest optional fix (not needed for the test; storage and RSS)
Export `ggml_backend_dev_buffer_type_alloc_only` from the CPU backend reg (return `ggml_backend_cpu_buffer_type()`) and also call `make_alloc_only_buft(cpu_dev)` in `load_tensors` (≈ 15 lines across `ggml-cpu.cpp` and `llama-model.cpp:1296-1303`). This would let the phone use `stripped.gguf` (1.64 GiB instead of 11.45 GiB: storage 21.3 → 11.5 GiB, adb push about halved), and probably allow mmap for the non-expert weights (page cache instead of anon RSS). Untested; only worth doing if the first phone run is promising.

## Verdict
**BUILD-OK.** Both binaries cross-compile with 2 small, behaviour-neutral patches and link only against Bionic system libs. The flags are the same as on desktop, and the desktop path was re-confirmed on the same revision (identical text). Read at the code level, none of the S0/S1/FLASH blockers makes the 8 GB run impossible: the full GGUF + `--no-mmap` path keeps RSS ≈ 3 GiB, and the experts are never read at load. Costs and open points: 21.3 GiB of storage on the phone; thinking budget only via `llama-cli`; no plain `llama-server`, so app integration means linking libllama from this fork; phone decode/prefill speed, thermal behaviour and lmkd pressure are **unmeasured** until the app maintainer runs `LESANDROID-RUNBOOK.md`. Not claimed: any phone number or quality on the phone.
