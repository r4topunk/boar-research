#!/usr/bin/env bash
# exp-02 runtime: llama.cpp b11010 (4bc272f, 2026-09-16; contains the `maple` arch, PR #27000 = 3d10bcd) in its own
# directory, CPU only, so the exp-01 build (bmoe 0e8c83e) is untouched. Timed; run through the heavy queue.
# Clone (outside the lock): git clone --depth 1 --branch b11010 https://github.com/ggml-org/llama.cpp.git <runner>/spikes/llama-b11010
set -euo pipefail
cd <runner>/spikes/llama-b11010
test "$(git rev-parse HEAD)" = 4bc272fd729bd094c0422e4b8353da8d2fec91f8
s=$(date +%s)
nice -n 10 cmake -S . -B build-cpu -G Ninja -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=OFF -DLLAMA_CURL=OFF > <runner>/kiln/build-b11010.configure.log 2>&1
c=$(date +%s)
nice -n 10 cmake --build build-cpu -j 4 --target llama-server llama-bench > <runner>/kiln/build-b11010.build.log 2>&1
e=$(date +%s)
echo "configure_s=$((c - s)) build_s=$((e - c)) total_s=$((e - s))" | tee <runner>/kiln/build-b11010.time
du -sh <runner>/spikes/llama-b11010 build-cpu | tee -a <runner>/kiln/build-b11010.time
./build-cpu/bin/llama-server --version 2>&1 | tail -2 | tee -a <runner>/kiln/build-b11010.time
