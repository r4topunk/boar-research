// Smoke-only stub of llama-server (no model, no CPU): /health, /props (model_path = the run's GGUF name), streaming /v1/chat/completions.
// Records every request body to <log>. Lets the plumbing (requests, places, D4 rewrite, facts override) be tested while another arm owns the CPU.
// Usage: node fake_server.mjs <port> <log.jsonl>
import { createServer } from "node:http";
import { appendFileSync } from "node:fs";
const [port, logPath] = process.argv.slice(2);
createServer((req, res) => {
  let body = "";
  req.on("data", (d) => (body += d));
  req.on("end", () => {
    if (req.url === "/health") return res.writeHead(200, { "content-type": "application/json" }).end('{"status":"ok"}');
    if (req.url === "/props") return res.writeHead(200, { "content-type": "application/json" }).end(JSON.stringify({ model_path: "/stub/Qwen3-4B-Instruct-2507-Q4_K_M.gguf", chat_template: "{{stub}}" }));
    if (req.method === "POST") {
      appendFileSync(logPath, JSON.stringify({ url: req.url, body: JSON.parse(body || "{}") }) + "\n");
      res.writeHead(200, { "content-type": "text/event-stream" });
      res.write(`data: ${JSON.stringify({ choices: [{ delta: { content: "Stub answer for the smoke test." } }] })}\n\n`);
      res.write(`data: ${JSON.stringify({ choices: [{ delta: {}, finish_reason: "stop" }], timings: { prompt_n: 1, prompt_ms: 1, predicted_n: 7, predicted_ms: 1 } })}\n\n`);
      return res.end("data: [DONE]\n\n");
    }
    res.writeHead(404).end();
  });
}).listen(Number(port), "127.0.0.1");
