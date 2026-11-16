//! MixBuddy Tap (v0)
//!
//! A passthrough effect for FL Studio's mixer. It does not change the audio.
//! It keeps the last `CAPACITY_SECONDS` of what it hears in a memory-mapped
//! file so the mix-buddy MCP server (Python) can analyze a mixer track live.
//!
//! File: `<temp dir>/mixbuddy/tap_<id>.bin` (on Windows, %TEMP%\mixbuddy).
//! The "Tap ID" parameter picks <id>; give every instance a different ID.
//! FL's controller script reads that parameter to know which mixer track
//! each tap sits on.
//!
//! Layout (little endian), see `ring` below and `mcp_server/tap_reader.py`:
//!   0  magic  b"MBTAP001"
//!   8  u32    format version (1)
//!  12  u32    tap id
//!  16  u32    sample rate
//!  20  u32    channels (always 2; mono input is duplicated)
//!  24  u32    capacity in frames
//!  28  u32    reserved
//!  32  u64    write position: total frames written (atomic, Release)
//!  40  u64    last update, unix ms (atomic)
//!  48  u64    sequence: bumped on every (re)open
//!  56  u64    reserved
//!  64  f32[]  interleaved ring buffer, capacity * channels samples

use nih_plug::prelude::*;
use std::sync::Arc;

pub mod ring;

const CAPACITY_SECONDS: f32 = 10.0;

pub struct MixBuddyTap {
    params: Arc<TapParams>,
    sample_rate: f32,
    ring: Option<ring::Ring>,
    open_id: i32,
}

#[derive(Params)]
struct TapParams {
    /// Which tap file this instance writes. Unique per instance.
    #[id = "tapid"]
    pub tap_id: IntParam,
}

impl Default for TapParams {
    fn default() -> Self {
        Self {
            tap_id: IntParam::new("Tap ID", 1, IntRange::Linear { min: 1, max: 64 }),
        }
    }
}

impl Default for MixBuddyTap {
    fn default() -> Self {
        Self {
            params: Arc::new(TapParams::default()),
            sample_rate: 44100.0,
            ring: None,
            open_id: 0,
        }
    }
}

impl MixBuddyTap {
    fn open(&mut self) {
        let id = self.params.tap_id.value();
        let cap = (self.sample_rate * CAPACITY_SECONDS).ceil() as u32;
        match ring::Ring::open(id as u32, self.sample_rate as u32, cap) {
            Ok(r) => {
                self.ring = Some(r);
                self.open_id = id;
            }
            Err(e) => {
                nih_log!("MixBuddy Tap: could not open tap file: {e}");
                self.ring = None;
                self.open_id = id;
            }
        }
    }
}

impl Plugin for MixBuddyTap {
    const NAME: &'static str = "MixBuddy Tap";
    const VENDOR: &'static str = "Boroma Studios";
    const URL: &'static str = "";
    const EMAIL: &'static str = "";
    const VERSION: &'static str = env!("CARGO_PKG_VERSION");

    const AUDIO_IO_LAYOUTS: &'static [AudioIOLayout] = &[
        AudioIOLayout {
            main_input_channels: NonZeroU32::new(2),
            main_output_channels: NonZeroU32::new(2),
            ..AudioIOLayout::const_default()
        },
        AudioIOLayout {
            main_input_channels: NonZeroU32::new(1),
            main_output_channels: NonZeroU32::new(1),
            ..AudioIOLayout::const_default()
        },
    ];

    const SAMPLE_ACCURATE_AUTOMATION: bool = false;
    type SysExMessage = ();
    type BackgroundTask = ();

    fn params(&self) -> Arc<dyn Params> {
        self.params.clone()
    }

    fn initialize(
        &mut self,
        _layout: &AudioIOLayout,
        config: &BufferConfig,
        _context: &mut impl InitContext<Self>,
    ) -> bool {
        self.sample_rate = config.sample_rate;
        self.open();
        // Passthrough works even if the tap file could not be opened.
        true
    }

    fn process(
        &mut self,
        buffer: &mut Buffer,
        _aux: &mut AuxiliaryBuffers,
        _context: &mut impl ProcessContext<Self>,
    ) -> ProcessStatus {
        // Changing "Tap ID" while running reopens the file once. That is a
        // rare, user-initiated event, so it is allowed off the strict
        // no-allocation path.
        if self.params.tap_id.value() != self.open_id {
            nih_plug::util::permit_alloc(|| self.open());
        }
        if let Some(ring) = self.ring.as_mut() {
            let slices = buffer.as_slice_immutable();
            match slices.len() {
                0 => {}
                1 => ring.write(slices[0], slices[0]),
                _ => ring.write(slices[0], slices[1]),
            }
        }
        // Audio is left untouched: this is a passthrough.
        ProcessStatus::Normal
    }
}

impl ClapPlugin for MixBuddyTap {
    const CLAP_ID: &'static str = "studio.boroma.mixbuddy-tap";
    const CLAP_DESCRIPTION: Option<&'static str> =
        Some("Shares the last seconds of a mixer track with mix-buddy");
    const CLAP_MANUAL_URL: Option<&'static str> = None;
    const CLAP_SUPPORT_URL: Option<&'static str> = None;
    const CLAP_FEATURES: &'static [ClapFeature] = &[ClapFeature::AudioEffect, ClapFeature::Analyzer, ClapFeature::Utility];
}

#[cfg(feature = "vst3")]
impl Vst3Plugin for MixBuddyTap {
    const VST3_CLASS_ID: [u8; 16] = *b"MixBuddyTapV0001";
    const VST3_SUBCATEGORIES: &'static [Vst3SubCategory] =
        &[Vst3SubCategory::Fx, Vst3SubCategory::Analyzer, Vst3SubCategory::Tools];
}

nih_export_clap!(MixBuddyTap);
#[cfg(feature = "vst3")]
nih_export_vst3!(MixBuddyTap);
