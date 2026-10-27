#!/usr/bin/env python3
"""DETECTOR-FT: embed every DETECTOR-HN set (embed_all.sets(), unchanged) with a NEW GGUF served on the dlib ports (here: mini b11010
build-cpu 4bc272f llama-servers reached through an ssh tunnel), into work/<tag>/emb.<set>.npz with its own text cache. 0 LLM.
usage: ft_embed.py <tag> [set ...]"""
import os, sys, time, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); import dlib, embed_all
tag = sys.argv[1]; W = embed_all.W + tag + "/"; os.makedirs(W, exist_ok=True)
S = embed_all.sets(); want = sys.argv[2:] or list(S)
for k in want:
    ids, ys, U = zip(*S[k]); t0 = time.time()
    X, _ = dlib.embed_turns(list(U), cache=W + "cache.npz")
    np.savez(W + f"emb.{k}.npz", ids=np.array(ids), labels=np.array(ys), vecs=X); print(k, len(ids), f"{time.time()-t0:.0f}s", flush=True)
