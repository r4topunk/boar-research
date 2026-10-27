// Native ceiling in Rust on the same per-question blocks: `zstd` crate (libzstd bindings) and `ruzstd` (pure Rust).
use std::{fs, io::Read, time::Instant};
fn main() {
    let data = fs::read("../blobs.bin").unwrap();
    let mut blobs = vec![]; let mut o = 0;
    while o < data.len() { let n = u32::from_le_bytes(data[o..o + 4].try_into().unwrap()) as usize; blobs.push(&data[o + 4..o + 4 + n]); o += 4 + n; }
    let per: Vec<Vec<usize>> = fs::read_to_string("../blobs.idx").unwrap().lines().map(|l| l.split_whitespace().map(|x| x.parse().unwrap()).collect()).collect();
    let mut dctx = zstd::bulk::Decompressor::new().unwrap();
    for name in ["zstd-crate", "ruzstd"] {
        let mut v = vec![];
        for q in &per {
            let mut best = f64::MAX;
            for _ in 0..5 {
                let t = Instant::now();
                for &i in q {
                    let out = if name == "zstd-crate" { dctx.decompress(blobs[i], 1 << 22).unwrap() } else {
                        let mut d = ruzstd::decoding::StreamingDecoder::new(blobs[i]).unwrap(); let mut out = Vec::new(); d.read_to_end(&mut out).unwrap(); out };
                    std::hint::black_box(out);
                }
                best = best.min(t.elapsed().as_secs_f64() * 1e3);
            }
            v.push(best);
        }
        let mut s = v.clone(); s.sort_by(|a, b| a.partial_cmp(b).unwrap());
        println!("{name}: per question p50 {:.2} ms p90 {:.2} ms total {:.1} ms", s[s.len() / 2], s[((s.len() - 1) as f64 * 0.9).round() as usize], v.iter().sum::<f64>());
    }
}
