"""DETECTOR-HN shared lib: detector_text (Sonar common2, unchanged, imported), GGUF pooled embeddings from LOCAL llama-servers
(v3b gguf, b11010 commit 4bc272f, --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512; ports 18301-18304; never :8094),
and the JS-equivalent mmbert-cls head in numpy (exact GELU via erf, LayerNorm no bias)."""
import json, os, sys, hashlib, numpy as np, requests
from concurrent.futures import ThreadPoolExecutor
from math import erf
SONAR = "<workspace>/rnd/research/sonar/exp/30-learned-detector"
os.environ.setdefault("HF_HUB_OFFLINE", "1")
sys.path.insert(0, SONAR)
import common2  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402
common2._tok = AutoTokenizer.from_pretrained(SONAR + '/results/mmbert-v3b.encoder')  # = jhu-clsp/mmBERT-small tokenizer saved with v3b
detector_text = common2.detector_text
PORTS = [18301, 18302, 18303, 18304]
MD = "<workspace>/shared-models/emergency-detector/"
HEAD_V3B = MD + "sonar-mmbert-small-emergency-v3b.head.json"
def emb_one(args):
    text, port = args
    r = requests.post(f"http://127.0.0.1:{port}/embedding", json={"content": text, "embd_normalize": -1}, timeout=120); r.raise_for_status()
    j = r.json(); e = j[0]["embedding"] if isinstance(j, list) else j["embedding"]
    return np.array(e[0] if isinstance(e[0], list) else e, dtype=np.float32)
def embed_texts(texts, workers=4):
    with ThreadPoolExecutor(workers) as ex:
        return np.stack(list(ex.map(emb_one, [(t, PORTS[i % len(PORTS)]) for i, t in enumerate(texts)])))
def embed_turns(turns_list, cache=None):
    """turns_list: list of user-turn lists. cache: .npz path keyed by sha of detector text."""
    texts = [detector_text(u) for u in turns_list]
    keys = [hashlib.sha256(t.encode()).hexdigest()[:20] for t in texts]
    have = {}
    if cache and os.path.exists(cache):
        z = np.load(cache); have = dict(zip(z["keys"].tolist(), z["vecs"]))
    need = sorted({k: t for k, t in zip(keys, texts) if k not in have}.items())
    if need:
        V = embed_texts([t for _, t in need])
        for (k, _), v in zip(need, V): have[k] = v
        if cache:
            ks = list(have); np.savez(cache, keys=np.array(ks), vecs=np.stack([have[k] for k in ks]))
    return np.stack([have[k] for k in keys]), texts
def load_head(path):
    H = json.load(open(path)); d = H["dim"]
    return dict(W=np.array(H["dense"], dtype=np.float64).reshape(d, d), g=np.array(H["norm"], dtype=np.float64),
                C=np.array(H["cls_w"], dtype=np.float64).reshape(2, d), b=np.array(H["cls_b"], dtype=np.float64), eps=H["eps"])
_verf = np.vectorize(erf)
def head_p(h, X):
    X = np.asarray(X, dtype=np.float64); z = X @ h["W"].T; z = 0.5 * z * (1 + _verf(z / np.sqrt(2)))
    z = (z - z.mean(1, keepdims=True)) / np.sqrt(z.var(1, keepdims=True) + h["eps"]) * h["g"]
    l = z @ h["C"].T + h["b"]; return 1 / (1 + np.exp(l[:, 0] - l[:, 1]))
