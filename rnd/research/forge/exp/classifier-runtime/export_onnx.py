import torch, time
from transformers import AutoTokenizer, AutoModelForSequenceClassification
tk = AutoTokenizer.from_pretrained('mmbert-small-cls'); m = AutoModelForSequenceClassification.from_pretrained('mmbert-small-cls', attn_implementation='eager').eval()
enc = tk('Meu filho foi picado por um escorpião, o que eu faço?', return_tensors='pt')
torch.onnx.export(m, (enc['input_ids'], enc['attention_mask']), 'mmbert-small-cls.onnx', input_names=['input_ids','attention_mask'], output_names=['logits'],
  dynamic_axes={'input_ids':{0:'b',1:'s'},'attention_mask':{0:'b',1:'s'}}, opset_version=17, dynamo=False)
from onnxruntime.quantization import quantize_dynamic, QuantType
quantize_dynamic('mmbert-small-cls.onnx', 'mmbert-small-cls-int8.onnx', weight_type=QuantType.QInt8)
print('ok')
