// Main-corpus semantic scan (retrieve.ts semanticSearch): 5300 chunks x 384-d float32, per question.
// A = today: rows -> Float32Array view per row + cosineSimilarity (dot + both norms) + object per row + sort.
// B = cached: one Float32Array matrix + precomputed row norms, dot only, top-k by a typed score array.
var now = typeof performance !== "undefined" ? function () { return performance.now(); } : function () { return Date.now(); };
var out = typeof print === "function" ? print : function (s) { console.log(s); };
var N = 5300, D = 384, seed = 1;
function rnd() { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff - 0.5; }
var rows = [];
for (var i = 0; i < N; i++) { var b = new Uint8Array(D * 4), f = new Float32Array(b.buffer); for (var j = 0; j < D; j++) f[j] = rnd(); rows.push({ chunk_id: "c" + i, body: "x", embedding: b }); }
var q = new Float32Array(D); for (var j = 0; j < D; j++) q[j] = rnd();
function cos(a, b) { var dot = 0, na = 0, nb = 0; for (var i = 0; i < a.length; i++) { dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; } return na === 0 || nb === 0 ? 0 : dot / (Math.sqrt(na) * Math.sqrt(nb)); }
function A() { var s = rows.map(function (r) { var v = new Float32Array(r.embedding.buffer, r.embedding.byteOffset, r.embedding.byteLength / 4); var sim = cos(q, v); return { chunkId: r.chunk_id, score: sim, similarity: sim }; }); s.sort(function (a, b) { return b.score - a.score; }); return s[0].chunkId; }
var M = new Float32Array(N * D), norms = new Float32Array(N);
for (var i = 0; i < N; i++) { var v = new Float32Array(rows[i].embedding.buffer); var n = 0; for (var j = 0; j < D; j++) { M[i * D + j] = v[j]; n += v[j] * v[j]; } norms[i] = Math.sqrt(n); }
function B() { var qn = 0; for (var j = 0; j < D; j++) qn += q[j] * q[j]; qn = Math.sqrt(qn); var sc = new Float32Array(N), best = -2, bi = -1;
  for (var i = 0; i < N; i++) { var o = i * D, dot = 0; for (var j = 0; j < D; j++) dot += q[j] * M[o + j]; sc[i] = dot / (qn * norms[i]); if (sc[i] > best) { best = sc[i]; bi = i; } } return "c" + bi; }
for (var name of ["A", "B"]) { var f = name === "A" ? A : B, r = 0, ts = []; for (var k = 0; k < 15; k++) { var t = now(); r = f(); ts.push(now() - t); } ts.sort(function (a, b) { return a - b; }); out(name + " min " + ts[0].toFixed(1) + " ms p50 " + ts[7].toFixed(1) + " ms (" + r + ")"); }
