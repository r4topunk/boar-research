# Arm requests for the phone session: the frozen 72-item g75 request (boar-eval/devices/requests/and-q15-quick.request.json)
# plus an explicit "perf" block (src/rag/perfFlags.ts in the arm build). Flags are cumulative, in the session order.
# Usage: python3 make_arm_requests.py  -> requests/and-q15-quick-<arm>.request.json (+ sha256 lines on stdout)
import hashlib, json, pathlib
SRC = pathlib.Path("<workspace>/boar-eval/devices/requests/and-q15-quick.request.json")
OFF = {"nativeZstd": False, "vectorCache": False, "sqlBatch": False}
ARMS = {
    "base": OFF,                                                   # base-dev, base-rel, and p7b (packs only)
    "p8": {**OFF, "sqlBatch": True},
    "zstd": {**OFF, "sqlBatch": True, "nativeZstd": True},
    "vcache": {**OFF, "sqlBatch": True, "nativeZstd": True, "vectorCache": True},
}
req = json.loads(SRC.read_text())
assert req["pipeline"] == "answer" and len(req["questions"]) == 72, "unexpected base request"
out = pathlib.Path(__file__).parent / "requests"
for arm, perf in ARMS.items():
    r = {**req, "perf": perf}  # requestId unchanged: android-run.sh --tag <arm> makes it unique per arm and rep
    p = out / f"and-q15-quick-{arm}.request.json"
    p.write_text(json.dumps(r, ensure_ascii=False) + "\n")
    print(hashlib.sha256(p.read_bytes()).hexdigest()[:16], p.name, json.dumps(perf))
print("base request", hashlib.sha256(SRC.read_bytes()).hexdigest()[:16], SRC)
