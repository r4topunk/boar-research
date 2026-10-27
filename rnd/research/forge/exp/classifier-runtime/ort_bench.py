import onnxruntime as ort, numpy as np, time, sys, json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
tk=AutoTokenizer.from_pretrained('mmbert-small-cls'); m=AutoModelForSequenceClassification.from_pretrained('mmbert-small-cls').eval()
so=ort.SessionOptions(); so.intra_op_num_threads=2; so.inter_op_num_threads=1; so.graph_optimization_level=ort.GraphOptimizationLevel.ORT_ENABLE_ALL
S={n:ort.InferenceSession(f,so,providers=['CPUExecutionProvider']) for n,f in [('fp32','mmbert-small-cls.onnx'),('int8','mmbert-small-cls-int8.onnx')]}
# parity on 2 real texts + a 150-token text (sliding window path)
long=' '.join(['Meu filho foi picado por um escorpião e está com dor forte no braço.']*9)
for t in ['My chest hurts and my left arm is numb','Which side won the American Civil War?',long]:
    e=tk(t,return_tensors='np'); 
    with torch.no_grad(): ref=m(**{k:torch.tensor(v) for k,v in e.items()}).logits[0].numpy()
    out={n:s.run(None,{'input_ids':e['input_ids'].astype(np.int64),'attention_mask':e['attention_mask'].astype(np.int64)})[0][0] for n,s in S.items()}
    print(len(e['input_ids'][0]),'tok HF',np.round(ref,3),{n:np.round(v,3).tolist() for n,v in out.items()})
best={}
for rep in range(4):
  for n in [16,32,64,128]:
    ids=np.full((1,n),5000,dtype=np.int64); ids[0,0]=2; ids[0,-1]=1; am=np.ones((1,n),dtype=np.int64)
    for name,s in S.items():
        ts=[]
        for _ in range(8):
            t0=time.perf_counter(); s.run(None,{'input_ids':ids,'attention_mask':am}); ts.append((time.perf_counter()-t0)*1000)
        best[(name,n)]=min(best.get((name,n),1e9),min(ts))
for k in sorted(best): print(k,'min ms',round(best[k],1))
