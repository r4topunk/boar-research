# LESANDROID runbook: Qwen3.6-35B-A3B with experts streamed from storage, on an 8 GB Android phone (POCO F3 / Snapdragon 870)

TL;DR: push 2 binaries + 1 script + the full GGUF + the `experts/` folder to `/data/local/tmp/les`, then run `sh lesandroid-run.sh all` (≈ 15–30 min) and send back the `results/` folder plus the filled table at the end. Only ~3 GB of RAM is used; the 9.8 GiB of experts are read from storage on demand. Engine: OpenBMB llama.cpp-omni @ `0b74404c` (LES = lookahead expert scheduling), CPU only, plus 2 build patches (see LESANDROID.md).

## 0. Prerequisites
- [ ] `adb devices` lists the phone (USB debugging on).
- [ ] **≥ 24 GB free** on internal storage (`adb shell df -h /data`). The files take 21.3 GiB.
- [ ] Battery ≥ 60 %. Run **unplugged** if possible (charging adds heat); otherwise note "charging".
- [ ] Close all apps (recents → clear all). Airplane mode is fine.
- [ ] Phone at room temperature, idle for 5 min before the first run.

## 1. Files (total ≈ 22.8 GB = 21.3 GiB)
| file | size | sha256 / check | where it comes from |
|---|---|---|---|
| `llama-cli` | 8,280,920 B | `c7dd47e3396c012b8fbfe6d933b1bd370ee6fc36ce41efc326c9161b6da57e76` | BOAR build (mini `<runner>/spikes/llama-omni-android/out/`) |
| `llama-completion` | 6,486,680 B | `f225ed6b3ad9877a0c0661a364f422234b9b4952a46f10cc76b66a60add4a49a` | same |
| `lesandroid-run.sh` | 4,607 B | `388e224ed795431f0c9099d01f3ed39f921840b81916dc72817c835abcd57f6c` | same |
| `prompt-00-lan-exp-001.rendered.txt` | 2,875 B | `d8b3126fc2384e2382596511ad9cb6b87d222004dcfc36675c600cf3727238cf` | same |
| `Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf` | 12,290,628,576 B (11.45 GiB) | `96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7` | HF `unsloth/Qwen3.6-35B-A3B-GGUF` @ `a483e9e6cb` (Apache-2.0) |
| `experts/` (40 × `layer_NNN.bin` + `manifest.json`) | 10,527,703,040 B + 76,629 B (9.80 GiB) | `experts.sha256` (40 lines) | generated from the GGUF (option B) or handed over |

The full GGUF is needed even though its expert bytes are never read (the CPU build cannot load the stripped GGUF; see LESANDROID.md).

**Option A (handed over):** you received a folder with all of the above. Go to step 2.

**Option B (generate the experts yourself, ~2 min plus download):**
```bash
mkdir les && cd les
curl -L -o Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf \
  https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/resolve/a483e9e6cb/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf
shasum -a 256 Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf      # must be 96b9c0af...
git clone https://github.com/OpenBMB/llama.cpp-omni fork && git -C fork checkout 0b74404c9b3dfe2c6b11aebe0dd58fc23f133ee2
python3 -m venv .venv && . .venv/bin/activate && pip install numpy pyyaml
python3 fork/tools/moe/experts.py extract --model Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf --out-dir experts
(cd experts && shasum -a 256 -c ../experts.sha256)   # 40 x OK (manifest.json differs per run; that is fine)
```

## 2. Push to the phone (USB 2.0 on the F3: expect 10–20 min)
Run from the folder that holds the files:
```bash
adb shell mkdir -p /data/local/tmp/les
adb push llama-cli llama-completion lesandroid-run.sh prompt-00-lan-exp-001.rendered.txt /data/local/tmp/les/
adb push Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf /data/local/tmp/les/
adb push experts /data/local/tmp/les/
adb shell chmod 755 /data/local/tmp/les/llama-cli /data/local/tmp/les/llama-completion
adb shell 'cd /data/local/tmp/les && sha256sum llama-cli llama-completion Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf && ls experts | wc -l'
```
Expected: the sha256 values from the table, and `41` files in `experts/`.

## 3. Sanity check (10 s)
```bash
adb shell 'cd /data/local/tmp/les && sh lesandroid-run.sh check'
```
Expected: model/Android version, `arm64-v8a`, a `Features` line that contains `asimddp`, MemTotal ≈ 7.5 GB, the llama-cli version `b2-0b74404`, and current temperatures. **Send this output.**

## 4. Runs
Each item is a fresh process (model load ~5–20 s included), with a 20 s cool-down between items. Everything goes to `/data/local/tmp/les/results/` (`summary.txt` holds one line per item).

