#!/usr/bin/env python3
"""Stub llama-server for prompt capture (0 generation). Usage: python3 -I stub_server.py <port> <model_path>
Answers /health, /props and streams a fixed one-sentence reply on /v1/chat/completions and /completion,
so the adapter's --dump-prompts records the exact messages the engine builds. Writes nothing."""
import json, sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

PORT, MODEL = int(sys.argv[1]), sys.argv[2]
REPLY = "The sources do not say this."


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith("/health"):
            return self._json({"status": "ok"})
        if self.path.startswith("/props"):
            return self._json({"chat_template": "{{ stub }}", "model_path": MODEL})
        return self._json({"error": "nf"}, 404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(n)
        t = {"prompt_n": 0, "prompt_ms": 0.0, "predicted_n": 7, "predicted_ms": 1.0}
        if self.path.startswith("/v1/chat/completions"):
            parts = [{"choices": [{"delta": {"content": REPLY}, "finish_reason": None}]},
                     {"choices": [{"delta": {}, "finish_reason": "stop"}], "timings": t}, "[DONE]"]
        elif self.path.startswith("/completion"):
            parts = [{"content": REPLY, "stop": False}, {"content": "", "stop": True, "timings": t}]
        else:
            return self._json({"error": "nf"}, 404)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        for p in parts:
            self.wfile.write(("data: " + (p if isinstance(p, str) else json.dumps(p)) + "\n\n").encode())
        self.wfile.flush()


ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
