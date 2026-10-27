import json, subprocess, sys, torch, numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
tk = AutoTokenizer.from_pretrained('mmbert-small-cls'); m = AutoModelForSequenceClassification.from_pretrained('mmbert-small-cls').eval()
TEXTS = ['Meu filho foi picado por um escorpião, o que eu faço?', 'My chest hurts and my left arm is numb', '¿Qué hago si alguien convulsiona?', 'Which side won the American Civil War?']
def llama(gguf, text, pool):
    out = subprocess.run(['llama.cpp/build/bin/llama-embedding','-m',gguf,'-p',text,'--pooling',pool,'--embd-normalize','-1','--embd-output-format','json','-t','2','-c','512'],capture_output=True,text=True).stdout
    return np.array(json.loads(out[out.index('{'):])['data'][0]['embedding'])
cos = lambda a,b: float(a@b/np.linalg.norm(a)/np.linalg.norm(b))
for t in TEXTS:
    enc = tk(t, return_tensors='pt')
    with torch.no_grad():
        h = m.model(**enc).last_hidden_state[0]; mean = h.mean(0).numpy(); logits = m(**enc).logits[0].numpy()
    row = [t[:30]]
    for g in ['mmbert-small-cls-q8_0.gguf','mmbert-small-cls-q8-te4.gguf']:
        e = llama(g, t, 'mean'); r = llama(g, t, 'rank')
        row += [f"{g.split('-')[-1][:4]} cos_mean={cos(e,mean):.4f} rank={np.round(r,3).tolist()}"]
    print(*row, f"HF logits={np.round(logits,3).tolist()}", sep=' | ')
