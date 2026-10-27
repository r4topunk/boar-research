// Stub llama-server for retrieval-only replays (Sonar exp-34): instant fixed answer, so the engine's real retrieval,
// gates and compression run and --event-source-text / --dump-prompts capture the context. Never for judged runs.
import http from "node:http";
const port = Number(process.argv[2] ?? 18500), model = process.argv[3];
const sse = (res, datas) => { res.writeHead(200, { "content-type": "text/event-stream" }); for (const d of datas) res.write(`data: ${d}\n\n`); res.end(); };
http.createServer((req, res) => {
  let body = ""; req.on("data", (c) => (body += c)); req.on("end", () => {
    if (req.url === "/health") { res.writeHead(200, { "content-type": "application/json" }); return res.end('{"status":"ok"}'); }
    if (req.url === "/props") { res.writeHead(200, { "content-type": "application/json" }); return res.end(JSON.stringify({ model_path: model, chat_template: "stub" })); }
    const t = { prompt_n: 1, prompt_ms: 1, predicted_n: 2, predicted_ms: 1 };
    if (req.url === "/v1/chat/completions") return sse(res, [JSON.stringify({ choices: [{ index: 0, delta: { content: "Stub answer [1]." }, finish_reason: null }] }), JSON.stringify({ choices: [{ index: 0, delta: {}, finish_reason: "stop" }], timings: t }), "[DONE]"]);
    if (req.url === "/completion") return sse(res, [JSON.stringify({ content: "Stub answer [1].", stop: false }), JSON.stringify({ content: "", stop: true, timings: t })]);
    res.writeHead(404); res.end();
  });
}).listen(port, "127.0.0.1", () => console.log("stub on", port));
