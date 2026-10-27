"""Shared helpers for the device-metrics converters (stdlib only)."""
import hashlib, json, math, statistics
from datetime import datetime, timezone

SCHEMA_VERSION = "0.1.0"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pct(xs, p):
    """Linear-interpolated percentile (same as numpy 'linear'); None when empty."""
    xs = sorted(x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x)))
    if not xs:
        return None
    k = (len(xs) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (k - lo), 3)


def stat(xs):
    v = [x for x in xs if x is not None]
    return {"n": len(v), "p50": pct(v, 0.5), "p95": pct(v, 0.95),
            "mean": round(statistics.fmean(v), 3) if v else None,
            "min": round(min(v), 3) if v else None, "max": round(max(v), 3) if v else None}


def mlperf_tps(tokens, first_token_ms, last_token_ms):
    """MLPerf Client TPS: rate of all tokens after the first. None when undefined (< 2 tokens)."""
    if tokens is None or tokens < 2 or first_token_ms is None or last_token_ms is None or last_token_ms <= first_token_ms:
        return None
    return round((tokens - 1) / ((last_token_ms - first_token_ms) / 1000), 3)


def sustained(tps_in_order, ttft_in_order):
    t = [x for x in tps_in_order if x is not None]
    f = [x for x in ttft_in_order if x is not None]
    first, last = (statistics.median(t[:5]), statistics.median(t[-5:])) if len(t) >= 10 else (None, None)
    ttf, ttl = (statistics.median(f[:5]), statistics.median(f[-5:])) if len(f) >= 10 else (None, None)
    return {"tps_first5": round(first, 3) if first else None, "tps_last5": round(last, 3) if last else None,
            "tps_ratio_last_first": round(last / first, 3) if first else None,
            "ttft_ratio_last_first": round(ttl / ttf, 3) if ttf else None}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")
