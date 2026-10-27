// fzstd (the app's pure-JS zstd) on the same per-question blocks as bench_c.c; best of 5 passes per question.
// Prelude (generated) defines BLOBS_B64 and PER. Runs under Node and the Hermes CLI.
var now = typeof performance !== "undefined" ? function () { return performance.now(); } : function () { return Date.now(); };
var out = typeof print === "function" ? print : function (s) { console.log(s); };
var B = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/", L = new Uint8Array(128);
for (var i = 0; i < 64; i++) L[B.charCodeAt(i)] = i;
function b64(s) { var n = (s.length * 3) >> 2; if (s.endsWith("==")) n -= 2; else if (s.endsWith("=")) n -= 1; var o = new Uint8Array(n), j = 0;
  for (var i = 0; i < s.length; i += 4) { var v = (L[s.charCodeAt(i)] << 18) | (L[s.charCodeAt(i + 1)] << 12) | (L[s.charCodeAt(i + 2)] << 6) | L[s.charCodeAt(i + 3)];
    if (j < n) o[j++] = (v >> 16) & 255; if (j < n) o[j++] = (v >> 8) & 255; if (j < n) o[j++] = v & 255; } return o; }
var blobs = BLOBS_B64.map(b64), res = [];
for (var q = 0; q < PER.length; q++) {
  var best = 1e9;
  for (var r = 0; r < 5; r++) { var t = now(); for (var k = 0; k < PER[q].length; k++) fzstd.decompress(blobs[PER[q][k]]); var dt = now() - t; if (dt < best) best = dt; }
  res.push(best);
}
out(JSON.stringify(res));
