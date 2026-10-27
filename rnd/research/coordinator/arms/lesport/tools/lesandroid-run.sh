#!/system/bin/sh
# LESANDROID driver: Qwen3.6-35B-A3B with experts streamed from storage (OpenBMB llama.cpp-omni LES fork, CPU).
# usage (on the phone):  sh lesandroid-run.sh check|desk|nothink|think|all
# Paths can be overridden with env D, MODEL, EXP, THREADS. Writes into $D/results/.
D=${D:-/data/local/tmp/les}
MODEL=${MODEL:-$D/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf}
EXP=${EXP:-$D/experts}
THREADS=${THREADS:-4}
R=$D/results
mkdir -p "$R"
export LLAMA_MOE_LOOKAHEAD_PREFETCH=1
# NOTE desk: -p "$(cat file)" (trailing newline stripped, 615 tokens) exactly as LESPORT S0/S1; -f would give 616 tokens.
# Common engine flags. --no-mmap is REQUIRED (with mmap the slot tensors are not CPU-writable);
# the loader then reads only the ~1.6 GiB of non-expert weights; the 9.8 GiB of experts stay on storage.
ENG="-m $MODEL --moe-experts $EXP --moe-slot-bank 1280 --no-mmap -fit off -t $THREADS -c 4096"
SAMP="--temp 0.7 --top-k 40 --top-p 0.95 --min-p 0.05 --seed 42"
SYS="You are Boar, a concise offline research assistant. Answer in 2-3 short, direct sentences or a brief paragraph, no preamble. If you are not sure, say so."
MSG="
I have thought enough; answering now.
"
Q1_ID=lan-exp-001; Q1="Give me a quick overview of Singapore: where it is, how it became independent, and what languages people speak there."
Q2_ID=lan-rsn-002; Q2="If you stood the Burj Khalifa on the deepest point of Lake Baikal, would its top stick out of the water?"
Q3_ID=vit-hlt-002; Q3="I'm at 4,000 m in the Andes with a headache and nausea. What should I do?"

now() { date +%s; }
therm() {
  # max CPU-ish thermal zone (milli-degC), battery temp (deci-degC), thermal status
  t=0
  for z in /sys/class/thermal/thermal_zone*; do
    ty=$(cat "$z/type" 2>/dev/null); v=$(cat "$z/temp" 2>/dev/null)
    case "$ty" in *cpu*|*CPU*|*tsens*|*apc*|*gold*|*silver*) [ -n "$v" ] && [ "$v" -gt "$t" ] 2>/dev/null && t=$v ;; esac
  done
  b=$(dumpsys battery 2>/dev/null | grep -m1 temperature | tr -dc 0-9)
  s=$(dumpsys thermalservice 2>/dev/null | grep -m1 -i "Thermal Status" | tr -dc 0-9)
  echo "cpu_mC=$t batt_dC=${b:-na} status=${s:-na}"
}
memavail() { grep MemAvailable /proc/meminfo 2>/dev/null | tr -dc 0-9; }

# run_one TAG BIN ARGS...  (ARGS already split by caller via set --)
run_one() {
  tag=$1; shift
  th0=$(therm); ma0=$(memavail); t0=$(now)
  "$@" < /dev/null > "$R/$tag.out" 2> "$R/$tag.err" &
  pid=$!
  hwm=0; rss=0
  while kill -0 $pid 2>/dev/null; do
    h=$(grep VmHWM /proc/$pid/status 2>/dev/null | tr -dc 0-9); [ -n "$h" ] && hwm=$h
    r=$(grep VmRSS /proc/$pid/status 2>/dev/null | tr -dc 0-9); [ -n "$r" ] && [ "$r" -gt "$rss" ] && rss=$r
    sleep 1
  done
  wait $pid; rc=$?
  t1=$(now); th1=$(therm)
  perf=$(grep -h -E "Prompt:.*Generation:|prompt eval time|^.*[^t] eval time|load time" "$R/$tag.out" "$R/$tag.err" 2>/dev/null | sed 's/^.*common_perf_print: *//' | tr '\n' ' ')
  line="$tag rc=$rc wall_s=$((t1-t0)) VmHWM_kB=$hwm VmRSS_max_kB=$rss MemAvailable0_kB=${ma0:-na} | before: $th0 | after: $th1 | $perf"
  echo "$line" | tee -a "$R/summary.txt"
}

cli() { # cli TAG QUESTION N REASONING(off|on)
  tag=$1; q=$2; n=$3; rea=$4
  if [ "$rea" = on ]; then
    run_one "$tag" ./llama-cli $ENG $SAMP -n "$n" --jinja -st --simple-io --reasoning on --reasoning-format none \
      --reasoning-budget 512 --reasoning-budget-message "$MSG" -sys "$SYS" -p "$q"
  else
    run_one "$tag" ./llama-cli $ENG $SAMP -n "$n" --jinja -st --simple-io --reasoning off -sys "$SYS" -p "$q"
  fi
  sleep 20   # short cool-down between items
}

cd "$D" || exit 1
case "$1" in
  check)
    getprop ro.product.model; getprop ro.build.version.release; getprop ro.product.cpu.abi
    grep -m1 Features /proc/cpuinfo
    grep -E "MemTotal|MemAvailable|SwapTotal|SwapFree" /proc/meminfo
    df -h "$D" | tail -1
    ls -l "$MODEL" llama-cli llama-completion; ls "$EXP" | wc -l
    ./llama-cli --version 2>&1 | tail -2
    therm ;;
  desk)  # desktop-comparable: same rendered prompt / flags as LESPORT S0/S1 item 00 (greedy, 128 tokens)
    run_one desk-00 ./llama-completion $ENG --temp 0 --top-k 1 -n 128 -p "$(cat "$D/prompt-00-lan-exp-001.rendered.txt")" -no-cnv --no-display-prompt ;;
  nothink)
    cli nothink-$Q1_ID "$Q1" 200 off; cli nothink-$Q2_ID "$Q2" 200 off; cli nothink-$Q3_ID "$Q3" 200 off ;;
  think)   # budget 512 thinking tokens + up to 200 answer tokens
    cli think-$Q1_ID "$Q1" 712 on; cli think-$Q2_ID "$Q2" 712 on; cli think-$Q3_ID "$Q3" 712 on ;;
  all)
    sh "$0" desk; sleep 20; sh "$0" nothink; sh "$0" think ;;
  *) echo "usage: sh lesandroid-run.sh check|desk|nothink|think|all"; exit 2 ;;
esac
