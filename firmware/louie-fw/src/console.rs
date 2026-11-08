//! Single-key commands from the primary console (UART0 = CH343 port on the Waveshare board).
//!
//! Without an installed UART driver the ESP-IDF console reads non-blocking: no key → error or 0 bytes.
//! The secondary console (USB-Serial-JTAG) is output only.

use std::io::Read;

/// Next key if one is waiting, otherwise `None`. Never blocks.
pub fn poll_key() -> Option<u8> {
    let mut buf = [0u8; 1];
    match std::io::stdin().lock().read(&mut buf) {
        Ok(1) => Some(buf[0]),
        _ => None,
    }
}

/// Wait up to `ms` for a key, polling every 10 ms.
pub fn wait_key(ms: u32) -> Option<u8> {
    for _ in 0..ms.div_ceil(10) {
        if let Some(k) = poll_key() {
            return Some(k);
        }
        std::thread::sleep(std::time::Duration::from_millis(10));
    }
    None
}

/// Print a key menu, one line per entry.
pub fn menu(entries: &[(&str, &str)]) {
    log::info!("Keys (CH343/UART port):");
    for (key, text) in entries {
        log::info!("  {key:<3} {text}");
    }
}
