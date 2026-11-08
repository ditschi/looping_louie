//! Step 0 of docs/firmware-architecture.md 11: board definition and thin wrappers around the ESP-IDF C API,
//! shared by the bring-up binary (`src/main.rs`) and the pre-order probes (`examples/`).
//!
//! The wrappers call `esp-idf-sys` directly. They are deliberately small; the HAL traits of the real firmware
//! (`louie-app::hal`, docs/firmware-architecture.md 3) come later and will build on what proves itself here.

pub mod board;
pub mod console;
pub mod diag;
pub mod hw;
pub mod sleep;

/// Common start for every binary: runtime patches, logger, boot banner.
pub fn init(name: &str) {
    esp_idf_svc::sys::link_patches();
    esp_idf_svc::log::EspLogger::initialize_default();
    diag::banner(name);
}