```bash
# a) desktop-identity item: same 615-token prompt and flags as our desktop runs (greedy, 128 tokens)
adb shell 'cd /data/local/tmp/les && sh lesandroid-run.sh desk'
# b) 3 questions, no thinking (<= 200 answer tokens)
adb shell 'cd /data/local/tmp/les && sh lesandroid-run.sh nothink'
adb shell 'cd /data/local/tmp/les && sh lesandroid-run.sh think'
```
Or all at once: `adb shell 'cd /data/local/tmp/les && sh lesandroid-run.sh all'`.

To keep it running with the screen off or if USB drops: `adb shell 'cd /data/local/tmp/les && nohup sh lesandroid-run.sh all > results/all.log 2>&1 &'`, then poll `adb shell cat /data/local/tmp/les/results/summary.txt`.

The 3 questions (BOAR bench v0.1 public): `lan-exp-001` Singapore overview; `lan-rsn-002` Burj Khalifa in Lake Baikal; `vit-hlt-002` 4,000 m headache and nausea. They are answered closed-book (no retrieval), so this tests the engine, not BOAR's answer quality.

What the engine runs (inside the script; for reference):
```
LLAMA_MOE_LOOKAHEAD_PREFETCH=1 ./llama-cli -m Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf --moe-experts experts --moe-slot-bank 1280 \
  --no-mmap -fit off -t 4 -c 4096 --temp 0.7 --top-k 40 --top-p 0.95 --min-p 0.05 --seed 42 -n 712 \
  --jinja -st --simple-io --reasoning on --reasoning-format none --reasoning-budget 512 \
  --reasoning-budget-message "<newline>I have thought enough; answering now.<newline>" -sys "<system>" -p "<question>"
```
(no-think: `--reasoning off -n 200`, without the budget flags). `--no-mmap` is required.

Optional live view in a second terminal: `adb shell 'top -b -n 1 | grep llama'`. Optional memory detail for the running process: `adb shell dumpsys meminfo $(adb shell pidof llama-cli)`.

## 5. What to record
The script writes most of it. Each `summary.txt` line has:
- `wall_s`: seconds per item, including model load
- `VmHWM_kB`: peak resident memory (from `/proc/<pid>/status`)
- `MemAvailable0_kB`: free RAM before the item
- CPU thermal zone (milli-°C), battery temperature (deci-°C) and thermal status, before and after
- speed: `[ Prompt: X t/s | Generation: Y t/s ]` (cli) or `prompt eval time / eval time` (desk)

Please send `adb pull /data/local/tmp/les/results` (folder, < 1 MB), the `check` output, and this table:

| item | wall s | prefill t/s | decode t/s | VmHWM GB | therm before → after (°C) | answer looks sane? (y/n) |
|---|---|---|---|---|---|---|
| desk-00 | | | | | | |
| nothink lan-exp-001 | | | | | | |
| nothink lan-rsn-002 | | | | | | |
| nothink vit-hlt-002 | | | | | | |
| think lan-exp-001 | | | | | | |
| think lan-rsn-002 | | | | | | |
| think vit-hlt-002 | | | | | | |

Plus: phone model and RAM/storage variant, Android version, charging (y/n), and whether any other app or the phone UI got killed or stuttered.

What we expect (desktop M4 numbers; the phone should be slower): desktop prefill ~34 t/s, decode 15–17 t/s, RSS 2.8–3.0 GB. Our phone estimate is 3–8 t/s decode, flash-bound (not measured). The 615-token desk prompt reads ~14 GiB from storage during prefill, so expect a long prefill (~1 min). Thinking items take the longest (512 reasoning tokens).

## 6. If something fails
| symptom | cause / fix |
|---|---|
| `rc=137`, `Killed`, or the run disappears | low-memory killer. Close everything, retry; then retry with a smaller bank: edit the script, `--moe-slot-bank 1280` → `640` (−0.6 GiB, slower) |
| `MoE slot tensor ... is not CPU-addressable` | `--no-mmap` missing (do not edit it out) |
| `MoE experts is missing routed tensor` / `failed to open MoE experts file` | `experts/` incomplete or in the wrong place: must be `/data/local/tmp/les/experts/manifest.json` + 40 `.bin` |
| `expert tensor ... byte size mismatch` | experts generated from a different GGUF; regenerate from the sha-verified file |
| `Permission denied` / `not executable` | `adb shell chmod 755 /data/local/tmp/les/llama-*` |
| `Illegal instruction` | CPU lacks dotprod (not expected on SD870); send the `check` output |
| very slow / thermal status ≥ 3 | let it cool 5 min; optional retry with `THREADS=3`: `adb shell 'cd /data/local/tmp/les && THREADS=3 sh lesandroid-run.sh nothink'` |

## 7. Stop and clean up
```bash
adb shell pkill -f llama-cli; adb shell pkill -f llama-completion; adb shell pkill -f lesandroid-run.sh
adb pull /data/local/tmp/les/results ./les-results     # first, keep the results
adb shell rm -rf /data/local/tmp/les                    # frees ~21.3 GiB
adb shell df -h /data
```
