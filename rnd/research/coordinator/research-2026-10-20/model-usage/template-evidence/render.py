import json, sys
from jinja2.sandbox import ImmutableSandboxedEnvironment
from jinja2 import StrictUndefined
env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True)
def raise_exception(m): raise Exception(m)
env.globals["raise_exception"] = raise_exception
tpl = env.from_string(open(sys.argv[1]).read())
msgs = json.load(open(sys.argv[2]))
kw = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
out = tpl.render(messages=msgs, add_generation_prompt=True, bos_token="", eos_token="<|im_end|>", tools=None, **kw)
open(sys.argv[3], "w").write(out)
