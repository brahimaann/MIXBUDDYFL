//! The plugin's window: which track the tap is assigned to, whether audio is
//! reaching mix-buddy, and an input level meter.

use nih_plug::prelude::*;
use nih_plug_egui::egui::{self, Color32, RichText, Stroke, Vec2};
use nih_plug_egui::{create_egui_editor, EguiState};
use std::sync::atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering};
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

use crate::{TapParams, UNASSIGNED};

/// Values the audio thread publishes for the window. Lock-free.
#[derive(Default)]
pub struct Shared {
    peak_l: AtomicU32,
    peak_r: AtomicU32,
    pub last_audio_ms: AtomicU64,
    pub file_ok: AtomicBool,
}

impl Shared {
    pub fn set_peaks(&self, l: f32, r: f32) {
        self.peak_l.store(l.to_bits(), Ordering::Relaxed);
        self.peak_r.store(r.to_bits(), Ordering::Relaxed);
    }
    fn peaks(&self) -> (f32, f32) {
        (f32::from_bits(self.peak_l.load(Ordering::Relaxed)),
         f32::from_bits(self.peak_r.load(Ordering::Relaxed)))
    }
}

pub fn now_ms() -> u64 {
    SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_millis() as u64).unwrap_or(0)
}

pub fn default_state() -> Arc<EguiState> {
    EguiState::from_size(300, 210)
}

struct Ui {
    shown_l: f32,
    shown_r: f32,
}

const GREEN: Color32 = Color32::from_rgb(80, 200, 120);
const AMBER: Color32 = Color32::from_rgb(230, 170, 60);
const RED: Color32 = Color32::from_rgb(230, 90, 80);

fn db(x: f32) -> f32 {
    if x <= 1e-6 { -96.0 } else { 20.0 * x.log10() }
}

fn meter(ui: &mut egui::Ui, label: &str, level: f32) {
    let d = db(level);
    ui.horizontal(|ui| {
        ui.label(RichText::new(label).monospace());
        let (rect, _) = ui.allocate_exact_size(Vec2::new(190.0, 12.0), egui::Sense::hover());
        let p = ui.painter();
        p.rect_filled(rect, 2.0f32, Color32::from_gray(40));
        // -60 dBFS .. 0 dBFS
        let frac = ((d + 60.0) / 60.0).clamp(0.0, 1.0);
        let mut fill = rect;
        fill.set_width(rect.width() * frac);
        let col = if d > -1.0 { RED } else if d > -12.0 { AMBER } else { GREEN };
        p.rect_filled(fill, 2.0f32, col);
        p.rect_stroke(rect, 2.0f32, Stroke::new(1.0_f32, Color32::from_gray(70)), egui::StrokeKind::Inside);
        ui.label(RichText::new(if d <= -95.0 { " -inf".to_string() } else { format!("{d:5.1}") })
            .monospace());
    });
}

pub fn create(params: Arc<TapParams>, shared: Arc<Shared>) -> Option<Box<dyn Editor>> {
    create_egui_editor(
        params.editor_state.clone(),
        Ui { shown_l: 0.0, shown_r: 0.0 },
        |_, _| {},
        move |ctx, _setter, st| {
            ctx.request_repaint();
            let (l, r) = shared.peaks();
            // Fast attack, slow fall so the meter is readable.
            st.shown_l = if l > st.shown_l { l } else { st.shown_l * 0.9 };
            st.shown_r = if r > st.shown_r { r } else { st.shown_r * 0.9 };

            egui::CentralPanel::default().show(ctx, |ui| {
                ui.heading("MixBuddy Tap");
                ui.add_space(6.0);

                let id = params.tap_id.value();
                if id == UNASSIGNED {
                    ui.label(RichText::new("Track: not assigned yet").color(AMBER));
                    ui.label(RichText::new("Ask Claude to analyze this track; it assigns itself.")
                        .small());
                } else if id == 0 {
                    ui.label(RichText::new("Track: Master").strong());
                } else {
                    ui.label(RichText::new(format!("Track: insert {id}")).strong());
                }

                let age = now_ms().saturating_sub(shared.last_audio_ms.load(Ordering::Relaxed));
                let (dot, text, col) = if !shared.file_ok.load(Ordering::Relaxed) {
                    ("x", "Can't write the tap file".to_string(), RED)
                } else if shared.last_audio_ms.load(Ordering::Relaxed) == 0 || age > 1500 {
                    ("o", "No audio (press play)".to_string(), AMBER)
                } else if st.shown_l.max(st.shown_r) < 1e-5 {
                    ("o", "Running, but silent".to_string(), AMBER)
                } else {
                    ("*", "Sending audio to mix-buddy".to_string(), GREEN)
                };
                ui.label(RichText::new(format!("{dot} {text}")).color(col));
                ui.add_space(8.0);

                meter(ui, "L", st.shown_l);
                meter(ui, "R", st.shown_r);
                ui.add_space(8.0);
                ui.label(RichText::new("Audio passes through unchanged. The last 10 s are shared \
                                        with mix-buddy. Put this last in the chain.").small());
            });
        },
    )
}
