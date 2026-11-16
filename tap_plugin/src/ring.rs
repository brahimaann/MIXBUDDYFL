//! Memory-mapped ring buffer shared with the Python reader.
//! See the layout in lib.rs. Only `write` runs on the audio thread: it does
//! no allocation, locking or system calls apart from reading the clock.

use memmap2::MmapMut;
use std::fs::OpenOptions;
use std::io;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{SystemTime, UNIX_EPOCH};

pub const MAGIC: &[u8; 8] = b"MBTAP001";
pub const VERSION: u32 = 1;
pub const HEADER: usize = 64;
pub const CHANNELS: u32 = 2;

pub fn tap_dir() -> PathBuf {
    std::env::temp_dir().join("mixbuddy")
}

pub fn tap_path(id: u32) -> PathBuf {
    tap_dir().join(format!("tap_{id}.bin"))
}

pub struct Ring {
    map: MmapMut,
    capacity: u64,
    write_pos: u64,
}

impl Ring {
    /// Create or reuse the tap file and reset its header. Allocates and does
    /// I/O: call from `initialize`, never from the audio callback.
    pub fn open(id: u32, sample_rate: u32, capacity_frames: u32) -> io::Result<Ring> {
        std::fs::create_dir_all(tap_dir())?;
        let path = tap_path(id);
        let bytes = HEADER as u64 + capacity_frames as u64 * CHANNELS as u64 * 4;
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .truncate(false)
            .open(&path)?;
        file.set_len(bytes)?;
        // SAFETY: the file is ours and is never truncated while mapped by us.
        // Another process (the reader) only maps it read-only.
        let mut map = unsafe { MmapMut::map_mut(&file)? };

        let old_seq = if &map[0..8] == MAGIC {
            u64::from_le_bytes(map[48..56].try_into().unwrap())
        } else {
            0
        };
        // Zero the audio area so stale audio from an old session never reads
        // as current; this also faults the pages in before playback.
        for b in map[HEADER..].iter_mut() {
            *b = 0;
        }
        map[0..8].copy_from_slice(MAGIC);
        map[8..12].copy_from_slice(&VERSION.to_le_bytes());
        map[12..16].copy_from_slice(&id.to_le_bytes());
        map[16..20].copy_from_slice(&sample_rate.to_le_bytes());
        map[20..24].copy_from_slice(&CHANNELS.to_le_bytes());
        map[24..28].copy_from_slice(&capacity_frames.to_le_bytes());
        map[28..32].copy_from_slice(&0u32.to_le_bytes());
        map[32..40].copy_from_slice(&0u64.to_le_bytes());
        map[40..48].copy_from_slice(&0u64.to_le_bytes());
        map[48..56].copy_from_slice(&(old_seq.wrapping_add(1)).to_le_bytes());
        map.flush()?;
        Ok(Ring { map, capacity: capacity_frames as u64, write_pos: 0 })
    }

    fn atomic(&self, offset: usize) -> &AtomicU64 {
        // SAFETY: offsets 32 and 40 are 8-byte aligned (page-aligned mapping),
        // in bounds, and only ever accessed as u64 through atomics.
        unsafe { &*(self.map.as_ptr().add(offset) as *const AtomicU64) }
    }

    /// Append one block. `left` and `right` must have the same length.
    pub fn write(&mut self, left: &[f32], right: &[f32]) {
        let n = left.len().min(right.len());
        if n == 0 || self.capacity == 0 {
            return;
        }
        let cap = self.capacity;
        let base = self.map.as_mut_ptr();
        for i in 0..n {
            let frame = (self.write_pos + i as u64) % cap;
            let off = HEADER + (frame as usize) * 8;
            // SAFETY: off + 8 <= HEADER + cap * 8 = map length.
            unsafe {
                std::ptr::copy_nonoverlapping(left[i].to_le_bytes().as_ptr(), base.add(off), 4);
                std::ptr::copy_nonoverlapping(right[i].to_le_bytes().as_ptr(), base.add(off + 4), 4);
            }
        }
        self.write_pos += n as u64;
        // Publish samples before the new position (Release pairs with the
        // reader's re-check of the position).
        self.atomic(32).store(self.write_pos, Ordering::Release);
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_millis() as u64)
            .unwrap_or(0);
        self.atomic(40).store(now, Ordering::Release);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn writes_wrap_and_publish() {
        let id = 63;
        let mut r = Ring::open(id, 1000, 100).unwrap();
        let l: Vec<f32> = (0..150).map(|i| i as f32).collect();
        let rr: Vec<f32> = (0..150).map(|i| -(i as f32)).collect();
        r.write(&l, &rr);
        let m = std::fs::read(tap_path(id)).unwrap();
        assert_eq!(&m[0..8], MAGIC);
        let pos = u64::from_le_bytes(m[32..40].try_into().unwrap());
        assert_eq!(pos, 150);
        // Frame 149 lands in slot 49 after wrapping.
        let off = HEADER + 49 * 8;
        let l49 = f32::from_le_bytes(m[off..off + 4].try_into().unwrap());
        let r49 = f32::from_le_bytes(m[off + 4..off + 8].try_into().unwrap());
        assert_eq!((l49, r49), (149.0, -149.0));
    }
}
