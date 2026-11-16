//! Test helper: writes a 440 Hz left / 880 Hz right sine through the real
//! Ring into tap <id> (default 62), in 512-frame blocks like a host would.
//! Used by tests/test_tap.py to check the Rust writer and Python reader agree.
use mixbuddy_tap::ring::Ring;

fn main() {
    let id: u32 = std::env::args().nth(1).and_then(|s| s.parse().ok()).unwrap_or(62);
    let sr = 48_000u32;
    let mut ring = Ring::open(id, sr, sr * 10).expect("open tap");
    let (mut l, mut r) = (vec![0f32; 512], vec![0f32; 512]);
    let mut n = 0u64;
    for _ in 0..(sr as usize * 13 / 512) {
        for i in 0..512 {
            let t = (n + i as u64) as f32 / sr as f32;
            l[i] = 0.5 * (2.0 * std::f32::consts::PI * 440.0 * t).sin();
            r[i] = 0.25 * (2.0 * std::f32::consts::PI * 880.0 * t).sin();
        }
        ring.write(&l, &r);
        n += 512;
    }
    println!("{n}");
}
