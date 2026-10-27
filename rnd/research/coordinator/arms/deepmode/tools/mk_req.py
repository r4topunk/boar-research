# DEEPMODE requests (0 LLM). Set A = TOPICS27 Detailed requests, set B = PARA135 p1 requests (CV5 51, K1 kit), with ONLY the settings changed:
# personalityId "detailed" (persona override keys removed), alwaysComplete true (= the app's Deep Research toggle, src/models/settings.ts:499), runId/arm renamed.
import json
A = "<workspace>/rnd/research/coordinator/arms/"
def conv(src, run, dst):
    out = []
    for l in open(src):
        r = json.loads(l); s = r["config"]["settings"]
        for k in ("personaSystemPrompt", "personaStyleReminder"): s.pop(k, None)
        s["personalityId"] = "detailed"; s["alwaysComplete"] = True
        r["runId"] = run; r["config"]["arm"] = "cut7-headpass-x2+litepacks+deepmode"; out.append(json.dumps(r))
    open(dst, "w").write("\n".join(out) + "\n"); print(dst, len(out))
conv(A + "topics27/in/t27-detailed-s42.requests.jsonl", "dm-a-deep-s42", A + "deepmode/in/dm-a-deep-s42.requests.jsonl")
conv(A + "para135/in/p135-b-p1-s42.requests.jsonl", "dm-b-deep-s42", A + "deepmode/in/dm-b-deep-s42.requests.jsonl")
